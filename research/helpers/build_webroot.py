#!/usr/bin/env python3
"""Build a RAM-only, device-specific HTTP server with a local root login.

This never changes a flash image. The input is the original backed-up httpd.
The new auth-table slot uses the server's existing role 0 and credential
encoder, leaving slots 1 (admin) and 2 (user) and all ACL masks intact.
"""
import hashlib
import io
import json
import secrets
import string
import struct
from pathlib import Path

from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parents[2] / "local-private" / "helpers" / "webroot"
SOURCE = HERE / "rootfs2/bin/httpd"
OUTPUT = HERE / "serve/httpd_webroot"
MANIFEST = HERE / "webroot-manifest.json"
CREDENTIALS = HERE / "webroot-credentials.json"
SOURCE_SHA = "199f8b7a0357616302c3f104e7f65e13ebd638977ff00160d9e968386a62044e"
BODY = 0x1FB60
HOOK = 0x16248
FILL = 0x1609C
ORIGINAL_RETURN = 0x1624C


def branch(source, target, *, link=False):
    delta = target - source - 8
    assert delta % 4 == 0 and -(1 << 25) <= delta < (1 << 25)
    return (0xEB000000 if link else 0xEA000000) | ((delta >> 2) & 0xFFFFFF)


def build():
    original = SOURCE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SOURCE_SHA
    assert len(original) == 67932
    elf = ELFFile(io.BytesIO(original))
    assert elf["e_machine"] == "EM_ARM" and elf.little_endian
    assert elf["e_entry"] == 0x125F0
    rx_index, rx = next((i, s) for i, s in enumerate(elf.iter_segments())
                        if s["p_type"] == "PT_LOAD" and s["p_flags"] == 5)
    assert rx["p_vaddr"] == 0x10000 and rx["p_offset"] == 0
    assert rx["p_filesz"] == rx["p_memsz"] == 0xFB60
    assert not any(original[0xFB60:0xFEEC])

    if CREDENTIALS.exists():
        credentials = json.loads(CREDENTIALS.read_text())
    else:
        alphabet = string.ascii_letters + string.digits
        credentials = {"username": "root",
                       "password": "".join(secrets.choice(alphabet) for _ in range(20))}
        CREDENTIALS.write_text(json.dumps(credentials, indent=2) + "\n")
    CREDENTIALS.chmod(0o600)
    assert credentials["username"] == "root"
    password = credentials["password"]
    assert len(password) == 20 and password.isascii() and password.isalnum()

    symbols = elf.get_section_by_name(".dynsym")
    plt = elf.get_section_by_name(".plt")
    functions = {symbols.get_symbol(r["r_info_sym"]).name:
                 plt["sh_addr"] + 20 + i * 12
                 for i, r in enumerate(elf.get_section_by_name(".rel.plt").iter_relocations())}
    assert functions["puts"] == 0x120D0
    assert functions["fflush"] == 0x11D58

    words = []
    literal_refs = []

    def emit(word):
        words.append(word)

    def literal(register, name):
        literal_refs.append((len(words), register, name))
        emit(0)

    # The original init function already saved r4-r6 and lr (16 bytes).
    # Keep the existing return and maintain the ARM EABI's 8-byte alignment.
    emit(0xE24DD008)                    # sub sp, sp, #8; fifth arg/padding
    emit(0xE3A00000)                    # mov r0, #0: root role
    emit(0xE58D0000)                    # str r0, [sp]: remoteEnable = 0
    literal(1, "username")
    literal(2, "password")
    emit(0xE3A03001)                    # mov r3, #1: local enable
    emit(branch(BODY + len(words) * 4, FILL, link=True))
    emit(0xE28DD008)                    # add sp, sp, #8
    literal(0, "notice")
    emit(branch(BODY + len(words) * 4, functions["puts"], link=True))
    emit(0xE3A00000)                    # mov r0, #0: flush all output streams
    emit(branch(BODY + len(words) * 4, functions["fflush"], link=True))
    emit(0xE3A00000)                    # original success return
    emit(branch(BODY + len(words) * 4, ORIGINAL_RETURN))
    code_bytes = len(words) * 4
    pointers = {}
    for name in ("username", "password", "notice"):
        pointers[name] = len(words) * 4
        emit(0)
    payload = bytearray(struct.pack("<" + "I" * len(words), *words))
    strings = {"username": b"root\0",
               "password": password.encode("ascii") + b"\0",
               "notice": b"WEBROOT_RAM: role=0 enabled=1 remote=0\0"}
    for name, value in strings.items():
        struct.pack_into("<I", payload, pointers[name], BODY + len(payload))
        payload.extend(value)
    while len(payload) % 4:
        payload.append(0)
    for index, register, name in literal_refs:
        displacement = BODY + pointers[name] - (BODY + index * 4 + 8)
        assert 0 <= displacement < 4096
        struct.pack_into("<I", payload, index * 4,
                         0xE59F0000 | register << 12 | displacement)
    assert 0xFB60 + len(payload) < 0xFEEC

    result = bytearray(original)
    changes = []

    def patch_word(address, expected, replacement, description):
        offset = address - 0x10000
        assert struct.unpack_from("<I", original, offset)[0] == expected
        struct.pack_into("<I", result, offset, replacement)
        changes.append({"offset": offset, "bytes": 4,
                        "address": hex(address), "description": description})

    patch_word(HOOK, 0xE3A00000, branch(HOOK, BODY), "register root after normal auth initialization")
    # The existing UI recognizes Admin/User strings only. Keep the server-side
    # role at 0; map roles 0/1 to Admin and preserve User for roles 2/3.
    assert struct.unpack_from("<I", original, 0x9ECC)[0] == 0xE3530001
    patch_word(0x19ED0, 0x059F3178, 0x959F3178, "select Admin UI for roles <= 1 (unsigned)")
    patch_word(0x19ED4, 0x159F3178, 0x859F3178, "preserve User UI for roles > 1 (unsigned)")

    result[0xFB60:0xFB60 + len(payload)] = payload
    changes.append({"offset": 0xFB60, "bytes": len(payload), "address": hex(BODY),
                    "description": "ARM registration code, pointers, local credentials"})
    header = elf["e_phoff"] + rx_index * elf["e_phentsize"]
    struct.pack_into("<II", result, header + 16,
                     0xFB60 + len(payload), 0xFB60 + len(payload))
    changes.append({"offset": header + 16, "bytes": 8,
                    "description": "map payload in existing read/execute segment"})

    assert len(result) == len(original)
    allowed = set()
    for change in changes:
        allowed.update(range(change["offset"], change["offset"] + change["bytes"]))
    changed_offsets = [i for i, (a, b) in enumerate(zip(original, result)) if a != b]
    assert all(i in allowed for i in changed_offsets)
    assert result[0xFEEC:] == original[0xFEEC:]  # RW data, dynamic linking, section headers
    updated = ELFFile(io.BytesIO(result))
    for i, (before, after) in enumerate(zip(elf.iter_segments(), updated.iter_segments())):
        expected = dict(before.header)
        if i == rx_index:
            expected["p_filesz"] += len(payload)
            expected["p_memsz"] += len(payload)
        assert dict(after.header) == expected
    assert updated["e_entry"] == elf["e_entry"]

    OUTPUT.write_bytes(result)
    OUTPUT.chmod(0o700)
    # An assembler-generated object lets llvm-objdump independently decode
    # the actual injected instructions; it is for PC inspection only.
    assembly = [".syntax unified", ".arch armv5te", ".arm", ".text",
                f".org {BODY}", ".global webroot_init", "webroot_init:"]
    for (word,) in struct.iter_unpack("<I", payload[:code_bytes]):
        assembly.append(f"    .inst 0x{word:08x}")
    assembly.append("webroot_code_end:")
    assembly.extend(f"    .byte 0x{v:02x}" for v in payload[code_bytes:])
    asm_path = HERE / "webroot-payload.S"
    asm_path.write_text("\n".join(assembly) + "\n")
    asm_path.chmod(0o600)
    info = {"source_sha256": SOURCE_SHA,
            "output_sha256": hashlib.sha256(result).hexdigest(),
            "bytes": len(result), "changed_bytes": len(changed_offsets),
            "patch_regions": changes, "payload_code_bytes": code_bytes,
            "payload_bytes": len(payload), "account_name": "root", "auth_role": 0,
            "local_enabled": True, "remote_enabled": False,
            "persistent": False, "flash_write_calls_added": False,
            "admin_registration_unchanged": result[0x2904:0x297C] == original[0x2904:0x297C],
            "auth_comparison_and_acl_unchanged": result[0x6160:0x6248] == original[0x6160:0x6248]
                and result[0x6254:0x6274] == original[0x6254:0x6274],
            "live_execution_verified": False, "live_root_login_verified": False}
    MANIFEST.write_text(json.dumps(info, indent=2) + "\n")
    MANIFEST.chmod(0o600)
    print(json.dumps({k: v for k, v in info.items() if k != "patch_regions"}, indent=2))


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
