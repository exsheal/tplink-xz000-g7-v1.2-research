# June and September 2025 banks

[Research index](README.md)

The two examined banks use the same v1.20 flash layout. Exactly **five regular rootfs files** differ; the rest match byte-for-byte. The [difference catalogue](data/bank-differences.json) records the compared files and ELF sections.

| File | Observed difference |
|---|---|
| BusyBox | Build date/information |
| `reduced_data_model.xml` | Build, revision and date fields |
| `libcmm.so` | Two selected native functions |
| `xpon_sdk.ko` | 665,908 → 687,700 bytes; 19 new named functions |
| `gc_omcid` | Text/data changes |

The September `initDev2GponAuth` path removes an automatic GPON-serial fallback write present in June. An explicit serial setter remains, so the change does not remove every serial-setting capability. The full behavioral effect of CTC changes is unresolved.

The examined kernel `.text` comparison found **127 differing 32-bit words**. They indicate pointer shifts of `+4` in that region; no changed instruction opcode was identified there. This does not make the complete kernel binaries identical. The configurations and Device Trees match. See the [word comparison](data/kernel-code-word-differences.json) and [earlier auth initialization](disassembly/bank1-auth-initialization.txt).

Every function's behavior was not exercised on each bank. These are firmware build dates, not board manufacturing or sale dates.
