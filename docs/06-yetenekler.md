# Yetenek matrisi

Bu tablo v1.2 / TR v1.20 Build 250926 içindir. Genel modelin pazarlama listesi ve firmware şeması ile çalışan özellikler ayrılmıştır.

| Yetenek | Durum | Dayanak / sınır |
|---|---|---|
| GPON kayıt ve hizmet | Canlı doğrulandı | Önceki O5 ve internet hizmeti; WAN PPPoE dış router’da |
| Ethernet–PON köprü | Canlı + kod doğrulandı | br0 / eth0.0 / pon0.0 ve SFU sürücüsü |
| Web yönetimi HTTP 80 | Canlı doğrulandı | Admin girişi doğrudan ve OpenWrt üzerinden |
| Telnet TCP 23 | Canlı doğrulandı | Admin üretici CLI oturumu |
| UART Linux UID 0 | Canlı doğrulandı | Admin adlı hesabın UID/GID 0 olması |
| Ağdan Linux shell | Belirsiz | Normal Telnet CLI shell değildir; yüksek rol yolu ayrı |
| SSH / Dropbear | Kapalı/eksik | Daemon yok; passwd/dizin tek başına yeterli değil |
| Kalıcı web root | Doğrulanmadı | Orijinal root hesabı kapalı; RAM denemesi menü yetkisini çözmedi |
| GPON SN/password ayarı | Kod yolu doğrulandı | CMM → flash/OMCI/SDK; servis üzerinde denenmedi |
| LOID / CTC | UI/API mevcut | Operatörle kullanım doğrulanmadı |
| VLAN OLT / Tag / Transparent | Kod yolu doğrulandı | OMCI reload → gerçek VLAN ioctl |
| VLAN translation/trunk | SDK/API mevcut | Tüm kombinasyonlar/hizmet profili denenmedi |
| T-CONT ve kuyruk | API sınırı doğrulandı | Getter 16 T-CONT, her T-CONT/LLID için 8 kuyruk döndürüyor |
| GEM / AES / FEC / DBA | Kod/API mevcut | Tüm OMCI profilleri denenmedi; genel ürün tablosu 256 GEM |
| Tx/Rx/ısı/voltaj/bias | Canlı + kod doğrulandı | Gerçek gccli bob opt ölçüm yolu |
| Ethernet loop detection | Süreç mevcut | Loop senaryosu denenmedi |
| EPON | Kod mevcut, canlı belirsiz | XPON/OAM araçları; mevcut hizmet GPON, EPON UI kapalı |
| XG-PON / XGS-PON | Destek kanıtı yok | 10G donanım desteği doğrulanmadı |
| DHCP/LAN | Program/UI mevcut | Hizmet testi yok; init’te boş pool görülebiliyor |
| IPv6 | Kernel mevcut, varsayılan kapalı | disable_ipv6 init ayarı ve eksik servisler |
| ONT üzerinde PPPoE/NAT router | Tam çalışma kanıtı yok | NAT kernel/API var; pppd yok ve SFU/NO_WAN derleme bağlamı |
| Wi-Fi / Mesh | Kapalı/eksik | Donanım/kernel yok; genel şema taşıması yanıltıcı |
| VPN / VoIP / LTE | Kapalı/eksik | İlgili program/donanım desteği yok |
| TR-069 / TR-369 | Kapalı/eksik | Genel yönetim tanımları etkin daemon kanıtı değil |
| Jumbo frame | Belirsiz | DT 9000, canlı uçtan uca test yok |
| TFTP/HTTP/XMODEM recovery | Kod mevcut | Restore deneyi yok |
| Firmware doğrulaması | Kod yolu doğrulandı | MD5 ve ürün/sürüm kontrolü; kriptografik imza zinciri ayrıca belirsiz |
| OpenWrt’yi ONT’ye kurma | Kanıt yok | Genel GPL kernel kaynağı tam çalışan OpenWrt portu değildir |

32 MiB RAM ve 8 MiB flash, genel amaçlı router iş yüklerini ciddi sınırlar. Gerçek çalışan köprüye yönlendirici/VPN özellikleri varmış gibi yaklaşmak uygun değildir. [Donanım](02-donanim.md), [GPON/VLAN](07-gpon-omci-olt.md), [ELF katalogu](../data/native-catalog.json).
