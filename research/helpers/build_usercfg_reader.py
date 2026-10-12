#!/usr/bin/env python3
"""Build a read-only account query using the backed-up TP-Link CLI.

The original CLI and sealed backup stay unchanged. The copy attaches the
existing data model and calls rdp_getObj(3, DEV2_USER_CFG, zero_stack, attrs).
It never calls the account setters, save, reset, or any flash operations.
"""
import hashlib
import json
import struct
from pathlib import Path

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parents[2] / "local-private" / "helpers" / "usercfg_reader"
SOURCE = HERE / "rootfs2/bin/cli"
OUTPUT = HERE / "serve/ont_usercfg_read"
START = 0x129E0
BODY = 0x12A58
BODY_LENGTH = 0x12BE4 - BODY


def branch(source, target, *, link=False, condition=14):
    delta = target - source - 8
    assert delta % 4 == 0 and -(1 << 25) <= delta < (1 << 25)
    return (condition << 28) | (0x0B000000 if link else 0x0A000000) | ((delta >> 2) & 0xFFFFFF)


def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == "972014acf7442d3ce7860486e9bcfc3096c5cd41bcb57c7abb9e5f0316678767"
    with SOURCE.open("rb") as stream:
        elf = ELFFile(stream)
        assert elf["e_machine"] == "EM_ARM" and elf.little_endian
        assert elf["e_entry"] == 0x11BD8
        symbols = elf.get_section_by_name(".dynsym")
        start = next(s for s in symbols.iter_symbols() if s.name == "start_cli")
        assert (start["st_value"], start["st_size"]) == (START, 120)
        segment = next(s for s in elf.iter_segments() if s["p_type"] == "PT_LOAD" and s["p_vaddr"] <= START < s["p_vaddr"] + s["p_filesz"])
        assert segment["p_vaddr"] - segment["p_offset"] == 0x10000
        plt = elf.get_section_by_name(".plt")
        functions = {
            symbols.get_symbol(r["r_info_sym"]).name: plt["sh_addr"] + 20 + i * 12
            for i, r in enumerate(elf.get_section_by_name(".rel.plt").iter_relocations())
        }

    words = []
    labels = {}
    pending = []
    constants = {}

    def emit(value):
        words.append(value)

    def mark(name):
        labels[name] = BODY + 4 * len(words)

    def call(name, condition=14):
        emit(branch(BODY + 4 * len(words), functions[name], link=True, condition=condition))

    def jump(name, condition):
        pending.append((len(words), "branch", name, condition))
        emit(0)

    def literal(register, name):
        pending.append((len(words), "literal", name, register))
        emit(0)

    emit(0xE92D4070)  # push {r4, r5, r6, lr}; aligned stack
    emit(0xE24DDA01)  # sub sp, sp, #4096: output buffer
    emit(0xE24DD010)  # sub sp, sp, #16: instance stack
    emit(0xE3A00000)  # mov r0, #0
    call("dm_shmInit")
    emit(0xE1A05000)  # mov r5, r0
    emit(0xE3500000)  # cmp r0, #0
    jump("report", 1)
    emit(0xE1A0000D)  # mov r0, sp
    emit(0xE3A01000)  # mov r1, #0
    emit(0xE3A0200E)  # mov r2, #14
    call("memset")
    emit(0xE28D4010)  # add r4, sp, #16
    emit(0xE1A00004)  # mov r0, r4
    literal(1, "query")
    call("strcpy")
    emit(0xE3A00003)  # mov r0, #3: CLI caller, same as original CLI
    literal(1, "object")
    emit(0xE1A0200D)  # mov r2, sp
    emit(0xE1A03004)  # mov r3, r4
    call("rdp_getObj")
    emit(0xE1A05000)  # mov r5, r0
    mark("report")
    literal(0, "format")
    emit(0xE1A01005)  # mov r1, r5
    call("printf")
    emit(0xE3550000)  # cmp r5, #0
    emit(0x01A00004)  # moveq r0, r4
    call("puts", condition=0)
    emit(0xE28DD010)  # add sp, sp, #16
    emit(0xE28DDA01)  # add sp, sp, #4096
    emit(0xE1A00005)  # mov r0, r5
    emit(0xE8BD8070)  # pop {r4, r5, r6, pc}

    for name in ("query", "object", "format"):
        labels["pointer_" + name] = BODY + 4 * len(words)
        constants[name] = len(words)
        emit(0)
    payload = bytearray(b"".join(struct.pack("<I", x) for x in words))
    strings = {
        "query": b"RootName\nRootPwd\nRootEnable\nRootRemoteEnable\nAdminName\nAdminPwd\nAdminEnable\nUserName\nUserEnable\n\0",
        "object": b"DEV2_USER_CFG\0",
        "format": b"ONT_USERCFG_READ_RC=%d\n\0",
    }
    for name, value in strings.items():
        labels[name] = BODY + len(payload)
        payload.extend(value)
        struct.pack_into("<I", payload, constants[name] * 4, labels[name])
    for index, kind, name, arg in pending:
        address = BODY + index * 4
        if kind == "branch":
            word = branch(address, labels[name], condition=arg)
        else:
            delta = labels["pointer_" + name] - address - 8
            assert 0 <= delta < 4096
            word = 0xE59F0000 | (arg << 12) | delta
        struct.pack_into("<I", payload, index * 4, word)
    assert len(payload) <= BODY_LENGTH
    payload.extend(b"\0" * (BODY_LENGTH - len(payload)))

    result = bytearray(original)
    start_offset, body_offset = START - 0x10000, BODY - 0x10000
    entry_code = struct.pack("<I", branch(START, BODY)) + struct.pack("<I", 0xE1A00000) * 29
    result[start_offset:start_offset + 120] = entry_code
    result[body_offset:body_offset + BODY_LENGTH] = payload
    assert len(result) == len(original)
    assert result[:start_offset] == original[:start_offset]
    assert result[body_offset + BODY_LENGTH:] == original[body_offset + BODY_LENGTH:]
    OUTPUT.write_bytes(result)
    OUTPUT.chmod(0o700)
    info = {
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "bytes": len(result),
        "patch_regions": [[hex(START), 120], [hex(BODY), BODY_LENGTH]],
        "calls": ["dm_shmInit(0)", "memset", "strcpy", "rdp_getObj(3, DEV2_USER_CFG, zero_stack, attrs)", "printf", "puts"],
        "reads": strings["query"].decode().rstrip("\0").splitlines(),
        "live_execution_verified": False,
    }
    manifest = HERE / "usercfg-reader-manifest.json"
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
