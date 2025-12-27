import tempfile
from pathlib import Path
import unittest

from muhasebe import Ledger


class LedgerTest(unittest.TestCase):
    def yeni_defter(self) -> Ledger:
        gecici = tempfile.NamedTemporaryFile(delete=False)
        Path(gecici.name).unlink()  # sıfırdan başlamak için
        return Ledger(Path(gecici.name))

    def test_ekle_ve_bakiye(self):
        ledger = self.yeni_defter()
        ledger.ekle("gelir", 100, "maas", "Nisan maaşı", tarih_str="2024-04-01")
        ledger.ekle("gider", 30, "market", "Haftalık alışveriş", tarih_str="2024-04-02")

        self.assertEqual(ledger.bakiye(), 70)

    def test_listeleme_filtreleri(self):
        ledger = self.yeni_defter()
        ledger.ekle("gelir", 50, "maas", "Ödeme", tarih_str="2024-03-10")
        ledger.ekle("gider", 10, "ulasim", "Otobüs", tarih_str="2024-03-11")
        ledger.ekle("gider", 5, "market", "Atıştırmalık", tarih_str="2024-04-01")

        tum = ledger.listele()
        sadece_mart = ledger.listele(baslangic="2024-03-01", bitis="2024-03-31")
        kategori_market = ledger.listele(kategori="market")

        self.assertEqual(len(tum), 3)
        self.assertEqual(len(sadece_mart), 2)
        self.assertEqual({k.kategori for k in kategori_market}, {"market"})

    def test_kategori_ozeti(self):
        ledger = self.yeni_defter()
        ledger.ekle("gelir", 200, "satis", "Ürün satışı", tarih_str="2024-01-05")
        ledger.ekle("gider", 50, "masraf", "Kargo", tarih_str="2024-01-06")
        ledger.ekle("gider", 20, "masraf", "Paketleme", tarih_str="2024-01-07")

        ozet = ledger.kategori_ozeti()
        self.assertEqual(ozet["satis"], 200)
        self.assertEqual(ozet["masraf"], -70)


if __name__ == "__main__":
    unittest.main()
