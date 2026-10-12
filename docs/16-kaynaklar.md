# Kaynaklar ve kanıtların konumu

## Birincil teknik kaynaklar

| Kaynak | Kullanım / sınır |
|---|---|
| [TP-Link XZ000-G7 özellikleri](https://service-provider.tp-link.com/gpon/xz000-g7/) | Genel model teknik özellikleri; TR build’in bütün seçeneklerinin canlı garantisi değil |
| [TP-Link TR download](https://www.tp-link.com/tr/support/download/xz000-g7/) | Genel V1 firmware yayını |
| [TP-Link CA download](https://www.tp-link.com/ca/support/download/xz000-g7/) | GPL indirme girişi |
| [TP-Link EN download](https://www.tp-link.com/en/support/download/xz000-g7/) | Donanım revizyon seçimleri; her V1 paketi v1.20 uyumlu demek değil |
| [ITU-T G.988](https://www.itu.int/rec/T-REC-G.988/en) | OMCI standardı |
| [OLT-G §9.12.2 metni](https://www.ietf.org/lib/dt/documents/LIAISON/file1019.pdf) | Class 131 vendor/equipment/version alanları; bağlı OLT’yi göstermiş bir çıktı değil |
| [RFC 1350](https://www.rfc-editor.org/rfc/rfc1350.html) | TFTP octet, 512 bayt blok, ACK |
| [RFC 2347](https://www.rfc-editor.org/rfc/rfc2347.html) | TFTP option negotiation |
| [tio manpage kaynağı](https://github.com/tio/tio/blob/master/man/tio.1.in) | UART terminali ve hız/gecikme seçenekleri |
| [OpenWrt modem yönetim erişimi](https://openwrt.org/docs/guide-user/network/wan/access.modem.through.nat) | Konuya ilişkin resmî rehber; bu depodaki örnek önceki yerel erişim deneyine dayanır |
| [GitHub repository oluşturma](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository) | İsim/visibility ve yeni depo akışı |
| [GitHub dosya yükleme](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository) | Webden yükleme ve boyut sınırları |

## Yerel statik kanıt

[evidence](../evidence/README.md) klasörü seçilmiş ARM/callpath parçalarını taşır. [data](../data/README.md) ortak firmware kataloglarını taşır. Statik parçaların adresleri incelenen build içindir; canlı donanım testinin yerine geçmez. Özel yedekler, tam UART kayıtları ve çözülmüş kullanıcı değerleri yayımlanmaz.

Derleme tarihleri, modeller, feature isimleri veya ortak kütüphane hash’leri teknik veridir. Cihaza özel tüm flash hash’i, kullanıcı parolaları ve seri numaraları teknik kaynak diye yayımlanmamıştır.
