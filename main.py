from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import psycopg2
from fastapi import HTTPException
import json
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Abone Yönetim Sistemi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://neondb_owner:npg_2QNMScor8GHy@ep-restless-lab-aswidi9l-pooler.c-4.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.post("/login")
def login(kullanici: dict):
    # Sunucu tarafında okunan değerleri loglara yazdıralım
    sistem_mail = os.getenv("KULLANICI_1_MAIL")
    print(f"DEBUG - Gelen Mail: {kullanici['mail']}, Sistemdeki Mail: {sistem_mail}")
    
    if kullanici["mail"] == sistem_mail and kullanici["sifre"] == os.getenv("KULLANICI_1_SIFRE"):
        return {"durum": "basarili"}
    
    app.mount("/static", StaticFiles(directory="."), name="static")
    
    raise HTTPException(status_code=401, detail="Hatalı giriş!")

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

@app.post("/sayaclar")
def sayac_ekle(sayac: SayacModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Sayaclar (SayacAd, SayacTipTuru) VALUES (%s, %s)", (sayac.SayacAd, sayac.SayacTipTuru))
    conn.commit()
    conn.close()
    return {"mesaj": "Sayaç eklendi."}

@app.get("/sayaclar")
def sayaclari_getir():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # INNER JOIN ile Sayaclar ve TipTur tablolarını birleştiriyoruz
    sorgu = """
    SELECT Sayaclar.SayacID, Sayaclar.SayacAd, Sayaclar.SayacTipTuru, TipTur.TipAd 
    FROM Sayaclar 
    INNER JOIN TipTur ON Sayaclar.SayacTipTuru = TipTur.TipID 
    ORDER BY Sayaclar.SayacID ASC
    """
    
    cursor.execute(sorgu)
    veri = cursor.fetchall()
    conn.close()
    
    # JSON verisine 'TipAd' (r[3]) bilgisini de ekliyoruz
    return [{"SayacID": r[0], "SayacAd": r[1], "SayacTipTuru": r[2], "TipAd": r[3]} for r in veri]

@app.put("/sayaclar/{sayac_id}")
def sayac_guncelle(sayac_id: int, sayac: SayacModel):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Sayaclar SET SayacAd = %s, SayacTipTuru = %s WHERE SayacID = %s", (sayac.SayacAd, sayac.SayacTipTuru, sayac_id))
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
    conn = get_db_connection()
    cursor = conn.cursor()
    sorgu = """
    INSERT INTO Abone (Ad, Soyad, Ilce, Sube, AboneTuru, TarifeTuru, SayacID) 
    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING AboneNumarasi
    """
    cursor.execute(sorgu, (abone.Ad, abone.Soyad, abone.Ilce, abone.Sube, abone.AboneTuru, abone.TarifeTuru, abone.SayacID))
    yeni_abone_no = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return {"mesaj": "Abone eklendi.", "AboneNumarasi": yeni_abone_no}

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
    cursor.execute("DELETE FROM Abone WHERE AboneNumarasi = %s", (abone_numarasi,))
    conn.commit()
    conn.close()
    return {"mesaj": "Abone silindi."}

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