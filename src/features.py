
"""
Kural tabanli feature cikarma modulu.
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

SANTAJ_TEHDIT_KELIMELERI = [
    "kacirir", "kacirim", "zarar veririm", "zarar gorursun", "pisman olursun",
    "basina bir sey gelir", "seni bulurum", "hesabini gorurum", "yoksa gorursun",
    "param gelmezse", "atmazsan", "vermezsen",
]

PARA_TALEBI_KELIMELERI = [
    "tl at", "para at", "para gonder", "havale yap", "eft yap", "gonderir misin",
    "ibana gonder", "hesabima gonder",
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
    return {
        "aciliyet_skoru": _kelime_sayisi(metin, ACILIYET_KELIMELERI),
        "odul_skoru": _kelime_sayisi(metin, ODUL_KELIMELERI),
        "tehdit_skoru": _kelime_sayisi(metin, TEHDIT_KELIMELERI),
        "santaj_tehdit_skoru": _kelime_sayisi(metin, SANTAJ_TEHDIT_KELIMELERI),
        "para_talebi_skoru": _kelime_sayisi(metin, PARA_TALEBI_KELIMELERI),
        "resmi_kurum_skoru": _kelime_sayisi(metin, RESMI_KURUM_KELIMELERI),
        "akrabalik_skoru": _kelime_sayisi(metin, AKRABALIK_KELIMELERI),
        "link_var": int(_link_var_mi(metin)),
        "supheli_link": int(_supheli_link_mi(metin)),
        "mesaj_uzunlugu": len(metin),
    }


def acikla(metin):
    nedenler = []
    ozellikler = ozellik_cikar(metin)

    if ozellikler["santaj_tehdit_skoru"] > 0 and ozellikler["para_talebi_skoru"] > 0:
        nedenler.append("Dogrudan tehdit icerip karsiliginda para talep ediyor - bu bir santaj/tehdit girisimi olabilir. Hemen 155 Polis Imdat'i arayin.")
    elif ozellikler["santaj_tehdit_skoru"] > 0:
        nedenler.append("Mesajda korkutucu/tehdit edici bir dil kullaniliyor.")
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
    if ozellikler["para_talebi_skoru"] > 0 and not nedenler:
        nedenler.append("Mesaj dogrudan para/havale talep ediyor - tanimadiginiz ya da supheli bir baglamda geldiyse dikkatli olun.")

    if not nedenler:
        nedenler.append("Belirgin bir kural tabanli kalip yakalanmadi.")

    return nedenler
