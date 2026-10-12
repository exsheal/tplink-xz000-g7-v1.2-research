# Tools

[Main guide](../README.md)

The tools here use Python 3's standard library. Commands are run from the repository root; the capture script runs in the ONT's Linux shell.

| Tool | Purpose |
|---|---|
| [admin_password.py](admin_password.py) | Calculate the examined build's conditional default from a LAN MAC; no network requests |
| [backup_receiver.py](backup_receiver.py) + [backup.sh](backup.sh) | Receive two full NOR reads, runtime files and metadata; verify hashes and extract partitions |
| [inspect_image.py](inspect_image.py) | Read basic layout and format markers from a local flash/update image |

```sh
python3 tools/admin_password.py 02:00:00:12:34:56
python3 tools/backup_receiver.py --help
python3 tools/inspect_image.py local-private/input/flash.bin --kind flash
```

The [password guide](../docs/passwords.md) explains when the formula applies. Follow the [backup guide](../docs/backup.md) for the two-read capture and verification sequence.

`inspect_image.py` does not print identity or calibration contents, but its full-image hash is still a unit fingerprint. Keep reports from real dumps private. It does not establish package compatibility, signature validity or a safe write target.

Build-specific application patchers are under [research/helpers](../research/helpers/README.md), together with their experimental results.
