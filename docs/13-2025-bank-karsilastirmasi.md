# 2025 Haziran ve Eylül firmware bankları

İki 2025 bankı aynı v1.20 flash düzenine sahiptir. Rootfs normal dosyaları arasında **beş dosya** farklı bulunmuştur; geri kalanı aynı içeriktir. [Dosya fark listesi](../data/bank-differences.json).

| Dosya | Özet |
|---|---|
| BusyBox | Derleme tarih/bilgi farkları |
| reduced_data_model.xml | Derleme/revizyon/tarih alanları |
| libcmm.so | İki hedefli native işlev farkı |
| xpon_sdk.ko | 665.908 → 687.700 bayt; 19 yeni adlandırılmış işlev |
| gc_omcid | Text/data farkları |

Eylül initDev2GponAuth yolu, Haziran’daki otomatik GPON SN fallback yazma davranışını kaldırmıştır; açık SN setter’ı hâlâ vardır. Bu, bütün SN değiştirme yeteneğinin kaldırıldığı anlamına gelmez. CTC farklarının bütün davranış etkileri kesinleşmedi.

Kernel .text karşılaştırmasında 127 adet 32 bit word farkı bulundu; bu incelenen bölgede pointer +4 kaymalarını işaret eder ve farklı instruction opcode’u saptanmadı. Bu sonuç bütün kernel binary’sinin aynı olduğu iddiasına genişletilmez. Config ve DTB karşılaştırmasında aynı içerik görülmüştür. [Kernel word farkları](../data/kernel-code-word-differences.json).

Her bir bank için bütün işlevlerin canlı davranışı ayrı ayrı denenmedi. Tarih bilgisi firmware build tarihidir; kartın üretim veya satış tarihi değildir.
