# Firmware images and update checks

[Back to the guide](../README.md#firmware)

## Three different file types

| File | Meaning |
|---|---|
| Web-upgrade package | Vendor header and packaged boot/kernel/rootfs components |
| Kernel partition image | A bank's kernel region, including its own header |
| Full flash backup | All 8 MiB, including both banks and private device records |

A `flash-a.bin` dump is not a web-upgrade package. The vendor `IMAGE_TAG` is **512 bytes**, but sharing a header structure does not make the files interchangeable.

## Integrity and identity validation

The traced validator saves the stored token, substitutes a fixed salt/key into the token field, and calls `cen_md5VerifyDigest`. A later `SKIPMD5` log string does not show that the preceding integrity check was skipped.

The updater also checks ProductID, product/hardware version and special version. MD5 integrity is separate from a manufacturer signature or secure boot. The presence of `INCLUDE_FWUPGRADE_CHECK_RSA` and RSA library functions does not establish a complete signature chain on this upload path.

Supporting excerpts: [firmware updater](../research/disassembly/firmware-upgrade.txt) and [cryptographic checks](../research/disassembly/crypto-verification.txt).

## Write targets

The code includes writes to the inactive firmware bank and an optional bootloader update. The boot region is `0x20000` bytes; a kernel region is `0x160000` bytes.

One rootfs size check contains `0x630000`, whereas the actual rootfs partition is `0x260000`. The surrounding validation has not been resolved into a complete safe bound. That discrepancy does not establish that a larger rootfs can be written safely.

Zero rootfs/boot tokens in a kernel-partition header belong to that header's context. They do not demonstrate a bypass of all checks on a web-upload package.

## Older V1 package

The generic July 2023 V1 package differs from the 2025 TR v1.20 in product identifiers, version fields, special version and bank layout. Its rejection by the normal validator is expected from the static checks; no upload or flash test was performed.

Shared CPU, kernel configuration and Device Tree are useful comparison evidence, but are insufficient to establish compatibility. The [firmware/GPL comparison](../research/firmware-comparison.md) records the identifiers, component offsets and missing source paths.

This repository has no firmware flasher or verified unlock image. The offline helper builders produce modified application copies for research, not replacements for the main flash.
