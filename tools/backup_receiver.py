#!/usr/bin/env python3
"""Receive a two-pass XZ000-G7 backup via TFTP; HTTP serves only its script.

No extra Python packages or root are needed. The receiver accepts only the
configured ONT IPv4 address, uses fresh private directories, and never serves
backup contents. RFC 1350 octet transfers use 512-byte blocks; RFC 2347 permits
ignoring requested options by replying ACK(0), rather than OACK.
"""

import argparse
import datetime
import hashlib
import ipaddress
import json
import os
from pathlib import Path, PurePosixPath
import socket
import struct
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

FLASH_SIZE = 0x800000
PARTITIONS = (
    ("uboot", 0x000000, 0x020000),
    ("kernel1", 0x020000, 0x180000),
    ("rootfs1", 0x180000, 0x3E0000),
    ("kernel2", 0x3E0000, 0x540000),
    ("rootfs2", 0x540000, 0x7A0000),
    ("misc", 0x7A0000, 0x7F0000),
    ("hwconfig", 0x7F0000, 0x800000),
)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as output:
        json.dump(value, output, indent=2, ensure_ascii=False)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def verify_backup(folder, extract=False):
    folder = Path(folder)
    report = {"full_flash_verified": False, "files": {}, "partitions": {}}
    for name in ("flash-a.bin", "flash-b.bin"):
        path = folder / name
        if path.is_file():
            report["files"][name] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    raw = report["files"]
    report["full_flash_verified"] = (
        len(raw) == 2
        and all(item["bytes"] == FLASH_SIZE for item in raw.values())
        and raw["flash-a.bin"]["sha256"] == raw["flash-b.bin"]["sha256"]
    )
    for name in raw:
        if raw[name]["bytes"] != FLASH_SIZE:
            continue
        with (folder / name).open("rb") as source:
            for partition, start, end in PARTITIONS:
                source.seek(start)
                data = source.read(end - start)
                entry = {"offset": hex(start), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                report["partitions"].setdefault(partition, {})[name] = entry
                if extract and (name == "flash-a.bin" or not report["full_flash_verified"]):
                    target_dir = folder / ("partitions" if report["full_flash_verified"] else f"partitions-{name[:-4]}")
                    target_dir.mkdir(mode=0o700, exist_ok=True)
                    target = target_dir / f"{partition}.bin"
                    if target.exists():
                        if sha256_file(target) != entry["sha256"]:
                            raise ValueError(f"Existing partition copy differs: {target}")
                    else:
                        with target.open("xb") as output:
                            output.write(data)
                            output.flush()
                            os.fsync(output.fileno())
    marker = folder / "meta/complete.txt"
    report["capture_complete"] = marker.is_file()
    report["runtime_errors"] = None
    if marker.is_file():
        for line in marker.read_text(encoding="ascii").splitlines():
            if line.startswith("RUNTIME_ERRORS="):
                report["runtime_errors"] = int(line.split("=", 1)[1].strip())
    atomic_json(folder / "verification.json", report)
    hashes = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.name not in ("SHA256SUMS", "SHA256SUMS.tmp") and not path.name.endswith(".part"):
            hashes.append(f"{sha256_file(path)}  {path.relative_to(folder).as_posix()}\n")
    temporary = folder / "SHA256SUMS.tmp"
    temporary.write_text("".join(hashes), encoding="utf-8")
    temporary.replace(folder / "SHA256SUMS")
    return report


def error_packet(code, message):
    return struct.pack("!HH", 5, code) + message.encode("ascii", errors="replace")[:160] + b"\0"


class Receiver:
    """Single active write transfer, with duplicate packet/final ACK handling."""

    def __init__(self, folder, peer_ip, announce=print):
        self.folder = Path(folder)
        self.peer_ip = peer_ip
        self.announce = announce
        self.active = None
        self.recent = {}
        self.files = {}
        self.completed_at = None
        self.total_bytes = 0

    def abort(self, reason):
        if self.active is not None:
            self.active["stream"].close()
            self.announce(f"PARTIAL TRANSFER PRESERVED: {self.active['name']} ({reason})", flush=True)
            self.active = None

    def allowed_name(self, name):
        if not name or len(name.encode("utf-8")) > 512 or "\x00" in name or "\\" in name:
            return False
        path = PurePosixPath(name)
        if path.is_absolute() or any(part in ("", ".", "..") for part in name.split("/")):
            return False
        return name in ("flash-a.bin", "flash-b.bin") or name.startswith(("meta/", "runtime/etc/", "runtime/var/", "runtime/tmp/"))

    def handle(self, packet, peer, now=None):
        now = time.monotonic() if now is None else now
        if peer[0] != self.peer_ip:
            return None
        self.recent = {key: value for key, value in self.recent.items() if value[3] > now}
        if self.active and now - self.active["activity"] > 60:
            self.abort("no data received for 60 seconds")
        if len(packet) < 2:
            return error_packet(4, "Malformed packet")
        opcode = struct.unpack("!H", packet[:2])[0]
        if opcode == 2:
            if self.active:
                if peer == self.active["peer"] and packet == self.active["request"]:
                    return self.active["ack"]
                return error_packet(0, "Transfer already in progress")
            try:
                fields = packet[2:].split(b"\0")
                if fields[-1] != b"" or len(fields) < 3 or len(fields) % 2 != 1:
                    raise ValueError("Bad WRQ fields")
                name = fields[0].decode("utf-8")
                if fields[1].lower() != b"octet" or not self.allowed_name(name):
                    return error_packet(2, "Only approved octet uploads are accepted")
                if len(self.files) >= 2048 or self.total_bytes >= 64 * 1024 * 1024:
                    return error_packet(3, "Session limit reached")
                target = self.folder / name
                target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                partial = target.with_name(target.name + ".part")
                if target.exists() or partial.exists():
                    return error_packet(6, "File already exists; use a new backup session")
                stream = partial.open("xb")
                self.active = {"name": name, "target": target, "partial": partial, "stream": stream,
                               "peer": peer, "request": packet, "ack": struct.pack("!HH", 4, 0),
                               "block": 0, "payload": None, "size": 0, "hash": hashlib.sha256(), "activity": now}
                self.announce(f"RECEIVING: {name}", flush=True)
                return self.active["ack"]
            except (OSError, UnicodeError, ValueError) as error:
                return error_packet(2, str(error))
        if opcode == 5:
            if self.active and peer == self.active["peer"]:
                self.abort("client reported an error")
            return None
        if opcode != 3 or len(packet) < 4 or len(packet) > 516:
            return error_packet(4, "Expected a 512-byte DATA packet")
        block = struct.unpack("!H", packet[2:4])[0]
        payload = packet[4:]
        if not self.active:
            previous = self.recent.get(peer)
            if previous and (block, payload) == previous[:2]:
                return previous[2]
            return error_packet(5, "Unknown transfer")
        state = self.active
        if peer != state["peer"]:
            return error_packet(5, "Unknown transfer ID")
        state["activity"] = now
        if block == state["block"]:
            if state["payload"] == payload:
                return state["ack"]
            return error_packet(4, "Conflicting duplicate block")
        if block != (state["block"] + 1) % 65536:
            return state["ack"]
        size = state["size"] + len(payload)
        if size > FLASH_SIZE or self.total_bytes + size > 64 * 1024 * 1024:
            self.abort("size limit exceeded")
            return error_packet(3, "File or session size limit exceeded")
        try:
            state["stream"].write(payload)
            state["hash"].update(payload)
            state["size"] = size
            state["block"] = block
            state["payload"] = payload
            state["ack"] = struct.pack("!HH", 4, block)
            if state["name"] in ("flash-a.bin", "flash-b.bin") and size and len(payload) == 512 and size % (1024 * 1024) == 0:
                self.announce(f"PROGRESS: {state['name']} {size // (1024 * 1024)}/8 MiB", flush=True)
            if len(payload) == 512:
                return state["ack"]
            if state["name"] in ("flash-a.bin", "flash-b.bin") and size != FLASH_SIZE:
                self.abort(f"full flash size is {size}; expected {FLASH_SIZE}")
                return error_packet(3, "Flash size must be exactly 8388608 bytes")
            if state["name"] == "meta/probe.txt" and size == 0:
                self.abort("empty probe file")
                return error_packet(4, "Probe file must not be empty")
            state["stream"].flush()
            os.fsync(state["stream"].fileno())
            state["stream"].close()
            state["partial"].rename(state["target"])
            self.files[state["name"]] = {"bytes": size, "sha256": state["hash"].hexdigest()}
            self.total_bytes += size
            atomic_json(self.folder / "received-files.json", self.files)
            self.recent[peer] = (block, payload, state["ack"], now + 30)
            self.active = None
            self.announce(f"SAVED: {state['name']} ({size} bytes)", flush=True)
            if state["name"] == "meta/complete.txt":
                self.completed_at = now
            return state["ack"]
        except OSError as error:
            self.abort(str(error))
            return error_packet(3, str(error))


def script_handler(script_bytes, peer_ip):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.client_address[0] != peer_ip:
                self.send_error(403)
            elif self.path != "/backup.sh":
                self.send_error(404)
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(script_bytes)))
                self.end_headers()
                self.wfile.write(script_bytes)

        def log_message(self, *args):
            pass

    return Handler


def show_report(report, folder):
    print(f"\nBACKUP DIRECTORY: {folder}", flush=True)
    if report["full_flash_verified"]:
        print("FULL FLASH VERIFIED: Both reads contain 8388608 bytes and have matching SHA-256 hashes.", flush=True)
    else:
        print("WARNING: Full flash copies are missing or differ; saved files have been preserved.", flush=True)
    print(f"RUNTIME CAPTURE: completion record={report['capture_complete']}, errors={report['runtime_errors']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Receive and verify two full XZ000-G7 flash reads and a runtime file capture")
    parser.add_argument("--bind", default="192.168.10.2")
    parser.add_argument("--peer", default="192.168.10.254")
    parser.add_argument("--port", type=int, default=1069)
    parser.add_argument("--http-port", type=int, default=8000)
    parser.add_argument("--verify", type=Path, metavar="BACKUP_DIRECTORY")
    args = parser.parse_args()
    os.umask(0o077)
    if args.verify:
        report = verify_backup(args.verify, extract=True)
        show_report(report, args.verify)
        return 0 if report["full_flash_verified"] and report["capture_complete"] and report["runtime_errors"] == 0 else 2
    bind = str(ipaddress.IPv4Address(args.bind))
    peer_ip = str(ipaddress.IPv4Address(args.peer))
    if not (1024 <= args.port <= 65535 and 1024 <= args.http_port <= 65535):
        parser.error("Ports must be in the range 1024..65535.")
    base = Path(__file__).resolve().parent
    script = (base / "backup.sh").read_text(encoding="utf-8")
    script = script.replace("ONT_PC_IP=192.168.10.2", f"ONT_PC_IP={bind}").replace("ONT_PC_PORT=1069", f"ONT_PC_PORT={args.port}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp:
        udp.bind((bind, args.port))
        udp.settimeout(1)
        http = ThreadingHTTPServer((bind, args.http_port), script_handler(script.encode("utf-8"), peer_ip))
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        folder = base.parent / "local-private" / "backups" / f"xz000-g7-tr-{stamp}-{uuid.uuid4().hex[:6]}"
        folder.mkdir(mode=0o700, parents=True)
        receiver = Receiver(folder, peer_ip)
        thread.start()
        print(f"READY: TFTP {bind}:{args.port}, script HTTP {bind}:{args.http_port}", flush=True)
        print(f"BACKUP DIRECTORY: {folder}", flush=True)
        print("Run these commands in the ONT Linux shell, one at a time:", flush=True)
        print(f"wget -O /var/tmp/backup.sh http://{bind}:{args.http_port}/backup.sh", flush=True)
        print("sh /var/tmp/backup.sh", flush=True)
        try:
            while receiver.completed_at is None or time.monotonic() - receiver.completed_at < 12:
                try:
                    packet, remote = udp.recvfrom(65535)
                except socket.timeout:
                    if receiver.active and time.monotonic() - receiver.active["activity"] > 60:
                        receiver.abort("no data received for 60 seconds")
                    continue
                reply = receiver.handle(packet, remote)
                if reply is not None:
                    udp.sendto(reply, remote)
        except KeyboardInterrupt:
            print("\nReceiver stopped; saved files have been preserved.", flush=True)
        finally:
            receiver.abort("receiver stopped")
            http.shutdown()
            http.server_close()
        report = verify_backup(folder, extract=True)
        show_report(report, folder)
        return 0 if report["full_flash_verified"] and report["capture_complete"] and report["runtime_errors"] == 0 else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f"RECEIVER ERROR: {error}", file=sys.stderr)
        sys.exit(1)
