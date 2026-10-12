# Firmware research

[Main guide](../README.md)

These notes explain the implementation behind the access procedures. The target is the **XZ000-G7 v1.2 TR variant**, reported as **v1.20**, running the September 2025 Build 250926.

The work combines live console/web observations, two matching 8 MiB main-flash reads, runtime file captures, both extracted firmware banks and a separately downloaded generic V1 firmware/GPL package. The original captures were kept unchanged; format adjustments were made to analysis copies.

## Browse the findings

| Area | Notes |
|---|---|
| Supported and missing features | [Capabilities](capabilities.md) |
| Filesystems, services and configuration flow | [System internals](system.md) |
| ARM, XML, GCS and web implementation | [Reverse engineering](reverse-engineering.md) |
| June and September 2025 firmware | [Bank comparison](bank-comparison.md) |
| Older V1 firmware and GPL sources | [Firmware comparison](firmware-comparison.md) |
| Symbols, command tables, schemas, kernel and DT | [Data catalogue](data/README.md) |
| Selected supporting ARM code | [Disassembly](disassembly/README.md) |
| Build-specific config/account/replay experiments | [Helper sources](helpers/README.md) |
| Manufacturer documentation and standards | [Sources](sources.md) |

## What was examined

The active rootfs contains 255 regular files and 49 ELF files: 27 programs, 15 libraries and 7 kernel modules. Both banks were inventoried. The decoded CLI has 42 tables and 130 entries; the web catalogue has 22 HTML pages and 383 feature names. XML and GCS structures were decoded, and selected password, account, GPON, VLAN and upgrade paths were traced through ARM disassembly and relocations.

The GPL archive contains 159,240 regular files. Its inspection focused on platform and build configuration, including archive counterparts of 72 selected firmware/build files. It is not a semantic review of every source line or every native function.

## How to read a finding

| Basis | What it establishes |
|---|---|
| Live observation | The behavior appeared in a console session or web interface |
| Traced code path | Data and calls were followed in the binary; hardware behavior may still be untested |
| Symbol, schema or template | A definition exists; reachability and functionality need further evidence |
| Disabled or missing component | A build flag, binary or implementation required by the feature is absent |
| Unresolved | The available evidence does not support a conclusion |

For example, a VLAN ioctl path is stronger evidence than a VLAN menu label, but it still does not prove every operator profile works. Matching Device Trees do not establish compatibility between entire firmware packages.

The catalogues describe common firmware structure. Unit identities, account values, calibration records and full capture hashes are excluded. Consequently, readers can inspect the selected code and structure without reproducing every private byte comparison.

## Open questions

- The attached OLT's make/model and a live OLT-G response.
- The source names and full semantics of manufacturing/privilege flags.
- A working Linux-shell path over the network and a complete permanent web-root implementation.
- External EEPROM, OTP and flash security-sector coverage.
- The complete RSA/secure-boot validation chain.
- EPON activation, additional OMCI/VLAN profiles, jumbo frames and performance measurements.
- A complete TR firmware build from available sources, including the missing proprietary components.
- The older V1 package's actual update outcome; static checks suggest incompatibility, but no flash test was performed.

New results should identify the hardware revision, region, firmware build and interface used. See [contributing](../CONTRIBUTING.md).
