from wolontariat.models import Organizacja, Uzytkownik, Projekt, Oferta, Zlecenie, Wiadomosc, Recenzja
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

# --- Wyczyść istniejące dane ---
print("Czyszczenie bazy danych...")
Recenzja.objects.all().delete()
Wiadomosc.objects.all().delete()
Zlecenie.objects.all().delete()
Oferta.objects.all().delete()
Projekt.objects.all().delete()
Uzytkownik.objects.all().delete()
Organizacja.objects.all().delete()

# --- Organizacje ---
print("Tworzenie organizacji...")
org_fundacja = Organizacja.objects.create(
    nazwa_organizacji="Fundacja Serce dla Zwierząt",
    nr_telefonu="501123456",
    nip="1234567890",
    weryfikacja=True
)

# --- Użytkownicy ---
print("Tworzenie użytkowników...")

# Organization Admin (Piotr)
piotr = Uzytkownik.objects.create(
    username="Piotr Zieliński",
    email="piotr@fundacja.pl",
    nr_telefonu="600100100",
    organizacja=org_fundacja,
    rola="organizacja",
    password=make_password("haslo123")
)

# Coordinator (Anna)
anna = Uzytkownik.objects.create(
    username="Anna Nowak",
    email="anna.nowak@szkola.pl",
    nr_telefonu="600200200",
    rola="koordynator",
    password=make_password("haslo123")
)

# Volunteer 1 (Jan)
jan = Uzytkownik.objects.create(
    username="Jan Kowalski",
    email="jan.kowalski@example.com",
    nr_telefonu="600300300",
    rola="wolontariusz",
    wiek=22,
    password=make_password("haslo123")
)

# Volunteer 2 (Kasia)
kasia = Uzytkownik.objects.create(
    username="Kasia Wiśniewska",
    email="kasia.wisniewska@gmail.com",
    nr_telefonu="600400400",
    rola="wolontariusz",
    wiek=17,
    password=make_password("haslo123")
)

# --- Projekty ---
print("Tworzenie projektu zakończonego...")
proj_zima = Projekt.objects.create(
    organizacja=org_fundacja,
    nazwa_projektu="Zbiórka Zimowa 2024",
    opis_projektu="Coroczna akcja zbiórki karmy, koców i zabawek dla podopiecznych schroniska przed nadejściem zimy."
)


oferta_sortowanie = Oferta.objects.create(
    organizacja=org_fundacja,
    projekt=proj_zima,
    tytul_oferty="Sortowanie darów w magazynie",
    lokalizacja="Kraków, Magazyn Centralny",
    data=timezone.now().date() - timedelta(days=30), # 1 month ago
    tematyka="Logistyka",
    czas_trwania="6h",
    wymagania="Dokładność, umiejętność pracy w zespole.",
    czy_ukonczone=True, # Offer is closed globally
    wolontariusz=jan   # Legacy field support
)

Zlecenie.objects.create(
    oferta=oferta_sortowanie,
    wolontariusz=jan,
    czy_potwierdzone=True, # He was accepted
    czy_ukonczone=True     # He finished the job
)

Recenzja.objects.create(
    organizacja=org_fundacja,
    wolontariusz=jan,
    oferta=oferta_sortowanie,
    ocena=5,
    komentarz="Janek to wzorowy wolontariusz! Bardzo sprawnie zorganizował segregację darów. Polecamy!"
)

print("Tworzenie projektu aktywnego...")
proj_schronisko = Projekt.objects.create(
    organizacja=org_fundacja,
    nazwa_projektu="Wsparcie Schroniska - Wiosna",
    opis_projektu="Bieżąca pomoc w wyprowadzaniu psów i pracach porządkowych w sezonie wiosennym."
)

oferta_spacery = Oferta.objects.create(
    organizacja=org_fundacja,
    projekt=proj_schronisko,
    tytul_oferty="Weekendowe spacery z psami",
    lokalizacja="Kraków, Schronisko ul. Rybna",
    data=timezone.now().date() + timedelta(days=2), # In 2 days
    tematyka="Opieka nad zwierzętami",
    czas_trwania="3h",
    wymagania="Brak alergii, ukończone szkolenie BHP (zapewniamy na miejscu).",
    czy_ukonczone=False
)

Zlecenie.objects.create(
    oferta=oferta_spacery,
    wolontariusz=kasia,
    czy_potwierdzone=True,
    czy_ukonczone=False
)

oferta_sprzatanie = Oferta.objects.create(
    organizacja=org_fundacja,
    projekt=proj_schronisko,
    tytul_oferty="Pomoc przy renowacji bud",
    lokalizacja="Kraków, Schronisko ul. Rybna",
    data=timezone.now().date() + timedelta(days=5),
    tematyka="Prace manualne",
    czas_trwania="4h",
    wymagania="Chęci do pracy fizycznej, ubrania robocze.",
    czy_ukonczone=False
)
print("Tworzenie wiadomości...")
Wiadomosc.objects.create(
    nadawca=jan,
    odbiorca=piotr,
    tresc="Dzień dobry, dziękuję za super atmosferę podczas zbiórki!"
)
Wiadomosc.objects.create(
    nadawca=piotr,
    odbiorca=jan,
    tresc="Dzięki Janek! Liczymy na Ciebie przy kolejnych akcjach."
)

print("Wszystkie dane testowe zostały pomyślnie utworzone!")
