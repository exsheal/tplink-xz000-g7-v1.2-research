# Capability matrix

[Research index](README.md)

This matrix describes **TR v1.20 Build 250926**. It separates working behavior from code, API and template coverage. Internet service in the tested setup used PPPoE on an external router.

| Capability | Evidence | Limits |
|---|---|---|
| GPON activation and service | Live | O5 and Internet service observed |
| Ethernet–PON bridge | Live and traced code | `br0`, `eth0.0`, `pon0.0` and SFU driver |
| HTTP management, port 80 | Live | Admin login directly and through OpenWrt |
| Telnet, port 23 | Live | Admin vendor-CLI session |
| UART Linux root | Live | Account named `admin`, UID/GID 0 |
| Linux shell over the network | Unresolved | Normal Telnet is a CLI; privileged shell path is separate |
| SSH / Dropbear | Missing | No daemon binary; account/directory alone is insufficient |
| Permanent web root | Unverified | Original slot disabled; RAM login did not resolve menu/CGI permissions |
| GPON SN/password settings | Traced code | CMM → flash/OMCI/SDK; not changed on the active service |
| LOID / CTC authentication | UI/API present | Operator use not verified |
| OLT / Tag / Transparent VLAN modes | Traced code | OMCI reload reaches a real VLAN ioctl |
| VLAN translation / trunk | SDK/API present | Not all combinations or service profiles tested |
| T-CONT and queues | API limits decoded | Getter returns 16 T-CONTs and 8 queues per T-CONT/LLID |
| GEM / AES / FEC / DBA | Code/API present | OMCI profiles not exhaustively tested; generic product listing gives 256 GEM ports |
| Tx/Rx power, temperature, voltage, bias | Live and traced code | Real `gccli bob opt` measurement path |
| Ethernet loop detection | Process observed | Loop scenario not tested |
| EPON | Code present | XPON/OAM tools exist; service used GPON and EPON UI was disabled |
| XG-PON / XGS-PON | No supporting evidence | No verified 10G PON hardware support |
| DHCP / LAN settings | Binary/UI present | No service test; empty pool seen at startup |
| IPv6 | Kernel present, default disabled | Init uses `disable_ipv6`; some services absent |
| PPPoE / NAT routing on the ONT | No complete working demonstration | NAT kernel/API exists; `pppd` is absent, with SFU/NO_WAN build context |
| Wi-Fi / Mesh | Disabled or missing | No established radio/kernel support; shared schema is insufficient |
| VPN / VoIP / LTE | Disabled or missing | Required program/hardware support not found |
| TR-069 / TR-369 | Disabled or missing | Generic management definitions do not establish active daemons |
| Jumbo frames | Unresolved | DT says 9000; no end-to-end test |
| TFTP / HTTP / XMODEM recovery | Code present | Restoration not tested |
| Firmware validation | Traced code | MD5 and product/version checks; signature chain remains unresolved |
| OpenWrt on the ONT | Unverified | Generic GPL kernel source is not a working port |

The 32 MiB RAM and 8 MiB flash also constrain additional workloads. No NAT, VPN or forwarding-performance benchmark was performed.

Related: [hardware](../docs/hardware.md), [GPON/VLAN](../docs/gpon.md), [ELF inventory](data/native-catalog.json).
