"""Basit bir muhasebe CLI aracı.

Gelir ve gider kayıtları eklemek, listelemek ve toplam bakiyeyi görmek için
kullanılabilir. Veriler JSON dosyasında saklanır.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_LEDGER_PATH = Path(__file__).with_name("ledger.json")
VALID_TYPES = {"gelir", "gider"}


@dataclass
class Transaction:
    """Tek bir gelir/gider hareketini temsil eder."""

    id: int
    tarih: str  # ISO format YYYY-MM-DD
    tur: str  # "gelir" veya "gider"
    kategori: str
    aciklama: str
    tutar: float

    def signalled_amount(self) -> float:
        """Gelirler pozitif, giderler negatif olarak dönsün."""

        return self.tutar if self.tur == "gelir" else -self.tutar


class Ledger:
    """JSON destekli basit defter."""

    def __init__(self, dosya: Path = DEFAULT_LEDGER_PATH):
        self.dosya = dosya
        self.kayitlar: List[Transaction] = []
        self._yukle()

    def _yukle(self) -> None:
        if not self.dosya.exists():
            return

        with self.dosya.open("r", encoding="utf-8") as f:
            data = json.load(f)

        self.kayitlar = [Transaction(**item) for item in data]

    def _kaydet(self) -> None:
        self.dosya.parent.mkdir(parents=True, exist_ok=True)
        with self.dosya.open("w", encoding="utf-8") as f:
            json.dump([asdict(k) for k in self.kayitlar], f, ensure_ascii=False, indent=2)

    def _siradaki_id(self) -> int:
        if not self.kayitlar:
            return 1
        return max(k.id for k in self.kayitlar) + 1

    def is_valid_type(self, tur: str) -> bool:
        return tur in VALID_TYPES

    def tarih_parse(self, tarih_str: str) -> date:
        try:
            return datetime.strptime(tarih_str, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Tarih formatı YYYY-MM-DD olmalıdır.") from exc

    def ekle(
        self,
        tur: str,
        tutar: float,
        kategori: str,
        aciklama: str,
        tarih_str: Optional[str] = None,
    ) -> Transaction:
        if not self.is_valid_type(tur):
            raise ValueError("Tür gelir ya da gider olmalıdır.")
        if tutar <= 0:
            raise ValueError("Tutar pozitif olmalıdır.")

        tarih_obj = self.tarih_parse(tarih_str) if tarih_str else date.today()
        kayit = Transaction(
            id=self._siradaki_id(),
            tarih=tarih_obj.isoformat(),
            tur=tur,
            kategori=kategori,
            aciklama=aciklama,
            tutar=round(float(tutar), 2),
        )
        self.kayitlar.append(kayit)
        self._kaydet()
        return kayit

    def listele(
        self,
        baslangic: Optional[str] = None,
        bitis: Optional[str] = None,
        kategori: Optional[str] = None,
    ) -> List[Transaction]:
        baslangic_tarih = self.tarih_parse(baslangic) if baslangic else None
        bitis_tarih = self.tarih_parse(bitis) if bitis else None

        def uygun_mu(kayit: Transaction) -> bool:
            tarih_obj = date.fromisoformat(kayit.tarih)
            if baslangic_tarih and tarih_obj < baslangic_tarih:
                return False
            if bitis_tarih and tarih_obj > bitis_tarih:
                return False
            if kategori and kayit.kategori.lower() != kategori.lower():
                return False
            return True

        return [k for k in self.kayitlar if uygun_mu(k)]

    def bakiye(self) -> float:
        return round(sum(k.signalled_amount() for k in self.kayitlar), 2)

    def kategori_ozeti(self, transactions: Optional[Iterable[Transaction]] = None) -> dict[str, float]:
        hedef = transactions if transactions is not None else self.kayitlar
        ozet: dict[str, float] = {}
        for kayit in hedef:
            mevcut = ozet.get(kayit.kategori, 0.0)
            ozet[kayit.kategori] = round(mevcut + kayit.signalled_amount(), 2)
        return ozet


def _yazdir_kayitlar(kayitlar: Iterable[Transaction]) -> None:
    satirlar = [
        [
            kayit.id,
            kayit.tarih,
            kayit.tur,
            kayit.kategori,
            kayit.aciklama,
            f"{kayit.tutar:,.2f}",
        ]
        for kayit in kayitlar
    ]
    if not satirlar:
        print("Kayıt bulunamadı.")
        return

    basliklar = ["ID", "Tarih", "Tür", "Kategori", "Açıklama", "Tutar"]
    sutun_genislikleri = [max(len(str(x)) for x in col) for col in zip(basliklar, *satirlar)]

    def satir_yaz(values: list[str | int]) -> None:
        hucreler = [str(v).ljust(genislik) for v, genislik in zip(values, sutun_genislikleri)]
        print(" | ".join(hucreler))

    satir_yaz(basliklar)
    print("-+-".join("-" * g for g in sutun_genislikleri))
    for satir in satirlar:
        satir_yaz(satir)


def _arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Basit muhasebe defteri")
    parser.add_argument(
        "--dosya",
        default=str(DEFAULT_LEDGER_PATH),
        help="Veri dosyasının yolu (varsayılan: ledger.json)",
    )
    subparsers = parser.add_subparsers(dest="komut", required=True)

    ekle_parser = subparsers.add_parser("ekle", help="Gelir veya gider ekle")
    ekle_parser.add_argument("tur", choices=sorted(VALID_TYPES))
    ekle_parser.add_argument("tutar", type=float)
    ekle_parser.add_argument("kategori")
    ekle_parser.add_argument("aciklama")
    ekle_parser.add_argument(
        "--tarih",
        help="YYYY-MM-DD formatında tarih (varsayılan: bugün)",
    )

    liste_parser = subparsers.add_parser("liste", help="Kayıtları listele")
    liste_parser.add_argument("--baslangic", help="Başlangıç tarihi (YYYY-MM-DD)")
    liste_parser.add_argument("--bitis", help="Bitiş tarihi (YYYY-MM-DD)")
    liste_parser.add_argument("--kategori", help="Kategori filtresi")

    subparsers.add_parser("bakiye", help="Toplam bakiyeyi göster")

    ozet_parser = subparsers.add_parser("ozet", help="Kategori bazlı özet")
    ozet_parser.add_argument(
        "--baslangic", help="Başlangıç tarihi (YYYY-MM-DD)")
    ozet_parser.add_argument("--bitis", help="Bitiş tarihi (YYYY-MM-DD)")
    ozet_parser.add_argument("--kategori", help="Kategori filtresi")

    return parser


def calistir(args: Optional[list[str]] = None) -> None:
    parser = _arg_parser()
    parsed = parser.parse_args(args=args)
    ledger = Ledger(Path(parsed.dosya))

    if parsed.komut == "ekle":
        kayit = ledger.ekle(
            tur=parsed.tur,
            tutar=parsed.tutar,
            kategori=parsed.kategori,
            aciklama=parsed.aciklama,
            tarih_str=parsed.tarih,
        )
        print(f"Kaydedildi: {kayit.id} - {kayit.tarih} {kayit.kategori} {kayit.tutar:,.2f}")
    elif parsed.komut == "liste":
        kayitlar = ledger.listele(
            baslangic=parsed.baslangic,
            bitis=parsed.bitis,
            kategori=parsed.kategori,
        )
        _yazdir_kayitlar(kayitlar)
    elif parsed.komut == "bakiye":
        print(f"Güncel bakiye: {ledger.bakiye():,.2f} TL")
    elif parsed.komut == "ozet":
        kayitlar = ledger.listele(
            baslangic=parsed.baslangic,
            bitis=parsed.bitis,
            kategori=parsed.kategori,
        )
        ozet = ledger.kategori_ozeti(kayitlar)
        if not ozet:
            print("Özet bulunamadı.")
        else:
            for kategori, toplam in sorted(ozet.items()):
                print(f"{kategori}: {toplam:,.2f} TL")


if __name__ == "__main__":
    calistir()
