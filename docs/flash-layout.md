# Flash layout and boot sequence

[Back to the guide](../README.md#flash-layout)

## Main SPI-NOR map

The complete main flash is `0x800000` bytes. The MTD `whole` partition overlaps the seven named regions below; it is not an eighth independent storage area.

| Device | Name | Start | End (exclusive) | Size |
|---|---|---:|---:|---:|
| `/dev/mtd0` | `whole` | `0x000000` | `0x800000` | 8 MiB |
| `/dev/mtd1` | `uboot` | `0x000000` | `0x020000` | 128 KiB |
| `/dev/mtd2` | `kernel1` | `0x020000` | `0x180000` | 1,408 KiB |
| `/dev/mtd3` | `rootfs1` | `0x180000` | `0x3e0000` | 2,432 KiB |
| `/dev/mtd4` | `kernel2` | `0x3e0000` | `0x540000` | 1,408 KiB |
| `/dev/mtd5` | `rootfs2` | `0x540000` | `0x7a0000` | 2,432 KiB |
| `/dev/mtd6` | `misc` | `0x7a0000` | `0x7f0000` | 320 KiB |
| `/dev/mtd7` | `hwconfig` | `0x7f0000` | `0x800000` | 64 KiB |

Each kernel region begins with a vendor `IMAGE_TAG`. The observed active and committed image was the slave image (index 1): `kernel2` / `rootfs2`, with `/dev/mtdblock5` mounted as root. This is an observed bank selection, not a rule for every unit.

The [machine-readable map](../research/data/flash-layout.json) includes record sizes and offsets. The [backup guide](backup.md) uses `/dev/mtd0` to capture all seven regions in one read.

## Identity and hardware records

These addresses were recovered from the examined readers and flash structure. Record contents are excluded.

| Flash offset | Purpose |
|---:|---|
| `0x7cb100` | LOID record |
| `0x7cb200` | GPON serial, type and checksum |
| `0x7cb300` | GPON password, type and checksum |
| `0x7ce000` | `Sign` record |
| `0x7cf300` | Device ID record |
| `0x7cf500` | Product serial reader location |
| `0x7d0000` | Boot / bank metadata |
| `0x7e0000` | LAN MAC |
| `0x7f0000` | System-information block, first 4096 bytes |
| `0x7f1000` | Optical BOB data, 4096 bytes |

The GPON authentication password is separate from the web admin password. A record named `Sign` does not by itself prove secure boot. The Device ID record has not been established as SPI OTP. See the [identity readers](../research/disassembly/password-identity.txt).

## Boot sequence

```text
SPI-NOR boot ROM
  → vendor U-Boot V1.2.3
  → bank selection and IMAGE_TAG read
  → Linux kernel and selected rootfs
  → /sbin/init and rcS
  → PON SDK, gcnet and gcponmap
  → COS, GCS, OMCI, HTTP and Telnet
```

The September 2025 vendor banner coexists with a U-Boot 2020.07 base. A default-environment warning means compiled defaults were used; a sample `ethaddr` in that environment need not be the live Linux MAC. Likewise, an `fpga` boot command name is not proof of physical FPGA hardware.

The bootloader contains TFTP/HTTP recovery, XMODEM and multicast-related code. No restore test was performed. A full main-flash read also leaves external I²C EEPROM, OTP and security sectors outside its scope.
