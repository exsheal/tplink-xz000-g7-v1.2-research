# Katkı rehberi

İlgili donanım revizyonunu (ör. v1.20), ülkeyi, firmware build’ini ve bulgunun kanıt düzeyini belirtin. Aynı model adı her bölge/revizyonda aynı binary’yi ifade etmez.

Katkıda sorunu/özelliği, hangi ortamda çalıştırılan hangi komutla gözlendiğini ve beklenen/gerçek sonucu açıklayın. Kısa, ayıklanmış örnekler ve ortak codepath bilgisi kullanın. Firmware yükleme, reset, optik kalibrasyon veya kimlik değiştirme sonucunu yalnız gerçekten denenmişse canlı doğrulandı diye yazın.

Gerçek MAC/SN/LOID/password, hesap hash’i, abonelik/WAN, Device ID, ham dump, runtime config, terminal geçmişi veya kalibrasyon dosyası göndermeyin. Ekran görüntüsünün arka plan sekmeleri, adres/hesap alanları ve dosya metadata’sı da özel bilgi taşıyabilir. Örneklerde 02:00:00:12:34:56 gibi yapay değer kullanın.

Yeni dosya eklemeden python3 tools/verify_public.py . çalıştırın; yerel testleri tamamlayın. Private çalışma alanını ve generated binary’leri commit etmeyin. Bilinmeyen bulguyu kesinleştirilmiş gibi sunmayın; neden belirsiz kaldığını belirtin.

Üretici GPL kaynakları ve proprietary binary’leri bu depoya bütünüyle kopyalamak yerine resmî bağlantı, ortak hash, hedefli yapı/işlev açıklaması kullanılır. [Kaynak/lisans notu](NOTICE.md).
