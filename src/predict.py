
"""
Egitilmis modeli yukleyip tahmin yapan modul.
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

    genel_fallback = "Belirgin bir kural tabanli kalip yakalanmadi"
    if tahmin == "guvenli":
        nedenler = ["Belirgin bir dolandırıcılık kalıbı tespit edilmedi, mesaj güvenli görünüyor. Yine de emin olmadığınız bir gönderense dikkatli olun."]
    elif len(nedenler) == 1 and genel_fallback in nedenler[0]:
        nedenler = ["Kelime bazlı kurallarımız net bir kalıp yakalamadı, ancak yapay zeka modelimiz metnin genel yapısında risk işaretleri tespit etti. Emin değilseniz gönderen kişiyi başka bir kanaldan (telefonla arayarak) doğrulayın."]

    etiket = RISK_ETIKETLERI.get(tahmin, RISK_ETIKETLERI["supheli"])

    return {
        "risk_seviyesi": tahmin,
        "emoji": etiket["emoji"],
        "baslik": etiket["baslik"],
        "olasiliklar": olasiliklar,
        "nedenler": nedenler,
        "kural_skorlari": kural_ozellikleri,
    }
