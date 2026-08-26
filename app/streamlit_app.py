import streamlit as st
import sys
import time
from pathlib import Path
from datetime import datetime
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
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 70%);
    }

    @keyframes yumusakGiris {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .baslik-kutu {
        text-align: center;
        padding: 2.8rem 1rem 2rem 1rem;
    }
    .baslik-ikon {
        font-size: 3.4rem;
        margin-bottom: 0.6rem;
        filter: drop-shadow(0 6px 16px rgba(129, 140, 248, 0.45));
    }
    .baslik-kutu h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    .baslik-kutu p {
        color: #A8B3C7;
        font-size: 1rem;
    }

    .bolum-baslik {
        color: #A8B3C7;
        font-size: 0.92rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin: 2.2rem 0 1rem 0;
    }

    .istatistik-serit {
        display: flex;
        gap: 0.9rem;
        margin: 0.5rem 0 2rem 0;
    }
    .istatistik-kutu {
        flex: 1;
        background-color: #12172A;
        border: 1px solid #1F2740;
        border-radius: 14px;
        padding: 0.95rem 0.6rem;
        text-align: center;
        transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
    }
    .istatistik-kutu:hover {
        transform: translateY(-3px) scale(1.03);
        border-color: #4C5578;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
    }
    .istatistik-sayi {
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .istatistik-etiket {
        font-size: 0.72rem;
        color: #7C8397;
        margin-top: 0.25rem;
        letter-spacing: 0.03em;
        font-weight: 600;
    }
    .sayi-toplam { color: #C7D2FE; }
    .sayi-yuksek { color: #F87171; }
    .sayi-supheli { color: #FBBF24; }
    .sayi-guvenli { color: #4ADE80; }

    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        display: none;
    }
    div[data-testid="stRadio"] > label {
        color: #A8B3C7;
        font-size: 0.92rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        gap: 0.6rem;
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 0.4rem;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        display: flex !important;
        flex: 1;
        text-align: center;
        border-radius: 12px;
        padding: 0.9rem 0.5rem !important;
        margin: 0 !important;
        transition: background-color 0.15s ease, box-shadow 0.15s ease;
        cursor: pointer;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #0EA5E9, #0369A1);
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.45);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        color: #F1F5F9 !important;
        white-space: nowrap;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        display: none;
    }

    .stTextArea textarea {
        border-radius: 16px;
        border: 1.5px solid rgba(255, 255, 255, 0.1);
        background: rgba(15, 23, 42, 0.65);
        color: #F8FAFC;
        font-size: 1.02rem;
        line-height: 1.6;
        padding: 1rem;
    }
    .stTextArea textarea:focus {
        border-color: #0EA5E9 !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25) !important;
    }

    .sonuc-cerceve {
        margin-top: 1.8rem;
        border-radius: 22px;
        padding: 2px;
        animation: yumusakGiris 0.45s ease-out;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
    }
    .sonuc-cerceve.cerceve-yuksek { background: linear-gradient(135deg, #EF4444, #7F1D1D); }
    .sonuc-cerceve.cerceve-supheli { background: linear-gradient(135deg, #F59E0B, #78350F); }
    .sonuc-cerceve.cerceve-guvenli { background: linear-gradient(135deg, #22C55E, #14532D); }

    .sonuc-ic {
        background-color: #0f172a;
        border-radius: 20px;
        padding: 2rem;
    }

    .sonuc-ust {
        display: flex;
        align-items: center;
        gap: 1.1rem;
        margin-bottom: 1.4rem;
    }
    .sonuc-daire {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        flex-shrink: 0;
        box-shadow: inset 0 0 0 1.5px rgba(255,255,255,0.12);
    }
    .daire-yuksek { background: rgba(239, 68, 68, 0.22); }
    .daire-supheli { background: rgba(245, 158, 11, 0.22); }
    .daire-guvenli { background: rgba(34, 197, 94, 0.22); }

    .sonuc-baslik-metin {
        font-size: 1.4rem;
        font-weight: 800;
        color: #F8FAFC;
    }
    .sonuc-alt-metin {
        color: #A8B3C7;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    .neden-baslik {
        color: #A8B3C7;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 0.9rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .neden-satiri {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.55rem 0;
        color: #E7EBF3;
        font-size: 1rem;
        line-height: 1.6;
    }
    .neden-nokta {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #0EA5E9;
        flex-shrink: 0;
        margin-top: 0.55rem;
    }

    .aksiyon-kutu {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 1.7rem;
        margin-top: 1.4rem;
        animation: yumusakGiris 0.5s ease-out;
    }
    .aksiyon-baslik {
        color: #F8FAFC;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 1.1rem;
    }
    .aksiyon-satiri {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.7rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    .aksiyon-satiri:first-of-type { border-top: none; }
    .aksiyon-numara {
        width: 30px;
        height: 30px;
        border-radius: 9px;
        background: linear-gradient(135deg, #0EA5E9, #0369A1);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: 800;
        color: #FFFFFF;
        flex-shrink: 0;
    }
    .aksiyon-metin {
        color: #D6DCE8;
        font-size: 0.96rem;
        line-height: 1.55;
    }
    .aksiyon-metin strong { color: #F8FAFC; }

    .gecmis-satiri {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        padding: 0.8rem 1rem;
        border-radius: 14px;
        margin-bottom: 0.6rem;
        background: rgba(30, 41, 59, 0.45);
        border-left: 4px solid transparent;
        font-size: 0.92rem;
        transition: all 0.2s ease;
    }
    .gecmis-satiri:hover { background: rgba(30, 41, 59, 0.75); }
    .gecmis-yuksek { border-left-color: #EF4444; }
    .gecmis-supheli { border-left-color: #F59E0B; }
    .gecmis-guvenli { border-left-color: #22C55E; }
    .gecmis-mesaj {
        color: #D6DCE8;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .gecmis-etiket {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        flex-shrink: 0;
    }
    .etiket-yuksek { background: rgba(239, 68, 68, 0.2); color: #F87171; }
    .etiket-supheli { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
    .etiket-guvenli { background: rgba(34, 197, 94, 0.2); color: #4ADE80; }
    .gecmis-saat {
        color: #7E8AA3;
        font-size: 0.78rem;
        flex-shrink: 0;
    }

    .footer-not {
        text-align: center;
        color: #7E8AA3;
        font-size: 0.82rem;
        margin-top: 3.2rem;
        padding-top: 1.4rem;
        border-top: 1px solid rgba(255, 255, 255, 0.07);
    }

    div[data-testid="stFileUploader"] {
        border: 1.5px dashed rgba(14, 165, 233, 0.35);
        border-radius: 16px;
        padding: 1.1rem;
        background: rgba(30, 41, 59, 0.3);
    }

    /* --- Buton: metalik mavi degrade, siber guvenlik temasina uygun --- */
    .stButton button {
        border-radius: 14px;
        font-weight: 700;
        font-size: 1.02rem;
        padding: 0.75rem 0;
        border: 1px solid rgba(125, 211, 252, 0.3) !important;
        background: linear-gradient(135deg, #38BDF8 0%, #0EA5E9 45%, #0369A1 100%) !important;
        box-shadow: 0 6px 18px rgba(14, 165, 233, 0.4), inset 0 1px 0 rgba(255,255,255,0.15) !important;
        color: #F0F9FF !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(14, 165, 233, 0.5), inset 0 1px 0 rgba(255,255,255,0.2) !important;
        border-color: rgba(186, 230, 253, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="baslik-kutu">
    <div class="baslik-ikon">🛡️</div>
    <h1>Dolandırıcı Mesaj Tespit Asistanı</h1>
    <p>Yapay Zeka Destekli Metin Analizi &nbsp;·&nbsp; Şüpheli İçerik Tespit Motoru</p>
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

if "gecmis" not in st.session_state:
    st.session_state.gecmis = []


def istatistik_html_uret():
    toplam = len(st.session_state.gecmis)
    yuksek_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "yuksek_riskli")
    supheli_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "supheli")
    guvenli_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "guvenli")
    return (
        f'<div class="istatistik-serit">'
        f'<div class="istatistik-kutu"><div class="istatistik-sayi sayi-toplam">{toplam}</div><div class="istatistik-etiket">Toplam</div></div>'
        f'<div class="istatistik-kutu"><div class="istatistik-sayi sayi-yuksek">{yuksek_sayisi}</div><div class="istatistik-etiket">Riskli</div></div>'
        f'<div class="istatistik-kutu"><div class="istatistik-sayi sayi-supheli">{supheli_sayisi}</div><div class="istatistik-etiket">Şüpheli</div></div>'
        f'<div class="istatistik-kutu"><div class="istatistik-sayi sayi-guvenli">{guvenli_sayisi}</div><div class="istatistik-etiket">Güvenli</div></div>'
        f'</div>'
    )


istatistik_yer_tutucu = st.empty()
if st.session_state.gecmis:
    istatistik_yer_tutucu.markdown(istatistik_html_uret(), unsafe_allow_html=True)

giris_yontemi = st.radio(
    "GİRİŞ YÖNTEMİ",
    ["📋 Metin Yapıştır", "📷 Fotoğraf Yükleyin"],
    horizontal=True,
)

mesaj = ""

if giris_yontemi == "📋 Metin Yapıştır":
    mesaj = st.text_area("Mesajınızı buraya yapıştırın:", height=150, placeholder="Örn: Kargonuz teslim edilemedi, adresinizi güncelleyin...", label_visibility="collapsed")
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
            okunan_metin = resimden_metin_cikar(resim)
        if okunan_metin:
            mesaj = st.text_area("Görselden okunan metin (gerekirse düzeltebilirsiniz):", value=okunan_metin, height=100)
        else:
            st.warning("Görselden metin okunamadı, lütfen daha net bir görsel yükleyin ya da metni elle yazın.")

analiz_butonu = st.button("🔍 Mesajı Analiz Et", type="primary", use_container_width=True)

ETIKET_METNI = {
    "yuksek_riskli": "Yüksek Riskli",
    "supheli": "Şüpheli",
    "guvenli": "Güvenli",
}

GECMIS_SINIF = {
    "yuksek_riskli": "gecmis-yuksek",
    "supheli": "gecmis-supheli",
    "guvenli": "gecmis-guvenli",
}

if analiz_butonu:
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin ya da görsel yükleyin.")
    else:
        with st.status("🛡️ Güvenlik kalkanı çalıştırılıyor...", expanded=True) as status:
            st.write("🔍 Metin ayıklanıyor ve taranıyor...")
            time.sleep(0.3)
            st.write("🤖 Yapay zeka bağlamı inceliyor...")
            time.sleep(0.3)
            st.write("⚠️ Tehdit ve oltalama kalıpları denetleniyor...")
            sonuc = tahmin_et(mesaj, tokenizer, model)
            time.sleep(0.2)
            status.update(label="✅ Analiz tamamlandı!", state="complete", expanded=False)

        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        st.session_state.gecmis.insert(0, {
            "mesaj": mesaj[:55] + ("..." if len(mesaj) > 55 else ""),
            "risk": risk,
            "saat": datetime.now().strftime("%H:%M"),
        })
        st.session_state.gecmis = st.session_state.gecmis[:10]

        istatistik_yer_tutucu.markdown(istatistik_html_uret(), unsafe_allow_html=True)

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
            f'<div class="neden-satiri"><span class="neden-nokta"></span><span>{n}</span></div>'
            for n in sonuc["nedenler"]
        )

        st.markdown(
            f'<div class="sonuc-cerceve {cerceve_sinif}">'
            f'<div class="sonuc-ic">'
            f'<div class="sonuc-ust">'
            f'<div class="sonuc-daire {daire_sinif}">{emoji}</div>'
            f'<div><div class="sonuc-baslik-metin">{baslik}</div>'
            f'<div class="sonuc-alt-metin">{alt_metin}</div></div>'
            f'</div>'
            f'<div class="neden-baslik">DEĞERLENDİRME GEREKÇESİ</div>'
            f'{nedenler_html}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if risk in ("yuksek_riskli", "supheli"):
            st.markdown(
                '<div class="aksiyon-kutu">'
                '<div class="aksiyon-baslik">🚨 Şimdi Ne Yapmalısınız?</div>'
                '<div class="aksiyon-satiri"><div class="aksiyon-numara">01</div>'
                '<div class="aksiyon-metin">Mesajdaki linke veya ek dosyaya <strong>kesinlikle tıklamayın</strong></div></div>'
                '<div class="aksiyon-satiri"><div class="aksiyon-numara">02</div>'
                '<div class="aksiyon-metin">Kişisel bilgi, şifre ya da para <strong>paylaşmayın</strong></div></div>'
                '<div class="aksiyon-satiri"><div class="aksiyon-numara">03</div>'
                '<div class="aksiyon-metin">Şüpheliyseniz ilgili kurumu <strong>resmi telefon numarasından</strong> arayıp doğrulayın</div></div>'
                '<div class="aksiyon-satiri"><div class="aksiyon-numara">04</div>'
                '<div class="aksiyon-metin">Tehdit/şantaj içeriyorsa hemen <strong>155 Polis İmdat</strong>\'ı arayın</div></div>'
                '<div class="aksiyon-satiri"><div class="aksiyon-numara">05</div>'
                '<div class="aksiyon-metin">Tanıdığınızdan gelse bile hesabı çalınmış olabilir, sesli arayarak teyit edin</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )

if st.session_state.gecmis:
    st.markdown('<div class="bolum-baslik">BU OTURUMDAKİ GEÇMİŞ KONTROLLER</div>', unsafe_allow_html=True)

    gecmis_html = ""
    for kayit in st.session_state.gecmis:
        gecmis_sinif = GECMIS_SINIF.get(kayit["risk"], "gecmis-supheli")
        etiket_sinif = {
            "yuksek_riskli": "etiket-yuksek",
            "supheli": "etiket-supheli",
            "guvenli": "etiket-guvenli",
        }.get(kayit["risk"], "etiket-supheli")
        etiket_metni = ETIKET_METNI.get(kayit["risk"], "Bilinmiyor")
        gecmis_html += (
            f'<div class="gecmis-satiri {gecmis_sinif}">'
            f'<div class="gecmis-mesaj">{kayit["mesaj"]}</div>'
            f'<div class="gecmis-etiket {etiket_sinif}">{etiket_metni}</div>'
            f'<div class="gecmis-saat">{kayit["saat"]}</div>'
            f'</div>'
        )
    st.markdown(gecmis_html, unsafe_allow_html=True)

    if st.button("🗑️ Geçmişi Temizle", use_container_width=True):
        st.session_state.gecmis = []
        st.rerun()

st.markdown("""
<div class="footer-not">
    Bu araç kesin doğruluk garanti etmez, şüphe durumunda her zaman sağduyunuzu kullanın.
</div>
""", unsafe_allow_html=True)
