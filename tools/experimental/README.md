# Deneysel RAM yardımcılarının kaynakları

Bu klasör yalnız elle yazılmış builder kaynakları ve ortak replay assembly’si içerir. Proprietary cli/httpd, üretilmiş binary, account dump, geçerli parola veya credential JSON dahil değildir. Kaynaklar incelenen **Build 250926’nin birebir eşleşen ELF’leri** içindir; SHA/entry/segment/patch-region kontrolleri kullanır.

## İşlevler ve önceki deneme sonuçları

| Kaynak | Eklenen yol | Önceki canlı kayıt sonucu |
|---|---|---|
| [build_cfg_reader.py](build_cfg_reader.py) | dm_shmInit(0) → dm_dumpCfg() | Yapılandırma çıktısı üretilmiş; özel çıktı yayımlanmaz |
| [build_usercfg_reader.py](build_usercfg_reader.py) | Mevcut DEV2_USER_CFG nesnesini okuma | Root kapalı, admin etkin bilgisi okunmuş; parolalar yayımlanmaz |
| [build_web_replay.py](build_web_replay.py) | Mevcut HTTP/challenge/user mesajlarını yeniden gönderme | Yeniden başlayan httpd için TCP 80 tekrar dinlemiş |
| [build_webroot.py](build_webroot.py) | RAM httpd role 0 kaydı ve UI role eşlemesi | Giriş görülmüş; ek menü yok, yönetimde 71231; kalıcı root çözümü değil |

Manifestlerdeki live_execution_verified=False builder’ın kendi doğrulama kapsamını belirtir: PC’de binary üretmek canlı test yapmaz. Yukarıdaki geçmiş sonuçlar kullanıcı kayıtlarından ayrıdır; bu yayında yeni canlı test yapılmadı.

## Çevrimdışı üretim

Yerel çıkarılmış orijinal binary’yi local-private/input altında saklayın. Araçlar değiştirilmiş kopyayı local-private/helpers altında üretir; orijinal input aynı kalır. Python assert’lerini kapatan -O ile çalıştırmayın.

```sh
python3 tools/experimental/build_cfg_reader.py --source local-private/input/cli
python3 tools/experimental/build_usercfg_reader.py --source local-private/input/cli
# ARM hedefi destekleyen clang gerekir; ONT_CLANG ile seçilebilir.
ONT_CLANG=clang python3 tools/experimental/build_web_replay.py --source local-private/input/cli
python3 tools/experimental/build_webroot.py --source local-private/input/httpd
```

Webroot builder her özel çıktı dizini için rastgele yerel parola üretir; credential dosyası 0600 tutulur. Binary ve oluşturduğu assembly bu parolayı içerir; **bunları yayımlamayın**. Kullanıcının önceki denemesinde kullanılan parola kaynakta yoktur.

Builder’lar ONT’ye bağlanmaz, servis öldürmez, firmware/flash yazmaz veya otomatik deploy yapmaz. Çıktıları cihazda çalıştırmak başka bir adımdır; bu kaynak yayını bütün libcmm çağrılarının her koşulda yan etkisizliğinin matematiksel ispatı değildir. Web/account yetki katmanları ve servis init mesajları için [erişim belgesi](../../docs/09-erisim-ve-cli.md).
