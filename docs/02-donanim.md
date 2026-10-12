# Donanım ve fiziksel sınırlar

| Bileşen | İncelenen v1.20 sonucu | Dayanak |
|---|---|---|
| SoC | Galachip GC1601 | Boot/kernel ve SDK |
| CPU | Tek çekirdek FA626TE, ARMv5TE, 533 MHz | CPU/saat açılış çıktısı |
| RAM | 32 MiB | Boot ve Device Tree |
| SDK rezervi | 4 MiB, fiziksel 0x41c00000 | Device Tree; Linux sayfa havuzuna dahil değil |
| Flash | 8 MiB SPI-NOR, JEDEC 0x204017 | Boot ve MTD sürücüsü |
| Flash adlandırması | Boot XM24QH64B; kernel XM25QH64B | İki ad aynı okunan JEDEC kimliğine karşılık geliyor |
| Sayfa / erase | 256 bayt / 64 KiB | SPI flash geometrisi |
| Ethernet | Tek 10/100/1000 RJ45, SGMII PHY | Genel ürün özelliği ve DT/SDK |
| Optik BOSA/BOB | UX3320S algılaması | Önceki canlı init/runtime kaydı |
| UART | ttyS0, 115200 8N1, MMIO 0x90400000 | Kernel ve konsol |
| I²C | Kontrolcü 0x90600000 etkin | DT/kernel; ikinci kontrolcü kapalı |
| Watchdog | Donanım başlangıcı 10 s; yazılım tanımı 60 s | Sürücü açılış kaydı |
| Kernel / ABI | Linux 3.16 PREEMPT, ARM LE EABI5 soft-float | Kernel ve ELF |
| Kullanıcı alanı | uClibc-ng 1.0.31; BusyBox 1.23.2; GCC 4.9.4 | Binary/kernel bilgisi |

## Hat hızı ve gerçek kapasite

Genel ürün tablosu GPON 2.488/1.244 Gb/s, EPON 1.25 Gb/s ve Class B+ bildirir. Bu genel bilgiler TR firmware’in tüm modlarının çalıştığına dair deney değildir. [Resmî ürün özellikleri](https://service-provider.tp-link.com/gpon/xz000-g7/).

Tek Gigabit Ethernet portu bilgisayara 2.488 Gb/s Ethernet çıkışı sağlayamaz. PON’un paylaşılan hat hızı, abone profili ve Ethernet/protokol ek yükü ayrı sınırlar oluşturur. Burada gigabit forwarding, paket/saniye veya NAT performansı ölçülmedi.

Kernel’de WLAN, USB, PCI, MMC ve UBI/JFFS2 kapalıdır. Genel şemadaki Wi-Fi/USB/VPN adları bu kartta ilgili donanımı oluşturmaz. DT’de max-frame-size 9000 bulunur; uçtan uca jumbo frame testi yapılmadı. PHY adresi **24 ondalık = 0x18**; eski/yeni metin gösterimleri farklı görünse de bu değer fark değildir.

Kaynak: [Device Tree](../data/gc1601-2025.dts), [kernel yapılandırması](../data/kernel-2025.config). Kart fotoğrafı, pinout/voltaj ölçümü ve harici EEPROM/OTP’nin tam haritası bu çalışmada yoktur; bunlar tahminle tamamlanmamıştır.
