# Reach the ONT through an OpenWrt router

[Back to the guide](../README.md#openwrt)

The ONT's management network can share the router's WAN cable with the Internet service. In the tested setup, management used untagged Ethernet while PPPoE used a VLAN device. OpenWrt held a management address on the underlying Ethernet device and translated LAN client traffic to it.

This worked for HTTP and Telnet on the examined unit. Other ONT port profiles or router layouts may differ.

## 1. Find the device facing the ONT

Connect to the router over SSH. Run these commands on **OpenWrt**, not on the ONT:

```sh
ubus call network.interface.wan status
ip -br link
ip -4 addr
uci show network
```

`l3_device: pppoe-wan` identifies the PPPoE interface. An underlying `device: eth1.35` means it uses a VLAN device on `eth1`. The names and VLAN ID are examples; inspect your own configuration. Bridge and DSA layouts need the actual device or port facing the ONT.

## 2. Add a management interface

Check for an existing section before creating one:

```sh
uci -q show network.ont_mgmt
```

If it exists, inspect its settings rather than replacing it blindly. For a new section, select the correct device and an unused management address:

```sh
WAN_DEVICE='eth1'
uci set network.ont_mgmt='interface'
uci set network.ont_mgmt.proto='static'
uci set network.ont_mgmt.device="$WAN_DEVICE"
uci set network.ont_mgmt.ipaddr='192.168.10.2'
uci set network.ont_mgmt.netmask='255.255.255.0'
uci set network.ont_mgmt.defaultroute='0'
uci set network.ont_mgmt.peerdns='0'
uci commit network
ifup ont_mgmt
ubus call network.interface.ont_mgmt status
ping -c 3 192.168.10.254
```

Leave the existing WAN/PPPoE interface in place. A successful router ping confirms the management path to the ONT.

## 3. Allow LAN clients to use that path

The ONT may have no return route to your LAN subnet. Adding `ont_mgmt` to the existing masquerading WAN zone gives requests a source address the ONT can reach. The router also needs its usual `lan` → `wan` forwarding policy.

```sh
uci show firewall
```

Do not assume the WAN zone is always `@zone[1]`. The following commands locate the zone by its name and proceed only if exactly one `wan` zone exists with masquerading enabled:

```sh
WAN_ZONE=$(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)\.name='wan'$/\1/p")
if [ -n "$WAN_ZONE" ] && [ "$(printf '%s\n' "$WAN_ZONE" | wc -l)" -eq 1 ] && [ "$(uci -q get "$WAN_ZONE.masq")" = '1' ]; then
    uci -q del_list "$WAN_ZONE.network=ont_mgmt"
    uci add_list "$WAN_ZONE.network=ont_mgmt"
    uci commit firewall
    /etc/init.d/firewall reload
else
    echo 'Check the WAN zone and masquerading settings; firewall was not changed.'
fi
```

The management interface inherits the zone's existing forwarding policy. Custom VPN, firewall and source-NAT rules may need adjustment. Use a separate management zone if you want access limited to selected clients or services.

## 4. Check the computer's route

On a Windows 11 computer, follow the [Windows guide](windows.md#access-through-a-router): keep the usual LAN settings and test port 80 with PowerShell. The commands below are for a Linux computer.

On Linux:

```sh
ip -4 route get 192.168.10.254
ip -br -4 addr
```

The route should go through the router's LAN address. If it instead points directly to a disconnected Ethernet interface, remove the old address used for a direct ONT connection:

```sh
PC_IFACE='YOUR_OLD_TEST_INTERFACE'
sudo ip addr del 192.168.10.2/24 dev "$PC_IFACE"
ip -4 route get 192.168.10.254
ping -c 3 192.168.10.254
telnet 192.168.10.254 23
```

Open [http://192.168.10.254/](http://192.168.10.254/) in the browser. `No route to host` and `ERR_ADDRESS_UNREACHABLE` are routing failures; they occur before password verification.

## Remove the management interface

If you created `ont_mgmt` with the steps above, remove it while leaving the Internet WAN configuration intact:

```sh
ifdown ont_mgmt
uci delete network.ont_mgmt
uci commit network
WAN_ZONE=$(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)\.name='wan'$/\1/p")
if [ -n "$WAN_ZONE" ] && [ "$(printf '%s\n' "$WAN_ZONE" | wc -l)" -eq 1 ]; then
    uci -q del_list "$WAN_ZONE.network=ont_mgmt"
    uci commit firewall
    /etc/init.d/firewall reload
fi
```

For the general OpenWrt approach, see [Accessing a modem through a router](https://openwrt.org/docs/guide-user/network/wan/access.modem.through.nat).
