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

# ---- Ozel CSS (kurumsal/koyu tema) ----
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0F172A 0%, #111827 100%);
    }
    .baslik-kutu {
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 1.5rem;
    }
    .baslik-kutu h1 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-bottom: 0.3rem;
    }
    .baslik-kutu p {
        color: #94A3B8;
        font-size: 0.95rem;
    }
    .sonuc-kart {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .sonuc-yuksek {
        background-color: #2A1215;
        border-left-color: #EF4444;
    }
    .sonuc-supheli {
        background-color: #2A2312;
        border-left-color: #F59E0B;
    }
    .sonuc-guvenli {
        background-color: #12241A;
        border-left-color: #22C55E;
    }
    .sonuc-baslik {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .footer-not {
        text-align: center;
        color: #64748B;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #1E293B;
    }
    div[data-testid="stFileUploader"] {
        border: 1px dashed #334155;
        border-radius: 10px;
        padding: 0.5rem;
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
            <div style="color:#CBD5E1; margin-top:0.8rem;">
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

        with st.expander("Teknik detaylar (opsiyonel)"):
            st.write("Model olasılık dağılımı:")
            st.json({k: round(float(v), 3) for k, v in sonuc["olasiliklar"].items()})
            st.write("Kural tabanlı sinyal skorları:")
            st.json(sonuc["kural_skorlari"])

st.markdown("""
<div class="footer-not">
    ⚠️ Bu araç bir yardımcı sistemdir, kesin doğruluk garanti etmez.<br>
    Şüphe durumunda her zaman ilgili kurumu resmi kanallardan doğrulayın.
</div>
""", unsafe_allow_html=True)
