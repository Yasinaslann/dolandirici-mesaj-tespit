"""
Ekran goruntusunden metin cikarma (OCR) modulu.
EasyOCR kullanir - Turkce dil destegi var, sistem seviyesinde
ek kurulum gerektirmez (Streamlit Cloud'da calisir).
"""

import easyocr
import numpy as np
from PIL import Image

_reader_cache = None


def reader_getir():
    """EasyOCR okuyucusunu bir kez yukleyip onbellekte tutar
    (her cagrida yeniden yuklemek cok yavas olur)."""
    global _reader_cache
    if _reader_cache is None:
        _reader_cache = easyocr.Reader(["tr", "en"], gpu=False)
    return _reader_cache


def resimden_metin_cikar(resim: Image.Image) -> str:
    """
    Verilen bir PIL Image nesnesinden metni cikarir.
    WhatsApp/SMS ekran goruntusundeki mesaj balonlarini okur.
    """
    reader = reader_getir()
    resim_array = np.array(resim.convert("RGB"))
    sonuclar = reader.readtext(resim_array, detail=0, paragraph=True)
    metin = " ".join(sonuclar)
    return metin.strip()
