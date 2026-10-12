# Biçimler ve tersine mühendislik yöntemi

## ELF / ARM

Firmware ARM little-endian EABI5 soft-float kullanır. Aktif 49 ELF’in bölümleri, import/export/defined function bilgileri ve modül etiketleri [native katalogda](../data/native-catalog.json). PLT ve relocation’lar çağrı hedeflerini izlemek için kullanıldı. Stripped binary’de adres/işlev yorumu doğrulama düzeyine göre sunulur; tüm sembollerin orijinal kaynak anlamı biliniyor denmez.

[106 sabit dönüş işlevi](../data/constant-return-functions.json) ayrı kataloglandı. İki instruction ile dönüş yapan her işlev sahte özellik değildir: T-CONT kapasitesi gibi donanım sınırı getter’ı sabit dönebilir; setter’ın hiçbir işlem yapmadan başarı dönmesi ise ilgili çağrı yolunda iş yapılmadığını gösterir. Daha sonraki OMCI apply yolu ayrı izlenmelidir.

## TP-Link XML

XML dosyalarında DES-ECB anahtar sabiti **478DA50FF9E3D2CB** görülür. Bu firmware sabiti cihazın özel admin parolası veya ayrı hesap hash’i değildir. Format üzerinde ayrıca container/padding kontrolleri gerekir; anahtarı bütün blob’lara körlemesine uygulamak doğru değil.

Vendor XML, tırnaksız attribute ve {i} adları gibi standart parser’a uymayan öğeler içerir. Parse etmek için yalnız analiz kopyası normalleştirildi. Aktif default_config 593 element, reduced_data_model 6182 elementtir. [XML şema katalogu](../data/xml-schema.json) yalnız yol/yapısal attribute/çocuk sayısı taşır; değer ve hesap varsayılanları çıkarılmıştır.

## GCS config heap

GCS default/current dosyaları LZMA ile paketlenmiş serileştirilmiş heap içerir. İncelenen düzende 1 MiB heap, 48 bayt nesne yapıları, uzunluk önekli adlar, parametre tanımları ve type/flag bilgileri vardır. 119 nesne / 685 parametre tanımı çözüldü. Değer blokları ve aynı nesnenin runtime örnekleri şemadan ayrıdır.

Özel default/current çözümünde 771 ve 853 typed value elde edilmesi, bütün tanımların o anda çalışan bir özellik olduğu anlamına gelmez. Değerler yayımlanmaz. [GCS şeması](../data/gcs-schema.json) ad/yol/type/flag bilgisi verir; [yerleşim izi](../evidence/gcs-heap-layout.txt) formatın statik yorumunu açıklar.

## iQoS ve web build flags

iQoS database.bin, 5 bayt başlık ardından LZMA/XML taşır; başka TP-Link ailelerinden uygulama tanımları kalabilir. Bu cihazda ilgili build seçeneklerinin kapalı olması nedeniyle 18 uygulama tanımı QoS’nin canlı çalıştığını kanıtlamaz.

Web’de 22 HTML sayfası, 383 özellik adı ve bunların atama yerleri kataloglandı. Bazı alt bayraklar 1 iken üst özellik 0’dır: WIFI11R=1 / WIFI=0, Wi-Fi var sonucunu vermez. WEBTELNET=0 webde ilgili kontrolü gizleyebilir; Telnet daemon’un kapalı olduğunu tek başına göstermez.

## Yeniden üretilebilirlik

Yöntem: girdiyi değiştirmeden hash → bölümleme → analiz kopyasını açma → format/symbol/relocation indeksleme → hedefli codepath → bağımsız çapraz kontrol. [Çevrimdışı imaj inceleyicisi](../tools/inspect_image.py) yalnız temel biçim/yerleşim kontrolü yapar; tam ARM davranış analizinin yerine geçmez.

Özel kaynaklar yayımlanmadığından tüm çözülmüş runtime değerlerinin yeniden üretimi mümkün değildir. Adresler Build 250926 içindir; değişik ELF’e aynı offset yaması uygulanmaz.
