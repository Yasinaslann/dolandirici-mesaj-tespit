"""
Otomatik regresyon testleri.

Bu dosya, gelistirme surecinde elle tek tek test ettigimiz tum senaryolari
kalici hale getirir. Herhangi bir kod degisikliginden sonra:

    pytest tests/test_predict.py -v

komutuyla calistirilir. Eger bir test kirilirsa, o degisikligin daha once
dogru calisan bir seyi bozdugu anlamina gelir.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest
from src.predict import tahmin_et, load_model

# Model ve tokenizer'i tum testler icin BIR KEZ yukluyoruz (her testte
# yeniden yuklemek cok yavas olurdu)
@pytest.fixture(scope="module")
def model_ve_tokenizer():
    tokenizer, model = load_model()
    return tokenizer, model


# ---------------------------------------------------------------------------
# YUKSEK RISKLI OLMASI GEREKEN SENARYOLAR
# ---------------------------------------------------------------------------

YUKSEK_RISKLI_MESAJLAR = [
    "bana 500 tl ver yoksa öldürürüm seni",
    "yarın bana gelmen lazım yoksa öldün",
    "seni taciz ederim bana gelmezsen",
    "Kargonuz gümrükte bekliyor, vergi ödemesi için tıklayın: bit.ly/odeme-hizli",
    "Anne benim, telefonum düştü, yeni numaram bu, acil param lazım",
    "Deniz Hesap: Kce0150 Şifre: adam1986@ URL: bur7.com Varlıklar: 2150153.61 USDT",
]


@pytest.mark.parametrize("mesaj", YUKSEK_RISKLI_MESAJLAR)
def test_yuksek_riskli_mesajlar(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "yuksek_riskli", (
        f"Beklenen: yuksek_riskli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


# ---------------------------------------------------------------------------
# GUVENLI OLMASI GEREKEN SENARYOLAR (yanlis pozitif kontrolu)
# ---------------------------------------------------------------------------

GUVENLI_MESAJLAR = [
    "yarın saat 3'te buluşalım mı kahve içmeye",
    "yarın saat 3'te buluşalım mı kahve içmeye, yoksa başka gün mü uygun",
    "Kızım yarın doktora gideceğiz saat kaçta müsaitsin",
    "Faturanız hazır, bu ay 245 TL",
    "Bu bir dolandırıcı mesajıdır",
]


@pytest.mark.parametrize("mesaj", GUVENLI_MESAJLAR)
def test_guvenli_mesajlar(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "guvenli", (
        f"Beklenen: guvenli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


# ---------------------------------------------------------------------------
# SUPHELI OLMASI GEREKEN SENARYOLAR
# ---------------------------------------------------------------------------

SUPHELI_MESAJLAR = [
    "bir miktar para ateşleyin",
    "tıkla 100 tl kupon hesabında",
]


@pytest.mark.parametrize("mesaj", SUPHELI_MESAJLAR)
def test_supheli_mesajlar(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "supheli", (
        f"Beklenen: supheli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


# ---------------------------------------------------------------------------
# OZEL ACIKLAMA ICERIGI KONTROLLERI
# ---------------------------------------------------------------------------

def test_fiziksel_tehdit_polis_uyarisi_iceriyor(model_ve_tokenizer):
    """Fiziksel tehdit iceren mesajlarda polis cagrisi mutlaka olmali."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("bana 500 tl ver yoksa öldürürüm seni", tokenizer, model)
    tum_nedenler = " ".join(sonuc["nedenler"])
    assert "polis" in tum_nedenler.lower() or "155" in tum_nedenler


def test_bos_mesaj_belirsiz_doner(model_ve_tokenizer):
    """Bos metin gonderilirse sistem cokmemeli, 'belirsiz' donmeli."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("", tokenizer, model)
    assert sonuc["risk_seviyesi"] == "belirsiz"


def test_turkce_karakter_normalizasyonu_calisiyor(model_ve_tokenizer):
    """Turkce ozel karakterlerle yazilan tehdit de yakalanmali."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("seni öldürürüm çünkü söylemedin", tokenizer, model)
    assert sonuc["risk_seviyesi"] == "yuksek_riskli"
