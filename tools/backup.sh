#!/bin/sh
# XZ000-G7 TR v1.20: read flash and upload it without an 8 MiB RAM copy.
# The only local output is a small, private directory on /var/tmp tmpfs.
umask 077
ONT_PC_IP=192.168.10.2
ONT_PC_PORT=1069
ONT_WORK=/var/tmp/ont-backup-work
mkdir -p "$ONT_WORK" || exit 1
ONT_ERRORS="$ONT_WORK/errors.txt"
: > "$ONT_ERRORS"

send_file() {
    tftp -p -l "$1" -r "$2" "$ONT_PC_IP" "$ONT_PC_PORT"
}

stop_backup() {
    echo "BACKUP STOPPED: $*"
    echo "Files already received on the PC have been preserved."
    exit 1
}

awk '$1 == "Uid:" && $2 == 0 && $3 == 0 && $4 == 0 && $5 == 0 { ok=1 }
     END { exit !ok }' /proc/self/status || stop_backup "Root authority is required."
awk '$1 == "mtd0:" && $2 == "00800000" && $3 == "00010000" && $4 == "\"whole\"" { ok=1 }
     END { exit !ok }' /proc/mtd || stop_backup "mtd0 is not the expected 8 MiB whole partition."
[ -c /dev/mtd0 ] && [ -r /dev/mtd0 ] || stop_backup "mtd0 is not readable."

case "${1-}" in
    '')
        ONT_FLASH_READS=2
        echo "1/4: Testing the transfer path..."
        send_file /proc/version meta/probe.txt || stop_backup "TFTP probe failed."
        echo "2/4: Sending the first full flash read directly to the PC..."
        send_file /dev/mtd0 flash-a.bin || stop_backup "First flash transfer failed."
        echo "3/4: Sending the second full flash read directly to the PC..."
        send_file /dev/mtd0 flash-b.bin || stop_backup "Second flash transfer failed."
        ;;
    --runtime-only)
        ONT_FLASH_READS=manual
        echo "Full flash reads were sent manually; continuing with runtime capture."
        ;;
    *) stop_backup "Unknown option: $1" ;;
esac

echo "4/4: Sending runtime files and system information..."
{
    echo '=== PROC VERSION ==='; cat /proc/version
    echo '=== CMDLINE ==='; cat /proc/cmdline
    echo '=== MTD ==='; cat /proc/mtd
    echo '=== MEMORY ==='; cat /proc/meminfo
    echo '=== CPU ==='; cat /proc/cpuinfo
    echo '=== UPTIME ==='; cat /proc/uptime
    echo '=== MOUNTS ==='; cat /proc/mounts
    echo '=== ADDRESSES ==='; ifconfig -a
    echo '=== ROUTES ==='; route -n
    echo '=== LISTENERS ==='; netstat -lnt
    echo '=== PROCESSES ==='; ps w
    echo '=== BUSYBOX ==='; busybox
} > "$ONT_WORK/system.txt" 2>&1
send_file "$ONT_WORK/system.txt" meta/system.txt || stop_backup "System information transfer failed."

set -- /etc /var
if [ -e /tmp ]; then
    set -- "$@" /tmp
fi
if ! find "$@" > "$ONT_WORK/metadata-paths.txt" 2>> "$ONT_ERRORS"; then
    echo 'METADATA_ERROR: file path inventory failed' >> "$ONT_ERRORS"
fi
: > "$ONT_WORK/file-metadata.txt"
while IFS= read -r ONT_ENTRY; do
    if ! ls -ldn "$ONT_ENTRY" >> "$ONT_WORK/file-metadata.txt" 2>> "$ONT_ERRORS"; then
        echo "METADATA_ERROR: cannot list $ONT_ENTRY" >> "$ONT_ERRORS"
    fi
done < "$ONT_WORK/metadata-paths.txt"
send_file "$ONT_WORK/file-metadata.txt" meta/file-metadata.txt || stop_backup "File metadata transfer failed."

if ! find "$@" -type f > "$ONT_WORK/file-list.txt" 2>> "$ONT_ERRORS"; then
    echo 'FIND_ERROR: file inventory failed' >> "$ONT_ERRORS"
fi
send_file "$ONT_WORK/file-list.txt" meta/file-list.txt || stop_backup "File inventory transfer failed."

while IFS= read -r ONT_FILE; do
    case "$ONT_FILE" in
        "$ONT_WORK"/*|/var/tmp/backup.sh) continue ;;
    esac
    if [ ! -r "$ONT_FILE" ]; then
        echo "UNREADABLE: $ONT_FILE" >> "$ONT_ERRORS"
        continue
    fi
    if ! send_file "$ONT_FILE" "runtime${ONT_FILE}"; then
        echo "TRANSFER_FAILED: $ONT_FILE" >> "$ONT_ERRORS"
    fi
done < "$ONT_WORK/file-list.txt"

send_file "$ONT_ERRORS" meta/errors.txt || stop_backup "Error report transfer failed."
ONT_FAILED=$(wc -l < "$ONT_ERRORS")
{
    echo "CAPTURE_COMPLETE=1"
    echo "RUNTIME_ERRORS=$ONT_FAILED"
    echo "FLASH_BYTES=8388608"
    echo "FLASH_READS=$ONT_FLASH_READS"
} > "$ONT_WORK/complete.txt"
send_file "$ONT_WORK/complete.txt" meta/complete.txt || stop_backup "Completion record transfer failed."

echo "Transfer finished. Check the PC receiver verification report."
if [ "$ONT_FAILED" -ne 0 ]; then
    echo "WARNING: $ONT_FAILED file/inventory errors; see meta/errors.txt on the PC."
    exit 2
fi
