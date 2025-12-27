# Muhasebe (Basit CLI)

Bu proje, dosya tabanlı küçük bir muhasebe aracı sağlar. Gelir ve gider
kayıtları ekleyebilir, listeleyebilir, bakiye ve kategori özetlerini
komut satırından görebilirsiniz.

## Kurulum

Sisteminizde Python 3.10+ bulunduğundan emin olun. Ek bağımlılık yoktur.

## Kullanım

```
python muhasebe.py <komut> [seçenekler]
```

Varsayılan olarak veriler `ledger.json` dosyasına yazılır. Başka bir dosya
kullanmak için `--dosya` parametresini ekleyin.

### Kayıt ekleme

```
python muhasebe.py ekle gelir 1500 maas "Mart maaşı"
python muhasebe.py ekle gider 250 fatura "Elektrik"
python muhasebe.py ekle gelir 200 satis "Ürün" --tarih 2024-04-10
```

### Listeleme

```
python muhasebe.py liste
python muhasebe.py liste --baslangic 2024-04-01 --bitis 2024-04-30
python muhasebe.py liste --kategori fatura
```

### Bakiye

```
python muhasebe.py bakiye
```

### Kategori özeti

```
python muhasebe.py ozet
python muhasebe.py ozet --baslangic 2024-01-01 --bitis 2024-03-31
```

## Testler

```
python -m unittest
```
