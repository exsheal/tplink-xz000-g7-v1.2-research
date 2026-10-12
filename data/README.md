# Yayımlanan veri katalogları

Bu dosyalar ortak firmware yapısını açıklayan, alanları seçilerek oluşturulmuş araştırma verileridir. Çalışan kullanıcı config’leri, değer blokları, account/system içerikleri ve özel capture hash’leri yoktur.

| Dosya | Kapsam |
|---|---|
| [research-scope.json](research-scope.json) | Sürüm, inceleme sayıları ve sınırlar |
| [firmware-files.json](firmware-files.json) / [TSV](firmware-files.tsv) | Aktif rootfs 255 normal dosya: tür, boyut, izin, rol, yöntem; hassas hesap/sistem hash’leri çıkarılmış |
| [native-catalog.json](native-catalog.json) | 49 ELF: işlev/import/dependency/modül etiketi; binary yok |
| [cli-commands.json](cli-commands.json) | 42 tablonun 130 girdisi: adres, mode, flag, handler, gizli/encoded durumu |
| [constant-return-functions.json](constant-return-functions.json) | İki instruction sabit dönüş bulunan 106 işlev; otomatik “sahte özellik” etiketi değildir |
| [web-page-catalog.json](web-page-catalog.json) | 22 sayfa; OID/CGI/flag kullanımı |
| [web-build-flags.json](web-build-flags.json) | 383 feature adı ve atama yerleri; üst feature bağlamı gerekir |
| [xml-schema.json](xml-schema.json) | Aktif default/reduced XML yapıları, değerler çıkarılmış |
| [gcs-schema.json](gcs-schema.json) | 119 GCS nesne / 685 parametre: ad/yol/type/flag, değer yok |
| [flash-layout.json](flash-layout.json) | MTD sınırları ve kimlik kayıt adres/boyutları; içerik yok |
| [symlink-catalog.json](symlink-catalog.json) | 85 ortak rootfs bağlantısı |
| [kernel-2025.config](kernel-2025.config) / [DT](gc1601-2025.dts) | Kernel build ayarları ve Device Tree |
| [bank-differences.json](bank-differences.json) | İki 2025 bankında farklı beş rootfs dosyası |
| [kernel-code-word-differences.json](kernel-code-word-differences.json) | İncelenen .text word farkları; tüm kernel davranışını ispatlamaz |
| [2023-rootfs-comparison.json](2023-rootfs-comparison.json) | Genel V1 eski/yeni dosya eşleşmeleri |
| [2023-native-comparison.json](2023-native-comparison.json) | Eski/yeni ELF farkları |
| [2023-web-flag-comparison.json](2023-web-flag-comparison.json) | Genel V1 / TR v1.20 feature farkları |
| [2023-kernel-config-comparison.json](2023-kernel-config-comparison.json) | Kernel config karşılaştırmaları |
| [2023-source-missing-paths.json](2023-source-missing-paths.json) | GPL build’de eksik özel yollar |
| [gpl-archive-summary.json](gpl-archive-summary.json) | GPL arşiv dosya sayıları/uzantı/grup bilgileri |
| [publication-checks.json](publication-checks.json) | Paket doğrulama sayıları; özel parmak izleri yok |
| [MANIFEST.sha256.txt](../MANIFEST.sha256.txt) | Yayımlanan dosyaların SHA-256 listesi; kendisini hariç tutar |

Adresler statik ELF/flash adresleridir. Dosya SHA-256’ları yalnız ortak firmware dosyalarına aittir; tüm cihaz dump SHA’sı yoktur. İçerik kategorileri tek başına çalışırlık kanıtı değildir. Katalogda bulunan yazma/kalibrasyon komutları kullanım talimatı olarak sunulmaz.
