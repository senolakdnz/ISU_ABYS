from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
import psycopg2
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI(title="Abone Yönetim Sistemi API")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.post("/login")
def login(kullanici: dict):
    try:
        # JSON dosyasını oku
        with open("kullanicilar.json", "r", encoding="utf-8") as f:
            kullanicilar = json.load(f)
        
        # Gelen mail ve şifreyi listede ara
        for kayit in kullanicilar:
            if kayit["mail"] == kullanici.get("mail") and kayit["sifre"] == kullanici.get("sifre"):
                return {"durum": "basarili"}
        
        return {"durum": "hata", "mesaj": "Hatalı mail veya şifre!"}
        
    except Exception as e:
        return {"durum": "hata", "mesaj": "Sistem hatası: Dosya okunamadı."}

@app.get("/index.html")
def get_index():
    return FileResponse("index.html")

@app.get("/")
def read_index():
    return FileResponse("login.html")

@app.get("/aboneler.html")
def get_aboneler(): return FileResponse("aboneler.html")
@app.get("/subeler.html")
def get_subeler(): return FileResponse("subeler.html")
@app.get("/tarifeler.html")
def get_tarifeler(): return FileResponse("tarifeler.html")
@app.get("/sayaclar.html")
def get_sayaclar(): return FileResponse("sayaclar.html")
@app.get("/ilceler.html")
def get_ilceler(): return FileResponse("ilceler.html")
@app.get("/tiptur.html")
def get_tiptur(): return FileResponse("tiptur.html")
@app.get("/abone_turleri.html")
def get_abone_turleri(): return FileResponse("abone_turleri.html")
@app.get("/sozlesmeler.html")
def get_sozlesmeler(): return FileResponse("sozlesmeler.html")
@app.get("/ambarlar.html")
def get_ambarlar(): return FileResponse("ambarlar.html")

class TarifeModel(BaseModel):
    TarifeAd: str
    TarifeUcret: float

@app.post("/tarifeler")
def tarife_ekle(tarife: TarifeModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tarifeler (TarifeAd, TarifeUcret) VALUES (%s, %s)", (tarife.TarifeAd, tarife.TarifeUcret))
    conn.commit()
    cursor.close()
    conn.close()
    return {"mesaj": "Tarife eklendi."}

@app.get("/tarifeler")
def tarifeleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TarifeID, TarifeAd, TarifeUcret FROM Tarifeler ORDER BY TarifeID ASC")
    veri = cursor.fetchall()
    conn.close()
    return [{"TarifeID": r[0], "TarifeAd": r[1], "TarifeUcret": r[2]} for r in veri]

@app.put("/tarifeler/{tarife_id}")
def tarife_guncelle(tarife_id: int, tarife: TarifeModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Tarifeler SET TarifeAd = %s, TarifeUcret = %s WHERE TarifeID = %s", (tarife.TarifeAd, tarife.TarifeUcret, tarife_id))
    conn.commit()
    conn.close()
    return {"mesaj": "Tarife güncellendi."}

@app.delete("/tarifeler/{tarife_id}")
def tarife_sil(tarife_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Tarifeler WHERE TarifeID = %s", (tarife_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Tarife silindi."}

class AboneTuruModel(BaseModel):
    Tur: str

@app.post("/abone-turleri")
def abone_turu_ekle(abone_turu: AboneTuruModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO AboneTurleri (Tur) VALUES (%s)", (abone_turu.Tur,))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone türü eklendi."}

@app.get("/abone-turleri")
def abone_turlerini_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TurID, Tur FROM AboneTurleri ORDER BY TurID ASC")
    veri = cursor.fetchall()
    conn.close()
    return [{"TurID": r[0], "Tur": r[1]} for r in veri]

@app.put("/abone-turleri/{tur_id}")
def abone_turu_guncelle(tur_id: int, abone_turu: AboneTuruModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE AboneTurleri SET Tur = %s WHERE TurID = %s", (abone_turu.Tur, tur_id))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone türü güncellendi."}

@app.delete("/abone-turleri/{tur_id}")
def abone_turu_sil(tur_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM AboneTurleri WHERE TurID = %s", (tur_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone türü silindi."}

class SubeModel(BaseModel):
    SubeAd: str
    SubeIlce: int

@app.post("/subeler")
def sube_ekle(sube: SubeModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Subeler (SubeAd, SubeIlce) VALUES (%s, %s)", (sube.SubeAd, sube.SubeIlce))
    conn.commit()
    conn.close()
    return {"mesaj": "Şube eklendi."}

@app.get("/subeler")
def subeleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # INNER JOIN ile Subeler tablosundaki SubeIlce ID'sini Ilce tablosundaki IlceID ile eşleştirip IlceAd'ını çekiyoruz
    sorgu = """
    SELECT Subeler.SubeID, Subeler.SubeAd, Subeler.SubeIlce, Ilce.IlceAd 
    FROM Subeler 
    INNER JOIN Ilce ON Subeler.SubeIlce = Ilce.IlceID 
    ORDER BY Subeler.SubeID ASC
    """
    
    cursor.execute(sorgu)
    veri = cursor.fetchall()
    conn.close()
    
    # JSON verisine 'IlceAd' (r[3]) bilgisini de ekliyoruz
    return [{"SubeID": r[0], "SubeAd": r[1], "SubeIlce": r[2], "IlceAd": r[3]} for r in veri]

@app.put("/subeler/{sube_id}")
def sube_guncelle(sube_id: int, sube: SubeModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Subeler SET SubeAd = %s, SubeIlce = %s WHERE SubeID = %s", (sube.SubeAd, sube.SubeIlce, sube_id))
    conn.commit()
    conn.close()
    return {"mesaj": "Şube güncellendi."}

@app.delete("/subeler/{sube_id}")
def sube_sil(sube_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Subeler WHERE SubeID = %s", (sube_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Şube silindi."}

class SayacModel(BaseModel):
    SayacAd: str
    SayacTipTuru: int
    SayacAmbari: int
    IslemTarihi: date

@app.post("/sayaclar")
def sayac_ekle(sayac: SayacModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Sayaclar (SayacAd, SayacTipTuru, SayacAmbari, IslemTarihi) VALUES (%s, %s, %s, %s)", 
                   (sayac.SayacAd, sayac.SayacTipTuru, sayac.SayacAmbari, sayac.IslemTarihi))
    conn.commit()
    conn.close()
    return {"mesaj": "Sayaç eklendi."}

@app.get("/sayaclar")
def sayaclari_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    sorgu = """
    SELECT s.SayacID, s.SayacAd, s.SayacTipTuru, t.TipAd, s.SayacAmbari, a.AmbarAd, s.IslemTarihi, s.LogHaritasi 
    FROM Sayaclar s 
    INNER JOIN TipTur t ON s.SayacTipTuru = t.TipID 
    LEFT JOIN Ambarlar a ON s.SayacAmbari = a.AmbarID
    ORDER BY s.SayacID ASC
    """
    cursor.execute(sorgu)
    veri = cursor.fetchall()
    conn.close()
    return [{"SayacID": r[0], "SayacAd": r[1], "SayacTipTuru": r[2], "TipAd": r[3], "SayacAmbari": r[4], "AmbarAd": r[5], "IslemTarihi": r[6], "LogHaritasi": r[7]} for r in veri]

@app.post("/sayaclar")
def sayac_ekle(sayac: SayacModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # İlk kayıt olduğu için geçmiş boş başlar '[]'
    cursor.execute("INSERT INTO Sayaclar (SayacAd, SayacTipTuru, SayacAmbari, IslemTarihi, LogHaritasi) VALUES (%s, %s, %s, %s, %s)", 
                   (sayac.SayacAd, sayac.SayacTipTuru, sayac.SayacAmbari, sayac.IslemTarihi, '[]'))
    conn.commit()
    conn.close()
    return {"mesaj": "Sayaç eklendi."}

@app.put("/sayaclar/{sayac_id}")
def sayac_guncelle(sayac_id: int, sayac: SayacModel):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Sayacın eski durumunu ve mevcut log geçmişini çek
    cursor.execute("SELECT s.SayacAmbari, a.AmbarAd, s.IslemTarihi, s.LogHaritasi FROM Sayaclar s LEFT JOIN Ambarlar a ON s.SayacAmbari = a.AmbarID WHERE s.SayacID = %s", (sayac_id,))
    eski_veri = cursor.fetchone()
    
    eski_ambar_id = eski_veri[0]
    eski_ambar_ad = eski_veri[1] or "Belirtilmedi"
    eski_tarih = eski_veri[2]
    mevcut_loglar = json.loads(eski_veri[3]) if eski_veri[3] else []

    # 2. Eğer ambar veya tarih değişmişse, kaybolmaması için eski durumu geçmişe (loga) ekle
    if eski_ambar_id != sayac.SayacAmbari or str(eski_tarih) != str(sayac.IslemTarihi):
        mevcut_loglar.append({"Ambar": eski_ambar_ad, "Tarih": str(eski_tarih)})

    # 3. Yeni değerleri ve uzayan log geçmişini tekrar sütuna kaydet
    cursor.execute("UPDATE Sayaclar SET SayacAd = %s, SayacTipTuru = %s, SayacAmbari = %s, IslemTarihi = %s, LogHaritasi = %s WHERE SayacID = %s", 
                   (sayac.SayacAd, sayac.SayacTipTuru, sayac.SayacAmbari, sayac.IslemTarihi, json.dumps(mevcut_loglar), sayac_id))
    
    conn.commit()
    conn.close()
    return {"mesaj": "Sayaç güncellendi."}

@app.delete("/sayaclar/{sayac_id}")
def sayac_sil(sayac_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Sayaclar WHERE SayacID = %s", (sayac_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Sayaç silindi."}

class IlceModel(BaseModel):
    IlceAd: str

@app.post("/ilceler")
def ilce_ekle(ilce: IlceModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Ilce (IlceAd) VALUES (%s)", (ilce.IlceAd,))
    conn.commit()
    conn.close()
    return {"mesaj": "İlçe eklendi."}

@app.get("/ilceler")
def ilceleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT IlceID, IlceAd FROM Ilce ORDER BY IlceID ASC")
    veri = cursor.fetchall()
    conn.close()
    return [{"IlceID": r[0], "IlceAd": r[1]} for r in veri]

@app.put("/ilceler/{ilce_id}")
def ilce_guncelle(ilce_id: int, ilce: IlceModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Ilce SET IlceAd = %s WHERE IlceID = %s", (ilce.IlceAd, ilce_id))
    conn.commit()
    conn.close()
    return {"mesaj": "İlçe güncellendi."}

@app.delete("/ilceler/{ilce_id}")
def ilce_sil(ilce_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ilce WHERE IlceID = %s", (ilce_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "İlçe silindi."}

# Veri Modeli
class TipTurModel(BaseModel):
    TipAd: str

# 1. EKLE (Create)
@app.post("/tipturler")
def tip_ekle(tip: TipTurModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO TipTur (TipAd) VALUES (%s)", (tip.TipAd,))
    conn.commit()
    conn.close()
    return {"mesaj": "Tip türü eklendi."}

# 2. ARA/LİSTELE (Read)
@app.get("/tipturler")
def tipleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TipID, TipAd FROM TipTur ORDER BY TipID ASC")
    veri = cursor.fetchall()
    conn.close()
    return [{"TipID": r[0], "TipAd": r[1]} for r in veri]

# 3. GÜNCELLE (Update)
@app.put("/tipturler/{tip_id}")
def tip_guncelle(tip_id: int, tip: TipTurModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE TipTur SET TipAd = %s WHERE TipID = %s", (tip.TipAd, tip_id))
    conn.commit()
    conn.close()
    return {"mesaj": "Tip türü güncellendi."}

# 4. SİL (Delete)
@app.delete("/tipturler/{tip_id}")
def tip_sil(tip_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TipTur WHERE TipID = %s", (tip_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Tip türü silindi."}

# 1. Veri Modeli
class AboneModel(BaseModel):
    Ad: str
    Soyad: str
    Ilce: int
    Sube: int
    AboneTuru: int
    TarifeTuru: int
    SayacID: int

# 2. Abone Ekle
@app.post("/aboneler")
def abone_ekle(abone: AboneModel):
    from datetime import date
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Abone ambarı ID'sini bul
    cursor.execute("SELECT AmbarID FROM Ambarlar WHERE AmbarAd = 'Abone Ambarı'")
    abone_ambar_id = cursor.fetchone()[0]
    
    # Seçilen sayacın eski verilerini çek
    cursor.execute("SELECT s.SayacAmbari, a.AmbarAd, s.IslemTarihi, s.LogHaritasi FROM Sayaclar s LEFT JOIN Ambarlar a ON s.SayacAmbari = a.AmbarID WHERE s.SayacID = %s", (abone.SayacID,))
    eski_veri = cursor.fetchone()
    
    eski_ambar_id = eski_veri[0]
    mevcut_loglar = json.loads(eski_veri[3]) if eski_veri[3] else []
    
    # Sayacın son durumunu loga ekle
    mevcut_loglar.append({"Ambar": eski_veri[1], "Tarih": str(eski_veri[2])})
    
    # Sayacın güncel durumunu Abone Ambarı yap, tarihini bugün yap ve log haritasını kaydet
    cursor.execute("UPDATE Sayaclar SET SayacAmbari = %s, EskiAmbari = %s, IslemTarihi = %s, LogHaritasi = %s WHERE SayacID = %s", 
                   (abone_ambar_id, eski_ambar_id, date.today(), json.dumps(mevcut_loglar), abone.SayacID))
    
    # Aboneyi kaydet
    sorgu = "INSERT INTO Abone (Ad, Soyad, Ilce, Sube, AboneTuru, TarifeTuru, SayacID) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING AboneNumarasi"
    cursor.execute(sorgu, (abone.Ad, abone.Soyad, abone.Ilce, abone.Sube, abone.AboneTuru, abone.TarifeTuru, abone.SayacID))
    
    conn.commit()
    conn.close()
    return {"mesaj": "Abone eklendi ve sayaç transfer edildi."}

# 3. Abone Listele (Sorgu ve Return Tam İstediğin Sırada)
@app.get("/aboneler")
def aboneleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sorgu = """
    SELECT 
        a.AboneNumarasi, 
        a.Ad, 
        a.Soyad, 
        a.Ilce, i.IlceAd, 
        a.Sube, sub.SubeAd,
        a.AboneTuru, atur.Tur,
        a.TarifeTuru, t.TarifeAd, 
        a.SayacID, s.SayacAd 
    FROM Abone a
    LEFT JOIN Ilce i ON a.Ilce = i.IlceID
    LEFT JOIN Subeler sub ON a.Sube = sub.SubeID
    LEFT JOIN AboneTurleri atur ON a.AboneTuru = atur.TurID
    LEFT JOIN Tarifeler t ON a.TarifeTuru = t.TarifeID
    LEFT JOIN Sayaclar s ON a.SayacID = s.SayacID
    ORDER BY a.AboneNumarasi ASC
    """
    
    cursor.execute(sorgu)
    veri = cursor.fetchall()
    conn.close()
    
    return [{
        "AboneNumarasi": r[0], 
        "Ad": r[1], 
        "Soyad": r[2], 
        "IlceID": r[3], "IlceAd": r[4], 
        "SubeID": r[5], "SubeAd": r[6],
        "AboneTuruID": r[7], "AboneTuruAd": r[8],
        "TarifeID": r[9], "TarifeAd": r[10], 
        "SayacID": r[11], "SayacAd": r[12]
    } for r in veri]

# 4. Abone Güncelle
@app.put("/aboneler/{abone_numarasi}")
def abone_guncelle(abone_numarasi: str, abone: AboneModel):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT AmbarID FROM Ambarlar WHERE AmbarAd = 'Abone Ambarı'")
    abone_ambar_id = cursor.fetchone()[0]

    # Mevcut sayacı bul
    cursor.execute("SELECT SayacID FROM Abone WHERE AboneNumarasi = %s", (abone_numarasi,))
    eski_sayac_id = cursor.fetchone()[0]

    # Eğer sayaç değiştirilmişse: Eski sayacı iade et, yeni sayacı Abone Ambarına al
    if eski_sayac_id != abone.SayacID:
        # Eski sayacı önceki ambarına iade et
        cursor.execute("UPDATE Sayaclar SET SayacAmbari = EskiAmbari, EskiAmbari = NULL WHERE SayacID = %s", (eski_sayac_id,))

        # Yeni sayacın şu anki ambarını al ve Abone Ambarı'na taşı
        cursor.execute("SELECT SayacAmbari FROM Sayaclar WHERE SayacID = %s", (abone.SayacID,))
        yeni_sayacin_eski_ambari = cursor.fetchone()[0]

        cursor.execute("UPDATE Sayaclar SET SayacAmbari = %s, EskiAmbari = %s WHERE SayacID = %s",
                       (abone_ambar_id, yeni_sayacin_eski_ambari, abone.SayacID))

    sorgu = """
    UPDATE Abone SET 
        Ad = %s, Soyad = %s, Ilce = %s, Sube = %s, AboneTuru = %s, TarifeTuru = %s, SayacID = %s 
    WHERE AboneNumarasi = %s
    """
    cursor.execute(sorgu, (abone.Ad, abone.Soyad, abone.Ilce, abone.Sube, abone.AboneTuru, abone.TarifeTuru, abone.SayacID, abone_numarasi))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone güncellendi."}

# 5. Abone Sil
@app.delete("/aboneler/{abone_numarasi}")
def abone_sil(abone_numarasi: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Abone silinirken üzerindeki sayacı bul ve eski ambarına iade et
    cursor.execute("SELECT SayacID FROM Abone WHERE AboneNumarasi = %s", (abone_numarasi,))
    sayac_row = cursor.fetchone()
    if sayac_row:
        eski_sayac_id = sayac_row[0]
        cursor.execute("UPDATE Sayaclar SET SayacAmbari = EskiAmbari, EskiAmbari = NULL WHERE SayacID = %s", (eski_sayac_id,))

    cursor.execute("DELETE FROM Abone WHERE AboneNumarasi = %s", (abone_numarasi,))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone silindi ve sayaç depoya iade edildi."}

# Sözleşme Veri Modeli
class SozlesmeModel(BaseModel):
    AboneNumarasi: str
    SozlesmeTarihi: date
    Durum: bool
    SubeID: int

@app.post("/sozlesmeler")
def sozlesme_ekle(s: SozlesmeModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Önce abone var mı kontrol et
    cursor.execute("SELECT AboneNumarasi FROM Abone WHERE AboneNumarasi = %s", (s.AboneNumarasi,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Abone bulunamadı!")
    
    cursor.execute("""
        INSERT INTO SozlesmeBilgisi (AboneNumarasi, SozlesmeTarihi, Durum, SubeID) 
        VALUES (%s, %s, %s, %s)
    """, (s.AboneNumarasi, s.SozlesmeTarihi, s.Durum, s.SubeID))
    conn.commit()
    conn.close()
    return {"mesaj": "Sözleşme eklendi."}

@app.get("/sozlesmeler")
def sozlesmeleri_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Abone ve Şube isimlerini JOIN ile çekiyoruz
    sorgu = """
    SELECT s.SozlesmeNo, s.AboneNumarasi, a.Ad, a.Soyad, s.SozlesmeTarihi, s.Durum, sub.SubeAd, s.SubeID
    FROM SozlesmeBilgisi s
    LEFT JOIN Abone a ON s.AboneNumarasi = a.AboneNumarasi
    LEFT JOIN Subeler sub ON s.SubeID = sub.SubeID
    ORDER BY s.SozlesmeNo ASC
    """
    cursor.execute(sorgu)
    veri = cursor.fetchall()
    conn.close()
    return [{"SozlesmeNo": r[0], "AboneNo": r[1], "AdSoyad": f"{r[2]} {r[3]}", "Tarih": str(r[4]), "Durum": r[5], "SubeAd": r[6], "SubeID": r[7]} for r in veri]

@app.delete("/sozlesmeler/{no}")
def sozlesme_sil(no: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SozlesmeBilgisi WHERE SozlesmeNo = %s", (no,))
    conn.commit()
    conn.close()
    return {"mesaj": "Sözleşme silindi."}

class AmbarModel(BaseModel):
    AmbarAd: str

@app.post("/ambarlar")
def ambar_ekle(ambar: AmbarModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Ambarlar (AmbarAd) VALUES (%s)", (ambar.AmbarAd,))
    conn.commit()
    conn.close()
    return {"mesaj": "Ambar eklendi."}

@app.get("/ambarlar")
def ambarlari_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AmbarID, AmbarAd FROM Ambarlar ORDER BY AmbarID ASC")
    veri = cursor.fetchall()
    conn.close()
    return [{"AmbarID": r[0], "AmbarAd": r[1]} for r in veri]

@app.put("/ambarlar/{ambar_id}")
def ambar_guncelle(ambar_id: int, ambar: AmbarModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Ambarlar SET AmbarAd = %s WHERE AmbarID = %s", (ambar.AmbarAd, ambar_id))
    conn.commit()
    conn.close()
    return {"mesaj": "Ambar güncellendi."}

@app.delete("/ambarlar/{ambar_id}")
def ambar_sil(ambar_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Ambarlar WHERE AmbarID = %s", (ambar_id,))
    conn.commit()
    conn.close()
    return {"mesaj": "Ambar silindi."}

# Sadece bu kalsın (en altta):
app.mount("/static", StaticFiles(directory="."), name="static")