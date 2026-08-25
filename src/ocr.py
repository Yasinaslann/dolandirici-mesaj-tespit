"""
Ekran goruntusunden metin cikarma (OCR) modulu.
EasyOCR kullanir, WhatsApp/SMS arayuz gurultusunu temizler.
"""

import re
import easyocr
import numpy as np
from PIL import Image

_reader_cache = None

# WhatsApp/SMS arayuzunde sabit gecen, mesaj olmayan ifadeler.
# Bunlari OCR ciktisindan temizleyerek asil mesaja odaklaniyoruz.
ARAYUZ_GURULTUSU = [
    r"mesajlar ve aramalar uçtan uca şifrelidir.*?dokunun\.?",
    r"whatsapp da dahil olmak üzere.*?dinleyemez\.?",
    r"telefon numarasının ait olduğu ülke:?\s*\w*",
    r"kişilerde kayıtlı değil",
    r"ortak grup yok",
    r"güvenlik araçları",
    r"\bengelle\b",
    r"\bkişiyi ekle\b",
    r"\bbugün\b",
    r"\bmesaj\b$",
    r"^\d{1,2}[:.]\d{2}$",
]


def reader_getir():
    global _reader_cache
    if _reader_cache is None:
        _reader_cache = easyocr.Reader(["tr", "en"], gpu=False)
    return _reader_cache


def _gurultuyu_temizle(metin: str) -> str:
    temiz = metin
    for kalip in ARAYUZ_GURULTUSU:
        temiz = re.sub(kalip, "", temiz, flags=re.IGNORECASE)
    # telefon numarasi kaliplarini da temizle (+91 6371 710 785 gibi)
    temiz = re.sub(r"\+?\d[\d\s]{8,}\d", "", temiz)
    # fazla bosluklari sadelestir
    temiz = re.sub(r"\s+", " ", temiz).strip()
    return temiz


def resimden_metin_cikar(resim: Image.Image) -> str:
    reader = reader_getir()
    resim_array = np.array(resim.convert("RGB"))
    sonuclar = reader.readtext(resim_array, detail=0, paragraph=True)
    ham_metin = " ".join(sonuclar)
    return _gurultuyu_temizle(ham_metin)
