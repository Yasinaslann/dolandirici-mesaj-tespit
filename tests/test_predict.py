# ... indirdiğin dosyanın tüm içeriğini buraya yapıştır ...
"""
Otomatik regresyon testleri.

Bu dosya, gelistirme surecinde elle tek tek test ettigimiz senaryolari
kalici hale getirir, artik cok daha genis kapsamli. 17 farkli dolandiricilik
kategorisinden ornekler + cesitli masum mesajlar iceriyor.

Calistirmak icin:
    pytest tests/test_predict.py -v
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest
from src.predict import tahmin_et, load_model


@pytest.fixture(scope="module")
def model_ve_tokenizer():
    tokenizer, model = load_model()
    return tokenizer, model


# ---------------------------------------------------------------------------
# EL YAZIMI, GERCEK DUNYADAN OGRENILEN KENAR DURUMLAR
# (bu ornekler, gelistirme surecinde bulunan gercek hatalardan geliyor)
# ---------------------------------------------------------------------------

OZEL_YUKSEK_RISKLI_MESAJLAR = [
    "bana 500 tl ver yoksa öldürürüm seni",
    "yarın bana gelmen lazım yoksa öldün",
    "seni taciz ederim bana gelmezsen",
    "Kargonuz gümrükte bekliyor, vergi ödemesi için tıklayın: bit.ly/odeme-hizli",
    "Anne benim, telefonum düştü, yeni numaram bu, acil param lazım",
    "Deniz Hesap: Kce0150 Şifre: adam1986@ URL: bur7.com Varlıklar: 2150153.61 USDT",
]


OZEL_GUVENLI_MESAJLAR = [
    "yarın saat 3'te buluşalım mı kahve içmeye",
    "yarın saat 3'te buluşalım mı kahve içmeye, yoksa başka gün mü uygun",
    "Kızım yarın doktora gideceğiz saat kaçta müsaitsin",
    "Faturanız hazır, bu ay 245 TL",
    "Bu bir dolandırıcı mesajıdır",
]


OZEL_SUPHELI_MESAJLAR = [
    "bir miktar para ateşleyin",
    "tıkla 100 tl kupon hesabında",
]


@pytest.mark.parametrize("mesaj", OZEL_YUKSEK_RISKLI_MESAJLAR)
def test_ozel_yuksek_riskli(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "yuksek_riskli", (
        f"Beklenen: yuksek_riskli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


@pytest.mark.parametrize("mesaj", OZEL_GUVENLI_MESAJLAR)
def test_ozel_guvenli(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "guvenli", (
        f"Beklenen: guvenli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


@pytest.mark.parametrize("mesaj", OZEL_SUPHELI_MESAJLAR)
def test_ozel_supheli(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    # supheli VEYA yuksek_riskli kabul ediyoruz - model daha temkinli
    # davranip yuksek_riskli derse bu bir hata degil, aksine daha guvenli.
    assert sonuc["risk_seviyesi"] in ("supheli", "yuksek_riskli"), (
        f"Beklenen: supheli/yuksek_riskli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )


def test_fiziksel_tehdit_polis_uyarisi_iceriyor(model_ve_tokenizer):
    """Fiziksel tehdit iceren mesajlarda polis cagrisi mutlaka olmali."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("bana 500 tl ver yoksa öldürürüm seni", tokenizer, model)
    tum_nedenler = " ".join(sonuc["nedenler"])
    assert "polis" in tum_nedenler.lower() or "155" in tum_nedenler


def test_bos_mesaj_belirsiz_doner(model_ve_tokenizer):
    """Bos metin gonderilirse sistem cokmemeli, 'belirsiz' donmeli."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("", tokenizer, model)
    assert sonuc["risk_seviyesi"] == "belirsiz"


def test_turkce_karakter_normalizasyonu_calisiyor(model_ve_tokenizer):
    """Turkce ozel karakterlerle yazilan tehdit de yakalanmali."""
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et("seni öldürürüm çünkü söylemedin", tokenizer, model)
    assert sonuc["risk_seviyesi"] == "yuksek_riskli"


# ---------------------------------------------------------------------------
# GENIS KAPSAMLI KATEGORI TESTLERI
# 17 farkli dolandiricilik kategorisinden ornekler + coklu masum mesaj.
# Bu ornekler generate_dataset.py sablonlarindan sabit bir tohumla (seed=123)
# uretildi, boylece her calistirmada ayni kalirlar.
# ---------------------------------------------------------------------------

KATEGORI_ORNEKLERI = [
    ("Trendyol Express: Kargonuz teslim edilemedi, adres bilgilerinizi 6 saat icinde guncelleyin: hesap-guncelle.xyz", "yuksek_riskli"),  # kargo
    ("Aras Kargo: Adresinizde kimse bulunamadi, teslimat bilgisini 6 saat icinde guncelleyin: banka-guvenlik-merkez.com", "yuksek_riskli"),  # kargo
    ("PTT Kargo bildirimi: 1 paketiniz var ancak adresiniz dogrulanamadi, onaylamak icin tiklayin: odul-teslimat.xyz", "yuksek_riskli"),  # kargo
    ("Dikkat! Denizbank hesabiniz kisitlandi, kisitlamayi kaldirmak icin bilgilerinizi giriniz: kargo-takip-tr.info", "yuksek_riskli"),  # banka
    ("Akbank musteri temsilcisiyim, hesabinizi guvenceye almak icin size gelen kodu soyler misiniz", "yuksek_riskli"),  # banka
    ("Ziraat Bankasi: Hesabinizda 2.750 TL tutarinda supheli bir islem tespit edildi, onaylamiyorsaniz hemen tiklayin: sistem-guncelleme.info", "yuksek_riskli"),  # banka
    ("anneanne merhaba, is yerinde telefonumu kaybettim, gecici numaradan yaziyorum, param bitti ihtiyacim var", "yuksek_riskli"),  # torun_tuzagi
    ("anne, telefonum kayboldu, yeni hat aldim. Bir sikinti var, hemen 50.000 TL gonderir misin, sonra anlatirim", "yuksek_riskli"),  # torun_tuzagi
    ("Merhaba amca, telefonum dustu kirildi, bu numaradan yaziyorum. Acil param lazim, IBAN'a havale yapar misin?", "yuksek_riskli"),  # torun_tuzagi
    ("Uzlasma dosyaniz burumuza devredilmistir, odeme yapilmazsa dosyaniz icra takibine donusturulecektir: hesap-guncelle.xyz", "yuksek_riskli"),  # dava_icra
    ("Isim soyisminizle kayitli bir dosya tespit edildi, 50.000 TL odeme yapilmazsa aleyhinize dava acilacaktir", "yuksek_riskli"),  # dava_icra
    ("Hakkinizda sikayet basvurusu bulunmaktadir, dosyaniz icin avukatimizla iletisime geciniz", "yuksek_riskli"),  # dava_icra
    ("Sistem: 486387 dogrulama kodunuzdur. Bu kodu kimseyle paylasmayin.", "supheli"),  # otp_kod
    ("Hesabiniza giris denemesi oldu, size gonderilen dogrulama kodunu bize iletirseniz erisimi kapatabiliriz", "supheli"),  # otp_kod
    ("Az once size gonderdigimiz 6 haneli guvenlik kodunu telefonda bana iletir misiniz", "supheli"),  # otp_kod
    ("Trafik cezaniz bulunmaktadir, itiraz etmezseniz ceza kesinlesecektir, detaylar: odul-teslimat.xyz", "yuksek_riskli"),  # resmi_kurum_taklidi
    ("E-Devlet sifreniz sifirlanmistir, yeni sifre almak icin linke tiklayiniz: hesap-dogrula-hizli.net", "yuksek_riskli"),  # resmi_kurum_taklidi
    ("Nufus mudurlugu: Kimlik bilgilerinizde hata tespit edildi, dogrulama icin tiklayiniz: resmi-dogrulama.net", "yuksek_riskli"),  # resmi_kurum_taklidi
    ("Yilbasi cekilisinde 3.200 TL kazandiniz, odemeniz icin banka bilgilerinizi giriniz: odul-teslimat.xyz", "yuksek_riskli"),  # sahte_odul
    ("Uyelik yenileme cekilisinde siz de kazandiniz, hemen bilgilerinizi dogrulayin: resmi-dogrulama.net", "yuksek_riskli"),  # sahte_odul
    ("Ucretsiz bir hediye ceki kazandiniz! Hediyenizi almak icin tiklayin: teslimat-onay.info", "yuksek_riskli"),  # sahte_odul
    ("Kripto yatirimla 1 haftada 3 kat kazanc! Simdi katil, yerler sinirli: bit.ly/hzl-odeme", "yuksek_riskli"),  # sahte_yatirim
    ("Dijital paraya yatirim yapip 1 ayda 2 katina cikarin, sinirli kontenjan: hesap-dogrula-hizli.net", "yuksek_riskli"),  # sahte_yatirim
    ("Uzman ekibimizle borsada garantili kazanc firsati, detaylar icin whatsapptan yazin", "yuksek_riskli"),  # sahte_yatirim
    ("Gunde 10.000 TL kazanin, sadece begeni yaparak gelir elde edin, detaylar icin yazin", "yuksek_riskli"),  # sahte_is
    ("Is basvurunuz onaylandi, gunluk 3.200 TL kazanabilirsiniz. Detaylar icin WhatsApp'tan yazin", "yuksek_riskli"),  # sahte_is
    ("Ek gelir arayanlara ozel, kolay is firsati, basvuru icin telegram grubuna katilin", "yuksek_riskli"),  # sahte_is
    ("Magazamiza 5 yildiz verirseniz size 2.750 TL odeme yapiyoruz, katilmak icin whatsapptan yazin", "yuksek_riskli"),  # gorev_dolandiriciligi
    ("Basit gorevler karsiligi gunluk kazanc firsati, ilk gorev icin telegram grubumuza katilin", "yuksek_riskli"),  # gorev_dolandiriciligi
    ("Video izleyerek para kazanin, ilk gorev icin IBAN bilgisi girmeniz gerekiyor", "yuksek_riskli"),  # gorev_dolandiriciligi
    ("Su faturaniz odenmedi, 24 saat icinde odenmezse suyunuz kesilecektir: guvenlik-dogrula.net", "yuksek_riskli"),  # fatura_dolandiriciligi
    ("Fatura borcunuzu odemediginiz icin elektroginiz kesilecek. 3 gun icinde odeyin: hesap-dogrula-hizli.net", "yuksek_riskli"),  # fatura_dolandiriciligi
    ("Dogalgaz faturanizda gecikme var, kesinti yasanmamasi icin hemen odeyin: banka-guvenlik-merkez.com", "yuksek_riskli"),  # fatura_dolandiriciligi
    ("Ozel musterilerimize ozel %70 indirim firsati, stoklar tukenmeden aliniz", "supheli"),  # sahte_kampanya
    ("Sadece bugun gecerli firsat, kacirmayin, hemen tiklayin: resmi-dogrulama.net", "supheli"),  # sahte_kampanya
    ("Yeni sezon urunlerimizde bugune ozel indirim var, kacirmayin: hesap-guncelle.xyz", "supheli"),  # sahte_kampanya
    ("Hesabiniz iptal edilme riski tasiyor, bilgilerinizi guncellemek icin tiklayiniz: hesap-guncelle.xyz", "yuksek_riskli"),  # phishing_genel
    ("Guvenlik nedeniyle sifrenizi yenilemeniz gerekiyor, link uzerinden islem yapiniz: kargo-takip-tr.info", "yuksek_riskli"),  # phishing_genel
    ("Kullaniciliginiz olusturuldugunu fark ettik, uyelik islemlerinizi tamamlamak icin tiklayin: guvenlik-dogrula.net", "yuksek_riskli"),  # phishing_genel
    ("Ilaniniza ilgi gosterdim, urunu almak istiyorum, once kargo ucretini gondermeniz gerekiyor", "yuksek_riskli"),  # sahte_ilan
    ("Urunle ilgileniyorum ama sehir disindayim, kargo ile gonderirseniz odemeyi sonra yaparim", "yuksek_riskli"),  # sahte_ilan
    ("Araciniz begendim, once bir miktar depozito atarsam yerinizi tutar misiniz", "yuksek_riskli"),  # sahte_ilan
    ("Merhaba, seninle tanismaktan mutluluk duydum, Turkiye'ye gelmek istiyorum ama vize param yok, yardim eder misin", "yuksek_riskli"),  # romantik_dolandiricilik
    ("Seni cok sevdim, ama su an zor durumdayim, 50.000 TL kucuk bir yardima ihtiyacim var", "yuksek_riskli"),  # romantik_dolandiricilik
    ("Askerdeyim, izin param cikmadi, bana 5.000 TL gonderir misin, seninle evlenmek istiyorum", "yuksek_riskli"),  # romantik_dolandiricilik
    ("Bilgisayariniz virus kapladi, uzaktan yardim icin bu baglantiyi indirip calistirin: teslimat-onay.info", "yuksek_riskli"),  # uzaktan_erisim
    ("Teknik destek ekibiyiz, sorununuzu cozmek icin ekran paylasim linkine tiklayin: banka-guvenlik-merkez.com", "yuksek_riskli"),  # uzaktan_erisim
    ("Telefonunuzda bir sorun tespit ettik, uzaktan mudahale icin bu linke tiklayip erisim verin: hesap-guncelle.xyz", "yuksek_riskli"),  # uzaktan_erisim
    ("Merhaba, aramizda ortak arkadasimiz var, sohbet etmek ister misin diye yazdim", "supheli"),  # sosyal_muhendislik
    ("Seninle tanismak isterim, whatsapp numarani alabilir miyim", "supheli"),  # sosyal_muhendislik
    ("Fotografini begendim, bu linkten profiline bakabilirsin: banka-guvenlik-merkez.com", "supheli"),  # sosyal_muhendislik
]


@pytest.mark.parametrize("mesaj,beklenen_risk", KATEGORI_ORNEKLERI)
def test_kategori_ornekleri(model_ve_tokenizer, mesaj, beklenen_risk):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    # supheli/yuksek_riskli arasinda kucuk sapmalara tolerans taniyoruz -
    # asil onemli olan mesajin "guvenli" CIKMAMASI
    assert sonuc["risk_seviyesi"] != "guvenli", (
        f"Bu riskli bir mesaj guvenli olarak isaretlendi! | Mesaj: {mesaj}"
    )


GENIS_GUVENLI_ORNEKLER = [
    "Yarin sabah spor yapmaya gidecegim, sen de gelir misin",
    "Bankamatikten para cektim, evdeyim artik",
    "Isyerinde toplanti uzadi, biraz gec kalabilirim",
    "Doktor randevunuz cuma saat 18:30 icin onaylanmistir.",
    "Yeni komsularimiz tasindi, hosgeldin ziyaretine gidelim mi",
    "Kredi karti ekstreniz hazirlanmistir, detaylar icin bankaniz mobil uygulamasini kullanabilirsiniz",
    "Bugun hava cok guzel, bahceye cikalim mi",
    "Dogum gunun kutlu olsun, seni cok seviyoruz",
        "Faturaniz hazir, bu ay 185 TL. Detaylar icin uygulamayi kullanabilirsiniz.",
    "Bu haftaki alisveris listesini cikardim, ekleyecegin bir sey var mi",
    "Bu hafta sonu ailece pikniğe gidelim mi",
    "Bu aksam misafirimiz var, saat 18:30 gelecekler",
    "Arabanin bakim zamani geldi, servise goturmemiz lazim",
    "Merhaba, siparisiniz kargoya verildi, takip numaraniz: TR925324768, resmi uygulamadan takip edebilirsiniz",
    "Yarinki doktor randevusunu unutma",
    "Kredi karti odemesini yaptim, ekstreyi kontrol edebilirsin",
    "Yarin hava yagmurlu gorunuyor, semsiyeni almayi unutma",
    "Hafta sonu sinemaya gidelim mi, yeni bir film cikmis",
    "Yarin sabah erken kalkmamiz lazim, uyandirir misin",
    "Ailece hafta sonu koye gidelim mi, hava da guzel olacakmis",
    "Kredi karti limitim arttirildi, bankadan mesaj geldi",
    "Telefon rehberine yeni numaramı kaydeder misin",
    "Tatil icin otel rezervasyonunu yaptim, detaylari mail attim",
    "Telefon faturasi bu ay biraz yuksek gelmis, kontrol edelim",
]


@pytest.mark.parametrize("mesaj", GENIS_GUVENLI_ORNEKLER)
def test_genis_guvenli_ornekler(model_ve_tokenizer, mesaj):
    tokenizer, model = model_ve_tokenizer
    sonuc = tahmin_et(mesaj, tokenizer, model)
    assert sonuc["risk_seviyesi"] == "guvenli", (
        f"Beklenen: guvenli, Gelen: {sonuc['risk_seviyesi']} | Mesaj: {mesaj}"
    )
