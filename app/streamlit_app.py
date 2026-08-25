import streamlit as st
import sys
from pathlib import Path

# src klasörünü sisteme tanıt
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.predict import load_model, predict_message

st.set_page_config(page_title="Dolandırıcı Mesaj Tespit", page_icon="🛡️")

st.title("🛡️ Dolandırıcı Mesaj Tespit Asistanı")
st.markdown("Şüphelendiğiniz mesajı aşağıya yapıştırın, **Yapay Zeka (BERT)** sizin için analiz etsin.")

# Modeli Streamlit'in önbelleğine (cache) alıyoruz (Sadece 1 kere indirilecek)
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
            sonuc = predict_message(mesaj, tokenizer, model)
            
        st.markdown("---")
        if sonuc == "yuksek_riskli":
            st.error("🚨 **YÜKSEK RİSKLİ MESAJ!** \n\nBu mesaj belirgin dolandırıcılık kalıpları (korku, aciliyet, sahte link vb.) içeriyor. **Lütfen içindeki linklere tıklamayın ve kişisel bilgilerinizi paylaşmayın.**")
        elif sonuc == "supheli":
            st.warning("⚠️ **ŞÜPHELİ MESAJ** \n\nBu mesajda şüpheli unsurlar (bedava kazanç, iş vaadi vb.) tespit edildi. Doğruluğundan emin olmadığınız sürece etkileşime girmeyin.")
        else:
            st.success("✅ **GÜVENLİ GÖRÜNÜYOR** \n\nMesajda yapay zeka tarafından dolandırıcılık veya risk unsuru tespit edilmedi. Yine de normal güvenlik tedbirlerinizi elden bırakmayın.")
