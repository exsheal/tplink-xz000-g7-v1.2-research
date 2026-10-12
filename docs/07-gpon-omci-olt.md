# GPON, OMCI, OLT ve optik veriler

## O5 ve ONU ID ne anlatır?

O5, ONT’nin GPON aktivasyonunda çalışma durumuna ulaştığını gösterir; her üst katman hizmetinin doğru VLAN/PPPoE profiliyle çalıştığını tek başına garanti etmez. ONU ID, OLT’nin o aktivasyonda atadığı PON içi kimliktir. OLT modeli, slot/port veya toplam abone sayısı değildir. Sayısı cihazın kalıcı seri numarası olarak kullanılmamalıdır.

Bağlı OLT’nin kesin modeli eldeki özel yedeklerde saptanmamıştır. Firmware’de üretici uyumluluk sabitleri veya seçilebilir OLT Mode bulunması, o üreticiye bağlı olduğumuzu göstermez.

## OLT-G sorgusu

OMCI OLT-G sınıfı **131**, instance **0**, vendor/equipment/version alanlarına sahip olabilir. Firmware’de bu nesnenin yerel MIB sorgu yolu ve gc_omcicli aracı bulunur:

```sh
# Linux shell gerekir; TP-Link(conf)# içinde çalıştırılmaz.
gc_omcicli mib get 131 0
```

Bu yol statik olarak doğrulandı; bağlı OLT’den canlı çıktı alınmadı. Nesne/alanlar doldurulmayabilir. UART protokol gereği zorunlu değildir: ağdan Linux shell veya MIB’i sunan başka yönetim yolu da yeterli olabilir; mevcut normal admin web/CLI’de böyle bir yol kanıtlanmadı. [ITU OLT-G, §9.12.2](https://www.ietf.org/lib/dt/documents/LIAISON/file1019.pdf).

## VLAN değişikliği gerçekten nereye gider?

CMM’deki bir setter’ın yalnız başarı döndürmesi tüm özelliği sahte yapmaz. İzlenen gerçek uygulama yolu:

```text
Web/data model
  → OMCI reload mesajı 707
  → gc_omcid
  → gcOmci_tpSetVlanMode @ 0x1df24
  → libgc_netApi_setVlanMode @ 0x6d00
  → gcnet ioctl + NAT/FDB temizleme işlemleri
```

İzlenen modlar 0=OLT, 1=Tag, 2=Transparent; VID 1–4094, priority 0–7. Bunlar bu binary’deki mapping’dir; tüm vendor/operatör profilleriyle canlı test yapılmadı. Reload yolu PON hizmetini etkileyebilir; katalogdaki ayarlar uygulama önerisi değildir. [Statik VLAN izi](../evidence/gcs-vlan.txt).

## Optik ölçüm ve kalibrasyon

Web Tx/Rx gücü, sıcaklık, voltaj ve bias alanları gccli bob opt üzerinden gerçek getter’lara gider. UX3320S canlı algılamasıyla runtime/flash optik blok eşleşmesi incelenmiştir. Gerçek ölçümler ve kalibrasyon bloğu bu yayına dahil değildir.

gc_default_bob*.bin dosyalarının bazıları uzantılarına rağmen metin register tablolarıdır. GN25L95/TSO40202 şablonlarının bulunması cihazın bu optiklerle donatıldığı anlamına gelmez. UX varsayılan tablosuyla eşleşen bir alt alan, tüm 4096 bayt kalibrasyonun varsayılan olduğu sonucunu vermez. EEPROM alanlarının tam semantiği çözülmedi.

Lazer gücü, bias, modülasyon ve LOS eşikleri değiştirilmedi. Ölçüm gösterimi, optik güç ayarını keyfî artırmanın çalışacağına dair kanıt değildir.

Sayaç yollarında 32 bit dönüşüm ve atoi kullanımı görülür; INT_MAX civarında görünen sabit değer kapasite veya kota diye yorumlanamaz. FEC getter’ında iki alanın aynı kaynaktan doldurulması iki bağımsız ölçüm olduğu varsayımını zayıflatır. [GPON getter/setter kanıtı](../evidence/gpon-status-auth.txt).
