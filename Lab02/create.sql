CREATE DATABASE "HD_Zlecenia" COLLATE Latin1_General_100_CI_AS_KS_SC_UTF8;
GO
USE "HD_Zlecenia";

CREATE TABLE "Gabaryty" (
	"ID_gabarytu" INT PRIMARY KEY,
	"Opis" NVARCHAR(20) NOT NULL,
	"Wymiar_X" INT NOT NULL CONSTRAINT "Wymiar_X" CHECK ("Wymiar_X" BETWEEN 1 AND 9999),
	"Wymiar_Y" INT NOT NULL CONSTRAINT "Wymiar_Y" CHECK ("Wymiar_Y" BETWEEN 1 AND 9999),
	"Wymiar_Z" INT NOT NULL CONSTRAINT "Wymiar_Z" CHECK ("Wymiar_Z" BETWEEN 1 AND 9999),
	"Marza" DECIMAL(5,2) NOT NULL CONSTRAINT "Marza" CHECK ("Marza" > 0)
);

CREATE TABLE "Placowki" (
	"ID_placowki" INT PRIMARY KEY,
	"Adres_placowki" NVARCHAR(250) NOT NULL,
	"Is_centrum_dystrybucyjne" BIT NOT NULL
)

CREATE TABLE "Statusy" (
	"ID_statusu" INT PRIMARY KEY,
	"Opis_statusu" NVARCHAR(12) NOT NULL
)

CREATE TABLE "Zlecenia" (
	"ID_zlecenia" INT PRIMARY KEY,
	"Nazwa_zamawiajacego" NVARCHAR(250) NOT NULL,
	"Tel_zamawiajacego" CHAR(12) NOT NULL CONSTRAINT "Tel_zamawiajacego" CHECK (Tel_zamawiajacego LIKE '+[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
	"Adres_nadania" NVARCHAR(250),
	"Adres_odbioru" NVARCHAR(250),
	"Punkt_nadania" INT,
	"Punkt_odbioru" INT,
	"Gabaryt" INT NOT NULL,
	"Cena" MONEY NOT NULL,
	"Nr_factury" CHAR(10) NOT NULL,
	"Status" INT NOT NULL,
	"Data_przyjecia" DATE NOT NULL,
	"Data_zakonczenia" DATE NOT NULL,
	FOREIGN KEY ("Punkt_nadania") REFERENCES "Placowki"("ID_placowki"),
	FOREIGN KEY ("Punkt_odbioru") REFERENCES "Placowki"("ID_placowki"),
	FOREIGN KEY ("Gabaryt") REFERENCES "Gabaryty"("ID_gabarytu"),
	FOREIGN KEY ("Status") REFERENCES "Statusy"("ID_statusu"),
	CONSTRAINT "Miejsce nadania" CHECK ("Adres_nadania" IS NOT NULL OR "Punkt_nadania" IS NOT NULL),
	CONSTRAINT "Miejsce odbioru" CHECK ("Adres_odbioru" IS NOT NULL OR "Punkt_odbioru" IS NOT NULL),
)

CREATE TABLE "TransportyZlecenia" (
	"ID_zlecenia" INT,
	"ID_transportu" INT,
	"Data_poczatek" DATE NOT NULL,
	"Data_koniec" DATE NOT NULL,
	"Skad" INT,
	"Dokad" INT,
	PRIMARY KEY ("ID_zlecenia", "ID_transportu"),
	FOREIGN KEY ("ID_zlecenia") REFERENCES "Zlecenia"("ID_zlecenia"),
	FOREIGN KEY ("Skad") REFERENCES "Placowki"("ID_placowki"),
	FOREIGN KEY ("Dokad") REFERENCES "Placowki"("ID_placowki"),
	CONSTRAINT "Miejsca" CHECK (("Skad" IS NOT NULL OR "Dokad" IS NOT NULL) AND "Skad" <> "Dokad")
)