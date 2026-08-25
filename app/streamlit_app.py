import streamlit as st
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.predict import load_model, tahmin_et

st.set_page_config(page_title="Dolandırıcı Mesaj Tespit", page_icon="🛡️")

st.title("🛡️ Dolandırıcı Mesaj Tespit Asistanı")
st.markdown("Şüphelendiğiniz mesajı aşağıya yapıştırın, **Yapay Zeka (BERT)** sizin için analiz etsin.")


@st.cache_resource(show_spinner="Yapay zeka modeli yükleniyor... Lütfen bekleyin.")
def get_model():
    return load_model()


try:
    tokenizer, model = get_model()
except Exception as e:
    st.error(f"Model yüklenirken bir hata oluştu: {e}")
    st.stop()

mesaj = st.text_area("Mesajınızı buraya yapıştırın:", height=150)

if st.button("Mesajı Analiz Et", type="primary"):
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin.")
    else:
        with st.spinner("Yapay zeka bağlamı inceliyor..."):
            sonuc = tahmin_et(mesaj, tokenizer, model)

        st.markdown("---")
        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        if risk == "yuksek_riskli":
            st.error(f"{emoji} **{baslik}**")
        elif risk == "supheli":
            st.warning(f"{emoji} **{baslik}**")
        else:
            st.success(f"{emoji} **{baslik}**")

        st.subheader("Neden bu sonucu aldık?")
        for neden in sonuc["nedenler"]:
            st.markdown(f"- {neden}")

        if risk in ("yuksek_riskli", "supheli"):
            st.info(
                "**Ne yapmalısınız?**\n\n"
                "- Mesajdaki linke **tıklamayın**\n"
                "- Kişisel bilgi ya da para göndermeyin\n"
                "- Şüpheliyseniz ilgili kurumu resmi telefon numarasından arayıp doğrulayın\n"
                "- Tehdit/şantaj içeriyorsa **155 Polis İmdat**'ı arayın\n"
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
