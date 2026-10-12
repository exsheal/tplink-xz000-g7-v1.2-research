#!/usr/bin/env python3
"""Build a RAM-only configuration reader from this ONT's backed-up CLI.

No device access. The installed CLI and the sealed backup are never modified.
The copied CLI calls only dm_shmInit(0) and dm_dumpCfg(), then returns.
"""
import hashlib
import json
import struct
from pathlib import Path

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parents[2] / "local-private" / "helpers" / "cfg_reader"
SOURCE = HERE / "rootfs2/bin/cli"
OUTPUT = HERE / "serve/ont_cfg_read"


def branch(source, target, *, link=False, condition=14):
    offset = target - (source + 8)
    assert offset % 4 == 0 and -(1 << 25) <= offset < (1 << 25)
    return (condition << 28) | (0x0B000000 if link else 0x0A000000) | ((offset >> 2) & 0xFFFFFF)


def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == "972014acf7442d3ce7860486e9bcfc3096c5cd41bcb57c7abb9e5f0316678767"
    with SOURCE.open("rb") as stream:
        elf = ELFFile(stream)
        assert elf["e_machine"] == "EM_ARM" and elf.little_endian
        assert elf["e_entry"] == 0x11BD8
        symbols = elf.get_section_by_name(".dynsym")
        start = next(s for s in symbols.iter_symbols() if s.name == "start_cli")
        address, length = start["st_value"], start["st_size"]
        assert (address, length) == (0x129E0, 120)
        segment = next(
            s for s in elf.iter_segments()
            if s["p_type"] == "PT_LOAD" and s["p_vaddr"] <= address < s["p_vaddr"] + s["p_filesz"]
        )
        offset = segment["p_offset"] + address - segment["p_vaddr"]
        plt = elf.get_section_by_name(".plt")
        functions = {
            symbols.get_symbol(r["r_info_sym"]).name: plt["sh_addr"] + 20 + i * 12
            for i, r in enumerate(elf.get_section_by_name(".rel.plt").iter_relocations())
        }
        assert functions["dm_shmInit"] == 0x118B0
        assert functions["dm_dumpCfg"] == 0x11B98
    assert original[offset:offset + 8] == bytes.fromhex("60409fe508402de9")
    instructions = [
        0xE92D4010,  # push {r4, lr}; maintain 8-byte stack alignment
        0xE3A00000,  # mov r0, #0: attach existing data model, do not create it
        branch(address + 8, functions["dm_shmInit"], link=True),
        0xE3500000,  # cmp r0, #0
        branch(address + 16, address + 24, condition=1),  # failure: return
        branch(address + 20, functions["dm_dumpCfg"], link=True),
        0xE8BD8010,  # pop {r4, pc}
    ]
    code = b"".join(struct.pack("<I", x) for x in instructions)
    code += struct.pack("<I", 0xE1A00000) * ((length - len(code)) // 4)
    result = bytearray(original)
    result[offset:offset + length] = code
    assert len(result) == len(original)
    assert result[:offset] == original[:offset]
    assert result[offset + length:] == original[offset + length:]
    OUTPUT.parent.mkdir(mode=0o700, exist_ok=True)
    OUTPUT.write_bytes(result)
    OUTPUT.chmod(0o700)
    info = {
        "source": str(SOURCE),
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "output": str(OUTPUT),
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "bytes": len(result),
        "patched_file_offset": hex(offset),
        "patched_function_address": hex(address),
        "patched_function_bytes": length,
        "calls": ["dm_shmInit(0)", "dm_dumpCfg()"],
        "live_execution_verified": False,
    }
    manifest = HERE / "cfg-reader-manifest.json"
    manifest.write_text(json.dumps(info, indent=2) + "\n")
    manifest.chmod(0o600)
    print(json.dumps(info, indent=2))


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
