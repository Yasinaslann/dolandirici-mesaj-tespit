import streamlit as st
import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.predict import load_model, tahmin_et

st.set_page_config(page_title="Dolandırıcı Mesaj Tespit", page_icon="🛡️")

st.title("🛡️ Dolandırıcı Mesaj Tespit Asistanı")
st.markdown("Şüphelendiğiniz mesajı yapıştırın ya da ekran görüntüsünü yükleyin, **Yapay Zeka (BERT)** sizin için analiz etsin.")


@st.cache_resource(show_spinner="Yapay zeka modeli yükleniyor... Lütfen bekleyin.")
def get_model():
    return load_model()


@st.cache_resource(show_spinner=False)
def get_ocr_reader():
    from src.ocr import reader_getir
    return reader_getir()


try:
    tokenizer, model = get_model()
except Exception as e:
    st.error(f"Model yüklenirken bir hata oluştu: {e}")
    st.stop()

giris_yontemi = st.radio(
    "Mesajı nasıl eklemek istersiniz?",
    ["✍️ Metni yapıştır", "📷 Ekran görüntüsü yükle"],
    horizontal=True,
)

mesaj = ""

if giris_yontemi == "✍️ Metni yapıştır":
    mesaj = st.text_area("Mesajınızı buraya yapıştırın:", height=150)
else:
    yuklenen_dosya = st.file_uploader(
        "SMS, WhatsApp ya da e-posta ekran görüntüsünü yükleyin",
        type=["png", "jpg", "jpeg"],
    )
    if yuklenen_dosya is not None:
        resim = Image.open(yuklenen_dosya)
        st.image(resim, caption="Yüklenen görsel", use_container_width=True)
        with st.spinner("Görseldeki metin okunuyor..."):
            from src.ocr import resimden_metin_cikar
            get_ocr_reader()  # onbellege alsin
            mesaj = resimden_metin_cikar(resim)
        if mesaj:
            st.text_area("Görselden okunan metin (gerekirse düzeltebilirsiniz):", value=mesaj, height=100, key="ocr_metin")
            mesaj = st.session_state.get("ocr_metin", mesaj)
        else:
            st.warning("Görselden metin okunamadı, lütfen daha net bir görsel deneyin ya da metni elle yazın.")

if st.button("Mesajı Analiz Et", type="primary"):
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin ya da görsel yükleyin.")
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
