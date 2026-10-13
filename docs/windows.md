# Windows 11: reach the web interface

[Back to the guide](../README.md#web-access)

The management address observed on the examined firmware is **[http://192.168.10.254/](http://192.168.10.254/)**. HTTP uses port **80**. If the management address has been changed, use the current address instead.

Choose the connection method that matches your setup:

| Connection | Where the management address is configured |
|---|---|
| PC connected directly to the ONT's Ethernet port | On the PC's Ethernet adapter |
| PC connected to a router, with the ONT on its WAN port | On the router's interface facing the ONT; the PC keeps its normal LAN settings |

## Direct Ethernet connection

Move the Ethernet cable from the router's WAN port to the PC, or connect the PC to the ONT with another cable. Keep the ONT powered on. Its optical connection can remain in place.

### 1. Set the Ethernet address

Record any existing manual IP and DNS settings before replacing them.

1. Press **Win + R**, type `ncpa.cpl`, and press **Enter**.
2. Right-click the **Ethernet adapter connected to the ONT** and select **Properties**. The adapter may have a different name, especially with a USB Ethernet adapter.
3. Select **Internet Protocol Version 4 (TCP/IPv4)** and click **Properties**.
4. Select **Use the following IP address** and set:

   | Field | Value |
   |---|---|
   | IP address | `192.168.10.2`, if unused on that link |
   | Subnet mask | `255.255.255.0` |
   | Default gateway | Leave blank |
   | Preferred / alternate DNS | Leave blank |

5. Click **OK** to save the IPv4 settings, then close the adapter properties.

The PC and ONT now share the `192.168.10.0/24` subnet. A gateway is unnecessary for this direct connection, and a numeric web address needs no DNS lookup. Windows may report **No Internet** on the Ethernet connection; the ONT's local management page can still be reachable.

### 2. Check HTTP and sign in

Open **Windows PowerShell** and run:

```powershell
Test-NetConnection -ComputerName 192.168.10.254 -Port 80
```

`TcpTestSucceeded : True` means the PC reached the HTTP port. Then enter the full address in the browser:

```text
http://192.168.10.254/
```

Sign in as **admin** with the password for your own ONT. The [password guide](passwords.md) explains the device-specific default and when the calculation applies. Another ONT's password is not interchangeable with yours.

### 3. Restore the previous network settings

When returning the cable to the router, open the same Ethernet adapter's IPv4 properties again.

If the adapter originally used DHCP, select **Obtain an IP address automatically** and **Obtain DNS server address automatically**, then save. If it previously used a manual configuration, restore those original values.

## Access through a router

The ONT can stay connected to the router's WAN port while the Windows PC uses the router's LAN or Wi-Fi.

```text
Windows PC ── LAN / Wi-Fi ── Router ── WAN Ethernet ── ONT
                                                   192.168.10.254
```

The router needs a management address in the ONT's subnet, such as an unused **192.168.10.2/24**, on the interface facing the ONT. It must route LAN requests to that interface and provide a return path. Source NAT is needed when the ONT has no route back to the LAN. The LAN and ONT management subnets must be different.

For an OpenWrt router, follow the [router management guide](openwrt.md). That setup was tested with untagged management traffic alongside VLAN-based PPPoE. Other routers need the equivalent management routing and return path.

On Windows:

1. Connect to the router's LAN or its main Wi-Fi network.
2. Keep the adapter's normal LAN configuration, usually **Automatic (DHCP)**. If you previously connected directly to the ONT, restore the old test adapter's settings as described above.
3. Run the port-80 test and open **http://192.168.10.254/**.

In this setup, `192.168.10.2` belongs to the router's ONT-facing interface. Giving the PC the same address can create a duplicate address or a route through the wrong adapter.

## If the page does not open

Start with the HTTP-port check above. A ping reply establishes ICMP reachability, but does not establish that the web service is available.

To inspect the adapter, address and route Windows selects, use:

```powershell
ipconfig
Test-NetConnection -ComputerName 192.168.10.254 -DiagnoseRouting -InformationLevel Detailed
```

For a direct connection, the selected source address should be the Ethernet address you assigned, and the route should be on-link. Through a router, the source should be the PC's normal LAN address and the next hop should be the router's LAN address.

| Result | Check next |
|---|---|
| A disconnected or old test adapter is selected | Restore its previous IP settings; remove the temporary direct-connection address |
| The router reaches the ONT, but the PC cannot | Check LAN forwarding and source NAT on the router |
| Ping works, but `TcpTestSucceeded` is `False` | Check whether port 80 is available and permitted by the ONT and router |
| Port 80 works, but the browser fails | Enter `http://` explicitly; check whether a proxy, VPN or HTTPS-only browser setting affects this local address |
| The page opens, but rejects the password | Check this ONT's LAN MAC and the default-password conditions, or use its current changed password |

Microsoft documents [Windows IP and DHCP settings](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/essential-network-settings-and-tasks-in-windows) and [PowerShell TCP and route diagnostics](https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection).
