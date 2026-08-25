
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

detayli_analiz = st.checkbox(
    "Detaylı kelime analizi de göster (biraz daha yavaş çalışır)",
    value=False,
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

        if detayli_analiz:
            st.subheader("🔍 Kelime bazlı analiz (deneysel)")
            try:
                with st.spinner("Kelimeler tek tek inceleniyor, bu biraz sürebilir..."):
                    from src.explain import shap_aciklama_uret
                    kelime_etkileri, _ = shap_aciklama_uret(metin, hedef_sinif=risk, max_evals=200)

                st.caption(
                    "Modelimiz kararını verirken hangi kelimelere ne kadar önem verdiğini gösterir. "
                    "🔴 kırmızı kelimeler riski artırıyor, 🟢 yeşil kelimeler riski azaltıyor. "
                    "Bu analiz deneyseldir, model bazen insan sezgisinden farklı kalıplar öğrenmiş olabilir."
                )

                en_etkili = [k for k in kelime_etkileri if abs(k[1]) > 0.01][:8]
                if not en_etkili:
                    st.write("Belirgin bir kelime etkisi bulunamadı.")
                else:
                    for kelime, deger in en_etkili:
                        if deger > 0:
                            st.markdown(f"🔴 **{kelime}** — riski artırıyor ({deger:+.3f})")
                        else:
                            st.markdown(f"🟢 **{kelime}** — riski azaltıyor ({deger:+.3f})")
            except Exception as e:
                st.caption(f"Kelime analizi şu an yapılamadı: {e}")

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
