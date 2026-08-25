"""
Iki katmanli tahmin mimarisi:

KATMAN 1 - Tehdit/Siddet/Zorlama Filtresi (kural tabanli, BERT'ten bagimsiz)
    Fiziksel siddet, olum tehdidi, santaj veya zorlama icerigi tespit
    edilirse, BERT'e hic sormadan/onune gecerek sonucu KOSULSUZ olarak
    yuksek_riskli yapar. Insan guvenligi soz konusu oldugunda baglam
    aramayiz - bu katman her zaman diger katmanlardan ONCELIKLIDIR.

KATMAN 2 - BERT Dolandiricilik/Oltalama Analizi
    Katman 1 tetiklenmediyse, BERT modeli metni analiz eder (kargo,
    banka, torun tuzagi, sahte odul vb. dolandiricilik kaliplari icin).
    Bu katman ayrica kimlik bilgisi/kripto varlik/supheli link gibi
    destekleyici kural tabanli sinyallerle guclendirilir.
"""

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


# ---------------------------------------------------------------------------
# KATMAN 1: Tehdit / Siddet / Zorlama Filtresi
# ---------------------------------------------------------------------------

def katman1_tehdit_filtresi(kural_ozellikleri: dict) -> dict | None:
    """
    Fiziksel siddet/olum tehdidi ya da genel santaj/zorlama kalibi
    tespit edilirse KOSULSUZ olarak yuksek_riskli sonucu dondurur.
    Hicbir sey tetiklenmediyse None dondurur (Katman 2'ye gecilir).

    Bu katman BERT'in tahminini HIC dikkate almaz - cunku fiziksel
    tehdit durumunda "BERT ne dedi" onemsizdir, guvenlik onceliklidir.
    """
    if kural_ozellikleri["fiziksel_siddet_skoru"] > 0:
        return {
            "tahmin": "yuksek_riskli",
            "oncelikli_nedenler": _fiziksel_siddet_nedenleri(kural_ozellikleri),
        }

    if kural_ozellikleri["santaj_tehdit_skoru"] > 0:
        return {
            "tahmin": "yuksek_riskli",
            "oncelikli_nedenler": _santaj_nedenleri(kural_ozellikleri),
        }

    return None


def _fiziksel_siddet_nedenleri(kural_ozellikleri: dict) -> list[str]:
    nedenler = ["Bu mesaj doğrudan fiziksel tehdit içermektedir, derhal polise bildirin."]
    if kural_ozellikleri["para_talebi_skoru"] > 0 or kural_ozellikleri["genel_para_talebi"]:
        nedenler.append("Ayrıca mesaj para/havale talebiyle birlikte geliyor - bu bir şantaj/tehdit girişimi olabilir. Hemen 155 Polis İmdat'ı arayın.")
    return nedenler


def _santaj_nedenleri(kural_ozellikleri: dict) -> list[str]:
    if kural_ozellikleri["para_talebi_skoru"] > 0:
        return ["Doğrudan tehdit içerip karşılığında para talep ediyor - bu bir şantaj/tehdit girişimi olabilir. Hemen 155 Polis İmdat'ı arayın."]
    return ["Mesajda korkutucu, zorlayıcı veya doğrudan tehdit edici bir dil kullanılıyor. Güvende değilseniz hemen 155 Polis İmdat'ı arayın."]


# ---------------------------------------------------------------------------
# KATMAN 2: BERT Dolandiricilik/Oltalama Analizi
# ---------------------------------------------------------------------------

def katman2_bert_analizi(metin: str, kural_ozellikleri: dict, tokenizer, model) -> dict:
    """
    BERT modeliyle dolandiricilik/oltalama tahmini yapar, sonucu
    destekleyici kural tabanli sinyallerle (kimlik bilgisi, kripto
    varlik, supheli link, genel para talebi) guclendirir/yukseltir.
    """
    inputs = tokenizer(metin, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    olasilik_tensor = torch.softmax(outputs.logits, dim=1)[0]
    olasiliklar = {ID_TO_ETIKET[i]: float(olasilik_tensor[i]) for i in range(3)}
    tahmin = ID_TO_ETIKET[int(olasilik_tensor.argmax())]

    nedenler = acikla(metin)

    if kural_ozellikleri["kimlik_bilgisi_skoru"] > 0 and (
        kural_ozellikleri["kripto_varlik_skoru"] > 0 or kural_ozellikleri["link_var"]
    ):
        tahmin = "yuksek_riskli"
    elif kural_ozellikleri["kripto_varlik_skoru"] > 0 and kural_ozellikleri["link_var"]:
        tahmin = "yuksek_riskli"
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

    return {"tahmin": tahmin, "nedenler": nedenler, "olasiliklar": olasiliklar}


# ---------------------------------------------------------------------------
# ANA GIRIS NOKTASI
# ---------------------------------------------------------------------------

def tahmin_et(metin: str, tokenizer=None, model=None) -> dict:
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

    kural_ozellikleri = ozellik_cikar(metin)

    # --- KATMAN 1: Tehdit/Siddet/Zorlama filtresi (BERT'ten once, kosulsuz) ---
    katman1_sonuc = katman1_tehdit_filtresi(kural_ozellikleri)

    if katman1_sonuc is not None:
        tahmin = katman1_sonuc["tahmin"]
        nedenler = katman1_sonuc["oncelikli_nedenler"]
        # Katman 1 tetiklendiginde BERT'i yine de bilgi amacli calistirip
        # olasilik dagilimini gosterelim (kullaniciya seffaflik icin)
        inputs = tokenizer(metin, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
        olasilik_tensor = torch.softmax(outputs.logits, dim=1)[0]
        olasiliklar = {ID_TO_ETIKET[i]: float(olasilik_tensor[i]) for i in range(3)}
    else:
        # --- KATMAN 2: BERT dolandiricilik/oltalama analizi ---
        katman2_sonuc = katman2_bert_analizi(metin, kural_ozellikleri, tokenizer, model)
        tahmin = katman2_sonuc["tahmin"]
        nedenler = katman2_sonuc["nedenler"]
        olasiliklar = katman2_sonuc["olasiliklar"]

    etiket = RISK_ETIKETLERI.get(tahmin, RISK_ETIKETLERI["supheli"])

    return {
        "risk_seviyesi": tahmin,
        "emoji": etiket["emoji"],
        "baslik": etiket["baslik"],
        "olasiliklar": olasiliklar,
        "nedenler": nedenler,
        "kural_skorlari": kural_ozellikleri,
    }
