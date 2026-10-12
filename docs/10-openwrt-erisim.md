# OpenWrt router üzerinden ONT yönetimine erişim

ONT’nin Ethernet’i router WAN portuna bağlıyken, router bu **fiziksel port üzerinde ayrıca 192.168.10.0/24 yönetim IP’si** taşıyabilir. İnternet PPPoE/VLAN arayüzünde çalışırken yönetim trafiği ayrı, etiketsiz fiziksel yol kullanabilir. Bu yöntem önceki kurulumda web/Telnet için çalışmıştır; her operatör/ONT port profilinde garanti değildir.

## 1. Doğru fiziksel aygıtı bulun

Router SSH içinde:

```sh
ubus call network.interface.wan status
ip -br link
ip -4 addr
uci show network
```

PPPoE l3_device ve altında VLAN aygıtı farklıdır. Örneğin pppoe-wan / eth1.35 görülüyorsa fiziksel aygıt eth1 olabilir. **eth1 ve VLAN 35 yalnız örnektir; kendi çıktınızı esas alın.** bridge/DSA yapısında portu körlemesine seçmeyin.

## 2. Yönetim arayüzünü ekleyin

Mevcut ont_mgmt bölümü varsa önce değerlerini inceleyin. Aşağıdaki komutlar bu örnekte yeni bölüm içindir. WAN_DEVICE’ı doğru aygıta ve yönetim IP’sini çakışmayacak adrese ayarlayın.

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

Bu yeni arayüzü kaldırmak için network.ont_mgmt bölümünü silip commit/ifdown kullanılır; var olan WAN internet ayarını değiştirmeye gerek yoktur.

## 3. LAN’dan erişim ve NAT

Router’dan ping başarılıysa fiziksel yol çalışıyordur. ONT’nin LAN bilgisayarlarına dönüş rotası olmayabilir; mevcut masquerading etkin wan zone’una ont_mgmt eklemek dönüşte router yönetim IP’sini kullanır. Mevcut lan → wan forwarding de gerekir.

```sh
uci show firewall
```

Zone sırasının daima @zone[1] olduğu varsayılmaz. name=wan olan zone’u bulup onun network listesine ont_mgmt ekleyin. Aşağıdaki doğrulama yalnız tek wan zone ve masq=1 için çalışır:

```sh
WAN_ZONE=$(uci show firewall | sed -n "s/^\(firewall\.[^.]*\)\.name='wan'$/\1/p")
if [ -n "$WAN_ZONE" ] && [ "$(printf '%s\n' "$WAN_ZONE" | wc -l)" -eq 1 ] && [ "$(uci -q get "$WAN_ZONE.masq")" = '1' ]; then
    uci -q del_list "$WAN_ZONE.network=ont_mgmt"
    uci add_list "$WAN_ZONE.network=ont_mgmt"
    uci commit firewall
    /etc/init.d/firewall reload
else
    echo 'WAN zone/masquerading ayarını inceleyin; firewall değiştirilmedi.'
fi
```

Bu örnek internet WAN’dan yeni bir gelen yönetim erişimi açmaz; LAN’dan yönlendirilen mevcut zone yolunu kullanır. Farklı firewall/policy/VPN kuralı varsa ayrıca değerlendirilir. WAN zone’una ekleme mevcut LAN→WAN politikasının erişim kapsamını kullanır; daha dar kapsam isteyen kurulum ayrı zone/rules tasarlamalıdır.

## 4. PC’de eski doğrudan ONT rotası

```sh
ip -4 route get 192.168.10.254
ip -br -4 addr
```

Hedef kapalı Ethernet arayüzüne doğrudan gidiyorsa daha önce verilen 192.168.10.2/24 adresi rota oluşturmuş olabilir. Bu adresin yalnız eski test ayarı olduğundan emin olduktan sonra ilgili PC arayüzünden kaldırın:

```sh
PC_IFACE='YOUR_OLD_TEST_INTERFACE'
sudo ip addr del 192.168.10.2/24 dev "$PC_IFACE"
ip -4 route get 192.168.10.254
ping -c 3 192.168.10.254
telnet 192.168.10.254 23
```

Hedefin router LAN IP’si üzerinden gitmesi beklenir. Web adresi http://192.168.10.254/ olur. Önceki “No route to host / ERR_ADDRESS_UNREACHABLE” hatasının nedeni bu PC rotasıydı; router ping’i başarılı olmasına rağmen PC yanlış yoldan gidiyordu. Ağ erişimi ile parola hatası farklı aşamalardır.
