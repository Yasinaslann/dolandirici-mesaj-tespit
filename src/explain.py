
"""
SHAP tabanli kelime seviyesinde aciklanabilirlik modulu.
Modelin ic yapisindan (TF-IDF/char n-gram) bagimsiz calisir;
"bu kelimeyi metinden cikarirsam tahmin nasil degisir" mantigiyla
hangi kelimelerin riski arttirip azalttigini bulur.
"""

import numpy as np
import shap

from src.predict import model_getir


def shap_aciklama_uret(metin, hedef_sinif=None, max_evals=200):
    """
    Verilen metin icin kelime bazli SHAP degerlerini dondurur.
    hedef_sinif belirtilmezse modelin tahmin ettigi sinif kullanilir.
    Donus: [(kelime, shap_degeri), ...] - pozitif deger riski artirir, negatif azaltir
    """
    pipeline = model_getir()
    siniflar = list(pipeline.classes_)

    if hedef_sinif is None:
        hedef_sinif = pipeline.predict([metin])[0]
    hedef_index = siniflar.index(hedef_sinif)

    masker = shap.maskers.Text(tokenizer=r"\W+")
    explainer = shap.Explainer(pipeline.predict_proba, masker, output_names=siniflar)

    shap_degerleri = explainer([metin], max_evals=max_evals, silent=True)

    kelimeler = shap_degerleri.data[0]
    degerler = shap_degerleri.values[0][:, hedef_index]

    sonuc = [
        (str(k).strip(), float(v))
        for k, v in zip(kelimeler, degerler)
        if str(k).strip()
    ]
    sonuc.sort(key=lambda x: abs(x[1]), reverse=True)
    return sonuc, hedef_sinif
