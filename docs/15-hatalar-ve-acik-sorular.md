# Açılış hatalarının yorumu ve açık sorular

| Mesaj / gözlem | Doğru yorum |
|---|---|
| init’te eth0/pon bulunamıyor | SDK ağ modülleri sonra yükleniyor; sonraki ifconfig/süreçlerle birlikte okunmalı |
| br0 zaten var / interface bridge üyesi | Init katmanlarının tekrar işlemleri; bridge’in hiçbir zaman çalışmadığı sonucu çıkmaz |
| mini_httpd/ntpc/dnsmasq/radvd/ethphxcmd yok | Şablon init başka ürünlerin servislerini çağırıyor; doğru httpd daha sonra başlayabiliyor |
| gcponmap File exists | Modül daha önce yüklenmiş; eksik modül anlamına gelmiyor |
| config signature 0xffffffff / aşırı uzunluk | Silinmiş/geçersiz kayıttan fallback yoluna gidiyor; özgün değerler bu yayında yok |
| unrecognized object/parameter | Varsayılan XML ile azaltılmış veri modeli arasındaki uyumsuzluk |
| /proc/gpon/debug veya vendor proc yok | Bu sürücü/build altında farklı ya da eksik proc yolu |
| iptables Bad rule | Olmayan kuralı silme/yeniden düzenleme gibi init işlemleri; trafiğin bütünü başarısız demek değil |
| df root %100 | Salt okunur SquashFS’in normal görünümü |
| HTTP process var, 80 yok | COS init mesajları eksik olabilir; dinleme ayrıca kontrol edilir |
| ERR_ADDRESS_UNREACHABLE / No route to host | Önce ağ/PC rotası kontrol edilir; parola doğrulamasına henüz ulaşılmamış olabilir |
| Web pwd not correct | HTTP doğrulaması başarısız; Linux passwd veya GPON password doğrudan yerine geçmez |
| Web 71231 role 0 deneyi | İlgili CGI’nin rol kontrolü deneysel root slotuyla uyuşmadı; yeni yönetim yetkisi kanıtı yok |
| ttyS0 input overrun | Hızlı gönderim/yoğun çıktı sırasında veri kaybı olabilir; komutlar sakin konsolda tek tek gönderilir |

## Kesinleşmeyen konular

- Bağlı OLT’nin üretici/modeli ve OLT-G nesnesinin canlı içeriği.
- Yetki/üretim bayraklarının tam kaynak isimleri ve ağdan Linux shell yolu.
- Kalıcı web root ve bütün sayfaları kapsayan rol desteği.
- Harici EEPROM/OTP/security sektörlerinin tam yedeği ve semantiği.
- RSA/secure boot zincirinin bütün doğrulama yolları.
- EPON aktivasyonu, ileri VLAN/OMCI profilleri, jumbo ve gerçek performans.
- GPL’de eksik özel kaynakların tam build etkisi ve çalışır TR firmware üretimi.
- V1 2023 paketinin fiilî update sonucu; statik kontroller uyumsuzluk gösterir, flash deneyi yoktur.

## Yeni katkı için yararlı bilgiler

Donanım revizyonu, firmware build’i, komutun hangi ortamda çalıştığı ve beklenen/gözlenen davranış birlikte belirtilmelidir. MAC/SN/LOID/parola/abonelik/adres/screenshot kişisel alanları ayıklanır. Kısa ortak codepath veya yeniden üretilebilir örnek, bütün özel dump yüklemekten daha değerlidir. [Katkı rehberi](../CONTRIBUTING.md).
