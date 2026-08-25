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
        background: radial-gradient(circle at 20% 0%, #1A1F35 0%, #0B0F19 55%);
    }

    .baslik-kutu {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
    }
    .baslik-ikon {
        font-size: 2.6rem;
        margin-bottom: 0.4rem;
    }
    .baslik-kutu h1 {
        font-size: 1.7rem;
        font-weight: 700;
        color: #F3F4F6;
        margin-bottom: 0.35rem;
        letter-spacing: -0.02em;
    }
    .baslik-kutu p {
        color: #8B93A7;
        font-size: 0.92rem;
    }

    .bolum-baslik {
        color: #C7CBDA;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 1.5rem 0 0.6rem 0;
    }

    .sonuc-cerceve {
        margin-top: 2rem;
        border-radius: 20px;
        padding: 2px;
    }
    .sonuc-cerceve.cerceve-yuksek { background: linear-gradient(135deg, #EF4444, #7F1D1D); }
    .sonuc-cerceve.cerceve-supheli { background: linear-gradient(135deg, #F59E0B, #78350F); }
    .sonuc-cerceve.cerceve-guvenli { background: linear-gradient(135deg, #22C55E, #14532D); }

    .sonuc-ic {
        background-color: #12172A;
        border-radius: 18px;
        padding: 1.8rem;
    }

    .sonuc-ust {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    .sonuc-daire {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        flex-shrink: 0;
    }
    .daire-yuksek { background-color: #3A1518; }
    .daire-supheli { background-color: #3A2E10; }
    .daire-guvenli { background-color: #103A22; }

    .sonuc-baslik-metin {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    .sonuc-alt-metin {
        color: #7C8397;
        font-size: 0.82rem;
        margin-top: 0.1rem;
    }

    .neden-satiri {
        display: flex;
        gap: 0.7rem;
        padding: 0.65rem 0;
        border-top: 1px solid #1F2740;
        color: #D1D5DB;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .neden-satiri:first-of-type { border-top: none; }
    .neden-ikon { color: #818CF8; flex-shrink: 0; }

    .aksiyon-kutu {
        background-color: #151B2B;
        border: 1px solid #232B45;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-top: 1.3rem;
    }
    .aksiyon-baslik {
        color: #F3F4F6;
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.9rem;
    }
    .aksiyon-satiri {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        color: #B8BECF;
        font-size: 0.87rem;
        padding: 0.4rem 0;
        line-height: 1.5;
    }
    .aksiyon-satiri .ikon {
        flex-shrink: 0;
    }

    .footer-not {
        text-align: center;
        color: #4B5268;
        font-size: 0.75rem;
        margin-top: 3rem;
        padding-top: 1.3rem;
        border-top: 1px solid #1A2036;
    }

    div[data-testid="stFileUploader"] {
        border: 1.5px dashed #2A3350;
        border-radius: 16px;
        padding: 1.1rem;
        background-color: #10152680;
    }
    .stButton button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.65rem 0;
        border: none;
        background: linear-gradient(135deg, #818CF8, #6366F1);
    }
    .stTextArea textarea {
        border-radius: 14px;
        border: 1.5px solid #232B45;
        background-color: #10152680;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="baslik-kutu">
    <div class="baslik-ikon">🛡️</div>
    <h1>Dolandırıcı Mesaj Tespit Asistanı</h1>
    <p>Yapay zeka destekli güvenlik katmanı&nbsp;&nbsp;·&nbsp;&nbsp;Ebeveynler için tasarlandı</p>
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

st.markdown('<div class="bolum-baslik">Mesajı Ekleyin</div>', unsafe_allow_html=True)

giris_yontemi = st.radio(
    "Giriş yöntemi",
    ["✍️ Metni yapıştır", "📷 Ekran görüntüsü yükle"],
    horizontal=True,
    label_visibility="collapsed",
)

mesaj = ""

if giris_yontemi == "✍️ Metni yapıştır":
    mesaj = st.text_area("Mesajınızı buraya yapıştırın:", height=150, placeholder="Örn: Kargonuz teslim edilemedi...", label_visibility="collapsed")
else:
    yuklenen_dosya = st.file_uploader(
        "SMS, WhatsApp ya da e-posta ekran görüntüsünü yükleyin",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed",
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

analiz_butonu = st.button("🔍  Mesajı Analiz Et", type="primary", use_container_width=True)

if analiz_butonu:
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin ya da görsel yükleyin.")
    else:
        with st.spinner("Yapay zeka bağlamı inceliyor..."):
            sonuc = tahmin_et(mesaj, tokenizer, model)

        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        cerceve_sinif = {
            "yuksek_riskli": "cerceve-yuksek",
            "supheli": "cerceve-supheli",
            "guvenli": "cerceve-guvenli",
        }.get(risk, "cerceve-supheli")

        daire_sinif = {
            "yuksek_riskli": "daire-yuksek",
            "supheli": "daire-supheli",
            "guvenli": "daire-guvenli",
        }.get(risk, "daire-supheli")

        alt_metin = {
            "yuksek_riskli": "Bilinen dolandırıcılık/tehdit kalıplarıyla eşleşti",
            "supheli": "Bazı şüpheli sinyaller tespit edildi",
            "guvenli": "Bilinen hiçbir riskli kalıba uymuyor",
        }.get(risk, "")

        nedenler_html = "".join(
            f'<div class="neden-satiri"><span class="neden-ikon">▸</span><span>{n}</span></div>'
            for n in sonuc["nedenler"]
        )

        st.markdown(f"""
        <div class="sonuc-cerceve {cerceve_sinif}">
            <div class="sonuc-ic">
                <div class="sonuc-ust">
                    <div class="sonuc-daire {daire_sinif}">{emoji}</div>
                    <div>
                        <div class="sonuc-baslik-metin">{baslik}</div>
                        <div class="sonuc-alt-metin">{alt_metin}</div>
                    </div>
                </div>
                {nedenler_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if risk in ("yuksek_riskli", "supheli"):
            st.markdown("""
            <div class="aksiyon-kutu">
                <div class="aksiyon-baslik">Ne yapmalısınız?</div>
                <div class="aksiyon-satiri"><span class="ikon">🔗</span><span>Mesajdaki linke&nbsp;<strong>tıklamayın</strong></span></div>
                <div class="aksiyon-satiri"><span class="ikon">🔒</span><span>Kişisel bilgi ya da para göndermeyin</span></div>
                <div class="aksiyon-satiri"><span class="ikon">📞</span><span>Şüpheliyseniz ilgili kurumu resmi telefon numarasından arayıp doğrulayın</span></div>
                <div class="aksiyon-satiri"><span class="ikon">🚨</span><span>Tehdit/şantaj içeriyorsa&nbsp;<strong>155 Polis İmdat</strong>&nbsp;arayın</span></div>
                <div class="aksiyon-satiri"><span class="ikon">👨‍👩‍👧</span><span>Yakınınızdan bir teknoloji konusunda daha bilgili birine danışın</span></div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div class="footer-not">
    Bu araç kesin doğruluk garanti etmez, sağduyunuzu her zaman kullanın.
</div>
""", unsafe_allow_html=True)
