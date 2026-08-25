import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re

MODEL_NAME = "YasinAsl0n/dolandirici-mesaj-tespit-bert"
ID_TO_ETIKET = {0: "guvenli", 1: "supheli", 2: "yuksek_riskli"}

# Asla affedilmeyecek, doğrudan yüksek risk sayılacak tehdit/gasp kelimeleri
TEHDIT_KELIMELERI = [
    "öldür", "oldur", "şantaj", "santaj", "vururum", "keseceğim", 
    "kan dökerim", "tehdit", "hapis", "gebert", "bıçak", "bicak"
]

def load_model():
    """Hugging Face Hub'dan model ve tokenizer'ı indirir/yükler."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return tokenizer, model

def acil_durum_kontrolu(text):
    """Mesajda fiziksel tehdit veya şantaj varsa True döner."""
    text_kucuk = text.lower()
    for kelime in TEHDIT_KELIMELERI:
        if kelime in text_kucuk:
            return True
    return False

def predict_message(text, tokenizer, model):
    """Gelen mesajı önce güvenlik filtresinden, sonra BERT modelinden geçirir."""
    
    # 1. Aşama: Kural Tabanlı Güvenlik Ağı (Guardrail)
    # Eğer adam açıkça ölümle veya şantajla tehdit ediyorsa BERT'e sormaya gerek yok!
    if acil_durum_kontrolu(text):
        return "yuksek_riskli"
        
    # 2. Aşama: BERT Yapay Zeka Analizi (Sinsi dolandırıcılıklar için)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    
    with torch.no_grad():
        outputs = model(**inputs)
        
    logits = outputs.logits
    predicted_class_id = logits.argmax(axis=1).item()
    
    return ID_TO_ETIKET[predicted_class_id]
