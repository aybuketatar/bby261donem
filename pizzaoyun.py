import tkinter as tk
import random  
import os
from PIL import Image, ImageTk
from datetime import datetime

MALZEME_BOYUT = (100, 100) 
TABAN_BOYUT = (700,700) 
RESIM_KLASORU = 'resimler'

MALZEME_BILGILERI = {
    "sucuk":    {"fiyat": 70,  "bg": "pink", "fg": "black"},
    "pastirma": {"fiyat": 80, "bg": "red", "fg": "black"},
    "mantar":   {"fiyat": 40,  "bg": "white", "fg": "black"},
    "biber":    {"fiyat": 40,  "bg": "lightgreen", "fg": "black"},
    "zeytin":   {"fiyat": 40,  "bg": "grey", "fg": "black"}
}
TEMEL_FIYAT = 25 
RENK_IZGARA_ARKAPLAN = 'white' 

pencere = tk.Tk()
pencere.title("Aybüke's Pizzaria")
pencere.resizable(True, True)
toplam_fiyat = TEMEL_FIYAT
konulan_malzemeler_idler = [] 
resim_nesneleri = {} 
topping_butonlari = []
hamur_id = None 

hedef_siparis_set = set()      
kullanici_pizzasi_liste = []  
son_puan = 0                  

UST_MALZEME_KONUMLARI = [
    (200, 200), (350, 200), (500, 200),
    (200, 350), (350, 350), (500, 350), 
    (200, 500), (350, 500), (500, 500)  
]

def resimleri_yukle():
    tabanlar = ['hamur.png', 'domatessosu.png', 'peynirli_taban.png', 'pestososu.png']
    for resim_adi in tabanlar:
        img = Image.open(os.path.join(RESIM_KLASORU, resim_adi))
        img = img.resize(TABAN_BOYUT)
        resim_nesneleri[resim_adi] = ImageTk.PhotoImage(img)

def yeni_musteri_siparis_olustur():
    global hedef_siparis_set
    
    hedef_sos = random.choice(['domates sosu', 'pesto sosu'])
    hedef_taban_peyniri = 'peynirli_taban'
    ust_malzemeler_listesi = list(MALZEME_BILGILERI.keys())
    hedef_ust_malzemeler = random.sample(ust_malzemeler_listesi, 2)
    
    hedef_siparis_set = {hedef_sos, hedef_taban_peyniri}
    hedef_siparis_set.update(hedef_ust_malzemeler)
    
    siparis_metni = "Müşteri İsteği:\n"
    if 'domates sosu' in hedef_siparis_set: siparis_metni += "- Domates Soslu\n"
    if 'pesto sosu' in hedef_siparis_set: siparis_metni += "- Pesto Soslu\n"
    siparis_metni += "- Peynirli Tabanlı\n"
    for malzeme in hedef_ust_malzemeler:
        siparis_metni += f"- {malzeme.capitalize()}\n"
        
    siparis_etiketi.config(text=siparis_metni)

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
    for buton in topping_butonlari:
        buton.config(state='normal')

def malzeme_ekle(malzeme_adi):
    global toplam_fiyat
    kullanici_pizzasi_liste.append(malzeme_adi) 
    
    resim_dosyasi = f"{malzeme_adi}.png"
    img = Image.open(os.path.join(RESIM_KLASORU, resim_dosyasi))
    img = img.resize(MALZEME_BOYUT)
    yeni_resim_nesnesi = ImageTk.PhotoImage(img)
    
    resim_nesneleri[f"malzeme_{malzeme_adi}"] = yeni_resim_nesnesi

    for (x_pos, y_pos) in UST_MALZEME_KONUMLARI:
        malzeme_id = pizza_canvasi.create_image(x_pos, y_pos, image=yeni_resim_nesnesi)
        konulan_malzemeler_idler.append(malzeme_id)
    
    toplam_fiyat += MALZEME_BILGILERI[malzeme_adi]["fiyat"]
    fiyat_etiketi.config(text=f"Toplam Fiyat: {toplam_fiyat} TL")
    
    for buton in topping_butonlari:
        if malzeme_adi in buton.cget("text").lower():
            buton.config(state="disabled")
    
def sifirla():
    global toplam_fiyat, hamur_id
    
    kapanis_cercevesi.pack_forget()
    menu_cercevesi.pack(side=tk.LEFT, fill=tk.Y)
    pizza_canvasi.pack(side=tk.RIGHT, padx=20, pady=20)

    for malzeme_id in konulan_malzemeler_idler:
        pizza_canvasi.delete(malzeme_id)
        
    pizza_canvasi.itemconfig(hamur_id, image=resim_nesneleri['hamur.png'])
    konulan_malzemeler_idler.clear()
    toplam_fiyat = TEMEL_FIYAT
    
    kullanici_pizzasi_liste.clear() 
    yeni_musteri_siparis_olustur() 
    
    sos_domates_butonu.config(state='normal')
    sos_pesto_butonu.config(state='normal')
    taban_peynir_butonu.config(state='disabled')
    for buton in topping_butonlari:
        buton.config(state='normal')
    
    fiyat_etiketi.config(text=f"Toplam Fiyat: {toplam_fiyat} TL")

def siparisi_tamamla():
    global son_puan, toplam_fiyat
    
    menu_cercevesi.pack_forget()
    pizza_canvasi.pack_forget()
    
    kullanici_seti = set(kullanici_pizzasi_liste)
    hedef_seti = hedef_siparis_set
    
    eksikler = hedef_seti.difference(kullanici_seti)
    fazlaliklar = kullanici_seti.difference(hedef_seti)
    
    puan = 100
    puan -= len(eksikler) * 20
    puan -= len(fazlaliklar) * 10 
    if puan < 0: puan = 0
    
    son_puan = puan 
    
    kapanis_baslik.config(text=f"Müşteri Puanı: {puan} / 100")
    kapanis_fiyat_etiketi.config(text=f"Toplam Tutar: {toplam_fiyat} TL")
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
        f.write(f"Toplam Tutar: {toplam_fiyat} TL\n")
        f.write("--------------------------\n\n")
    
    kaydet_butonu.config(text="Fişe Kaydedildi!", state="disabled")

menu_cercevesi = tk.Frame(pencere, padx=10, pady=10)
pizza_canvasi = tk.Canvas(pencere, width=TABAN_BOYUT[0], height=TABAN_BOYUT[1], bg=RENK_IZGARA_ARKAPLAN)

resimleri_yukle()

hamur_id = pizza_canvasi.create_image(
    TABAN_BOYUT[0] // 2, 
    TABAN_BOYUT[1] // 2, 
    image=resim_nesneleri['hamur.png']
) 

menu_baslik = tk.Label(menu_cercevesi, text="Pizza Oluştur", font=("Arial", 16, "bold"), fg="red")
menu_baslik.pack(pady=10)

siparis_etiketi = tk.Label(menu_cercevesi, text="Sipariş yükleniyor...", font=("Arial", 11, "bold"), justify=tk.LEFT, relief="sunken", padx=5)
siparis_etiketi.pack(pady=10, fill="x")

sos_domates_butonu = tk.Button(menu_cercevesi, text="Domates Sosu", font=("Arial", 12, "bold"), width=15, 
                               bg='white', fg='black', command=lambda: sos_ekle('domates'))
sos_domates_butonu.pack(pady=5)

sos_pesto_butonu = tk.Button(menu_cercevesi, text="Pesto Sosu", font=("Arial", 12, "bold"), width=15, 
                             bg='white', fg='black', command=lambda: sos_ekle('pesto'))
sos_pesto_butonu.pack(pady=5)

taban_peynir_butonu = tk.Button(menu_cercevesi, text="Peynir Ekle (Taban)", font=("Arial", 12, "bold"), width=15, 
                                bg="white", fg="black", command=taban_peyniri_ekle)
taban_peynir_butonu.pack(pady=5)
taban_peynir_butonu.config(state='disabled') 

tk.Label(menu_cercevesi, text="--- Malzemeler ---", font=("Arial", 10)).pack(pady=10)

for malzeme_adi in MALZEME_BILGILERI:
    bilgi = MALZEME_BILGILERI[malzeme_adi]
    buton = tk.Button(menu_cercevesi, 
                      text=f"{malzeme_adi.capitalize()} (+{bilgi['fiyat']} TL)", 
                      font=("Arial", 12, "bold"), 
                      width=15, bg=bilgi['bg'], fg=bilgi['fg'], 
                      command=lambda m=malzeme_adi: malzeme_ekle(m))
    buton.pack(pady=5)
    buton.config(state='disabled') 
    topping_butonlari.append(buton) 

fiyat_etiketi = tk.Label(menu_cercevesi, text=f"Toplam Fiyat: {TEMEL_FIYAT} TL", font=("Arial", 14, "bold"))
fiyat_etiketi.pack(pady=20, side=tk.BOTTOM) 

siparisi_tamamla_butonu = tk.Button(menu_cercevesi, text="SİPARİŞİ VER", font=("Arial", 14, "bold"), 
                                    bg="lightblue", fg="black", command=siparisi_tamamla)
siparisi_tamamla_butonu.pack(pady=10, side=tk.BOTTOM)

kapanis_cercevesi = tk.Frame(pencere, padx=40, pady=40)
kapanis_baslik = tk.Label(kapanis_cercevesi, text="Müşteri Puanı: 0 / 100", font=("Arial", 20, "bold"), fg="blue")
kapanis_baslik.pack(pady=20)
kapanis_fiyat_etiketi = tk.Label(kapanis_cercevesi, text="Toplam Tutar: 0 TL", font=("Arial", 16))
kapanis_fiyat_etiketi.pack(pady=5)
kapanis_eksikler = tk.Label(kapanis_cercevesi, text="Eksik Malzemeler: -", font=("Arial", 12))
kapanis_eksikler.pack(pady=5)
kapanis_fazlaliklar = tk.Label(kapanis_cercevesi, text="Fazla Malzemeler: -", font=("Arial", 12))
kapanis_fazlaliklar.pack(pady=5)
kaydet_butonu = tk.Button(kapanis_cercevesi, text="Siparişi Fişe Kaydet (.txt)", font=("Arial", 12, "bold"), 
                           bg="grey", fg="black", command=siparis_kaydet_txt)
kaydet_butonu.pack(pady=20)
yeni_siparis_butonu = tk.Button(kapanis_cercevesi, text="Yeni Müşteri Al", font=("Arial", 12, "bold"), 
                                bg="lightgreen", fg="black", command=sifirla)
yeni_siparis_butonu.pack(pady=10)

menu_cercevesi.pack(side=tk.LEFT, fill=tk.Y)
pizza_canvasi.pack(side=tk.RIGHT, padx=20, pady=20)
yeni_musteri_siparis_olustur() 

pencere.mainloop()