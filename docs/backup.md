# Back up flash and runtime files

[Back to the guide](../README.md#backup)

The examined device has **8 MiB of SPI-NOR**. `/dev/mtd0` is the `whole` partition and covers the complete main flash. Two independent reads were transferred and verified to be identical.

The capture uses flash reads and small temporary files under `/var/tmp`. It avoids copying an 8 MiB image into the ONT's limited RAM. It requires a **Linux shell with UID 0**, normally obtained over UART; the TP-Link Telnet CLI cannot run these commands.

## 1. Prepare the computer

For a direct Ethernet connection on Linux, choose the interface connected to the ONT and an unused address:

```sh
PC_IFACE='YOUR_ETHERNET_INTERFACE'
sudo ip link set dev "$PC_IFACE" up
sudo ip addr add 192.168.10.2/24 dev "$PC_IFACE"
python3 tools/backup_receiver.py --bind 192.168.10.2 --peer 192.168.10.254
```

Run the receiver from your repository checkout. It listens for TFTP uploads on UDP **1069** and serves `backup.sh` over HTTP on TCP **8000**. It does not open UART. Local firewall rules must permit those connections from the ONT.

The receiver accepts uploads from the specified peer and serves only the capture script. Each session is stored under `local-private/backups/` with private directory/file permissions. TFTP has no encryption; use a trusted local connection.

Fiber service is not needed for a local Ethernet capture.

## 2. Wait for the ONT's network to be ready

Let the startup output settle, activate the Linux console, then run:

```sh
ifconfig br0
route -n
ping -c 3 192.168.10.2
```

Confirm that `br0` has `192.168.10.254/24` and a local route to the computer. A shell prompt can appear before network initialization finishes; do not start the transfer until this check succeeds.

## 3. Transfer two complete reads

Run each command separately and wait for it to return:

```sh
tftp -p -l /proc/version -r meta/probe.txt 192.168.10.2 1069
tftp -p -l /dev/mtd0 -r flash-a.bin 192.168.10.2 1069
tftp -p -l /dev/mtd0 -r flash-b.bin 192.168.10.2 1069
```

BusyBox TFTP can finish silently. Watch the PC receiver: both flash files must be **8,388,608 bytes**. Keep the device powered while a transfer is active.

## 4. Capture runtime files

After both flash reads have completed:

```sh
wget -O /var/tmp/backup.sh http://192.168.10.2:8000/backup.sh
sh /var/tmp/backup.sh --runtime-only
```

The script captures system information, file metadata and regular files from `/etc`, `/var`, and `/tmp` when present. It records failures in `meta/errors.txt`. It checks UID 0, the expected `mtd0` layout and read access before proceeding.

Alternatively, `sh /var/tmp/backup.sh` without `--runtime-only` performs the probe, both flash reads and runtime capture itself. Do not use the runtime-only flag as a substitute for the two full reads.

## 5. Verify the saved session

The receiver verifies the files when the capture finishes. To repeat verification on the computer:

```sh
python3 tools/backup_receiver.py --verify local-private/backups/YOUR_SESSION
```

A complete result requires both flash files to have the expected size and matching SHA-256 hashes, plus a runtime completion record with no reported errors. The receiver writes `verification.json`, `received-files.json`, `SHA256SUMS` and separate partition files.

An error while copying a runtime file does not invalidate two matching flash reads. It does mean that the runtime capture needs inspection. Read `meta/errors.txt` before calling that part complete.

## What the backup covers

| Captured | Coverage |
|---|---|
| Main flash | Bootloader, both kernel/rootfs banks, `misc`, `hwconfig` |
| Runtime files | RAM configuration and readable regular files at capture time |
| Metadata | Paths, ownership/mode output, links and system state |

Runtime files are copied sequentially, so they are not an atomic snapshot. Sockets are represented in metadata rather than copied as restorable services. A main MTD read does not cover an external EEPROM, OTP or separate flash security sectors. Restoration has not been tested.

Keep the images, runtime account files and calibration records private. A backup hash can also identify the unit; exclude it from public reports.

## After a direct connection

If the temporary PC address is no longer needed, remove it from the interface you used:

```sh
sudo ip addr del 192.168.10.2/24 dev "$PC_IFACE"
```

Leaving that address on a disconnected interface can interfere with later ONT access through a router.
