# Admin passwords and account roles

[Back to the guide](../README.md#admin-password)

## Default password calculation

In the examined TR v1.20 Build 250926, a conditional initialization path constructs the admin password from the LAN MAC:

```text
password = "TsPeLbN" + uppercase_hex(LAN_MAC_bytes[2:6])
```

For the synthetic address `02:00:00:12:34:56`, the last four bytes are `00:12:34:56`, giving `TsPeLbN00123456`.

```sh
python3 tools/admin_password.py 02:00:00:12:34:56
```

The calculator runs locally and prints the result. It does not connect to an ONT or attempt a login. Use the ONT's actual LAN MAC; the GPON serial, router MAC and bootloader's sample `ethaddr` are different inputs.

## When the firmware uses it

The code path runs when both of these conditions hold:

1. The initial `AdminPwd` value is `xz000`.
2. A 32-bit field at offset `0x4d0` in the `DevInfo` block is zero.

The exact source name of that field has not been recovered. A manufacturing or mode interpretation remains tentative. The [password code excerpt](../research/disassembly/password-identity.txt) records the implementation and related identity readers.

The formula describes a default, not the current password after a user or ISP changes it. Other builds, regional defaults or provisioning flags can take another initialization path. A password from one unit will therefore not necessarily work on another unit of the same model.

## Three separate account systems

| Interface | Observed identity | Authority |
|---|---|---|
| UART Linux shell | Account `admin`, UID/GID 0 | Operating-system root |
| Telnet TP-Link CLI | Admin role 2 | Manufacturer CLI commands |
| HTTP | Separate root, admin and user slots | Web session and CGI permissions |

In `/etc/passwd`, the username is the first field; a `root` description later in the line is not a second account. UID `0` supplies Linux root privileges. The Linux password hash and the web `AdminPwd` are separate credentials.

The original web account query returned empty `rootName` and `rootPwd`, with `rootEnable=0`. Changing `/etc/passwd` does not create a web-root account: COS/CMM manages the web slots. XML fields such as `PwdSign` do not replace the initialization formula with a universal decryption key.

## What the web-root experiment showed

A temporary httpd patch enabled the role-0 account slot. Login succeeded, but the interface gained no additional menus and the management page returned error `71231`. The relevant `/cgi/auth` path accepts roles 1 and 2; enabling role 0 did not satisfy every CGI permission check.

This experiment did not demonstrate a permanent root account or a complete management unlock. The [helper sources](../research/helpers/README.md) are retained to document the result, separate from the ordinary access instructions.
