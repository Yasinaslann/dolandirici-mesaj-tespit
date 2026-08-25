"""
Sablon tabanli veri artirma (data augmentation) scripti.
Her kategori icin bir kalip cumle + degisken kelime listeleri tanimlanir,
kombinasyonlarla binlerce cesitli ama gercekci ornek uretilir.
"""

import csv
import random
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
CIKTI_YOLU = BASE_DIR / "data" / "mesajlar.csv"

KARGO_FIRMALARI = ["PTT Kargo", "Aras Kargo", "Yurtici Kargo", "MNG Kargo", "Surat Kargo", "UPS", "Trendyol Express"]
BANKA_ISIMLERI = ["Ziraat Bankasi", "Garanti BBVA", "Is Bankasi", "Halkbank", "Vakifbank", "Akbank", "Yapi Kredi", "Denizbank"]
SURELER = ["2 saat", "24 saat", "6 saat", "12 saat", "1 gun", "3 gun", "bugun"]
SUPHELI_LINKLER = [
    "kargo-takip-tr.info", "hesap-guncelle.xyz", "bit.ly/hzl-odeme", "guvenlik-dogrula.net",
    "odeme-sistem-tr.com", "teslimat-onay.info", "hesap-dogrula-hizli.net", "kargo-bedel.xyz",
    "banka-guvenlik-merkez.com", "resmi-dogrulama.net", "sistem-guncelleme.info", "odul-teslimat.xyz",
]
TUTARLAR = ["1.500 TL", "2.750 TL", "5.000 TL", "10.000 TL", "25.000 TL", "50.000 TL", "3.200 TL"]
YAKINLIK_ISIMLERI = ["anne", "baba", "anneciğim", "babacığım", "dede", "anneanne", "teyze", "amca"]
IS_TEKLIFI_TUTARLARI = ["500 TL", "750 TL", "1000 TL", "1500 TL", "2000 TL"]
ODUL_ESYALARI = ["iPhone 15", "50.000 TL nakit", "araba", "tatil paketi", "akilli saat", "laptop"]

SABLONLAR = {
    "kargo": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "{firma}: Kargonuz teslim edilemedi, adres bilgilerinizi {sure} icinde guncelleyin: {link}",
            "{firma}: Paketiniz gumrukte bekliyor, vergi odemesi icin tiklayin: {link}",
            "{firma}: Adresinizde kimse bulunamadi, teslimat bilgisini {sure} icinde guncelleyin: {link}",
            "{firma}: Kargonuz depoda bekletiliyor, dogrulama yapilmazsa iade edilecektir: {link}",
            "{firma}: Siparisiniz icin ek nakliye bedeli odenmesi gerekiyor, {sure} icinde odenmezse iade edilecek: {link}",
            "{firma} bildirimi: 1 paketiniz var ancak adresiniz dogrulanamadi, onaylamak icin tiklayin: {link}",
        ],
    },
    "banka": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "{banka}: Hesabinizda supheli islem tespit edildi, {sure} icinde dogrulamazsaniz hesabiniz bloke edilecektir: {link}",
            "{banka} Guvenlik: Hesabiniz gecici olarak bloke edilmistir, hemen dogrulayin: {link}",
            "{banka}: Kredi karti isleminiz onaylanmadi, kart bilgilerinizi tekrar giriniz: {link}",
            "Dikkat! {banka} hesabiniz kisitlandi, kisitlamayi kaldirmak icin bilgilerinizi giriniz: {link}",
            "{banka} musteri temsilcisiyim, hesabinizi guvenceye almak icin size gelen kodu soyler misiniz",
            "{banka}: Hesabinizda {tutar} tutarinda supheli bir islem tespit edildi, onaylamiyorsaniz hemen tiklayin: {link}",
        ],
    },
    "torun_tuzagi": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Merhaba {yakin}, telefonum dustu kirildi, bu numaradan yaziyorum. Acil param lazim, IBAN'a havale yapar misin?",
            "{yakin} benim, yeni numaram bu, eski telefonum calindi. Sana bir sey soracaktim, musait misin?",
            "{yakin}cigim ben, telefonum suya dustu, gecici numaradan yaziyorum. Bana {tutar} gonderebilir misin, cok acil",
            "{yakin}, telefonum kayboldu, yeni hat aldim. Bir sikinti var, hemen {tutar} gonderir misin, sonra anlatirim",
            "{yakin} merhaba, is yerinde telefonumu kaybettim, gecici numaradan yaziyorum, param bitti ihtiyacim var",
        ],
    },
    "dava_icra": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Hakkinizda icra takibi baslatilmistir, {sure} icinde odeme yapilmazsa haciz islemi uygulanacaktir: {link}",
            "Ceza dosyaniz hukuk burosuna devredilmistir, {sure} icinde odeme yapilmazsa yasal islem baslatilacaktir",
            "Uzlasma dosyaniz burumuza devredilmistir, odeme yapilmazsa dosyaniz icra takibine donusturulecektir: {link}",
            "Mahkeme karari geregi hakkinizda {sure} icinde islem uygulanacaktir, detaylar icin arayiniz",
            "Hakkinizda sikayet basvurusu bulunmaktadir, dosyaniz icin avukatimizla iletisime geciniz",
            "Isim soyisminizle kayitli bir dosya tespit edildi, {tutar} odeme yapilmazsa aleyhinize dava acilacaktir",
        ],
    },
    "otp_kod": {
        "risk": "supheli",
        "kaliplar": [
            "Sistem: {kod} dogrulama kodunuzdur. Bu kodu kimseyle paylasmayin.",
            "Bankamiz musteri temsilcisiyim, hesabinizi guvenceye almak icin size gelen kodu soyler misiniz",
            "Az once size gonderdigimiz 6 haneli guvenlik kodunu telefonda bana iletir misiniz",
            "Kart dogrulama islemi icin sms ile gelen kodu paylasmaniz gerekiyor, hemen iletir misiniz",
            "Hesabiniza giris denemesi oldu, size gonderilen dogrulama kodunu bize iletirseniz erisimi kapatabiliriz",
        ],
    },
    "resmi_kurum_taklidi": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Vergi borcunuz bulunmaktadir, {sure} icinde odeme yapilmazsa yasal islem baslatilacaktir: {link}",
            "E-Devlet sifreniz sifirlanmistir, yeni sifre almak icin linke tiklayiniz: {link}",
            "SGK sisteminde kaydiniz guncellenmemistir, hemen giris yapin: {link}",
            "Nufus mudurlugu: Kimlik bilgilerinizde hata tespit edildi, dogrulama icin tiklayiniz: {link}",
            "Trafik cezaniz bulunmaktadir, itiraz etmezseniz ceza kesinlesecektir, detaylar: {link}",
        ],
    },
    "sahte_odul": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Tebrikler! {odul} kazandiniz. Odulunuzu almak icin bilgilerinizi girin: {link}",
            "Numaraniz cekilise secildi, {odul} kazandiniz, teslimat icin adres bilgisi gonderin",
            "Ucretsiz bir hediye ceki kazandiniz! Hediyenizi almak icin tiklayin: {link}",
            "Yilbasi cekilisinde {tutar} kazandiniz, odemeniz icin banka bilgilerinizi giriniz: {link}",
            "Uyelik yenileme cekilisinde siz de kazandiniz, hemen bilgilerinizi dogrulayin: {link}",
        ],
    },
    "sahte_yatirim": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Kripto yatirimla 1 haftada 3 kat kazanc! Simdi katil, yerler sinirli: {link}",
            "Uzman ekibimizle borsada garantili kazanc firsati, detaylar icin whatsapptan yazin",
            "Yatirim danismaniniz olarak size ozel gunluk %5 kazanc firsati sunuyoruz, hemen katilin",
            "Dijital paraya yatirim yapip 1 ayda 2 katina cikarin, sinirli kontenjan: {link}",
            "Borsa robotu ile otomatik kazanc, hicbir risk yok, hemen kayit olun: {link}",
        ],
    },
    "sahte_is": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Is basvurunuz onaylandi, gunluk {tutar} kazanabilirsiniz. Detaylar icin WhatsApp'tan yazin",
            "Evden calisma firsati! Gunde 2 saat calisip {tutar} kazanin, basvuru icin tiklayin: {link}",
            "Gunde {tutar} kazanin, sadece begeni yaparak gelir elde edin, detaylar icin yazin",
            "Ek gelir arayanlara ozel, kolay is firsati, basvuru icin telegram grubuna katilin",
        ],
    },
    "gorev_dolandiriciligi": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Magazamiza 5 yildiz verirseniz size {tutar} odeme yapiyoruz, katilmak icin whatsapptan yazin",
            "Basit gorevler karsiligi gunluk kazanc firsati, ilk gorev icin telegram grubumuza katilin",
            "Urun begenip yildiz vermeniz karsiliginda odeme yapiyoruz, detaylar icin mesaj atin",
            "Video izleyerek para kazanin, ilk gorev icin IBAN bilgisi girmeniz gerekiyor",
        ],
    },
    "fatura_dolandiriciligi": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Fatura borcunuzu odemediginiz icin elektroginiz kesilecek. {sure} icinde odeyin: {link}",
            "Su faturaniz odenmedi, {sure} icinde odenmezse suyunuz kesilecektir: {link}",
            "Dogalgaz faturanizda gecikme var, kesinti yasanmamasi icin hemen odeyin: {link}",
            "Internet faturaniz odenmedi, hizmetiniz durdurulacak, hemen odeme yapin: {link}",
        ],
    },
    "sahte_kampanya": {
        "risk": "supheli",
        "kaliplar": [
            "Az kaldi! Kampanyamiz sadece bugun gecerli, hemen tiklayip kaydolun: {link}",
            "Sayin uyemiz, uyelik puanlariniz sona ermek uzere, hemen kullanin: {link}",
            "Yeni sezon urunlerimizde bugune ozel indirim var, kacirmayin: {link}",
            "Ozel musterilerimize ozel %70 indirim firsati, stoklar tukenmeden aliniz",
            "Sadece bugun gecerli firsat, kacirmayin, hemen tiklayin: {link}",
        ],
    },
    "phishing_genel": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Kullaniciliginiz olusturuldugunu fark ettik, uyelik islemlerinizi tamamlamak icin tiklayin: {link}",
            "Hesabiniz iptal edilme riski tasiyor, bilgilerinizi guncellemek icin tiklayiniz: {link}",
            "Sisteme giris yapamadiginiz icin hesabiniz askiya alindi, aktiflestirmek icin linke tiklayin: {link}",
            "Guvenlik nedeniyle sifrenizi yenilemeniz gerekiyor, link uzerinden islem yapiniz: {link}",
        ],
    },
    "sahte_ilan": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Ilaniniza ilgi gosterdim, urunu almak istiyorum, once kargo ucretini gondermeniz gerekiyor",
            "Merhaba, ilaniniz cok ilgimi cekti, hemen almak istiyorum, kapora olarak {tutar} gonderir misiniz",
            "Urunle ilgileniyorum ama sehir disindayim, kargo ile gonderirseniz odemeyi sonra yaparim",
            "Araciniz begendim, once bir miktar depozito atarsam yerinizi tutar misiniz",
        ],
    },
    "romantik_dolandiricilik": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Merhaba, seninle tanismaktan mutluluk duydum, Turkiye'ye gelmek istiyorum ama vize param yok, yardim eder misin",
            "Seni cok sevdim, ama su an zor durumdayim, {tutar} kucuk bir yardima ihtiyacim var",
            "Askerdeyim, izin param cikmadi, bana {tutar} gonderir misin, seninle evlenmek istiyorum",
        ],
    },
    "uzaktan_erisim": {
        "risk": "yuksek_riskli",
        "kaliplar": [
            "Bilgisayariniz virus kapladi, uzaktan yardim icin bu baglantiyi indirip calistirin: {link}",
            "Telefonunuzda bir sorun tespit ettik, uzaktan mudahale icin bu linke tiklayip erisim verin: {link}",
            "Teknik destek ekibiyiz, sorununuzu cozmek icin ekran paylasim linkine tiklayin: {link}",
        ],
    },
    "sosyal_muhendislik": {
        "risk": "supheli",
        "kaliplar": [
            "Merhaba, aramizda ortak arkadasimiz var, sohbet etmek ister misin diye yazdim",
            "Seninle tanismak isterim, whatsapp numarani alabilir miyim",
            "Fotografini begendim, bu linkten profiline bakabilirsin: {link}",
        ],
    },
}

GUVENLI_KALIPLAR = [
    "Selam, {saat} bulusalim mi kahve icmeye?",
    "Yarinki toplantiyi {saat} alabilir miyiz, musait misin?",
    "{yakin} bugun eve gec gelecegim, yemek yeme beni bekleme",
    "Faturaniz hazir, bu ay {tutar_kucuk}. Detaylar icin uygulamayi kullanabilirsiniz.",
    "Merhaba, siparisiniz kargoya verildi, takip numaraniz: {takip_no}, resmi uygulamadan takip edebilirsiniz",
    "Doktor randevunuz {gun} saat {saat} icin onaylanmistir.",
    "Iyi aksamlar, yarin market alisverisi yapacagim, bir seye ihtiyacin var mi?",
    "Okul toplantisi bu {gun} saat {saat} yapilacaktir, katiliminizi rica ederiz",
    "Kredi karti ekstreniz hazirlanmistir, detaylar icin bankaniz mobil uygulamasini kullanabilirsiniz",
    "Merhaba, komsu, asagida bir kargonuz var, teslim aldim, ne zaman musaitsin alalim",
    "Dogum gunun kutlu olsun, seni cok seviyoruz",
    "Toplanti notlarini mail attim, kontrol edebilir misin",
    "Yarin hava yagmurlu gorunuyor, semsiyeni almayi unutma",
    "{yakin}, randevunuzu {gun} gunune erteledik, uygun mu",
    "Bu hafta sonu ailece pikniğe gidelim mi",
    "Kitabini geri getirmeyi unutma lutfen",
    "Yarin okula kac numarali otobusle gelecegim",
    "Aksam yemegi icin ne pisirelim, fikrin var mi",
    "Sinav sonuclari aciklandi, kontrol eder misin",
    "Bugun hava cok guzel, bahceye cikalim mi",
    "Toplanti saati degisti, {saat} oldu",
    "Eczaneden ilacimi alabilir misin, receteyi masaya biraktim",
    "Yarin misafirlerimiz gelecek, evi biraz toplayalim",
    "Telefon faturasi bu ay biraz yuksek gelmis, kontrol edelim",
    "Cocuklarin okul kayit islemleri tamamlandi, tesekkurler",
    "Hafta sonu sinemaya gidelim mi, yeni bir film cikmis",
    "Isyerinde bugun yogunum, aksam gec donebilirim",
    "Bankamatikten para cektim, evdeyim artik",
    "Yarinki doktor randevusunu unutma",
    "Market listesini hazirladim, cikarken alalim",
    "Komsu cocuk bugun bize gelip oynayacak",
    "Bu ay elektrik faturasi normal gorunuyor",
    "Ailece bayram icin planimiz ne olacak konusalim",
    "Yeni telefon numaramı kaydet, eski hattim iptal oluyor",
    "Tatil icin otel rezervasyonunu yaptim, detaylari mail attim",
    "Bu haftaki alisveris listesini cikardim, ekleyecegin bir sey var mi",
    "Yarin sabah erken kalkmamiz lazim, uyandirir misin",
    "Kredi karti odemesini yaptim, ekstreyi kontrol edebilirsin",
    "Yeni is yerimde ilk haftam cok iyi gecti",
    "Cocuklarin asi randevusu {gun} gunu",
    "Bahar temizligi icin bu hafta sonu vakit ayiralim",
    "Otobüs saatini kontrol ettim, {saat} kalkacak",
    "Yeni yil hediyeni aldim, cok begeneceksin sanirim",
    "Dogum gunu partisi icin pasta siparisi verdim",
    "Su ay bankadan gelen ekstre biraz farkli gorunuyor, birlikte bakalim",
    "Ailece hafta sonu koye gidelim mi, hava da guzel olacakmis",
    "Yarinki is gorusmesi icin basarilar dilerim",
    "Ev sahibi kira zammi icin mesaj atmis, konusalim",
    "Cocugun karnesi geldi, hep beraber bakalim aksam",
    "Telefon rehberine yeni numaramı kaydeder misin",
    "Yarin is toplantisinda sunum yapacagim, dua et benim icin",
    "{yakin} bugun okuldan erken cikacak, alabilir misin",
    "Cok guzel bir tarif buldum, aksam deneyelim mi",
    "Arabanin bakim zamani geldi, servise goturmemiz lazim",
    "Yarin sabah spor yapmaya gidecegim, sen de gelir misin",
    "Elektrik kesintisi olacakmis yarin sabah, komsu haber verdi",
    "Cok guzel bir kitap oneririm sana, kutuphaneden aldim",
    "Bu aksam misafirimiz var, saat {saat} gelecekler",
    "Yeni ayakkabilarim geldi, cok begendim",
    "Yarin toplanti oncesi kisa bir gorusme yapalim mi",
    "Cocuklarla parka gidip biraz vakit gecirelim",
    "Bu hafta is yogun, hafta sonu dinlenmemiz lazim",
    "Aksam yemegine misafir davet ettim, haberin olsun",
    "Isyerinde toplanti uzadi, biraz gec kalabilirim",
    "Bu hafta sonu balik tutmaya gidelim mi",
    "Cocuklarin karnesi cok iyi gelmis, kutluyoruz",
    "Bahcedeki agaclari sulamayi unutma lutfen",
    "Yarin toplanti odasi rezervasyonu yaptim",
    "Kredi karti limitim arttirildi, bankadan mesaj geldi",
    "Yeni komsularimiz tasindi, hosgeldin ziyaretine gidelim mi",
]

SAATLER = ["09:00", "10:30", "14:00", "15:00", "16:30", "17:00", "18:30", "saat 3'te", "saat 5'te"]
GUNLER = ["pazartesi", "sali", "carsamba", "persembe", "cuma", "cumartesi", "pazar", "yarin", "3 gun sonraya"]
TUTAR_KUCUK = ["185 TL", "245 TL", "312 TL", "410 TL", "156 TL", "278 TL"]


def kod_uret():
    return str(random.randint(100000, 999999))


def takip_no_uret():
    return "TR" + str(random.randint(100000000, 999999999))


def sablon_doldur(kalip: str) -> str:
    return kalip.format(
        firma=random.choice(KARGO_FIRMALARI),
        banka=random.choice(BANKA_ISIMLERI),
        sure=random.choice(SURELER),
        link=random.choice(SUPHELI_LINKLER),
        tutar=random.choice(TUTARLAR),
        yakin=random.choice(YAKINLIK_ISIMLERI),
        odul=random.choice(ODUL_ESYALARI),
        kod=kod_uret(),
        saat=random.choice(SAATLER),
        gun=random.choice(GUNLER),
        tutar_kucuk=random.choice(TUTAR_KUCUK),
        takip_no=takip_no_uret(),
    )


def veri_uret(hedef_riskli_sayi: int = 550, hedef_guvenli_sayi: int = 550) -> list[dict]:
    satirlar = []
    gorulen_mesajlar = set()

    kategori_listesi = list(SABLONLAR.items())
    while len([s for s in satirlar if s["risk_seviyesi"] != "guvenli"]) < hedef_riskli_sayi:
        kategori_adi, bilgi = random.choice(kategori_listesi)
        kalip = random.choice(bilgi["kaliplar"])
        mesaj = sablon_doldur(kalip)
        if mesaj in gorulen_mesajlar:
            continue
        gorulen_mesajlar.add(mesaj)
        satirlar.append({"mesaj": mesaj, "risk_seviyesi": bilgi["risk"], "kategori": kategori_adi})

    while len([s for s in satirlar if s["risk_seviyesi"] == "guvenli"]) < hedef_guvenli_sayi:
        kalip = random.choice(GUVENLI_KALIPLAR)
        mesaj = sablon_doldur(kalip)
        if mesaj in gorulen_mesajlar:
            continue
        gorulen_mesajlar.add(mesaj)
        satirlar.append({"mesaj": mesaj, "risk_seviyesi": "guvenli", "kategori": "normal"})

    random.shuffle(satirlar)
    return satirlar


def kaydet(satirlar: list[dict]):
    CIKTI_YOLU.parent.mkdir(exist_ok=True)
    with open(CIKTI_YOLU, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mesaj", "risk_seviyesi", "kategori"])
        writer.writeheader()
        writer.writerows(satirlar)


if __name__ == "__main__":
    satirlar = veri_uret(hedef_riskli_sayi=550, hedef_guvenli_sayi=550)
    kaydet(satirlar)
    print(f"Toplam {len(satirlar)} mesaj uretildi ve kaydedildi: {CIKTI_YOLU}")
