import streamlit as st
import sys
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
        background: radial-gradient(circle at 20% 0%, #1A1F35 0%, #0B0F19 55%);
    }

    @keyframes yumusakGiris {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .baslik-kutu {
        text-align: center;
        padding: 2.5rem 1rem 1.8rem 1rem;
    }
    .baslik-ikon {
        font-size: 2.8rem;
        margin-bottom: 0.4rem;
        filter: drop-shadow(0 4px 12px rgba(129, 140, 248, 0.35));
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
        margin: 1.6rem 0 0.7rem 0;
    }

    .istatistik-serit {
        display: flex;
        gap: 0.7rem;
        margin: 0.5rem 0 1.5rem 0;
    }
    .istatistik-kutu {
        flex: 1;
        background-color: #12172A;
        border: 1px solid #1F2740;
        border-radius: 14px;
        padding: 0.9rem 0.6rem;
        text-align: center;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .istatistik-kutu:hover {
        transform: translateY(-2px);
        border-color: #3A4368;
    }
    .istatistik-sayi {
        font-size: 1.5rem;
        font-weight: 800;
    }
    .istatistik-etiket {
        font-size: 0.72rem;
        color: #7C8397;
        margin-top: 0.15rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .sayi-yuksek { color: #F87171; }
    .sayi-supheli { color: #FBBF24; }
    .sayi-guvenli { color: #4ADE80; }

    .sonuc-cerceve {
        margin-top: 1.6rem;
        border-radius: 20px;
        padding: 2px;
        animation: yumusakGiris 0.45s ease-out;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
    }
    .sonuc-cerceve.cerceve-yuksek { background: linear-gradient(135deg, #EF4444, #7F1D1D); }
    .sonuc-cerceve.cerceve-supheli { background: linear-gradient(135deg, #F59E0B, #78350F); }
    .sonuc-cerceve.cerceve-guvenli { background: linear-gradient(135deg, #22C55E, #14532D); }

    .sonuc-ic {
        background-color: #12172A;
        border-radius: 18px;
        padding: 1.9rem;
    }

    .sonuc-ust {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.3rem;
    }
    .sonuc-daire {
        width: 58px;
        height: 58px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.7rem;
        flex-shrink: 0;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);
    }
    .daire-yuksek { background-color: #3A1518; }
    .daire-supheli { background-color: #3A2E10; }
    .daire-guvenli { background-color: #103A22; }

    .sonuc-baslik-metin {
        font-size: 1.28rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    .sonuc-alt-metin {
        color: #7C8397;
        font-size: 0.82rem;
        margin-top: 0.15rem;
    }

    .neden-baslik {
        color: #9CA3B8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.7rem;
        padding-top: 0.4rem;
        border-top: 1px solid #1F2740;
    }
    .neden-satiri {
        display: flex;
        align-items: flex-start;
        gap: 0.65rem;
        padding: 0.5rem 0;
        color: #D6D9E4;
        font-size: 0.92rem;
        line-height: 1.55;
    }
    .neden-nokta {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #818CF8;
        flex-shrink: 0;
        margin-top: 0.55rem;
    }

    /* --- Aksiyon listesi: numarali rozet tasarimi --- */
    .aksiyon-kutu {
        background-color: #151B2B;
        border: 1px solid #232B45;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        margin-top: 1.3rem;
        animation: yumusakGiris 0.5s ease-out;
    }
    .aksiyon-baslik {
        color: #F3F4F6;
        font-weight: 700;
        font-size: 0.98rem;
        margin-bottom: 1.1rem;
    }
    .aksiyon-satiri {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        padding: 0.6rem 0;
        border-top: 1px solid #1E2540;
    }
    .aksiyon-satiri:first-of-type { border-top: none; }
    .aksiyon-numara {
        width: 26px;
        height: 26px;
        border-radius: 8px;
        background: linear-gradient(135deg, #6366F1, #4F46E5);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: #E0E3FF;
        flex-shrink: 0;
    }
    .aksiyon-metin {
        color: #C3C8D6;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .aksiyon-metin strong { color: #F3F4F6; }

    .gecmis-satiri {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.65rem 0.85rem;
        border-radius: 10px;
        margin-bottom: 0.4rem;
        background-color: #12172A;
        border: 1px solid #1B2338;
        font-size: 0.85rem;
        transition: border-color 0.15s ease;
    }
    .gecmis-satiri:hover { border-color: #2E3757; }
    .gecmis-nokta {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .nokta-yuksek { background-color: #EF4444; }
    .nokta-supheli { background-color: #F59E0B; }
    .nokta-guvenli { background-color: #22C55E; }
    .gecmis-mesaj {
        color: #C7CBDA;
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .gecmis-etiket {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        flex-shrink: 0;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .etiket-yuksek { background-color: #3A1518; color: #F87171; }
    .etiket-supheli { background-color: #3A2E10; color: #FBBF24; }
    .etiket-guvenli { background-color: #103A22; color: #4ADE80; }
    .gecmis-saat {
        color: #565E77;
        font-size: 0.75rem;
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
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.35);
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

if "gecmis" not in st.session_state:
    st.session_state.gecmis = []

if st.session_state.gecmis:
    toplam = len(st.session_state.gecmis)
    yuksek_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "yuksek_riskli")
    supheli_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "supheli")
    guvenli_sayisi = sum(1 for g in st.session_state.gecmis if g["risk"] == "guvenli")

    st.markdown(f"""
    <div class="istatistik-serit">
        <div class="istatistik-kutu">
            <div class="istatistik-sayi">{toplam}</div>
            <div class="istatistik-etiket">Toplam Kontrol</div>
        </div>
        <div class="istatistik-kutu">
            <div class="istatistik-sayi sayi-yuksek">{yuksek_sayisi}</div>
            <div class="istatistik-etiket">Yüksek Riskli</div>
        </div>
        <div class="istatistik-kutu">
            <div class="istatistik-sayi sayi-supheli">{supheli_sayisi}</div>
            <div class="istatistik-etiket">Şüpheli</div>
        </div>
        <div class="istatistik-kutu">
            <div class="istatistik-sayi sayi-guvenli">{guvenli_sayisi}</div>
            <div class="istatistik-etiket">Güvenli</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

ETIKET_METNI = {
    "yuksek_riskli": "Yüksek Riskli",
    "supheli": "Şüpheli",
    "guvenli": "Güvenli",
}

if analiz_butonu:
    if not mesaj.strip():
        st.warning("Lütfen analiz edilecek bir mesaj girin ya da görsel yükleyin.")
    else:
        with st.spinner("Yapay zeka bağlamı inceliyor..."):
            sonuc = tahmin_et(mesaj, tokenizer, model)

        risk = sonuc["risk_seviyesi"]
        emoji = sonuc["emoji"]
        baslik = sonuc["baslik"]

        st.session_state.gecmis.insert(0, {
            "mesaj": mesaj[:60] + ("..." if len(mesaj) > 60 else ""),
            "risk": risk,
            "saat": datetime.now().strftime("%H:%M"),
        })
        st.session_state.gecmis = st.session_state.gecmis[:10]

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
                <div class="neden-baslik">Değerlendirme Gerekçesi</div>
                {nedenler_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if risk in ("yuksek_riskli", "supheli"):
            st.markdown("""
            <div class="aksiyon-kutu">
                <div class="aksiyon-baslik">Şimdi Ne Yapmalısınız?</div>
                <div class="aksiyon-satiri">
                    <div class="aksiyon-numara">01</div>
                    <div class="aksiyon-metin">Mesajdaki linke <strong>kesinlikle tıklamayın</strong></div>
                </div>
                <div class="aksiyon-satiri">
                    <div class="aksiyon-numara">02</div>
                    <div class="aksiyon-metin">Kişisel bilgi ya da para <strong>paylaşmayın</strong></div>
                </div>
                <div class="aksiyon-satiri">
                    <div class="aksiyon-numara">03</div>
                    <div class="aksiyon-metin">Şüpheliyseniz kurumu <strong>resmi telefon numarasından</strong> arayıp doğrulayın</div>
                </div>
                <div class="aksiyon-satiri">
                    <div class="aksiyon-numara">04</div>
                    <div class="aksiyon-metin">Tehdit/şantaj içeriyorsa hemen <strong>155 Polis İmdat</strong>'ı arayın</div>
                </div>
                <div class="aksiyon-satiri">
                    <div class="aksiyon-numara">05</div>
                    <div class="aksiyon-metin">Emin değilseniz, teknolojiye yakın bir yakınınıza danışın</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

if st.session_state.gecmis:
    st.markdown('<div class="bolum-baslik">Bu Oturumdaki Geçmiş Kontroller</div>', unsafe_allow_html=True)

    nokta_sinif_haritasi = {
        "yuksek_riskli": "nokta-yuksek",
        "supheli": "nokta-supheli",
        "guvenli": "nokta-guvenli",
    }
    etiket_sinif_haritasi = {
        "yuksek_riskli": "etiket-yuksek",
        "supheli": "etiket-supheli",
        "guvenli": "etiket-guvenli",
    }

    gecmis_html = ""
    for kayit in st.session_state.gecmis:
        nokta_sinif = nokta_sinif_haritasi.get(kayit["risk"], "nokta-supheli")
        etiket_sinif = etiket_sinif_haritasi.get(kayit["risk"], "etiket-supheli")
        etiket_metni = ETIKET_METNI.get(kayit["risk"], "Bilinmiyor")
        gecmis_html += f"""
        <div class="gecmis-satiri">
            <div class="gecmis-nokta {nokta_sinif}"></div>
            <div class="gecmis-mesaj">{kayit['mesaj']}</div>
            <div class="gecmis-etiket {etiket_sinif}">{etiket_metni}</div>
            <div class="gecmis-saat">{kayit['saat']}</div>
        </div>
        """
    st.markdown(gecmis_html, unsafe_allow_html=True)

    if st.button("Geçmişi temizle", use_container_width=True):
        st.session_state.gecmis = []
        st.rerun()

st.markdown("""
<div class="footer-not">
    Bu araç kesin doğruluk garanti etmez, sağduyunuzu her zaman kullanın.
</div>
""", unsafe_allow_html=True)
