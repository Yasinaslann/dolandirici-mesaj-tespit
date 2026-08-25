import numpy as np
import pandas as pd
import torch
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from datasets import Dataset

BASE_DIR = Path(__file__).resolve().parent.parent
VERI_YOLU = BASE_DIR / "data" / "mesajlar.csv"
MODEL_CIKTI_YOLU = BASE_DIR / "models" / "bert_model"
MODEL_ADI = "dbmdz/bert-base-turkish-cased"

ETIKET_TO_ID = {"guvenli": 0, "supheli": 1, "yuksek_riskli": 2}
ID_TO_ETIKET = {v: k for k, v in ETIKET_TO_ID.items()}

def veri_hazirla():
    df = pd.read_csv(VERI_YOLU)
    df = df.dropna(subset=["mesaj", "risk_seviyesi"])
    df["label"] = df["risk_seviyesi"].map(ETIKET_TO_ID)

    train_df, test_df = train_test_split(
        df, test_size=0.15, random_state=42, stratify=df["risk_seviyesi"]
    )
    return train_df, test_df

def tokenize_fonksiyonu(ornekler, tokenizer):
    return tokenizer(
        ornekler["mesaj"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )

def metrikleri_hesapla(eval_pred):
    logits, labels = eval_pred
    tahminler = np.argmax(logits, axis=-1)
    dogruluk = (tahminler == labels).mean()
    return {"dogruluk": dogruluk}

def egit():
    print("GPU kullaniliyor mu:", torch.cuda.is_available())
    train_df, test_df = veri_hazirla()
    print(f"Egitim: {len(train_df)}, Test: {len(test_df)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ADI)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ADI, num_labels=3)

    train_dataset = Dataset.from_pandas(train_df[["mesaj", "label"]])
    test_dataset = Dataset.from_pandas(test_df[["mesaj", "label"]])

    train_dataset = train_dataset.map(lambda x: tokenize_fonksiyonu(x, tokenizer), batched=True)
    test_dataset = test_dataset.map(lambda x: tokenize_fonksiyonu(x, tokenizer), batched=True)

    training_args = TrainingArguments(
        output_dir=str(BASE_DIR / "bert_ciktilar"),
        num_train_epochs=4,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=20,
        learning_rate=2e-5,
        weight_decay=0.01,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=metrikleri_hesapla,
    )

    trainer.train()

    tahmin_ciktisi = trainer.predict(test_dataset)
    tahminler = np.argmax(tahmin_ciktisi.predictions, axis=-1)
    gercek = test_df["label"].values

    print("\n--- Test seti performansi (BERT) ---")
    print(classification_report(
        gercek, tahminler,
        target_names=list(ETIKET_TO_ID.keys()),
        zero_division=0,
    ))

    MODEL_CIKTI_YOLU.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(MODEL_CIKTI_YOLU)
    tokenizer.save_pretrained(MODEL_CIKTI_YOLU)
    print(f"\nModel kaydedildi: {MODEL_CIKTI_YOLU}")

if __name__ == "__main__":
    egit()
