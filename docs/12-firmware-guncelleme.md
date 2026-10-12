# Firmware paketleri ve güncelleme doğrulaması

## IMAGE_TAG ve doğrulama

Vendor IMAGE_TAG 512 bayttır. Tek web upload paketi, kernel partition başlığı ve bütün flash aynı formatta dosya değildir; flash-a.bin doğrudan web update paketi olarak kabul edilmez.

İzlenen doğrulama yolu dosyada saklanan token’ı kaydeder, ilgili token alanını sabit salt/key ile değiştirir ve cen_md5VerifyDigest çağırır. Başarıdan sonra görülen SKIPMD5 log metni bütünlüğün hiç denetlenmediği anlamına gelmez. MD5 bütünlük kontrolü, tek başına üretici imzası doğrulaması veya secure boot değildir.

ProductID, product version/hardware version ve special version kontrolleri de vardır. INCLUDE_FWUPGRADE_CHECK_RSA ve RSA kütüphane işlevinin mevcut olması, bu upload yolunda doğrulanmış imza zinciri bulunduğunu tek başına kanıtlamaz. [Update kod yolu](../evidence/firmware-upgrade.txt), [crypto doğrulama](../evidence/crypto-verification.txt).

## Yazma hedefleri ve sınırlar

Kodda aktif olmayan bankı yazma ve isteğe bağlı bootloader update bulunur. Boot alanı 0x20000, kernel alanı 0x160000’dır. Bir rootfs sınır kontrolünde 0x630000 görülürken gerçek partition 0x260000’dır; diğer kontroller/bağlamla güvenli sınırın tamamı kesinleştirilmedi. Bu farklılık, büyük rootfs’nin güvenle yazılabileceği şeklinde yorumlanmaz.

Kernel partition başlığının rootfs/boot token’larının sıfır olması bir kernel-only başlık bağlamıdır; genel upload paketinin bütün kontrollerini atlama veya bypass sonucu çıkarılmaz.

## Revizyon kararı

2023 V1 paketinin ProductID ve version/special değerleri 2025 TR v1.20’den farklıdır. Normal kontrol yolunun reddetmesi beklenir; fiilî upload/flash deneyi yapılmadı. Boyutların alana sığması uyumluluğu kanıtlamaz. Zorla yazma, bootloader/MAC/kalibrasyon bloklarını etkileyebilir; bu araştırmada yapılmadı.

Bu depo firmware yazma aracı veya bir “unlock image” içermez. Kaynak build/helper çıktıları ana flash’ın yerine geçmez. [V1/GPL karşılaştırması](14-v1-2023-ve-gpl.md).
