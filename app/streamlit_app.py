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
    .stApp { background-color: #FFFFFF; }

    .baslik-kutu {
        text-align: center;
        padding: 2.2rem 1rem 1.8rem 1rem;
    }
    .baslik-kutu h1 {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1E1B2E;
        margin-bottom: 0.3rem;
    }
    .baslik-kutu p {
        color: #8B8A99;
        font-size: 0.9rem;
    }

    .rozet-alan {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .rozet {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.9rem 1.8rem;
        border-radius: 999px;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .rozet-yuksek { background-color: #FEE2E2; color: #B91C1C; }
    .rozet-supheli { background-color: #FEF3C7; color: #B45309; }
    .rozet-guvenli { background-color: #D1FAE5; color: #047857; }

    .etiket-alan {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        padding: 1.2rem 0;
    }
    .etiket {
        background-color: #F5F5FF;
        color: #4F46E5;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 500;
        max-width: 100%;
    }

    .aksiyon-kutu {
        background-color: #F9FAFB;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #374151;
    }

    .footer-not {
        text-align: center;
        color: #C4C3CC;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid #F0F0F5;
    }

    div[data-testid="stFileUploader"] {
        border: 1.5px dashed #DDDCE8;
        border-radius: 14px;
        padding: 1rem;
        background-color: #FAFAFF;
    }
    .stButton button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 0;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1.5px solid #E5E4EE;
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

        rozet_sinifi = {
            "yuksek_riskli": "rozet-yuksek",
            "supheli": "rozet-supheli",
            "guvenli": "rozet-guvenli",
        }.get(risk, "rozet-supheli")

        st.markdown(f"""
        <div class="rozet-alan">
            <div class="rozet {rozet_sinifi}">{emoji} {baslik}</div>
        </div>
        """, unsafe_allow_html=True)

        etiketler_html = "".join(f'<span class="etiket">{n}</span>' for n in sonuc["nedenler"])
        st.markdown(f'<div class="etiket-alan">{etiketler_html}</div>', unsafe_allow_html=True)

        if risk in ("yuksek_riskli", "supheli"):
            st.markdown("""
            <div class="aksiyon-kutu">
                <strong>Ne yapmalısınız?</strong><br><br>
                • Mesajdaki linke <strong>tıklamayın</strong><br>
                • Kişisel bilgi ya da para göndermeyin<br>
                • Şüpheliyseniz ilgili kurumu resmi telefon numarasından arayıp doğrulayın<br>
                • Tehdit/şantaj içeriyorsa <strong>155 Polis İmdat</strong>'ı arayın<br>
                • Yakınınızdan bir teknoloji konusunda daha bilgili birine danışın
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div class="footer-not">
    Bu araç kesin doğruluk garanti etmez, sağduyunuzu her zaman kullanın.
</div>
""", unsafe_allow_html=True)
