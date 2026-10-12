# Generic V1 firmware and GPL comparison

[Research index](README.md) · [Update checks](../docs/firmware.md)

The generic V1 package and the TR v1.20 share substantial platform code. They also differ in identifiers, regional options and bank layout. **The older package's compatibility with TR v1.20 has not been established.** No build/flash experiment was performed.

## Downloaded packages

These are hashes of the downloaded common packages, not of a private device dump. Filenames and dates match the download listing used during research; an independent re-download from the official server was not compared byte-for-byte. Internal CRC/MD5 consistency alone does not authenticate the package's origin.

| File | Bytes | SHA-256 |
|---|---:|---|
| `GPL_XZ000-G7.tar.gz` | 1,261,652,937 | `4c364beb9f051f9f1fdc71a19a6b4995f4c0040ceda17ba68ad68621b57d2e74` |
| `XZ000-G7 firmware.bin.zip` | 3,812,493 | `966db0f54daef536850bac05198a8215f6f84c614ecdba10e66e1e5b88705e6c` |
| `XZ000-G7_UP_BOOT_2023-07-24_09.24.13.bin` inside ZIP | 3,832,078 | `2346108f950bb4093e3ed6c11a9ddada0d43ade4903c2263274032eb96c84feb` |

The boot/kernel build is from July 2023; the filename is dated July 24, 2023. The download listing examined during research gave March 12, 2025 as the publication date. A filename, internal build date and publication date describe different events. Likewise, the TR firmware's 2025 date does not date the physical unit.

Official references: [TR download](https://www.tp-link.com/tr/support/download/xz000-g7/) and [GPL download](https://www.tp-link.com/ca/support/download/xz000-g7/).

## Identifiers and packaging

| Field | Generic V1 package | 2025 TR v1.20 |
|---|---|---|
| ProductID | `0x20e69d01` | `0x4a4b0901` |
| Product version | `0x60066` | `0x6008e` |
| Logical hardware ID | `08b8f956df9ec339d6747e407a5a06e3` | `425ee1fe6e8ef1653d208f90090ee34a` |
| Special version | `0` | `1` |
| Platform | `0xa5030000` | `0xa5030000` |
| Boot layout | Single kernel/rootfs placement | Two firmware banks |
| UI | Generic UN / English | TR and v1.2 options |

The logical hardware IDs are common firmware-model identifiers, not unit MAC/serial records. Their difference does not prove that every board component differs. Static product/version checks suggest the normal updater would reject the old package; this was not tested by uploading it.

The 2023 upload package contains:

| Component | File offset | Bytes |
|---|---:|---:|
| Header | `0x0` | 512 |
| Bootloader | `0x200` | 127,012 |
| Kernel, including inner tag | `0x1f224` | 1,422,960 |
| Rootfs | `0x17a894` | 2,281,594 |

Internal MD5/CRC checks are consistent. A verified manufacturer signature was not established.

## Rootfs, kernel and web differences

The 2023 rootfs has 249 regular files and 85 symlinks; the 2025 rootfs has 255 and 85. There are 219 identical regular files, 30 changed files and 6 additions in 2025. The additions are five TR locale files and a TSO BOB table. Of 49 ELF files, 29 match and 20 differ.

| Binary/module | 2023 bytes | September 2025 bytes |
|---|---:|---:|
| `gcnet` | 69,440 | 79,736 |
| `xpon_sdk` | 660,964 | 687,700 |
| `gc_omcid` | 279,504 | 284,184 |
| `libcmm` | 873,800 | 877,900 |
| `libgc` | 87,856 | 91,952 |

See the [rootfs comparison](data/2023-rootfs-comparison.json) and [ELF comparison](data/2023-native-comparison.json).

The 7088-byte 2023 DTB matches both 2025 banks, with SHA-256 `197fd172b30e49c80e53ef6d42f39a2d9e43ec3997c682a233df5d1a11b9570a`. The kernel configuration also matches, with SHA-256 `23e97985b6f1a1d88269320d06cd5608634bd566f15b4149f58a6b2030062fec`. These common-file hashes do not establish identical bootloader, identity handling or driver behavior.

`DUALIMAGE`, `DUALCONFIG`, Turkish language and `INCLUDE_SPEC_XZ000G7V1_2` are enabled on the 2025 side. `WEBAGILE`, `AUTHPASSWORD` and ISP selections also differ; see the [flag comparison](data/2023-web-flag-comparison.json). The old image also lacks an SSH binary and disables the web-root slot by default.

## What the GPL archive supplies

The archive contains **159,240 regular files**, about **3.25 GB** unpacked. It supplies Linux, U-Boot and many third-party sources, but not all required proprietary CMM/COS/CLI/HTTP and PON source. The [missing build paths](data/2023-source-missing-paths.json) and [archive inventory](data/gpl-archive-summary.json) identify that gap.

The model selection is UN, with no TR model. Some configuration files contain `FLASH_8M`, but the `gc1601evb_sfu4M` target, 4 MiB/single-bank layout and actual build parameters must be considered together. The archive README says its generated image is not directly usable for web update.

The snapshot combines source and prebuilts from different dates, including a 2022 boot prebuilt and 2024 model/config/kernel material. Its prebuilt DTB is 7092 bytes, reserves 6 MiB for the SDK at `0x41a00000`, and has different PON LED GPIO/LOS initialization. The running 2025 DTB reserves 4 MiB at `0x41c00000`. PHY address `24` and `0x18` are equivalent.

The UN `config.kernel` matches the real kernel configuration, while another `kernel.config` differs in 80 options. The build copy path determines which file matters. An enabled Dropbear option in a source configuration also does not place an SSH binary in the examined firmware.

The archive is useful for understanding platform and build choices. It is not an established complete TR firmware build or a ready OpenWrt port.
