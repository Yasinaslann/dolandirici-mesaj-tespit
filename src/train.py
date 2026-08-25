
"""
Baseline model egitim scripti.
TF-IDF (karakter n-gram, Turkce karakter sorunlarina daha dayanikli)
+ Lojistik Regresyon ile risk_seviyesi siniflandirmasi yapar.
"""

import pickle
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent
VERI_YOLU = BASE_DIR / "data" / "mesajlar.csv"
MODEL_YOLU = BASE_DIR / "models" / "risk_model.pkl"


def veri_yukle():
    df = pd.read_csv(VERI_YOLU)
    df = df.dropna(subset=["mesaj", "risk_seviyesi"])
    return df


def model_kur():
    vektorlestirici = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 4),
        min_df=1,
        lowercase=True,
    )
    siniflandirici = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
    )
    return Pipeline([
        ("tfidf", vektorlestirici),
        ("clf", siniflandirici),
    ])


def egit_ve_kaydet():
    df = veri_yukle()
    print(f"Toplam {len(df)} mesaj yuklendi.")
    print(df["risk_seviyesi"].value_counts())

    X = df["mesaj"]
    y = df["risk_seviyesi"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    pipeline = model_kur()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\n--- Test seti performansi ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    MODEL_YOLU.parent.mkdir(exist_ok=True)
    with open(MODEL_YOLU, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\nModel kaydedildi: {MODEL_YOLU}")


if __name__ == "__main__":
    egit_ve_kaydet()
