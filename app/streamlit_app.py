import streamlit as st
import sys
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.predict import load_model, tahmin_et

st.set_page_config(
    page_title="Dolandırıcı Mesaj Tespit Asistanı",
    page_icon="🛡️",
    layout="centered",
)

st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
    }
    .baslik-kutu {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
    }
    .baslik-kutu h1 {
        font-size: 1.9rem;
        font-weight: 600;
        color: #37352F;
        margin-bottom: 0.4rem;
    }
    .baslik-kutu p {
        color: #9B9A97;
        font-size: 0.95rem;
    }
    .sonuc-kart {
        border-radius: 14px;
        padding: 1.6rem;
        margin: 1.2rem 0;
    }
    .sonuc-yuksek {
        background-color: #FDECEC;
    }
    .sonuc-supheli {
        background-color: #FBF3DB;
    }
    .sonuc-guvenli {
        background-color: #E9F3EC;
    }
    .sonuc-baslik {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #37352F;
    }
    .sonuc-nedenler {
        color: #5F5E5B;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .footer-not {
        text-align: center;
        color: #B4B3AF;
        font-size: 0.78rem;
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid #F0EFEC;
    }
    div[data-testid="stFileUploader"] {
        border: 1.5px dashed #E3E2DF;
        border-radius: 14px;
        padding: 1rem;
        background-color: #FBFBFA;
    }
    .stButton button {
        border-radius: 10px;
        font-weight: 500;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1.5px solid #E3E2DF;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="baslik-kutu">
    <h1>🛡️ Dolandırıcı Mesaj Tespit Asistanı</h1>
    <p>Yapay zeka destekli, ebeveynler için güvenlik katmanı</p>
</div>
""", unsafe_allow_html=True)


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
    mesaj = st.text_area("Mesajınızı buraya yapıştırın:", height=150, placeholder="Örn: Kargonuz teslim edilemedi...")
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
            get_ocr_reader()
            mesaj = resimden_metin_cikar(resim)
        if mesaj:
            mesaj = st.text_area("Görselden okunan metin (gerekirse düzeltebilirsiniz):", value=mesaj, height=100)
        else:
            st.warning("Görselden metin okunamadı, lütfen daha net bir görsel deneyin ya da metni elle yazın.")

analiz_butonu = st.button("🔍 Mesajı Analiz Et", type="primary", use_container_width=True)

if analiz_butonu:
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin ya da görsel yükleyin.")
    else:
        with st.spinner("Yapay zeka bağlamı inceliyor..."):
            sonuc = tahmin_et(mesaj, tokenizer, model)

        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        sinif_haritasi = {
            "yuksek_riskli": "sonuc-yuksek",
            "supheli": "sonuc-supheli",
            "guvenli": "sonuc-guvenli",
        }
        css_sinifi = sinif_haritasi.get(risk, "sonuc-supheli")

        nedenler_html = "".join(f"<li>{n}</li>" for n in sonuc["nedenler"])

        st.markdown(f"""
        <div class="sonuc-kart {css_sinifi}">
            <div class="sonuc-baslik">{emoji} {baslik}</div>
            <div class="sonuc-nedenler">
                <strong>Neden bu sonucu aldık?</strong>
                <ul style="margin-top:0.5rem;">{nedenler_html}</ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if risk in ("yuksek_riskli", "supheli"):
            st.info(
                "**Ne yapmalısınız?**\n\n"
                "- Mesajdaki linke **tıklamayın**\n"
                "- Kişisel bilgi ya da para göndermeyin\n"
                "- Şüpheliyseniz ilgili kurumu resmi telefon numarasından arayıp doğrulayın\n"
                "- Tehdit/şantaj içeriyorsa **155 Polis İmdat**'ı arayın\n"
                "- Yakınınızdan bir teknoloji konusunda daha bilgili birine danışın"
            )

st.markdown("""
<div class="footer-not">
    Bu araç kesin doğruluk garanti etmez, sağduyunuzu her zaman kullanın.
</div>
""", unsafe_allow_html=True)
