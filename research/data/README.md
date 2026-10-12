# Firmware data catalogue

[Research index](../README.md)

These files describe common firmware structure. They contain no current account values, unit identity records, calibration contents or full device-capture hashes.

## Files, commands and configuration

| File | Contents |
|---|---|
| [firmware-files.json](firmware-files.json) / [TSV](firmware-files.tsv) | 255 active-rootfs regular files: type, size, mode, role and analysis method |
| [native-catalog.json](native-catalog.json) | 49 ELF files: functions, imports, dependencies and module tags |
| [cli-commands.json](cli-commands.json) | 130 entries in 42 tables: address, mode, flags, handler and hidden/encoded status |
| [constant-return-functions.json](constant-return-functions.json) | 106 functions with a two-instruction constant return |
| [web-page-catalog.json](web-page-catalog.json) | 22 pages and their OID/CGI/flag references |
| [web-build-flags.json](web-build-flags.json) | 383 feature names and assignment locations |
| [xml-schema.json](xml-schema.json) | Active default/reduced XML structure, with values removed |
| [gcs-schema.json](gcs-schema.json) | 119 GCS objects / 685 parameter definitions: names, paths, types and flags |
| [symlink-catalog.json](symlink-catalog.json) | 85 common rootfs symbolic links |

## Platform and comparisons

| File | Contents |
|---|---|
| [flash-layout.json](flash-layout.json) | MTD boundaries and identity-record offsets/sizes, without record contents |
| [kernel-2025.config](kernel-2025.config) | Kernel build configuration |
| [gc1601-2025.dts](gc1601-2025.dts) | Device Tree |
| [bank-differences.json](bank-differences.json) | Five differing rootfs files across the 2025 banks |
| [kernel-code-word-differences.json](kernel-code-word-differences.json) | Compared kernel `.text` word changes |
| [2023-rootfs-comparison.json](2023-rootfs-comparison.json) | Old/new regular-file and symlink matches |
| [2023-native-comparison.json](2023-native-comparison.json) | Old/new ELF differences |
| [2023-web-flag-comparison.json](2023-web-flag-comparison.json) | Generic V1 versus TR v1.20 build flags |
| [2023-kernel-config-comparison.json](2023-kernel-config-comparison.json) | Kernel configuration comparisons |
| [2023-source-missing-paths.json](2023-source-missing-paths.json) | Required proprietary paths absent from the GPL archive |
| [gpl-archive-summary.json](gpl-archive-summary.json) | GPL archive counts, extensions and groups |

Addresses are static ELF or flash locations. A symbol or schema entry does not prove an operational feature. Privileged writes and calibration handlers in the command catalogue are inventory entries, not recommended commands. Account/system hashes that could identify the unit are omitted.
