# İki okumalı tam flash ve çalışan sistem yedeği

Bu yöntem mevcut Linux UID 0 shell gerektirir. **TP-Link(conf)# bir Linux shell değildir.** ONT flash’ına yazmaz; yalnız flash okur, küçük geçici RAM dosyaları oluşturur ve PC’ye aktarır.

## Hazırlık

1. PC ile ONT Ethernet bağlantısını kurun. Yedek sırasında fiber bağlı olmak zorunda değildir.
2. PC’ye ONT yönetim ağı içinde kullanılmayan bir IP verin. Aşağıdaki 192.168.10.2 örnektir; ONT’nin varsayılan yönetimi 192.168.10.254’tür.
3. PC’de yeni terminalde alıcıyı çalıştırın. UART’ı alıcı betiği açmaz; konsol sizde kalır.
4. Açılış uyarılarının bitmesini, br0 IP’sini ve PC’ye erişimi bekleyin. Önceki otomatik denemede wget, IP/rota oluşmadan çalıştırılmıştı.

PC örneği; PC_IFACE fiziksel Ethernet arayüzünü kendiniz belirleyin:

```sh
PC_IFACE='YOUR_ETHERNET_INTERFACE'
sudo ip link set dev "$PC_IFACE" up
sudo ip addr add 192.168.10.2/24 dev "$PC_IFACE"
python3 tools/backup_receiver.py --bind 192.168.10.2 --peer 192.168.10.254
```

Alıcı TFTP UDP 1069 ve betik HTTP TCP 8000 kullanır. Yedekleri sunmaz; HTTP yalnız backup.sh verir. Çıktılar local-private/backups altında 0700 dizin/özel izinlerle tutulur.

## UART/Linux shell’de sıra

```sh
ifconfig br0
route -n
ping -c 3 192.168.10.2
tftp -p -l /proc/version -r meta/probe.txt 192.168.10.2 1069
tftp -p -l /dev/mtd0 -r flash-a.bin 192.168.10.2 1069
tftp -p -l /dev/mtd0 -r flash-b.bin 192.168.10.2 1069
wget -O /var/tmp/backup.sh http://192.168.10.2:8000/backup.sh
sh /var/tmp/backup.sh --runtime-only
```

Her aktarım bittikten sonra sıradakine geçin. TFTP’nin sessizce prompt’a dönmesi başarısızlık göstergesi değildir; PC alıcısındaki kaydedilen boyuta bakın. İki manuel flash aktarımı yapmadan --runtime-only seçmeyin. Alternatif olarak betiği seçenek vermeden çalıştırmak iki okumayı da yaptırır.

Alıcı mtd0’ı RAM’e kopyalatmadan doğrudan okur. Küçük RAM kapasitesinde gereksiz 8 MiB geçici kopyayı önler. ONT betiği UID 0, whole adı, 8 MiB boyut ve 64 KiB erase geometrisini kontrol eder; başka yerleşimde durur.

## Doğrulama

```sh
python3 tools/backup_receiver.py --verify local-private/backups/YOUR_SESSION
```

İki dosya ayrı ayrı 8.388.608 bayt olmalı ve SHA-256’ları aynı olmalıdır. Alıcı yedi bölümü çıkarır, SHA256SUMS ve verification.json oluşturur. Çalışan sistem tamamlanma kaydı/hata sayısı ayrıca değerlendirilir: runtime hatası tam flash eşitliğini kendiliğinden geçersiz kılmaz, fakat tüm dosyaların alındığı da söylenemez.

Çalışan RAM dosyaları ardışık alınır; atomik RAM görüntüsü değildir. İzin/bağ/dizin listesi dosya içeriklerinden ayrıdır. Socket’ler sıradan dosya kopyasıyla çalışır hâle getirilemez. Ana NOR yedeği ayrı EEPROM/OTP’yi kapsadığını kanıtlamaz.

**Yedek çıktıları özel bilgidir; bu depoya yüklenmez.** İleride PC router üzerinden yönetilecekse geçici doğrudan Ethernet IP’sini kaldırın; aksi hâlde kapalı Ethernet arayüzünün yerel rotası Wi-Fi üzerinden erişimi engelleyebilir.
