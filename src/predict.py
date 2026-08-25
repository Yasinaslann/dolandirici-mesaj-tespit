import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Kendi Hugging Face deponun adı
MODEL_NAME = "YasinAsl0n/dolandirici-mesaj-tespit-bert"

# Sınıf eşleştirmeleri (Model eğitimindeki sıraya göre)
ID_TO_ETIKET = {0: "guvenli", 1: "supheli", 2: "yuksek_riskli"}

def load_model():
    """Hugging Face Hub'dan model ve tokenizer'ı indirir/yükler."""
    print("BERT modeli Hugging Face'ten yükleniyor...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return tokenizer, model

def predict_message(text, tokenizer, model):
    """Gelen mesajı BERT modeli ile analiz eder."""
    # Mesajı modelin anlayacağı formata (tensor) çevir
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    
    # Tahmin yap
    with torch.no_grad():
        outputs = model(**inputs)
        
    # En yüksek olasılıklı sınıfı bul
    logits = outputs.logits
    predicted_class_id = logits.argmax(axis=1).item()
    
    # ID'yi metne çevir (örn: 2 -> yuksek_riskli)
    sonuc_etiket = ID_TO_ETIKET[predicted_class_id]
    
    return sonuc_etiket
