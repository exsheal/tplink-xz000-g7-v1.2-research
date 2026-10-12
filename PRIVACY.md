# Yayın kapsamı ve gizlilik

Yayınlananlar: ortak donanım/firmware açıklamaları, bölüm ve kayıt **adresleri**, parola **üretim algoritması**, yapay örnekler, kaynak araçlar ve yapısal kataloglar.

Yayınlanmayanlar: gerçek MAC, GPON SN, LOID/PON password, web/Linux/router parolası, hesap hash’i, cihaz serial/Device ID, tam flash fingerprint’i, PPPoE/abonelik bilgisi, gerçek WAN/PC adresi, kullanıcı/hostname/yerel yol, calibration içeriği, ham UART/runtime/screenshot ve yedekler.

Ortak ProductID/HWID ve firmware dosya hash’i tek cihaz serial’i değildir. Açık belgelerdeki 192.168.10.254 varsayılan yönetim IP’sidir; 192.168.10.2 ve 02:00:00:12:34:56 örnek değerlerdir. Koşullu parola formülü bu yapay MAC ile gösterilir.

## Yerel çıktıların yeri

Araç çıktıları local-private altında tutulur ve .gitignore ile dışarıda kalır. Kopyaları, terminal görüntüleri ve başka ad verilmiş dosyalar için .gitignore tek başına koruma değildir. Ham binary/backup dosyaları public paket kontrolü tarafından da reddedilir.

```sh
python3 tools/verify_public.py .
# Özel parmak izleri listesi de kontrol edilebilir; JSON dosyası deponun dışında olmalı.
python3 tools/verify_public.py . --deny-file /PRIVATE/PATH/deny.json
```

Genel tarama dosya türü, MAC örnekleri, anahtar kalıpları ve yerel linkleri kontrol eder. Kesin cihaz parmak izi taraması yayın hazırlanırken özel liste ile ayrıca uygulanır; bu liste ve eşleşen değerler yayımlanmaz. Bilinmeyen veya yeni bir özel verinin her olası kodlamasını otomatik saptama garantisi yoktur; yeni dosyalar alan seçimi ve insan incelemesi gerektirir.

Git commit geçmişi de veridir. Bu paket önceki özel çalışma dizininin Git geçmişini taşımaz. Yanlışlıkla push edilen secret yalnız son dosyadan silmekle geçmişten kalkmaz. Katkıda önce [rehberi](CONTRIBUTING.md) izleyin.
