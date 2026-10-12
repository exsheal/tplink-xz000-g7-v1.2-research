# GitHub deposunu oluşturma ve yükleme

Önerilen depo adı **tplink-xz000-g7-v1.2-research**. Başlık **TP-Link XZ000-G7 v1.2 — TR**, açıklama:

```text
Independent research on TP-Link XZ000-G7 v1.2 (v1.20 TR): hardware, flash layout, password derivation, firmware analysis and management access.
```

## Yeni depo

1. [GitHub yeni depo formunu](https://github.com/new?name=tplink-xz000-g7-v1.2-research&visibility=public) açın ve kendi hesabınızı seçin.
2. İsim/açıklamayı kullanın. Public seçimi dosyaları herkese açar.
3. Hazır yerel dosyaları aktaracağınız için ek README/.gitignore oluşturmayın. Yeni içerik lisansı seçilmediğinden lisans seçimi ayrıca yapılabilir.
4. Create repository ile oluşturun. Bu yerel paket kendi başına GitHub’da depo açmamıştır.

## Tarayıcıyla yükleme

ZIP’i açın. Paket klasörünün **içeriğini** yeni deponun Add file → Upload files ekranına sürükleyin; ZIP’i tek dosya olarak yüklemek belgeleri GitHub’da gezilebilir yapmaz. README.md en üst düzeyde olmalı. Gizli .gitignore/.github dosyalarının da geldiğini kontrol edin.

GitHub tarayıcı yüklemesinde dosya başına 25 MiB ve bir seferde 100 dosya sınırı vardır; bu paketin sayısını publication-checks.json gösterir. [Resmî upload rehberi](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

## Git ile yükleme

Yalnız bu temiz paket klasörünü repo yapın; özel yedeklerin bulunduğu üst çalışma klasörünü git add . ile eklemeyin. Gerçek ad/email’i commit metadata’sında istemiyorsanız aşağıdaki örnek yerel kimliği kullanabilirsiniz:

```sh
# Temiz paket klasöründeyken:
python3 tools/verify_public.py .
git init -b main
git config user.name 'XZ000-G7 Research'
git config user.email 'research@example.invalid'
git add .
git diff --cached --stat
git commit -m 'Document XZ000-G7 v1.2 TR hardware and firmware research'
git remote add origin https://github.com/YOUR_ACCOUNT/tplink-xz000-g7-v1.2-research.git
git push -u origin main
```

YOUR_ACCOUNT yerine hesabınızı yazın; bu URL örnektir. Kimlik doğrulamayı GitHub’ın desteklediği kendi yönteminizle yapın; token/parolayı dosyaya veya komut URL’sine eklemeyin. Remote yükleme için depo bağlantısı/hesap bilgisi bu paketten bağımsızdır.

Public kontrol raporu ve manifest paket içeriğini doğrular. Sonradan eklenen dosyalar ayrıca taranır. Orijinal yedekler, logs, analysis ve indirilen firmware/GPL arşivleri bu paketin dışında kalır.
