# Troubleshooting

[Back to the guide](../README.md)

## Cannot reach the web page or Telnet

Check reachability before changing credentials. On Linux:

```sh
ip -4 route get 192.168.10.254
ping -c 3 192.168.10.254
```

On Windows 11, use PowerShell:

```powershell
Test-NetConnection -ComputerName 192.168.10.254 -Port 80
Test-NetConnection -ComputerName 192.168.10.254 -DiagnoseRouting -InformationLevel Detailed
```

The [Windows guide](windows.md) covers adapter settings, DHCP restoration and interpreting the results.

If the router can ping the ONT but the computer cannot, inspect the computer's route and any old direct-Ethernet test address. The [OpenWrt guide](openwrt.md) explains the management interface, NAT and return path.

`ERR_ADDRESS_UNREACHABLE` and `No route to host` indicate a network failure. A web message saying `pwd not correct` means the request reached authentication; check the LAN MAC and [default-password conditions](passwords.md), or use the current changed password.

## Startup messages

The startup scripts contain paths inherited from other product configurations. Read early failures alongside the final interface, listener and process state.

| Message or observation | Interpretation |
|---|---|
| `eth0` / `pon` missing early in init | SDK network modules load later; inspect the interfaces after boot finishes |
| `br0` already exists / interface already in bridge | Repeated initialization; does not by itself show a broken bridge |
| `mini_httpd`, `ntpc`, `dnsmasq`, `radvd`, `ethphxcmd` missing | Shared scripts request unavailable binaries; the actual `httpd` can still start later |
| `gcponmap`: `File exists` | Module was already loaded |
| Config signature `0xffffffff` / excessive length | Erased or invalid stored record triggers a fallback path |
| Unrecognized XML object or parameter | Default XML and reduced data model differ |
| Missing `/proc/gpon/debug` or other vendor paths | This driver/build exposes different or fewer proc entries |
| `iptables: Bad rule` | Often a deletion or reconfiguration of a rule that is absent; does not prove all forwarding failed |
| Root filesystem at 100% in `df` | Expected for the fixed read-only SquashFS image |
| `ttyS0` input overrun | Input may be lost during heavy output; wait for a quiet console and send commands individually |

On the ONT's Linux shell, supported checks include:

```sh
ifconfig -a
route -n
netstat -lnt
ps w
cat /proc/mtd
```

This BusyBox does not support `netstat -p`, and lacks `id` and `ip` applets.

## Web service and error 71231

An httpd process without a port-80 listener can be waiting for COS initialization. The [access guide](access.md#restarting-the-web-service) describes the messages observed after an experimental restart.

Error `71231` occurred on the management page after a role-0 RAM patch. Login succeeded but did not satisfy the page's CGI role checks. There is no verified permanent web-root fix in these notes.

## Backup warnings

Use the receiver's report to distinguish a flash-transfer failure from a runtime-copy error. Both full reads must contain 8,388,608 bytes with matching SHA-256 hashes. Runtime failures are listed separately in `meta/errors.txt`.

Do not restart a transfer into an existing saved filename: the receiver preserves completed files. Start a fresh receiver session if another complete capture is needed. See [backup verification](backup.md#5-verify-the-saved-session).

Unresolved firmware questions are tracked in the [research overview](../research/README.md#open-questions).
