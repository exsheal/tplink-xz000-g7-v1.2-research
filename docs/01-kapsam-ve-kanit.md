# Araştırmanın kapsamı ve kanıt düzeyleri

Hedef **XZ000-G7 v1.2 / TR**, yazılımın bildirdiği sürüm **v1.20**. İnceleme, önceki canlı konsol/web kayıtları, iki bağımsız 8 MiB SPI-NOR okuması, çalışan sistem dosyaları, açılmış iki firmware bankı ve sonradan indirilen genel V1 firmware/GPL paketine dayanır. Bu yayın hazırlanırken ONT’ye komut gönderilmemiştir.

## Sayısal kapsam

| İncelenen küme | Sayı | Anlamı |
|---|---:|---|
| Girdi/çıkarılmış kayıt | 857 | Normal dosyalar ve bağlantılar, tekrarlı banklar dahil |
| Farklı normal dosya içeriği | 333 | Birebir aynı dosyalar tek içerik sayılır |
| Numaralandırılan metin satırı | 70.249 | Tekrarlı ve çözülmüş metinler dahil; farklı kaynak satırı sayısı değildir |
| Aktif rootfs normal dosyası | 255 | Dosya rolleri [katalogda](../data/firmware-files.json) |
| Aktif ELF | 49 | 27 program, 15 kütüphane, 7 çekirdek modülü |
| İki bank ELF toplamı | 98 | Bütün dosyaların sembol/bölüm/bağımlılık envanteri |
| CLI | 42 tablo, 130 girdi | Help’te görünmeyen satırlar dahil |
| Web | 22 HTML sayfası, 383 özellik adı | 92 ad için etkin atama; bağlam kontrolü yine gerekir |
| GPL arşivi | 159.240 normal dosya | Arşiv envanteri; bütün dosyaların semantiği tek tek çözülmedi |

Metinler indekslendi; kernel/config/DTB, şifreli XML ve GCS/iQoS içerikleri çözüldü. Aktif ELF’lerin ARM disassembly’si üretildi; parola üretimi, hesap/CLI yetkisi, flash okuyucuları, GPON getter/setter’ları, VLAN ve güncelleme yolları ayrıca izlendi. GPL incelemesi seçilmiş platform/build dosyalarıyla sınırlıdır; 72 odak dosyanın arşiv karşılıkları da kontrol edilmiştir.

## Bulgular nasıl okunmalı?

| Etiket | Ne gösterir? |
|---|---|
| Canlı doğrulandı | Önceki kullanıcı çıktısı veya ekranında gerçekten çalıştı |
| Kod yolu doğrulandı | Veri ve çağrılar statik olarak izlendi; canlı donanım etkisi denenmedi |
| Kod/şema mevcut | Bir tanım, program veya API var; erişilebilirliği/donanım desteği kanıtlı değil |
| Kapalı/eksik | Derleme bayrağı kapalı, gerekli program yok veya ilgili işlev boş |
| Belirsiz | Mevcut veriler sonuç çıkarmaya yetmiyor |

Her dosyanın hash’inin alınması bütün native işlevlerin bütün hata yollarının çözülmesi değildir. Sürücü register etkileri, ileri OMCI profilleri, kalıcı root ve performans için ek deney gerekir. [Makine okunur kapsam](../data/research-scope.json).

## Açık ve özel kanıt

Açık kataloglar ortak firmware yapısını ve seçilmiş statik kod yollarını taşır. Cihaz kimliği, mevcut kullanıcı yapılandırması, hesap hash’leri ve kalibrasyon verileri dışarıda tutulur. Tam yedek hash’i de cihaza özel bir parmak izi olduğu için yayımlanmaz. Özel yedek olmadan her byte karşılaştırmasını tekrar üretme iddiası yoktur.

Orijinal girdiler değiştirilmemiştir. SquashFS uyumluluk düzeltmesi yalnız analiz kopyasına uygulandı. İşlev isimleri, derleme bayrakları ve şema nesneleri tek başına özellik kanıtı olarak değerlendirilmedi.
