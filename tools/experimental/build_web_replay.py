#!/usr/bin/env python3
"""Replay current web configuration to a restarted vendor httpd.

The backed-up CLI supplies its original loader and native libraries. This copy
only reads three shared data-model objects, then replays the existing HTTP,
authentication challenge, and user messages. It never invokes object setters,
flash writes, configuration save, reset, GPON or VLAN changes.
"""
import hashlib
import os
import io
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parents[2] / "local-private" / "helpers" / "web_replay"
SOURCE = HERE / "rootfs2/bin/cli"
OUTPUT = HERE / "serve/ont_web_replay"
BODY = 0x1DA14
SOURCE_SHA = "972014acf7442d3ce7860486e9bcfc3096c5cd41bcb57c7abb9e5f0316678767"
IMPORTS = {
    "oal_sys_readFunctionCodeFlash": "rsl_sendHttpdAuthChallenge",
    "oal_sys_readZoneFlash": "rsl_sendHttpdUserCfg",
    "oal_sys_resetButtonStatus": "msg_connCliAndSend",
}


def branch(source, target, link=False):
    delta = target - source - 8
    assert delta % 4 == 0 and -(1 << 25) <= delta < (1 << 25)
    return (0xEB000000 if link else 0xEA000000) | ((delta >> 2) & 0xFFFFFF)


def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA
    elf = ELFFile(io.BytesIO(original))
    assert elf["e_entry"] == 0x11BD8 and elf["e_machine"] == "EM_ARM"
    rx_index, rx = next((i, s) for i, s in enumerate(elf.iter_segments())
                        if s["p_type"] == "PT_LOAD" and s["p_flags"] == 5)
    assert rx["p_vaddr"] == 0x10000 and rx["p_offset"] == 0
    assert rx["p_filesz"] == rx["p_memsz"] == BODY - 0x10000
    gap_start, gap_end = BODY - 0x10000, 0xDEEC
    assert not any(original[gap_start:gap_end])
    symbols = elf.get_section_by_name(".dynsym")
    dynstr = elf.get_section_by_name(".dynstr")
    plt = elf.get_section_by_name(".plt")
    functions = {symbols.get_symbol(r["r_info_sym"]).name:
                 plt["sh_addr"] + 20 + i * 12
                 for i, r in enumerate(elf.get_section_by_name(".rel.plt").iter_relocations())}
    for old, new in IMPORTS.items():
        functions[new] = functions[old]
    functions = {k: functions[k] for k in (
        "dm_shmInit", "memset", "rdp_getObjStruct", "memcpy", "printf",
        "msg_connCliAndSend", "rsl_sendHttpdAuthChallenge", "rsl_sendHttpdUserCfg")}

    # Assemble instructions, local branches, and literal pools independently.
    # Only absolute addresses and external ARM call relocations need fixing.
    assembly = Path(__file__).with_name("web-replay-payload.S")
    object_file = HERE / "web-replay-payload.o"
    subprocess.run([os.environ.get("ONT_CLANG", "clang"), "--target=arm-linux-gnueabi",
                    "-march=armv5te", "-marm", "-c", str(assembly),
                    "-o", str(object_file)], check=True)
    object_file.chmod(0o600)
    obj = ELFFile(io.BytesIO(object_file.read_bytes()))
    payload = bytearray(obj.get_section_by_name(".text").data())
    relocations = []
    symtab = obj.get_section_by_name(".symtab")
    for rel in obj.get_section_by_name(".rel.text").iter_relocations():
        offset, kind = rel["r_offset"], rel["r_info_type"]
        symbol = symtab.get_symbol(rel["r_info_sym"])
        old_word = struct.unpack_from("<I", payload, offset)[0]
        if kind == 28:  # R_ARM_CALL; assembler encodes a -8 addend.
            assert old_word == 0xEBFFFFFE
            if symbol["st_shndx"] == "SHN_UNDEF":
                target = functions[symbol.name]
            else:
                assert symbol["st_shndx"] == obj.get_section_index(".text")
                target = BODY + symbol["st_value"]
            word = branch(BODY + offset, target, link=True)
        elif kind == 2:  # R_ARM_ABS32; literal pointing inside .text.
            assert symbol["st_shndx"] == obj.get_section_index(".text")
            word = BODY + symbol["st_value"] + old_word
        else:
            raise AssertionError((kind, symbol.name, hex(offset)))
        struct.pack_into("<I", payload, offset, word)
        relocations.append({"offset": offset, "type": kind, "symbol": symbol.name})
    assert gap_start + len(payload) <= gap_end

    result = bytearray(original)
    changes = []
    for old, new in IMPORTS.items():
        symbol = next(s for s in symbols.iter_symbols() if s.name == old)
        assert symbol["st_shndx"] == "SHN_UNDEF"
        start = dynstr["sh_offset"] + symbol["st_name"]
        length = len(old) + 1
        assert len(new) <= len(old)
        assert original[start:start + length] == old.encode() + b"\0"
        assert all(s["st_name"] == symbol["st_name"] or
                   not symbol["st_name"] < s["st_name"] < symbol["st_name"] + length
                   for s in symbols.iter_symbols())
        result[start:start + length] = (new.encode() + b"\0").ljust(length, b"\0")
        changes.append({"offset": start, "bytes": length, "old": old, "new": new})
    assert struct.unpack_from("<I", original, 0x29E0)[0] == 0xE59F4060
    struct.pack_into("<I", result, 0x29E0, branch(0x129E0, BODY))
    changes.append({"offset": 0x29E0, "bytes": 4, "purpose": "replace CLI entry"})
    assert struct.unpack_from("<I", original, 0x1BD0)[0] == 0xE3A00000
    struct.pack_into("<I", result, 0x1BD0, 0xE1A00000)
    changes.append({"offset": 0x1BD0, "bytes": 4, "purpose": "preserve helper exit status"})
    result[gap_start:gap_start + len(payload)] = payload
    changes.append({"offset": gap_start, "bytes": len(payload), "purpose": "replay payload"})
    header_offset = elf["e_phoff"] + rx_index * elf["e_phentsize"] + 16
    struct.pack_into("<II", result, header_offset,
                     gap_start + len(payload), gap_start + len(payload))
    changes.append({"offset": header_offset, "bytes": 8, "purpose": "map RX payload"})

    allowed = {i for c in changes for i in range(c["offset"], c["offset"] + c["bytes"])}
    assert len(result) == len(original)
    assert all(a == b or i in allowed for i, (a, b) in enumerate(zip(original, result)))
    assert result[gap_end:] == original[gap_end:]
    updated = ELFFile(io.BytesIO(result))
    assert updated["e_entry"] == elf["e_entry"]
    for i, (before, after) in enumerate(zip(elf.iter_segments(), updated.iter_segments())):
        expected = dict(before.header)
        if i == rx_index:
            expected["p_filesz"] += len(payload)
            expected["p_memsz"] += len(payload)
        assert dict(after.header) == expected
    for old, new in IMPORTS.items():
        before = next(s for s in symbols.iter_symbols() if s.name == old)
        after = next(s for s in updated.get_section_by_name(".dynsym").iter_symbols() if s.name == new)
        assert dict(before.entry) == dict(after.entry)
    OUTPUT.write_bytes(result)
    OUTPUT.chmod(0o700)
    info = {
        "source_sha256": SOURCE_SHA,
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "bytes": len(result), "payload_bytes": len(payload),
        "payload_address": hex(BODY), "patch_regions": changes,
        "calls": functions, "relocations": relocations,
        "reads": {"DEV2_HTTP_CFG": 414, "DEV2_USER_CFG": 256, "DEV2_DEV_INFO": 1428},
        "messages": [2030, 2033, 2031], "destination_module": 14,
        "configuration_setters_added": False, "flash_write_calls_added": False,
        "live_execution_verified": False,
    }
    manifest = HERE / "web-replay-manifest.json"
    manifest.write_text(json.dumps(info, indent=2) + "\n")
    manifest.chmod(0o600)
    print(json.dumps({k: v for k, v in info.items() if k not in ["patch_regions", "relocations"]}, indent=2))


def main():
    import argparse
    import os
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                        help="locally extracted original binary; exact firmware SHA required")
    args = parser.parse_args()
    os.umask(0o077)
    SOURCE = args.source.resolve(strict=True)
    HERE.mkdir(mode=0o700, parents=True, exist_ok=True)
    (HERE / "serve").mkdir(mode=0o700, exist_ok=True)
    build()


if __name__ == "__main__":
    main()
