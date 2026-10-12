# Yerel araştırma araçları

| Araç | İşlev | Ağ/cihaz etkisi |
|---|---|---|
| [default_admin_password.py](default_admin_password.py) | Build 250926 koşullu varsayılanını LAN MAC’ten hesaplar | Ağ yok; kendiliğinden login denemez |
| [backup_receiver.py](backup_receiver.py) + [backup.sh](backup.sh) | İki okumalı NOR/runtime yedeği, SHA ve bölümleme | PC’de alıcı; ONT betiği flash okur, RAM dosyası yazar |
| [inspect_image.py](inspect_image.py) | Yerel flash/update dosyası biçim ve bölüm kontrolü | Dosya okuma; kimlik içeriklerini göstermez |
| [verify_public.py](verify_public.py) | Yayın tür/kimlik kalıpları/özel deny list/link kontrolü | Yalnız yerel dosya |
| [experimental](experimental/README.md) | RAM config/account/replay/webroot helper kaynakları | Builder yalnız yerel binary kopyası üretir; cihazda çalıştırma ayrı ve deneysel |

Standart araçlar Python 3 standard library kullanır. Deneysel ELF builder’lar pyelftools; replay ayrıca ARM hedefi destekleyen clang ister. Kurulum ortamı tercihi kullanıcıya aittir; araçlar kendiliğinden paket kurmaz.

## Örnekler

```sh
python3 tools/default_admin_password.py 02:00:00:12:34:56
python3 tools/backup_receiver.py --help
python3 tools/inspect_image.py local-private/input/flash.bin --kind flash
python3 tools/verify_public.py .
python3 -m unittest discover -s tests -v
```

inspect_image’ın özel dosya hash’i/yerel path çıktısı özel çalışma verisidir; doğrudan issue’ya yapıştırmayın. Yeni araç çıktıları local-private altında tutulur. Backup alıcı TFTP’yi güvenilir yerel bağlantı için kullanır; protokol şifreleme sağlamaz.

Build hash’i ve ELF adresleri başka firmware’e taşınmaz. Helper kaynaklarını yayımlamak, tüm denemelerin başarılı veya kalıcı root sağladığı anlamına gelmez. [Hesap mekanizması](../docs/08-parola-ve-hesaplar.md).
