import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
from datetime import datetime

MALZEME_BOYUT = (80, 80) 
TABAN_BOYUT = (700, 700) 
RESIM_KLASORU = 'resimler'
BASLANGIC_SURESI = 40
MALZEME_ADETI = 9

MALZEME_BILGILERI = {
    "sucuk":      {"fiyat": 70,  "bg": "red",    "fg": "black", "kilit_bedeli": 0},
    "mantar":     {"fiyat": 40,  "bg": "grey",       "fg": "black", "kilit_bedeli": 0},
    "biber":      {"fiyat": 40,  "bg": "green",      "fg": "black", "kilit_bedeli": 0},
    "zeytin":     {"fiyat": 40,  "bg": "white",      "fg": "black", "kilit_bedeli": 0},
    "misir":      {"fiyat": 40,  "bg": "yellow",     "fg": "black", "kilit_bedeli": 150},
    "kirmizibiber": {"fiyat": 40, "bg": "pink",       "fg": "black", "kilit_bedeli": 200},
    "tonbaligi": {"fiyat": 80, "bg": "brown",       "fg": "black", "kilit_bedeli": 300},
    "pastirma":   {"fiyat": 70, "bg": "firebrick",  "fg": "black", "kilit_bedeli": 0} 
}
TEMEL_FIYAT = 25 
RENK_IZGARA_ARKAPLAN = 'white' 

pencere = tk.Tk()
pencere.title("Aybüke's Pizzeria")
pencere.resizable(True, True)

toplam_fiyat = TEMEL_FIYAT
konulan_malzemeler_idler = []
resim_nesneleri = {} 
topping_butonlari = {} 
hamur_id = None 
hedef_siparis_set = set()      
kullanici_pizzasi_liste = []  
son_puan = 0                  
kalan_sure = BASLANGIC_SURESI
zamanlayici_id = None 
toplam_butce = 0
acik_kilitler = [] 

UST_MALZEME_KONUMLARI = [
    (200, 200), (350, 200), (500, 200),
    (200, 350), (350, 350), (500, 350),
    (200, 500), (350, 500), (500, 500)
]

def verileri_yukle():
    global toplam_butce, acik_kilitler
    try:
        with open("butce.txt", "r") as f:
            toplam_butce = int(f.read())
    except (FileNotFoundError, ValueError):
        toplam_butce = 0 

    try:
        with open("kilitler.txt", "r") as f:
            acik_kilitler = f.read().splitlines()
    except FileNotFoundError:
        acik_kilitler = []
    
    guncelle_butce_etiketi()

def verileri_kaydet():
    try:
        with open("butce.txt", "w") as f:
            f.write(str(toplam_butce))
    except Exception as e:
        print(f"Bütçe hatası: {e}")
        
    try:
        with open("kilitler.txt", "w") as f:
            for malzeme in acik_kilitler:
                f.write(f"{malzeme}\n")
    except Exception as e:
        print(f"Kilit hatası: {e}")

def guncelle_butce_etiketi():
    try:
        butce_etiketi.config(text=f"KASA: {toplam_butce} TL")
    except NameError:
        pass

def resimleri_yukle():
    tabanlar = ['hamur.png', 'domatessosu.png', 'peynirli_taban.png', 'pestososu.png']
    for resim_adi in tabanlar:
        try:
            img = Image.open(os.path.join(RESIM_KLASORU, resim_adi))
            img = img.resize(TABAN_BOYUT)
            resim_nesneleri[resim_adi] = ImageTk.PhotoImage(img)
        except FileNotFoundError:
            print(f"HATA: {resim_adi} bulunamadı!")

def yeni_musteri_siparis_olustur():
    global hedef_siparis_set
    hedef_sos = random.choice(['domates sosu', 'pesto sosu'])
    hedef_taban_peyniri = 'peynirli_taban'
    
    acik_olanlar = [m for m in MALZEME_BILGILERI if MALZEME_BILGILERI[m]['kilit_bedeli'] == 0 or m in acik_kilitler]
    
    kac_tane = random.randint(1, 3)
    if len(acik_olanlar) < kac_tane:
        kac_tane = len(acik_olanlar)
        
    hedef_ust_malzemeler = random.sample(acik_olanlar, kac_tane)
    
    hedef_siparis_set = {hedef_sos, hedef_taban_peyniri}
    hedef_siparis_set.update(hedef_ust_malzemeler)
    
    siparis_metni = "Müşteri İsteği:\n"
    if 'domates sosu' in hedef_siparis_set: siparis_metni += "- Domates Soslu\n"
    if 'pesto sosu' in hedef_siparis_set: siparis_metni += "- Pesto Soslu\n"
    siparis_metni += "- Peynirli Tabanlı\n"
    for malzeme in hedef_ust_malzemeler:
        siparis_metni += f"- {malzeme.capitalize()}\n"
    siparis_etiketi.config(text=siparis_metni)

def geri_sayim():
    global kalan_sure, zamanlayici_id
    if kalan_sure > 0:
        kalan_sure -= 1 
        sure_etiketi.config(text=f"Kalan Süre: {kalan_sure} sn")
        zamanlayici_id = pencere.after(1000, geri_sayim) 
    else:
        sure_etiketi.config(text="SÜRE BİTTİ!")
        siparisi_tamamla() 

def malzeme_satin_al(malzeme_adi):
    global toplam_butce
    bedel = MALZEME_BILGILERI[malzeme_adi]['kilit_bedeli']
    cevap = messagebox.askyesno("Satın Al", f"{malzeme_adi.capitalize()} kilidini açmak için {bedel} TL ödemek istiyor musun?")
    if cevap:
        if toplam_butce >= bedel:
            toplam_butce -= bedel
            acik_kilitler.append(malzeme_adi)
            verileri_kaydet()
            guncelle_butce_etiketi()
            butonlari_guncelle()
            messagebox.showinfo("Başarılı", f"{malzeme_adi.capitalize()} artık kullanılabilir!")
        else:
            messagebox.showerror("Yetersiz Bakiye", f"Paran yetmiyor :( (Eksik: {bedel - toplam_butce} TL)")

def butonlari_guncelle():
    for malzeme_adi, buton in topping_butonlari.items():
        info = MALZEME_BILGILERI[malzeme_adi]
        if info['kilit_bedeli'] == 0 or malzeme_adi in acik_kilitler:
            buton.config(text=f"{malzeme_adi.capitalize()} (+{info['fiyat']} TL)", 
                         bg=info['bg'], fg=info['fg'], 
                         command=lambda m=malzeme_adi: malzeme_ekle(m))
            if taban_peynir_butonu['state'] == 'normal':
                 buton.config(state='disabled')
            else:
                 pass 
        else:
            buton.config(text=f"{malzeme_adi.capitalize()} (KİLİTLİ: {info['kilit_bedeli']} TL)",
                         bg='grey', fg='black', state='normal',
                         command=lambda m=malzeme_adi: malzeme_satin_al(m))

def geri_al():
    global toplam_fiyat
    if not konulan_malzemeler_idler:
        return

    son_grup = konulan_malzemeler_idler.pop()
    ids, malzeme_adi = son_grup
    
    for resim_id in ids:
        pizza_canvasi.delete(resim_id)
        
    fiyat = MALZEME_BILGILERI[malzeme_adi]["fiyat"]
    toplam_fiyat -= fiyat
    fiyat_etiketi.config(text=f"Toplam Fiyat: {toplam_fiyat} TL")
    
    if malzeme_adi in kullanici_pizzasi_liste:
        for i in range(len(kullanici_pizzasi_liste)-1, -1, -1):
            if kullanici_pizzasi_liste[i] == malzeme_adi:
                del kullanici_pizzasi_liste[i]
                break
    
def sos_ekle(sos_tipi):
    global hamur_id
    if sos_tipi == 'domates':
        pizza_canvasi.itemconfig(hamur_id, image=resim_nesneleri['domatessosu.png'])
        kullanici_pizzasi_liste.append('domates sosu') 
    elif sos_tipi == 'pesto':
        pizza_canvasi.itemconfig(hamur_id, image=resim_nesneleri['pestososu.png'])
        kullanici_pizzasi_liste.append('pesto sosu') 
    sos_domates_butonu.config(state='disabled')
    sos_pesto_butonu.config(state='disabled')
    taban_peynir_butonu.config(state='normal') 

def taban_peyniri_ekle(): 
    global hamur_id
    pizza_canvasi.itemconfig(hamur_id, image=resim_nesneleri['peynirli_taban.png'])
    kullanici_pizzasi_liste.append('peynirli_taban') 
    taban_peynir_butonu.config(state='disabled')

    for malzeme_adi, buton in topping_butonlari.items():
        info = MALZEME_BILGILERI[malzeme_adi]
        if info['kilit_bedeli'] == 0 or malzeme_adi in acik_kilitler:
            buton.config(state='normal')

def malzeme_ekle(malzeme_adi):
    global toplam_fiyat
    
    try:
        resim_dosyasi = f"{malzeme_adi}.png"
        img = Image.open(os.path.join(RESIM_KLASORU, resim_dosyasi))
        img = img.resize(MALZEME_BOYUT)
  
        if malzeme_adi == "zeytin":
          img = img.resize((60, 60)) # Zeytinse 60x60 olsun (Küçük)
        else:
          img = img.resize(MALZEME_BOYUT) # Diğerleri standart (100x100) kalsın
        yeni_resim_nesnesi = ImageTk.PhotoImage(img)
        resim_nesneleri[f"malzeme_{malzeme_adi}"] = yeni_resim_nesnesi
    except FileNotFoundError:
        messagebox.showerror("Hata", f"{malzeme_adi}.png bulunamadı!")
        return

    eklenecek_konumlar = random.sample(UST_MALZEME_KONUMLARI, MALZEME_ADETI)

    bu_tur_eklenen_ids = []
    for (x_pos, y_pos) in eklenecek_konumlar:
        malzeme_id = pizza_canvasi.create_image(x_pos, y_pos, image=yeni_resim_nesnesi)
        bu_tur_eklenen_ids.append(malzeme_id)
    

    konulan_malzemeler_idler.append((bu_tur_eklenen_ids, malzeme_adi))

    kullanici_pizzasi_liste.append(malzeme_adi)
    toplam_fiyat += MALZEME_BILGILERI[malzeme_adi]["fiyat"]
    fiyat_etiketi.config(text=f"Toplam Fiyat: {toplam_fiyat} TL")

def sifirla():
    global toplam_fiyat, hamur_id, kalan_sure, zamanlayici_id
    
    if zamanlayici_id:
        pencere.after_cancel(zamanlayici_id)
        zamanlayici_id = None
    
    kapanis_cercevesi.pack_forget()
    menu_cercevesi.pack(side=tk.LEFT, fill=tk.Y)
    pizza_canvasi.pack(side=tk.RIGHT, padx=20, pady=20)

    for grup in konulan_malzemeler_idler:
        ids = grup[0]
        for resim_id in ids:
            pizza_canvasi.delete(resim_id)
        
    pizza_canvasi.itemconfig(hamur_id, image=resim_nesneleri['hamur.png'])
    konulan_malzemeler_idler.clear()
    toplam_fiyat = TEMEL_FIYAT
    kullanici_pizzasi_liste.clear() 
    
    yeni_musteri_siparis_olustur() 
    guncelle_butce_etiketi()
    
    sos_domates_butonu.config(state='normal')
    sos_pesto_butonu.config(state='normal')
    taban_peynir_butonu.config(state='disabled')
    
    butonlari_guncelle()
    for btn in topping_butonlari.values():
        if "KİLİT" not in btn.cget("text"):
            btn.config(state='disabled')

    fiyat_etiketi.config(text=f"Toplam Fiyat: {toplam_fiyat} TL")
    kalan_sure = BASLANGIC_SURESI
    sure_etiketi.config(text=f"Kalan Süre: {kalan_sure} sn")
    geri_sayim()

def siparisi_tamamla():
    global son_puan, toplam_fiyat, zamanlayici_id, toplam_butce
    
    if zamanlayici_id:
        pencere.after_cancel(zamanlayici_id)
        zamanlayici_id = None
    
    menu_cercevesi.pack_forget()
    pizza_canvasi.pack_forget()
    
    kullanici_seti = set(kullanici_pizzasi_liste)
    hedef_seti = hedef_siparis_set
    eksikler = hedef_seti.difference(kullanici_seti)
    fazlaliklar = kullanici_seti.difference(hedef_seti)
    
    dogruluk_puani = 100
    dogruluk_puani -= len(eksikler) * 20
    dogruluk_puani -= len(fazlaliklar) * 10 
    if dogruluk_puani < 0: dogruluk_puani = 0
    son_puan = dogruluk_puani
    
    bahsis = 0
    if son_puan == 100 and kalan_sure > (BASLANGIC_SURESI // 2): 
        bahsis = 15
    elif son_puan == 100: 
        bahsis = 7
    elif son_puan >= 80:
        bahsis = 3
    
    toplam_kazanc = toplam_fiyat + bahsis
    toplam_butce += toplam_kazanc
    verileri_kaydet() 
    
    kapanis_baslik.config(text=f"Müşteri Puanı: {son_puan} / 100")
    kapanis_fiyat_etiketi.config(text=f"Pizza Fiyatı: {toplam_fiyat} TL")
    kapanis_bahsis_etiketi.config(text=f"Bahşiş: +{bahsis} TL")
    kapanis_kazanc_etiketi.config(text=f"Toplam Kazanç: {toplam_kazanc} TL")
    kapanis_eksikler.config(text=f"Eksik Malzemeler: {list(eksikler) if eksikler else 'YOK'}")
    kapanis_fazlaliklar.config(text=f"Fazla Malzemeler: {list(fazlaliklar) if fazlaliklar else 'YOK'}")
    
    kaydet_butonu.config(text="Siparişi Fişe Kaydet", state="normal") 
    kapanis_cercevesi.pack(pady=50)

def siparis_kaydet_txt():
    with open("siparisler.txt", "a", encoding="utf-8") as f:
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("--- YENİ SİPARİŞ FİŞİ ---\n")
        f.write(f"Tarih: {zaman}\n")
        f.write(f"Müşteri İsteği: {hedef_siparis_set}\n")
        f.write(f"Yapılan Pizza: {kullanici_pizzasi_liste}\n")
        f.write(f"Alınan Puan: {son_puan}\n")
        f.write(f"Toplam Tutar: {toplam_fiyat}\n") 
        f.write("--------------------------\n\n")
    kaydet_butonu.config(text="Fişe Kaydedildi!", state="disabled")

menu_cercevesi = tk.Frame(pencere, padx=10, pady=10)
menu_cercevesi.pack(side=tk.LEFT, fill=tk.Y)
pizza_canvasi = tk.Canvas(pencere, width=TABAN_BOYUT[0], height=TABAN_BOYUT[1], bg=RENK_IZGARA_ARKAPLAN)
pizza_canvasi.pack(side=tk.RIGHT, padx=20, pady=20)

resimleri_yukle()

hamur_id = pizza_canvasi.create_image(
    TABAN_BOYUT[0] // 2, 
    TABAN_BOYUT[1] // 2, 
    image=resim_nesneleri['hamur.png']
) 

menu_baslik = tk.Label(menu_cercevesi, text="Pizza Oluştur", font=("Arial", 16, "bold"), fg="black")
menu_baslik.pack(pady=10)

butce_etiketi = tk.Label(menu_cercevesi, text="KASA: 0 TL", font=("Arial", 14, "bold"), fg="black", relief="ridge")
butce_etiketi.pack(pady=10, fill="x")

sure_etiketi = tk.Label(menu_cercevesi, text=f"Kalan Süre: {BASLANGIC_SURESI} sn", font=("Arial", 14, "bold"), fg="black", relief="groove")
sure_etiketi.pack(pady=10, fill="x")

siparis_etiketi = tk.Label(menu_cercevesi, text="Sipariş yükleniyor...", font=("Arial", 11, "bold"), justify=tk.LEFT, relief="sunken", padx=5)
siparis_etiketi.pack(pady=10, fill="x")

sos_domates_butonu = tk.Button(menu_cercevesi, text="Domates Sosu", font=("Arial", 12, "bold"), width=15, 
                               bg='red', fg='black', command=lambda: sos_ekle('domates'))
sos_domates_butonu.pack(pady=5)
sos_pesto_butonu = tk.Button(menu_cercevesi, text="Pesto Sosu", font=("Arial", 12, "bold"), width=15, 
                             bg='green', fg='black', command=lambda: sos_ekle('pesto'))
sos_pesto_butonu.pack(pady=5)
taban_peynir_butonu = tk.Button(menu_cercevesi, text="Peynir Ekle (Taban)", font=("Arial", 12, "bold"), width=15, 
                                bg="darkorange", fg="black", command=taban_peyniri_ekle)
taban_peynir_butonu.pack(pady=5)
taban_peynir_butonu.config(state='disabled') 

tk.Label(menu_cercevesi, text="--- Malzemeler ---", font=("Arial", 10)).pack(pady=5)

for malzeme_adi in MALZEME_BILGILERI:
    bilgi = MALZEME_BILGILERI[malzeme_adi]
    buton = tk.Button(menu_cercevesi, width=15, font=("Arial", 12, "bold"))
    buton.pack(pady=3)
    topping_butonlari[malzeme_adi] = buton

geri_al_butonu = tk.Button(menu_cercevesi, text="SON İŞLEMİ GERİ AL", font=("Arial", 11, "bold"), 
                           bg="orange", fg="black", command=geri_al)
geri_al_butonu.pack(pady=10)

fiyat_etiketi = tk.Label(menu_cercevesi, text=f"Toplam Fiyat: {TEMEL_FIYAT} TL", font=("Arial", 14, "bold"))
fiyat_etiketi.pack(pady=10, side=tk.BOTTOM) 
siparisi_tamamla_butonu = tk.Button(menu_cercevesi, text="SİPARİŞİ VER", font=("Arial", 14, "bold"), 
                                    bg="lightblue", fg="black", command=siparisi_tamamla)
siparisi_tamamla_butonu.pack(pady=10, side=tk.BOTTOM)

kapanis_cercevesi = tk.Frame(pencere, padx=40, pady=40)
kapanis_baslik = tk.Label(kapanis_cercevesi, text="Müşteri Puanı: 0 / 100", font=("Arial", 20, "bold"), fg="black")
kapanis_baslik.pack(pady=10)
kapanis_fiyat_etiketi = tk.Label(kapanis_cercevesi, text="Pizza Fiyatı: 0 TL", font=("Arial", 16))
kapanis_fiyat_etiketi.pack(pady=5)
kapanis_bahsis_etiketi = tk.Label(kapanis_cercevesi, text="Bahşiş: +0 TL", font=("Arial", 16, "bold"), fg="black")
kapanis_bahsis_etiketi.pack(pady=5)
kapanis_kazanc_etiketi = tk.Label(kapanis_cercevesi, text="Toplam Kazanç: 0 TL", font=("Arial", 16, "bold"))
kapanis_kazanc_etiketi.pack(pady=5)
kapanis_eksikler = tk.Label(kapanis_cercevesi, text="Eksik Malzemeler: -", font=("Arial", 12))
kapanis_eksikler.pack(pady=5)
kapanis_fazlaliklar = tk.Label(kapanis_cercevesi, text="Fazla Malzemeler: -", font=("Arial", 12))
kapanis_fazlaliklar.pack(pady=5)
kaydet_butonu = tk.Button(kapanis_cercevesi, text="Siparişi Fişe Kaydet (.txt)", font=("Arial", 12, "bold"), 
                           bg="grey", fg="black", command=siparis_kaydet_txt)
kaydet_butonu.pack(pady=20)
yeni_siparis_butonu = tk.Button(kapanis_cercevesi, text="Yeni Müşteri Al", font=("Arial", 12, "bold"), 
                                bg="green", fg="black", command=sifirla)
yeni_siparis_butonu.pack(pady=10)

verileri_yukle()
butonlari_guncelle()
yeni_musteri_siparis_olustur() 
geri_sayim() 

menu_cercevesi.pack(side=tk.LEFT, fill=tk.Y)
pizza_canvasi.pack(side=tk.RIGHT, padx=20, pady=20)

pencere.mainloop()
