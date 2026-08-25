import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from src.features import acikla, ozellik_cikar

MODEL_NAME = "YasinAsl0n/dolandirici-mesaj-tespit-bert"
ID_TO_ETIKET = {0: "guvenli", 1: "supheli", 2: "yuksek_riskli"}

RISK_ETIKETLERI = {
    "guvenli": {"emoji": "🟢", "baslik": "Güvenli görünüyor"},
    "supheli": {"emoji": "🟡", "baslik": "Şüpheli, dikkatli olun"},
    "yuksek_riskli": {"emoji": "🔴", "baslik": "Yüksek riskli - dolandırıcılık olabilir!"},
}

_tokenizer_cache = None
_model_cache = None


def load_model():
    global _tokenizer_cache, _model_cache
    if _tokenizer_cache is None:
        _tokenizer_cache = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model_cache = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return _tokenizer_cache, _model_cache


def tahmin_et(metin, tokenizer=None, model=None):
    if not metin or not metin.strip():
        return {
            "risk_seviyesi": "belirsiz",
            "emoji": "⚪",
            "baslik": "Analiz edilecek metin bulunamadı",
            "olasiliklar": {},
            "nedenler": [],
            "kural_skorlari": {},
        }

    if tokenizer is None or model is None:
        tokenizer, model = load_model()

    inputs = tokenizer(metin, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    olasilik_tensor = torch.softmax(outputs.logits, dim=1)[0]
    olasiliklar = {ID_TO_ETIKET[i]: float(olasilik_tensor[i]) for i in range(3)}
    tahmin = ID_TO_ETIKET[int(olasilik_tensor.argmax())]

    kural_ozellikleri = ozellik_cikar(metin)
    nedenler = acikla(metin)

    if kural_ozellikleri["fiziksel_siddet_skoru"] > 0:
        tahmin = "yuksek_riskli"
    elif kural_ozellikleri["santaj_tehdit_skoru"] > 0:
        tahmin = "yuksek_riskli"
    elif kural_ozellikleri["kimlik_bilgisi_skoru"] > 0 and (
        kural_ozellikleri["kripto_varlik_skoru"] > 0 or kural_ozellikleri["link_var"]
    ):
        tahmin = "yuksek_riskli"
    elif kural_ozellikleri["kripto_varlik_skoru"] > 0 and kural_ozellikleri["link_var"]:
        tahmin = "yuksek_riskli"
    elif kural_ozellikleri["tikla_odul"]:
        tahmin = "supheli"
    elif tahmin == "guvenli" and (kural_ozellikleri["supheli_link"] or kural_ozellikleri["tehdit_skoru"] >= 2):
        tahmin = "supheli"
    elif tahmin == "guvenli" and kural_ozellikleri["genel_para_talebi"]:
        tahmin = "supheli"
        nedenler = [
            "Bu mesaj tanıdığınız birinden gelse bile hesabı çalınmış olabilir. "
            "Para göndermeden önce mutlaka kişiyi sesli arayarak teyit edin."
        ]

    genel_fallback = "Belirgin bir kural tabanli kalip yakalanmadi"
    if tahmin == "guvenli":
        nedenler = ["Belirgin bir dolandırıcılık kalıbı tespit edilmedi, mesaj güvenli görünüyor. Yine de emin olmadığınız bir gönderense dikkatli olun."]
    elif len(nedenler) == 1 and genel_fallback in nedenler[0]:
        nedenler = ["Kelime bazlı kurallarımız net bir kalıp yakalamadı, ancak yapay zeka modelimiz (BERT) metnin genel yapısında risk işaretleri tespit etti. Emin değilseniz gönderen kişiyi başka bir kanaldan doğrulayın."]

    etiket = RISK_ETIKETLERI.get(tahmin, RISK_ETIKETLERI["supheli"])

    return {
        "risk_seviyesi": tahmin,
        "emoji": etiket["emoji"],
        "baslik": etiket["baslik"],
        "olasiliklar": olasiliklar,
        "nedenler": nedenler,
        "kural_skorlari": kural_ozellikleri,
    }
