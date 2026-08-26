"""
Turkce BERT fine-tuning scripti - gelistirilmis versiyon.
Sinif agirligi + erken durdurma ile daha dengeli ve guvenilir egitim.
Coklu GPU (DataParallel) uyumlu.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
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


def _num_labels_al(model):
    if hasattr(model, "module"):
        return model.module.config.num_labels
    return model.config.num_labels


class AgirlikliTrainer(Trainer):
    def __init__(self, class_weights, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        num_labels = _num_labels_al(model)
        loss_fct = nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fct(logits.view(-1, num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def egit():
    print("GPU kullaniliyor mu:", torch.cuda.is_available())
    print("GPU sayisi:", torch.cuda.device_count())

    train_df, test_df = veri_hazirla()
    print(f"Egitim: {len(train_df)}, Test: {len(test_df)}")
    print("\nSinif dagilimi (egitim):")
    print(train_df["risk_seviyesi"].value_counts())

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1, 2]),
        y=train_df["label"].values,
    )
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
    print("\nHesaplanan sinif agirliklari:", dict(zip(["guvenli", "supheli", "yuksek_riskli"], class_weights)))

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ADI)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ADI, num_labels=3
    )

    train_dataset = Dataset.from_pandas(train_df[["mesaj", "label"]])
    test_dataset = Dataset.from_pandas(test_df[["mesaj", "label"]])

    train_dataset = train_dataset.map(
        lambda x: tokenize_fonksiyonu(x, tokenizer), batched=True
    )
    test_dataset = test_dataset.map(
        lambda x: tokenize_fonksiyonu(x, tokenizer), batched=True
    )

    training_args = TrainingArguments(
        output_dir=str(BASE_DIR / "bert_ciktilar"),
        num_train_epochs=6,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="dogruluk",
        greater_is_better=True,
        logging_steps=20,
        learning_rate=2e-5,
        weight_decay=0.01,
        report_to="none",
        save_total_limit=2,
    )

    trainer = AgirlikliTrainer(
        class_weights=class_weights_tensor,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=metrikleri_hesapla,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()

    tahmin_ciktisi = trainer.predict(test_dataset)
    tahminler = np.argmax(tahmin_ciktisi.predictions, axis=-1)
    gercek = test_df["label"].values

    print("\n--- Test seti performansi (BERT, sinif agirlikli + erken durdurma) ---")
    print(classification_report(
        gercek, tahminler,
        target_names=list(ETIKET_TO_ID.keys()),
        zero_division=0,
    ))

    MODEL_CIKTI_YOLU.mkdir(parents=True, exist_ok=True)

    kaydedilecek_model = model.module if hasattr(model, "module") else model
    kaydedilecek_model.save_pretrained(MODEL_CIKTI_YOLU)
    tokenizer.save_pretrained(MODEL_CIKTI_YOLU)
    print(f"\nModel kaydedildi: {MODEL_CIKTI_YOLU}")


if __name__ == "__main__":
    egit()
