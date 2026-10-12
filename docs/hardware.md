# Hardware and platform

[Back to the guide](../README.md#hardware)

The target is the **XZ000-G7 v1.2 TR variant**, reported by the firmware as **v1.20**. The September 2025 build date identifies the software build; it does not establish the board's manufacturing date.

## Observed components

| Component | Evidence from the examined unit |
|---|---|
| SoC / CPU | Galachip GC1601; Faraday FA626TE, ARMv5TE, one core, 533 MHz |
| RAM | 32 MiB physical DDR |
| SDK reservation | 4 MiB starting at physical `0x41c00000`, outside the normal Linux memory pool |
| Main flash | 8 MiB SPI-NOR; JEDEC ID `0x204017` |
| Flash geometry | 256-byte pages, 64 KiB erase blocks |
| Ethernet | One Gigabit RJ45 port; SGMII PHY |
| Optics | UX3320S BOSA/BOB detected during startup |
| UART | `ttyS0`, `115200 8N1`, controller at `0x90400000` |
| I²C | Controller at `0x90600000` enabled; second controller disabled |
| Watchdogs | Hardware timeout initialized to 10 seconds; software margin to 60 seconds |

U-Boot names the flash `XM24QH64B`; the kernel calls it `XM25QH64B`. Both report the same JEDEC ID and 8 MiB geometry, so the differing names alone do not establish different chips.

## Software platform

Linux 3.16.0 is built with PREEMPT. Native executables use ARM little-endian EABI5 with soft-float, GCC 4.9.4 and uClibc-ng 1.0.31. The actual BusyBox binary is 1.23.2; newer BusyBox labels in template files do not change that.

The [kernel configuration](../research/data/kernel-2025.config) and [Device Tree](../research/data/gc1601-2025.dts) are included for platform analysis. WLAN, USB, PCI, MMC, UBI and JFFS2 are disabled in this kernel configuration. Shared Wi-Fi, VPN and USB schema entries are therefore not evidence that the corresponding hardware or service is available.

## PON and Ethernet limits

TP-Link's [generic model specification](https://service-provider.tp-link.com/gpon/xz000-g7/) lists GPON at 2.488 Gbps downstream / 1.244 Gbps upstream and EPON at 1.25 Gbps, with Class B+ optics. The examined unit was observed operating in GPON mode; EPON was not activated in the tests.

The single Gigabit Ethernet port limits the client-facing link. No forwarding-rate, NAT or sustained throughput benchmark was performed. The Device Tree contains a maximum frame size of 9000 bytes; that alone does not establish working jumbo-frame service through the operator profile.

The PHY address appears as decimal `24` in one source and hexadecimal `0x18` in another. They are the same value.

## Still to establish

The board pinout, UART electrical level, full EEPROM/OTP map and effects of low-level register changes are not documented from measurements. There is no confirmed OpenWrt port for this ONT in this research.
