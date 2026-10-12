# Sources

[Research index](README.md)

| Primary source | Used for |
|---|---|
| [TP-Link XZ000-G7 specifications](https://service-provider.tp-link.com/gpon/xz000-g7/) | Generic model specification; not proof that every TR firmware option works |
| [TP-Link TR download](https://www.tp-link.com/tr/support/download/xz000-g7/) | Generic V1 firmware listing |
| [TP-Link CA download](https://www.tp-link.com/ca/support/download/xz000-g7/) | GPL download entry |
| [TP-Link EN download](https://www.tp-link.com/en/support/download/xz000-g7/) | Revision selection; a V1 listing alone does not establish v1.20 compatibility |
| [ITU-T G.988](https://www.itu.int/rec/T-REC-G.988/en) | OMCI standard |
| [OLT-G definition, section 9.12.2](https://www.ietf.org/lib/dt/documents/LIAISON/file1019.pdf) | Class 131 vendor/equipment/version fields |
| [RFC 1350](https://www.rfc-editor.org/rfc/rfc1350.html) | TFTP octet mode, 512-byte blocks and acknowledgments |
| [RFC 2347](https://www.rfc-editor.org/rfc/rfc2347.html) | TFTP option negotiation |
| [tio manual source](https://github.com/tio/tio/blob/master/man/tio.1.in) | UART terminal settings |
| [OpenWrt modem-management guide](https://openwrt.org/docs/guide-user/network/wan/access.modem.through.nat) | Separate management access through a router |

## Repository evidence

[Disassembly excerpts](disassembly/README.md) support selected account, format and driver findings. The [data catalogue](data/README.md) contains common firmware structure, symbols, schemas and comparisons. Static addresses refer to the examined build and do not replace live hardware tests.

Raw device backups, complete UART logs and decoded account/configuration values are excluded. Common library/package hashes are included where useful; the full device-dump hash is not.
