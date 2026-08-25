import re

TURKCE_HARF_HARITASI = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i", "I": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
})


def _normalize(metin):
    return metin.translate(TURKCE_HARF_HARITASI).lower()


ACILIYET_KELIMELERI = [
    "hemen", "acil", "son gun", "son dakika", "24 saat", "2 saat",
    "simdi", "gecikmeden", "bugun", "derhal", "kaybetmeyin", "az kaldi",
]

ODUL_KELIMELERI = [
    "kazandiniz", "tebrikler", "odul", "hediye", "cekilis", "ikramiye",
    "ucretsiz", "bedava", "firsat", "indirim", "kupon", "puan kazandiniz",
    "bonus", "hesabinizda kupon", "hesabinizda hediye",
]

TEHDIT_KELIMELERI = [
    "bloke", "kapatilacak", "iptal edilecek", "kesilecek", "yasal islem",
    "borcunuz", "gumrukte", "dogrulama", "sifirlanmistir",
]

FIZIKSEL_SIDDET_KELIMELERI = [
    "oldur", "oldun", "oldururum", "oldurulur", "gebert", "gebertirim",
    "vururum", "keserim", "bicaklarim", "kan dokerim", "doverim",
    "kacirir", "kacirim", "zarar veririm", "zarar gorursun",
    "hayatina son veririm", "canina kiyarim", "mahvederim seni",
]

SANTAJ_TEHDIT_KELIMELERI = [
    "pisman olursun", "basina bir sey gelir", "seni bulurum", "hesabini gorurum",
    "param gelmezse", "atmazsan", "vermezsen", "santaj",
    "tehdit ederim", "hapis", "taciz", "tecavuz", "zorla", "isterse zarar",
    "ifsa ederim", "rezil ederim", "isini bitiririm", "hayatini karartirim",
    "yakarim",
]

GENEL_KOSUL_BAGLACLARI = ["yoksa"]

ZORLAMA_KOSUL_KELIMELERI = [
    "gelmezsen", "yapmazsan", "vermezsen", "aramazsan", "cevap vermezsen",
    "soylemezsen", "gelmez isen", "gelmedigin takdirde", "odemezsen",
    "gelmen lazim", "yapman lazim", "gelmelisin",
]

PARA_TALEBI_KELIMELERI = [
    "tl at", "para at", "para gonder", "havale yap", "eft yap", "gonderir misin",
    "ibana gonder", "hesabima gonder", "tl ver", "para ver", "para isterim",
    "para istiyorum", "para atesle", "atesleyin",
]

KIMLIK_BILGISI_KELIMELERI = [
    "sifre:", "parola:", "şifre:", "hesap:", "kullanici adi:", "kullanıcı adı:",
]

KRIPTO_VARLIK_KELIMELERI = [
    "usdt", "btc", "bitcoin", "kripto", "cuzdan", "wallet", "varliklar",
    "coin", "binance", "aktarmama yardim", "transfer yardim",
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
    r"\b[a-z]{2,6}\d\.com\b",
]

PARA_TALEBI_REGEX = re.compile(
    r"\d+\s*(tl|lira|dolar|euro)\b.{0,15}\b(ver|at|gonder|yolla|istiyorum|isterim|lazim|atesle)"
)

GENEL_PARA_TALEBI_REGEX = re.compile(
    r"\b(biraz|bir miktar|birazcik|acil|az)?\s*para\s*"
    r"(atesle|at|gonder|yolla|ver|isterim|istiyorum|lazim)"
)

TIKLA_ODUL_REGEX = re.compile(
    r"\btikla\b.{0,20}\b(tl|lira|kupon|odul|hediye|bonus)\b|"
    r"\b(tl|lira|kupon|odul|hediye|bonus)\b.{0,20}\btikla\b"
)


def _kelime_sayisi(metin, kelime_listesi):
    metin_normalize = _normalize(metin)
    return sum(1 for kelime in kelime_listesi if kelime in metin_normalize)


def _link_var_mi(metin):
    return bool(re.search(r"http[s]?://|www\.|\.[a-z]{2,4}/", metin.lower()))


def _supheli_link_mi(metin):
    metin_kucuk = metin.lower()
    return any(re.search(kalip, metin_kucuk) for kalip in SUPHELI_DOMAIN_KALIPLARI)


def _zorlama_kalibi_mi(metin):
    metin_normalize = _normalize(metin)
    tehdit_var = any(k in metin_normalize for k in SANTAJ_TEHDIT_KELIMELERI) or any(
        k in metin_normalize for k in FIZIKSEL_SIDDET_KELIMELERI
    )
    if not tehdit_var:
        return False
    kosul_var = any(k in metin_normalize for k in ZORLAMA_KOSUL_KELIMELERI)
    genel_baglac_var = any(k in metin_normalize for k in GENEL_KOSUL_BAGLACLARI)
    return kosul_var or genel_baglac_var


def _para_talebi_regex_mi(metin):
    return bool(PARA_TALEBI_REGEX.search(_normalize(metin)))


def _genel_para_talebi_mi(metin):
    return bool(GENEL_PARA_TALEBI_REGEX.search(_normalize(metin)))


def _tikla_odul_mi(metin):
    return bool(TIKLA_ODUL_REGEX.search(_normalize(metin)))


def ozellik_cikar(metin):
    fiziksel_siddet_skoru = _kelime_sayisi(metin, FIZIKSEL_SIDDET_KELIMELERI)

    santaj_skoru = _kelime_sayisi(metin, SANTAJ_TEHDIT_KELIMELERI)
    if _zorlama_kalibi_mi(metin):
        santaj_skoru += 1

    para_skoru = _kelime_sayisi(metin, PARA_TALEBI_KELIMELERI)
    if _para_talebi_regex_mi(metin):
        para_skoru += 1

    genel_para_talebi = _genel_para_talebi_mi(metin)

    odul_skoru = _kelime_sayisi(metin, ODUL_KELIMELERI)
    tikla_odul = _tikla_odul_mi(metin)

    kimlik_skoru = _kelime_sayisi(metin, KIMLIK_BILGISI_KELIMELERI)
    kripto_skoru = _kelime_sayisi(metin, KRIPTO_VARLIK_KELIMELERI)

    return {
        "aciliyet_skoru": _kelime_sayisi(metin, ACILIYET_KELIMELERI),
        "odul_skoru": odul_skoru,
        "tikla_odul": int(tikla_odul),
        "tehdit_skoru": _kelime_sayisi(metin, TEHDIT_KELIMELERI),
        "fiziksel_siddet_skoru": fiziksel_siddet_skoru,
        "santaj_tehdit_skoru": santaj_skoru,
        "para_talebi_skoru": para_skoru,
        "genel_para_talebi": int(genel_para_talebi),
        "kimlik_bilgisi_skoru": kimlik_skoru,
        "kripto_varlik_skoru": kripto_skoru,
        "resmi_kurum_skoru": _kelime_sayisi(metin, RESMI_KURUM_KELIMELERI),
        "akrabalik_skoru": _kelime_sayisi(metin, AKRABALIK_KELIMELERI),
        "link_var": int(_link_var_mi(metin)),
        "supheli_link": int(_supheli_link_mi(metin)),
        "mesaj_uzunlugu": len(metin),
    }


def acikla(metin):
    nedenler = []
    ozellikler = ozellik_cikar(metin)

    if ozellikler["fiziksel_siddet_skoru"] > 0:
        nedenler.append("Bu mesaj doğrudan fiziksel tehdit içermektedir, derhal polise bildirin.")
        if ozellikler["para_talebi_skoru"] > 0 or ozellikler["genel_para_talebi"]:
            nedenler.append("Ayrica mesaj para/havale talebiyle birlikte geliyor - bu bir santaj/tehdit girisimi olabilir. Hemen 155 Polis Imdat'i arayin.")
    elif ozellikler["santaj_tehdit_skoru"] > 0 and ozellikler["para_talebi_skoru"] > 0:
        nedenler.append("Dogrudan tehdit icerip karsiliginda para talep ediyor - bu bir santaj/tehdit girisimi olabilir. Hemen 155 Polis Imdat'i arayin.")
    elif ozellikler["santaj_tehdit_skoru"] > 0:
        nedenler.append("Mesajda korkutucu, zorlayici veya dogrudan tehdit edici bir dil kullaniliyor. Guvende degilseniz hemen 155 Polis Imdat'i arayin.")

    if ozellikler["kimlik_bilgisi_skoru"] > 0 and (ozellikler["kripto_varlik_skoru"] > 0 or ozellikler["link_var"]):
        nedenler.append("Mesajda acik metin sifre/hesap bilgisi ve kripto varlik/link birlikte geciyor - bu genelde ele gecirilmis bir hesaptan gonderilen dolandiricilik mesajidir. Bu bilgilerle hicbir islem yapmayin.")
    elif ozellikler["kripto_varlik_skoru"] > 0 and ozellikler["link_var"]:
        nedenler.append("Kripto varlik transferi ve supheli bir link birlikte geciyor - bu tur mesajlar genelde dolandiricilik icerir.")

    if ozellikler["tikla_odul"]:
        nedenler.append("'Tıkla' çağrısı bir tutar/kupon/ödül vaadiyle birlikte geliyor - bu klasik bir sahte kupon/ödül tuzağıdır, gerçek kurumlar bu şekilde bildirim yapmaz.")

    if ozellikler["aciliyet_skoru"] > 0:
        nedenler.append("Mesaj sizi aceleye getirmeye calisiyor (ornek: 'hemen', 'son gun').")
    if ozellikler["odul_skoru"] > 0 and not ozellikler["tikla_odul"]:
        nedenler.append("Bir odul, hediye ya da kazanc vaat ediyor - bu klasik bir tuzak yontemidir.")
    if ozellikler["tehdit_skoru"] > 0:
        nedenler.append("Hesabinizin kapatilacagi/bloke edilecegi gibi bir tehdit iceriyor.")
    if ozellikler["supheli_link"]:
        nedenler.append("Icindeki link, resmi kurumlarin kullanmadigi supheli bir adrese benziyor.")
    if ozellikler["akrabalik_skoru"] > 0 and ozellikler["link_var"] == 0:
        nedenler.append("'Yeni numaram', 'telefonum dustu' gibi ifadeler 'torun/yakin tuzagi' dolandiriciliginda sik kullanilir.")
    if ozellikler["resmi_kurum_skoru"] > 0 and ozellikler["supheli_link"]:
        nedenler.append("Resmi bir kurum adi kullaniliyor ama link o kuruma ait gorunmuyor.")
    if ozellikler["para_talebi_skoru"] > 0 and not nedenler:
        nedenler.append("Mesaj dogrudan para/havale talep ediyor - tanimadiginiz ya da supheli bir baglamda geldiyse dikkatli olun.")

    if ozellikler["genel_para_talebi"] and not nedenler:
        nedenler.append(
            "Bu mesaj tanıdığınız birinden gelse bile hesabı çalınmış olabilir. "
            "Para göndermeden önce mutlaka kişiyi sesli arayarak teyit edin."
        )

    if not nedenler:
        nedenler.append("Belirgin bir kural tabanli kalip yakalanmadi.")

    return nedenler
