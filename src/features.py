
"""
Kural tabanli feature cikarma modulu.
Bu modul, mesaj metninden dolandiricilik belirtisi olabilecek
kaliplari (aciliyet, odul vurgusu, supheli link vb.) tespit eder.
NLP modelinden bagimsiz calisir, hem baseline hem de aciklanabilirlik
katmani olarak kullanilir.
"""

import re

ACILIYET_KELIMELERI = [
    "hemen", "acil", "son gun", "son dakika", "24 saat", "2 saat",
    "simdi", "gecikmeden", "bugun", "derhal", "kaybetmeyin", "az kaldi",
]

ODUL_KELIMELERI = [
    "kazandiniz", "tebrikler", "odul", "hediye", "cekilis", "ikramiye",
    "ucretsiz", "bedava", "firsat", "indirim",
]

TEHDIT_KELIMELERI = [
    "bloke", "kapatilacak", "iptal edilecek", "kesilecek", "yasal islem",
    "borcunuz", "gumrukte", "dogrulama", "sifirlanmistir",
]

RESMI_KURUM_KELIMELERI = [
    "bddk", "e-devlet", "edevlet", "gib", "ziraat", "halkbank", "vakifbank",
    "is bankasi", "garanti", "ptt", "kargo",
]

AKRABALIK_KELIMELERI = [
    "anne", "baba", "oglum", "kizim", "torunum", "yeni numaram",
    "telefonum dustu", "telefonum kirildi", "telefonum calindi",
]

SUPHELI_DOMAIN_KALIPLARI = [
    r"bit\.ly", r"tinyurl", r"\.info\b", r"\.xyz\b", r"\.top\b",
    r"-guvenlik\.", r"-odeme\.", r"-tr\.com", r"hizli\.com",
]


def _kelime_sayisi(metin, kelime_listesi):
    metin_kucuk = metin.lower()
    return sum(1 for kelime in kelime_listesi if kelime in metin_kucuk)


def _link_var_mi(metin):
    return bool(re.search(r"http[s]?://|www\.|\.[a-z]{2,4}/", metin.lower()))


def _supheli_link_mi(metin):
    metin_kucuk = metin.lower()
    return any(re.search(kalip, metin_kucuk) for kalip in SUPHELI_DOMAIN_KALIPLARI)


def ozellik_cikar(metin):
    """Bir mesaj metninden kural tabanli ozellikleri sozluk olarak dondurur."""
    return {
        "aciliyet_skoru": _kelime_sayisi(metin, ACILIYET_KELIMELERI),
        "odul_skoru": _kelime_sayisi(metin, ODUL_KELIMELERI),
        "tehdit_skoru": _kelime_sayisi(metin, TEHDIT_KELIMELERI),
        "resmi_kurum_skoru": _kelime_sayisi(metin, RESMI_KURUM_KELIMELERI),
        "akrabalik_skoru": _kelime_sayisi(metin, AKRABALIK_KELIMELERI),
        "link_var": int(_link_var_mi(metin)),
        "supheli_link": int(_supheli_link_mi(metin)),
        "mesaj_uzunlugu": len(metin),
    }


def acikla(metin):
    """Kullaniciya gosterilecek sade dilde uyari nedenlerini dondurur."""
    nedenler = []
    ozellikler = ozellik_cikar(metin)

    if ozellikler["aciliyet_skoru"] > 0:
        nedenler.append("Mesaj sizi aceleye getirmeye calisiyor (ornek: \'hemen\', \'son gun\').")
    if ozellikler["odul_skoru"] > 0:
        nedenler.append("Bir odul, hediye ya da kazanc vaat ediyor - bu klasik bir tuzak yontemidir.")
    if ozellikler["tehdit_skoru"] > 0:
        nedenler.append("Hesabinizin kapatilacagi/bloke edilecegi gibi bir tehdit iceriyor.")
    if ozellikler["supheli_link"]:
        nedenler.append("Icindeki link, resmi kurumlarin kullanmadigi supheli bir adrese benziyor.")
    if ozellikler["akrabalik_skoru"] > 0 and ozellikler["link_var"] == 0:
        nedenler.append("\'Yeni numaram\', \'telefonum dustu\' gibi ifadeler \'torun/yakin tuzagi\' dolandiriciliginda sik kullanilir.")
    if ozellikler["resmi_kurum_skoru"] > 0 and ozellikler["supheli_link"]:
        nedenler.append("Resmi bir kurum adi kullaniliyor ama link o kuruma ait gorunmuyor.")

    if not nedenler:
        nedenler.append("Belirgin bir dolandiricilik kalibi tespit edilmedi, ancak yine de dikkatli olun.")

    return nedenler
