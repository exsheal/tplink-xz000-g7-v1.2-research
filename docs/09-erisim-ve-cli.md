# UART, Telnet, SSH ve web erişimi

## Normal giriş

Önceki durumda HTTP 80 ve Telnet 23 dinlemiştir. Admin web/Telnet girişi başarılıdır; parola üretiminin koşulları [ayrı belgede](08-parola-ve-hesaplar.md). Mevcut erişim/firmware durumuna göre servis yeniden kapatılmış olabilir; tek bir eski süreç listesi gelecekteki dinleme durumunu garanti etmez.

```sh
telnet 192.168.10.254 23
```

Telnet sonunda TP-Link(conf)# görünmesi Linux shell elde edildiğini göstermez. UART Linux prompt’u ve web hesap rolü de ayrı sistemlerdir. SSH daemon binary’si mevcut imajda yok; passwd’de dropbear adı bulunması SSH erişimi sağlamaz.

## CLI tablosu

130 girdi ve 42 tablo çözüldü. Admin rolü 2; sh ve enable rol 3 ister. Help tüm girdileri göstermeyebilir. Gizli olmak, normal admin tarafından çalıştırılabilir olmak anlamına gelmez.

Yazma/reset içermeyen, tablodan doğrulanmış sorgular:

```text
help
dev version
dev show prodName
dev show prodVer
dev show prodSoftVer
dev show prodHardVer
gponctrl show status
gponctrl show optical
```

gponctrl show sn de tablodadır, fakat özel GPON seri numarası döndürür; çıktısı katkıya eklenmez. Yukarıdaki her sorgu yeni canlı oturumda tekrar denenmemiştir. [Tam CLI katalogu](../data/cli-commands.json) keşif verisidir; yazma/reset/kalibrasyon girdileri çalıştırma listesi değildir.

## Gizli sys ve factory yolları

MAC/SN/ürün bilgisi, register/I²C, dumpDm/dumpCfg, UART ve optik kalibrasyon işlevleri bulunur. sys yolu rol/argüman kontrolüne ek olarak DevInfo’dan alınan özel bayrak veya uptime ≤600 s şartını kullanır. Bayrağın kesin kaynak adı belirlenmedi. factory içindeki WLAN/WPS adları fiziksel Wi-Fi kanıtı değildir.

sys üst argümanı Base64 + DES çözümü kullanır. Taban baytlar 47 8d e3 f9 0b a5 d2 cf; normal yolda ProductID sorgusundan sonra tamponun ilk sekiz baytıyla XOR yapılır. Bu taban değer sabit çalışma anahtarı diye kullanılamaz. Tüm özel durum/çağırıcı koşulları kesinleştirilmedi.

Bazı register handler’ları argümanı shell metnine birleştirir. Bu statik olasılık, erişilebilir parser/handler/rol koşulları ve canlı test olmadan başarıyla çalışan komut enjeksiyonu veya ağdan root erişimi diye sunulmaz.

## Web servisini yeniden başlatma neden sorun çıkardı?

httpd sürecinin varlığı TCP 80’in dinlediğini göstermez. COS mesajları 2030 HTTP yapılandırması, 2033 challenge, 2031 kullanıcı bilgisi için init/replay sağlar. Önceki replay deneyi sonrası TCP 80 tekrar dinlemiştir. Sadece /bin/httpd çalıştırmak bu mesajlar alınmadan yeterli olmayabilir. Yeniden başlatılan daemon ve RAM yama deneyi geçici işlemlerdir; kalıcı firmware değişikliği değildir.

Yayınlanan yardımcı build kaynakları ONT’ye bağlanmaz veya otomatik servis öldürmez; eşleşen yerel binary kopyaları üzerinde çalışır. [Araç kapsamı](../tools/experimental/README.md).
