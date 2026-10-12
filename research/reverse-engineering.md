# Formats and reverse engineering

[Research index](README.md)

## ELF and ARM

The firmware uses ARM little-endian EABI5 with soft-float. Sections, imports, exports, defined functions and module tags for the active 49 ELF files are in the [native catalogue](data/native-catalog.json). PLT entries and relocations were used to follow calls. For stripped code, inferred names and addresses are tied to the examined build; not every function's original source meaning is known.

The [constant-return catalogue](data/constant-return-functions.json) records 106 functions with a two-instruction constant return. That shape alone is not proof of a dummy feature: a hardware-capacity getter can validly return a constant. A setter returning success without doing work establishes only that behavior on its own path; later OMCI apply calls must be traced separately.

## TP-Link XML

The XML files use the firmware DES-ECB constant **`478DA50FF9E3D2CB`**. This is a common format key, separate from a unit's admin password or account hash. Container and padding validation are still required; arbitrary blobs are not all encoded in this format.

Vendor XML can contain unquoted attributes and `{i}` names that ordinary parsers reject. Analysis copies were normalized for parsing. The active `default_config` has 593 elements; `reduced_data_model` has 6182. The [XML catalogue](data/xml-schema.json) includes paths, structural attributes and child counts, with values and account defaults removed.

## GCS serialized heap

Default/current GCS files contain an LZMA-packed serialized heap. The examined layout uses a 1 MiB heap, 48-byte object structures, length-prefixed names, parameter definitions and type/flag information. The decoded schema has **119 objects and 685 parameter definitions**.

Value blocks and runtime object instances are separate from that schema. Private default/current decoding yielded 771 and 853 typed values respectively; those counts do not establish that every defined feature is active. The values are excluded from the repository.

See the [GCS schema](data/gcs-schema.json) and [heap layout excerpt](disassembly/gcs-heap-layout.txt).

## iQoS and web flags

`database.bin` has a five-byte header followed by LZMA/XML. Its 18 application definitions can originate from other TP-Link products. The corresponding build features are disabled here, so the definitions do not establish a working QoS engine.

The [web catalogue](data/web-page-catalog.json) covers 22 HTML pages. The [build-flag catalogue](data/web-build-flags.json) records 383 feature names and assignment locations. Parent flags matter: `WIFI11R=1` with `WIFI=0` does not establish Wi-Fi. `WEBTELNET=0` can hide a web control while a Telnet daemon still runs.

## Analysis workflow

The workflow kept original inputs unchanged: hash the input, split the image, extract analysis copies, index formats/symbols/relocations, then trace selected behavior and cross-check it against another source or observation.

The [offline image inspector](../tools/inspect_image.py) checks basic layout and markers. It does not perform full ARM analysis, validate all vendor tags or establish firmware compatibility.

Private captures are excluded, so every runtime-value comparison cannot be reproduced from this repository alone. Helper addresses and patch regions belong to exact Build 250926 ELF files and must not be carried into another firmware unmodified.
