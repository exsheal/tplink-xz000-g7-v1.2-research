# TP-Link XZ000-G7 v1.2 — TR

**TP-Link XZ000-G7 v1.2 donanımı ve TR firmware’i üzerine bağımsız teknik araştırma.** Cihazın yazılımda bildirdiği tam donanım sürümü **v1.20**; incelenen aktif yazılım **0.8.0 3.0.0 v608e.0 Build 250926 Rel.61253n**. Başlıktaki v1.2, bu revizyonu belirtir. Genel **V1 / 2023** indirme paketi ayrıca karşılaştırılmıştır; aynı model adını taşıması uyumluluk kanıtı değildir.

Bu model, GC1601 / ARMv5TE işlemci, 32 MiB RAM, 8 MiB SPI-NOR ve tek Gigabit Ethernet portu taşıyan bir köprü ONT’sidir. GPON, Ethernet–PON köprüsü, optik ölçümler, web/Telnet yönetimi ve UART üzerinden Linux UID 0 erişimi önceki canlı kayıtlarla doğrulanmıştır. Wi-Fi/VPN gibi genel yönlendirici şemalarının bulunması, bunların kullanılabildiği anlamına gelmez.

Parola üretim mekanizması, hesaplama aracı, flash bölüm düzeni ve kayıt adresleri bu depoya dahildir. **Gerçek cihaz parolaları, MAC/GPON seri numaraları, kişisel bilgiler, ham flash ve kalibrasyon içerikleri dahil değildir.** Örnek kimlikler yapaydır. Üretici firmware’i ve büyük GPL arşivi yeniden dağıtılmaz; bunların karşılaştırma sonuçları ve resmî kaynak bağlantıları sunulur.

## Belgeler

| Kategori | İçerik |
|---|---|
| [Araştırmanın kapsamı](docs/01-kapsam-ve-kanit.md) | Hangi veriler incelendi, ne doğrulandı, ne belirsiz? |
| [Donanım ve sınırlar](docs/02-donanim.md) | SoC, RAM, optik, Ethernet, performans sınırları |
| [Flash ve açılış](docs/03-flash-ve-boot.md) | Tam bölüm tablosu, kimlik kayıt adresleri, iki bank |
| [Yedek alma](docs/04-yedekleme.md) | Manuel UART + iki okumalı TFTP aktarımı, bütünlük ve kapsam |
| [Linux ve servisler](docs/05-linux-ve-servisler.md) | SquashFS, RAM dosyaları, SDK/CMM/COS/OMCI mimarisi |
| [Yetenek matrisi](docs/06-yetenekler.md) | Çalışan, kodda bulunan, kapalı ve belirsiz özellikler |
| [GPON, OMCI ve OLT](docs/07-gpon-omci-olt.md) | ONU ID, OLT-G, VLAN yolu, optik ölçüm ve sayaçlar |
| [Parola ve hesaplar](docs/08-parola-ve-hesaplar.md) | Varsayılan admin formülü, koşulları, Linux/CLI/web farkları |
| [UART, Telnet, SSH ve web](docs/09-erisim-ve-cli.md) | CLI yetki tablosu, sorgular, web root denemesinin sonucu |
| [OpenWrt üzerinden erişim](docs/10-openwrt-erisim.md) | WAN fiziksel portunda ONT yönetim ağı, NAT, eski PC rotası |
| [Tersine mühendislik](docs/11-tersine-muhendislik.md) | ARM, XML/GCS/iQoS biçimleri, sabit dönen işlevler |
| [Firmware kontrolü](docs/12-firmware-guncelleme.md) | IMAGE_TAG, MD5, ürün/sürüm kontrolleri ve sınırlar |
| [2025 bank farkları](docs/13-2025-bank-karsilastirmasi.md) | Haziran–Eylül bankları arasındaki beş dosya farkı |
| [2023 V1 ve GPL karşılaştırması](docs/14-v1-2023-ve-gpl.md) | Eski firmware, GPL kapsamı, v1.20 uyumluluk değerlendirmesi |
| [Hatalar ve açık sorular](docs/15-hatalar-ve-acik-sorular.md) | Açılış uyarıları, eksik programlar, henüz kanıtlanmayanlar |
| [Veri katalogları](data/README.md) | Dosya, ELF, CLI, web, şema ve karşılaştırma tabloları |
| [Araçlar](tools/README.md) | Parola hesaplayıcı, yedek alıcı, analiz ve yayın kontrolleri |
| [Teknik kaynaklar](docs/16-kaynaklar.md) | Resmî ürün, indirme, OMCI, TFTP ve araç belgeleri |
| [Gizlilik](PRIVACY.md) | Yayımlama kapsamı ve katkılarda özel bilgi ayıklama |
| [GitHub’a yükleme](PUBLISHING.md) | Hazır paketten depo oluşturma ve yükleme |

## Hızlı başlangıç

```sh
# Yapay MAC örneği; gerçek parolayı buraya veya issue'ya yazmayın.
python3 tools/default_admin_password.py 02:00:00:12:34:56
# Beklenen: TsPeLbN00123456

# Ağ/ONT bağlantısı olmadan yerel dosyaları kontrol eder.
python3 tools/verify_public.py .
python3 -m unittest discover -s tests -v
```

Belgelerde **canlı doğrulandı**, **kod yolu doğrulandı**, **kod/şema mevcut**, **kapalı/eksik** ve **belirsiz** ayrımı kullanılır. Dosyaların bütün baytlarının okunması, bütün assembly işlevlerinin her girdideki davranışının kanıtlandığı anlamına gelmez. Özel girdiler yayımlanmadığı için ham yedeğe bağlı her sonucu bu depodan tek başına yeniden üretmek mümkün değildir.

**English:** Independent research on the TP-Link XZ000-G7 v1.2 (device-reported v1.20), Turkish 2025 firmware. Includes password derivation, flash layout, categorized findings, sanitized catalogs and locally usable research tools. No unit credentials, identifiers, raw dumps or vendor firmware binaries. Older generic V1 firmware compatibility is not established.

TP-Link veya internet servis sağlayıcısıyla resmî bir bağlantı yoktur. [Lisans ve kaynak kapsamı](NOTICE.md).
