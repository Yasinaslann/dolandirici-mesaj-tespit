
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.predict import tahmin_et

st.set_page_config(
    page_title="Dolandırıcı Mesaj Tespit Asistanı",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ Dolandırıcı Mesaj Tespit Asistanı")
st.caption("Şüpheli bir SMS, WhatsApp ya da e-posta mesajı mı aldınız? Aşağıya yapıştırın, birlikte kontrol edelim.")

st.divider()

metin = st.text_area(
    "Mesajı buraya yapıştırın",
    height=150,
    placeholder="Örn: Kargonuz teslim edilemedi, adresinizi güncelleyin: ...",
)

kontrol_edildi = st.button("Mesajı Kontrol Et", type="primary", use_container_width=True)

if kontrol_edildi:
    if not metin.strip():
        st.warning("Lütfen kontrol etmek istediğiniz mesajı yapıştırın.")
    else:
        with st.spinner("Mesaj analiz ediliyor..."):
            sonuc = tahmin_et(metin)

        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        if risk == "yuksek_riskli":
            st.error(emoji + " **" + baslik + "**")
        elif risk == "supheli":
            st.warning(emoji + " **" + baslik + "**")
        else:
            st.success(emoji + " **" + baslik + "**")

        st.subheader("Neden bu sonucu aldık?")
        for neden in sonuc["nedenler"]:
            st.markdown("- " + neden)

        if risk in ("yuksek_riskli", "supheli"):
            st.info(
                "**Ne yapmalısınız?**\n\n"
                "- Mesajdaki linke **tıklamayın**\n"
                "- Kişisel bilgi ya da para göndermeyin\n"
                "- Şüpheliyseniz ilgili kurumu (banka, kargo şirketi vb.) "
                "**resmi telefon numarasından** arayıp doğrulayın\n"
                "- Yakınınızdan bir teknoloji konusunda daha bilgili birine danışın"
            )

        with st.expander("Teknik detaylar (opsiyonel)"):
            st.write("Model olasılık dağılımı:")
            st.json({k: round(float(v), 3) for k, v in sonuc["olasiliklar"].items()})
            st.write("Kural tabanlı sinyal skorları:")
            st.json(sonuc["kural_skorlari"])

st.divider()
st.caption(
    "⚠️ Bu araç bir yardımcı sistemdir, kesin doğruluk garanti etmez. "
    "Şüphe durumunda her zaman ilgili kurumu resmi kanallardan doğrulayın."
)
