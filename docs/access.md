# Web, Telnet and UART access

[Back to the guide](../README.md#telnet)

## Web and Telnet login

HTTP on port 80 and Telnet on port 23 were observed on the examined firmware. Both accepted the admin account. Reach `192.168.10.254` by a direct Ethernet connection or through [an OpenWrt router](openwrt.md), then use the [default password calculation](passwords.md) if the default is still in effect.

For Windows 11, see the [web-access guide](windows.md), including direct Ethernet settings and access through a router.

```sh
telnet 192.168.10.254 23
```

The prompt `TP-Link(conf)#` is the vendor CLI. It is distinct from the Linux shell obtained over UART. Service availability can change with firmware or operator configuration.

## Information commands

The decoded CLI contains 130 entries across 42 tables. These queries were identified in the binary and do not request a reset, configuration write or calibration:

```text
help
dev version
dev show prodName
dev show prodVer
dev show prodSoftVer
dev show prodHardVer
gponctrl show status
gponctrl show optical
```

Not every query was repeated in a live session. `gponctrl show sn` also exists, but returns the unit's private GPON serial. The [full command catalogue](../research/data/cli-commands.json) includes hidden and privileged handlers; it is a research inventory, not a list to run indiscriminately.

The admin CLI role is 2. `sh` and `enable` require role 3 in the decoded tables. A command being hidden from `help` does not make it available to admin.

## UART Linux shell

The console uses `ttyS0` at **115200 baud, 8 data bits, no parity, 1 stop bit**. With a correctly connected adapter, a PC terminal can be opened with:

```sh
tio -b 115200 /dev/ttyUSB0
```

The adapter name may differ. A board pinout and electrical level have not been established in this repository.

Once Linux has finished booting, press Enter to activate the console. The examined image offered an `admin` shell with UID 0. Verify the process identity using an applet actually present in this BusyBox build:

```sh
cat /proc/self/status
```

`Uid: 0 0 0 0` confirms root authority. `id`, `ip`, `dd`, `tar` and `nc` are absent from the examined BusyBox applet list. For listeners, use `netstat -lnt`; this build does not support `netstat -p`.

## SSH

No SSH server binary was found in this image. A `dropbear` entry in `/etc/passwd` does not establish a running Dropbear daemon. A working SSH setup on this ONT has not been demonstrated.

## Privileged and factory paths

The CLI contains handlers for MAC/SN/product fields, register and I²C access, `dumpDm`, `dumpCfg`, UART control and optical calibration. The `sys` path checks arguments and privilege, plus a private `DevInfo` flag or an uptime of at most 600 seconds. The field's source name is unresolved. WLAN/WPS labels in factory code do not establish radio hardware.

The top-level `sys` argument uses Base64 and DES decoding. Its base bytes are `47 8d e3 f9 0b a5 d2 cf`; on the normal path, a ProductID query is followed by XOR with the first eight buffer bytes. The base bytes alone are not a fixed working key. Caller and exceptional-path conditions remain incomplete.

Some register handlers concatenate an argument into shell text. That is a static observation; the parser, role checks and live reachability have not been resolved into a working network-shell method.

## Restarting the web service

An httpd process can exist without listening on port 80. COS supplies initialization messages for HTTP configuration (`2030`), challenge state (`2033`) and user information (`2031`). Replaying those messages restored a listener after an experimental restart. Starting `/bin/httpd` alone was insufficient in that case.

The [research helpers](../research/helpers/README.md) document that behavior. They are tied to exact Build 250926 binaries and are not part of the normal login procedure.
