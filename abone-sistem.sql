CREATE TABLE AboneTurleri (
    TurID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Tur VARCHAR(50)
)

CREATE TABLE Ilce (
    IlceID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    IlceAd VARCHAR(10)
)

CREATE TABLE Subeler (
    SubeID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SubeAd VARCHAR(60) UNIQUE,
    SubeIlce INT,
    CONSTRAINT Ilce FOREIGN KEY (SubeIlce) REFERENCES Ilce(IlceID)
)

CREATE TABLE TipTur (
    TipID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TipAd VARCHAR(50)
)

CREATE TABLE Sayaclar (
    SayacID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SayacAd VARCHAR(30),
    SayacTipTuru INT,
    CONSTRAINT Syctt FOREIGN KEY (SayacTipTuru) REFERENCES TipTur(TipID)
)

CREATE SEQUENCE sozlesme_id_seq START 1;

CREATE TABLE SozlesmeBilgisi (
    id_num_soz INT DEFAULT nextval('sozlesme_id_seq'),
    SozlesmeNo VARCHAR(20) GENERATED ALWAYS AS (
        'S' || LPAD(id_num_soz::text, 9, '0')
    ) STORED PRIMARY KEY,
    AboneNumarasi VARCHAR(20),
    CONSTRAINT AbNum FOREIGN KEY (AboneNumarasi) REFERENCES Abone(AboneNumarasi),
    SozlesmeTarihi DATE,
    Durum BOOLEAN,
    AboneTuru INT,
    CONSTRAINT AbTur FOREIGN KEY (AboneTuru) REFERENCES AboneTurleri(TurID)
)

CREATE SEQUENCE personeller_id_seq START 1;

CREATE TABLE Abone (
    id_num INT DEFAULT nextval('personeller_id_seq'),
    AboneNumarasi VARCHAR(20) GENERATED ALWAYS AS (
        'ISU' || LPAD(id_num::text, 9, '0')
    ) STORED PRIMARY KEY,
    Ad VARCHAR(50),
    Soyad VARCHAR(50),
    Ilce INT,
    CONSTRAINT Ilce FOREIGN KEY (Ilce) REFERENCES Ilce(IlceID),
    SayacID INT,
    CONSTRAINT Syc FOREIGN KEY (SayacID) REFERENCES Sayaclar(SayacID),
    TarifeTuru INT,
    CONSTRAINT Trf FOREIGN KEY (TarifeTuru) REFERENCES Tarifeler(TarifeID)
)

ALTER TABLE Abone
ADD Sube INT

ALTER TABLE Abone
ADD CONSTRAINT Sb FOREIGN KEY (Sube) REFERENCES Subeler(SubeID)

CREATE TABLE Tarifeler (
    TarifeID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TarifeAd VARCHAR(50),
    TarifeUcret FLOAT
)