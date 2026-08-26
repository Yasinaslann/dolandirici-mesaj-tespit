"""
Cok genis ve cesitli tehdit/santaj/zorlama veri ureticisi.
"""

import csv
import random
from pathlib import Path

random.seed(99)

BASE_DIR = Path("/content/dolandirici-mesaj-tespit")
VERI_YOLU = BASE_DIR / "data" / "mesajlar.csv"

TEHDIT_SONUC_FIILLERI = [
    "öldürürüm", "öldürürsün", "ölürsün", "geberirsin", "gebertirim",
    "döverim", "vururum", "keserim", "bıçaklarım", "kan dökerim",
    "kaçırırım", "kaçırılırsın", "zarar veririm", "zarar görürsün",
    "canına kıyarım", "hayatına son veririm", "mahvederim",
    "rezil ederim", "ifşa ederim", "işini bitiririm", "hayatını karartırım",
    "yakarım evini", "paranı çalarım", "seni soyarım", "gasp ederim",
    "başına iş açarım", "pişman olursun", "bedelini ödersin",
    "acı çekersin", "hapse girersin", "polislik olur", "kanun karışır",
    "işini kaybedersin", "ailen zarar görür", "çocuğun tehlikede olur",
    "canını yakarım", "seni ezerim", "kolunu kırarım", "hastanelik ederim",
    "elini kolunu kırarım", "korkunç şeyler olur", "başın belaya girer",
]

KOSUL_KALIPLARI_GENIS = [
    "param gelmezse", "bana gelmezsen", "dediğimi yapmazsan", "vermezsen",
    "yarına kadar ödemezsen", "beni aramazsan", "istediğimi göndermezsen",
    "bu işi bitirmezsen", "cevap vermezsen", "beni engellersen",
    "polise gidersen", "kimseye söylersen", "susmazsan", "itiraz edersen",
    "geri adım atmazsan", "sözümü dinlemezsen", "anlaşmayı bozarsan",
    "borcunu ödemezsen", "toplantıya gelmezsen", "hesabı kapatmazsan",
    "500 tl vermezsen", "1000 tl atmazsan", "yoksa", "aksi halde",
    "aksi takdirde", "yapmazsan eğer", "gelmezsen eğer",
]

CUMLE_KALIPLARI_GENIS = [
    "{kosul}, {fiil}",
    "{fiil}, {kosul}",
    "Sana son kez söylüyorum, {kosul} {fiil}",
    "Bunu ciddiye al: {kosul} {fiil}",
    "Şaka yapmıyorum, {kosul} {fiil}",
    "Dikkatli ol, {kosul} {fiil}",
    "Bak sana söylüyorum {kosul} {fiil}",
    "{fiil}. {kosul} bunu unutma.",
    "Uyarıyorum seni, {kosul} {fiil}",
    "Bu son uyarım, {kosul} {fiil}",
    "İyi düşün, {kosul} {fiil}",
    "Ciddiyim, {kosul} {fiil}",
    "Emin ol {kosul} {fiil}",
    "Görürsün, {kosul} {fiil}",
    "{fiil} eğer {kosul_ham}",
]

KOSUL_HAM_KALIPLARI = [
    "param gelmezse", "bana gelmezsen", "dediğimi yapmazsan",
    "500 tl vermezsen", "susmazsan", "itiraz edersen",
]


def sablon_doldur(kalip):
    return kalip.format(
        kosul=random.choice(KOSUL_KALIPLARI_GENIS),
        fiil=random.choice(TEHDIT_SONUC_FIILLERI),
        kosul_ham=random.choice(KOSUL_HAM_KALIPLARI),
    )


def uret(adet=600):
    satirlar = []
    gorulen = set()
    denenen = 0
    while len(satirlar) < adet and denenen < adet * 15:
        denenen += 1
        kalip = random.choice(CUMLE_KALIPLARI_GENIS)
        mesaj = sablon_doldur(kalip)
        mesaj = mesaj[0].upper() + mesaj[1:]
        if mesaj in gorulen:
            continue
        gorulen.add(mesaj)
        satirlar.append({"mesaj": mesaj, "risk_seviyesi": "yuksek_riskli", "kategori": "dogrudan_tehdit_santaj_genis"})
    return satirlar


yeni_satirlar = uret(600)

with open(VERI_YOLU, "a", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["mesaj", "risk_seviyesi", "kategori"])
    writer.writerows(yeni_satirlar)

print(f"{len(yeni_satirlar)} yeni genis tehdit ornegi eklendi.")

import pandas as pd
df = pd.read_csv(VERI_YOLU)
onceki = len(df)
df = df.drop_duplicates(subset=["mesaj"])
df.to_csv(VERI_YOLU, index=False)
print(f"Toplam veri seti (tekrarsiz): {len(df)} (tekrar temizlendi: {onceki - len(df)})")
print(df["risk_seviyesi"].value_counts())
