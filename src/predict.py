
"""
Egitilmis modeli yukleyip tahmin yapan modul.
NLP model skoru + kural tabanli feature skorlarini birlestirerek
nihai risk seviyesini ve aciklamayi dondurur.
"""

import pickle
from pathlib import Path

from src.features import acikla, ozellik_cikar

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_YOLU = BASE_DIR / "models" / "risk_model.pkl"

_model_cache = None


def model_getir():
    global _model_cache
    if _model_cache is None:
        with open(MODEL_YOLU, "rb") as f:
            _model_cache = pickle.load(f)
    return _model_cache


RISK_ETIKETLERI = {
    "guvenli": {"emoji": "🟢", "baslik": "Güvenli görünüyor"},
    "supheli": {"emoji": "🟡", "baslik": "Şüpheli, dikkatli olun"},
    "yuksek_riskli": {"emoji": "🔴", "baslik": "Yüksek riskli - dolandırıcılık olabilir!"},
}


def tahmin_et(metin):
    """
    Bir mesaj metni alir, model tahmini + kural tabanli aciklama +
    olasilik skorlarini birlestirip sonuc sozlugu dondurur.
    """
    if not metin or not metin.strip():
        return {
            "risk_seviyesi": "belirsiz",
            "emoji": "⚪",
            "baslik": "Analiz edilecek metin bulunamadı",
            "olasiliklar": {},
            "nedenler": [],
            "kural_skorlari": {},
        }

    pipeline = model_getir()
    tahmin = pipeline.predict([metin])[0]
    olasiliklar = dict(zip(pipeline.classes_, pipeline.predict_proba([metin])[0]))

    kural_ozellikleri = ozellik_cikar(metin)
    nedenler = acikla(metin)

    if (
        tahmin == "guvenli"
        and (kural_ozellikleri["supheli_link"] or kural_ozellikleri["tehdit_skoru"] >= 2)
    ):
        tahmin = "supheli"
        nedenler.insert(0, "Model güvenli dese de bazı şüpheli kalıplar tespit edildiği için temkinli davranıyoruz.")

    etiket = RISK_ETIKETLERI.get(tahmin, RISK_ETIKETLERI["supheli"])

    return {
        "risk_seviyesi": tahmin,
        "emoji": etiket["emoji"],
        "baslik": etiket["baslik"],
        "olasiliklar": olasiliklar,
        "nedenler": nedenler,
        "kural_skorlari": kural_ozellikleri,
    }
