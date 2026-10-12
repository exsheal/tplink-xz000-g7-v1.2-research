# Varsayılan admin parolası ve hesapların ayrımı

## Formül

İncelenen TR v1.20 Build 250926 libcmm kodunda koşullu varsayılan admin üretimi:

```text
parola = "TsPeLbN" + LAN_MAC_son_4_baytının_büyük_harfli_HEX_gösterimi
```

Yapay örnek:

```text
MAC:    02:00:00:12:34:56
Son 4:  00:12:34:56
HEX:    00123456
Parola: TsPeLbN00123456
```

```sh
python3 tools/default_admin_password.py 02:00:00:12:34:56
```

Bu depo formülü ve [hesaplama aracını](../tools/default_admin_password.py) yayımlar; gerçek bir cihaza ait hesaplanan parolayı veya MAC’i içermez. [Parola üretim kod izi](../evidence/password-identity.txt).

## Koşullar ve sınırlamalar

Kod yolu AdminPwd başlangıç değerinin xz000 olması ve DevInfo bloğunda 0x4d0 offset’teki 32 bit alanın sıfır olması koşuluyla çalışır. Alanın kaynak seviyesindeki kesin adı çözülemedi; üretim/mode bağlamı tahmindir. Girdi gerçek LAN MAC’tir; GPON SN veya U-Boot’un örnek ethaddr değeri değildir.

Bu, sonradan değiştirilen parolayı geri getirme formülü değildir. ISP provisioning, farklı ülke/build, başka varsayılan veya değişmiş bayrak bu yolu geçersiz kılabilir. Aynı modelde farklı LAN MAC’ler farklı varsayılanlar üretir. Bir ünitenin parolasını diğer cihazlarda denemek genel parola testi değildir.

## Birbirinden ayrı üç yetki sistemi

| Ortam | Hesap/rol | Ne sağlar? |
|---|---|---|
| UART Linux | admin adı, UID/GID 0 | İşletim sistemi root yetkisi |
| Telnet TP-Link CLI | Admin rolü 2 | Üretici komutları, doğrudan shell değil |
| HTTP | Ayrı root/admin/user slotları | Web oturum/CGI yetkisi |

/etc/passwd satırındaki root açıklama alanı kullanıcı adının root olduğunu göstermez. UID 0 yetkidir; root adlı ayrı hesap kaydı olmadan bu adla login kabul edilmesi beklenmez. DEScrypt hash’inden Linux parolası ve XML’deki AdminPwd birbirinden bağımsız değerlendirilmelidir. Gerçek hash/parola bu depoda bulunmaz.

Orijinal web account sorgusunda rootName/rootPwd boş ve rootEnable=0 görülmüştür. passwd değişikliği otomatik web root hesabı oluşturmaz; web hesabı COS/CMM tarafında yönetilir. PwdSign gibi XML bayrakları açık metin parola üretim formülünün yerine geçen evrensel bir şifre çözüm anahtarı değildir.

## Root web denemesinin sonucu

RAM’de httpd hesabının role 0 slotunu kullanan deneysel yama ile giriş mümkün olmuş; ek menüler ortaya çıkmamış ve yönetim sayfasında hata 71231 görülmüştür. /cgi/auth ilgili yolu rol 1/2 için kabul eder; role 0 eklenmesi tüm sayfaların yetki kontrolünü çözmez. **Kalıcı root veya tam yönetim menüsü açıldı sonucu yoktur.** [Deneysel kaynaklar ve sınırları](../tools/experimental/README.md).
