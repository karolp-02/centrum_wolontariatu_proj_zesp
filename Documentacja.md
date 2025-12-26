# Wolontariat — Dokumentacja projektu

Spis treści
- [Opis projektu](#opis-projektu)
- [Struktura repozytorium (skrót)](#struktura-repozytorium-skrót)
- [Szybkie uruchomienie (deweloper / admin)](#szybkie-uruchomienie-deweloper--admin)
  - [Wymagania wstępne](#wymagania-wstępne)
  - [Uruchomienie z Docker Compose (zalecane)](#uruchomienie-z-docker-compose-zalecane)
  - [Zadania po uruchomieniu (migracje, dane testowe, superuser)](#zadania-po-uruchomieniu-migracje-dane-testowe-superuser)
- [Konfiguracja środowiska](#konfiguracja-środowiska)
  - [Plik `.env`](#plik-env)
  - [Frontend — zmienne Vite](#frontend---zmienne-vite)
- [Role i przepływy użytkownika (krótkie)](#role-i-przepływy-użytkownika-krótkie)
  - [Wolontariusz](#wolontariusz)
  - [Organizacja](#organizacja)
  - [Koordynator](#koordynator)
- [Instrukcja dla administratora](#instrukcja-dla-administratora)
  - [1. Przygotowanie i uruchomienie środowiska](#1-przygotowanie-i-uruchomienie-środowiska)
  - [2. Tworzenie superużytkownika i dostęp do panelu admina](#2-tworzenie-superużytkownika-i-dostęp-do-panelu-admina)
  - [3. Zarządzanie danymi testowymi i seed](#3-zarządzanie-danymi-testowymi-i-seed)
  - [4. Bieżące zadania administracyjne](#4-bieżące-zadania-administracyjne)
  - [5. Konfiguracja PDF i fontów](#5-konfiguracja-pdf-i-fontów)
  - [6. Backup i baza danych](#6-backup-i-baza-danych)
- [Instrukcja dla użytkownika końcowego](#instrukcja-dla-użytkownika-końcowego)
  - [Rejestracja i logowanie](#rejestracja-i-logowanie)
  - [Wolontariusz — jak aplikować i pobierać certyfikaty](#wolontariusz---jak-aplikować-i-pobierać-certyfikaty)
  - [Organizacja — publikacja i zarządzanie ofertą](#organizacja---publikacja-i-zarządzanie-ofertą)
  - [Koordynator — obsługa projektów](#koordynator---obsługa-projektów)
  - [Recenzje i oceny](#recenzje-i-oceny)
- [API — przegląd istotnych punktów końcowych](#api---przegląd-istotnych-punktów-końcowych)
- [Najczęstsze problemy i ich rozwiązania](#najczęstsze-problemy-i-ich-rozwiązania)
- [Przydatne pliki i miejsca w repozytorium](#przydatne-pliki-i-miejsca-w-repozytorium)
- [Licencja i kontakt](#licencja-i-kontakt)

---

## Opis projektu

Wolontariat to aplikacja (backend w Django + REST, frontend w React/Vite) do zarządzania ofertami wolontariatu, projektami i przypisywania wolontariuszy. Umożliwia:
- tworzenie projektów i ofert przez organizacje / koordynatorów,
- zgłaszanie się wolontariuszy (pojedyncze lub wieloosobowe uczestnictwo),
- przypisywanie i zatwierdzanie uczestników,
- generowanie zaświadczeń PDF po zakończeniu oferty,
- wystawianie recenzji (organizacje → wolontariusze).

---

## Struktura repozytorium (skrót)

- `backend/` — kod Django (Dockerfile, `manage.py` itd.)
  - `wolontariat/` — app + `models.py`, `pdf_utils.py`, `seed.py`, `settings.py`, migracje
  - `api/` — REST API (serializers, views, urls)
- `frontend/` — aplikacja React + Vite (TypeScript)
- `docker-compose.yml` — konfiguracja usług: `backend`, `frontend`, `db`

Ważne: w projekcie autorsko zmodyfikowany model użytkownika `Uzytkownik` i model `Oferta`, `Zlecenie`, `Recenzja` (zmiany migracji widoczne w katalogu `migrations/`).

---

## Szybkie uruchomienie (deweloper / admin)

### Wymagania wstępne
- Docker + Docker Compose
- (opcjonalnie) lokalne Python / Node.js do pracy bez kontenerów

### Uruchomienie z Docker Compose (zalecane)
1. Sklonuj repo:
   - `git clone <repo-url>`
2. Przejdź do katalogu projektu:
   - `cd wolontariat`
3. Skopiuj przykładowy plik `.env`:
   - `cp .env.example .env`
   - Dostosuj wartości (opcjonalnie).
4. Uruchom kontenery:
   - `docker-compose up -d`
5. Zainicjuj bazę i dane:
   - `docker-compose exec backend python manage.py migrate`
   - (opcjonalnie) `docker-compose exec backend python manage.py loaddata <plik.json>` — jeśli używasz dumpów
6. Utwórz superużytkownika:
   - `docker-compose exec backend python manage.py createsuperuser`
7. (Opcjonalnie) załaduj dane testowe:
   - `docker-compose exec backend python manage.py shell -c "from wolontariat.seed import seed_data; seed_data()"`
   - W repo istnieje `seed.py` — uruchamiany skrypt tworzy kilka organizacji, użytkowników, projektów, ofert, zleceń i wiadomości.

Frontend dostępny domyślnie pod `http://localhost:3000`, backend API pod `http://localhost:8080/api/`.

### Zadania po uruchomieniu (migracje, dane testowe, superuser)
- Uruchom migracje (`manage.py migrate`).
- Utwórz `superuser` (panel admina).
- Seed danych jest przydatny do szybkich testów — sprawdź `backend/wolontariat/seed.py`.

---

## Konfiguracja środowiska

### Plik `.env`
Plik `.env` (kopiuj z `.env.example`) zawiera:
- `DEBUG` — 0/1
- `SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_*` — ustawienia połączenia z bazą

Upewnij się, że `POSTGRES_*` są zgodne z konfiguracją `docker-compose.yml` lub z Twoją bazą.

### Frontend — zmienne Vite
Frontend używa `VITE_API_URL` (zmienna środowiskowa w środowisku Vite) lub domyślnie `http://localhost:8080/api/`. Jeżeli uruchamiasz frontend niezależnie, ustaw:
- `VITE_API_URL=http://localhost:8080/api/`

W kodzie klient używa tokenu DRF w `localStorage` pod kluczem `token`.

---

## Role i przepływy użytkownika (krótkie)

### Wolontariusz
- Rejestracja: wymaga `wiek`.
- Może przeglądać oferty, aplikować, wycofywać zgłoszenie.
- Po przypisaniu i zakończeniu oferty może pobrać certyfikat PDF (`/api/offers/{id}/certificate/` albo `/api/auth/certificate/`).

### Organizacja
- Publikuje projekty i oferty.
- Przypisuje wolontariuszy, zatwierdza ukończenie.
- Wystawia recenzje (tylko organizacja może tworzyć recenzje w modelu).

### Koordynator
- Podobne uprawnienia jak organizacja w niektórych miejscach — może tworzyć projekty i oferty.

---

## Instrukcja dla administratora

### 1. Przygotowanie i uruchomienie środowiska
- Postępuj zgodnie z sekcją "Szybkie uruchomienie".
- Sprawdź logi backendu: `docker-compose logs -f backend`.
- Jeżeli aplikacja nie łączy się z bazą, upewnij się, że kontener `db` jest zdrowy (`docker ps`, `docker logs postgres-db`).

### 2. Tworzenie superużytkownika i dostęp do panelu admina
- `docker-compose exec backend python manage.py createsuperuser`
- Panel admin: `http://localhost:8080/admin/`

W panelu admin możesz:
- przeglądać/edycję modeli: `Organizacja`, `Uzytkownik`, `Projekt`, `Oferta`, `Zlecenie`, `Recenzja`, `Wiadomosc`.

### 3. Zarządzanie danymi testowymi i seed
- Skrypt `wolontariat/seed.py` tworzy dane testowe. Możesz go uruchomić z `manage.py shell` (patrz wyżej).
- Jeśli chcesz resetować dane: wykonaj kolejno usuwanie i migracje lub zrzut/restore bazy.

### 4. Bieżące zadania administracyjne
- Weryfikacja organizacji: pole `Organizacja.weryfikacja` domyślnie ustawiane, jeśli NIP istnieje.
- Monitorowanie zleceń i recenzji: recenzje mają unikalność (`oferta`, `organizacja`) — usunięcie recenzji należy robić ostrożnie.
- Zarządzanie tokenami: DRF Token w modelu `authtoken`.

### 5. Konfiguracja PDF i fontów
- PDF generowany przez `reportlab`. Projekt zawiera `pdf_utils.py`, który rejestruje czcionki TTF (DejaVu/Liberation etc.) — sprawdź potencjalne ścieżki w systemie.
- Możesz ustawić zmienne środowiskowe `PDF_FONT_REGULAR` i `PDF_FONT_BOLD`, aby wymusić konkretne pliki TTF (przydatne w produkcji, by mieć poprawne polskie znaki).
- Jeśli PDF ma problemy z diakrytykami, upewnij się, że w kontenerze backendu zainstalowane są czcionki (Dockerfile instaluje `fonts-dejavu-core`, `fonts-liberation`).

### 6. Backup i baza danych
- Backup bazy Postgres: `pg_dump` z hosta lub użyj wolumenów Dockera.
- W `docker-compose.yml` używany jest wolumen `postgres_data`. Przechowuj kopie lub używaj zewnętrznych mechanizmów backupu.

---

## Instrukcja dla użytkownika końcowego

Poniżej krótkie, praktyczne wskazówki dla trzech głównych ról.

### Rejestracja i logowanie
- Wejdź na frontend (`/register`), wybierz typ konta: `wolontariusz`, `koordynator`, `organizacja`.
- Wolontariusze muszą podać `wiek` — system automatycznie ustali `czy_maloletni`.
- Po rejestracji otrzymasz token (zapisany w `localStorage`) i przekierowanie do panelu.

### Wolontariusz — jak aplikować i pobierać certyfikaty
- Przeglądaj oferty: `/volunteer/offers`.
- Aplikuj jednym przyciskiem: system doda Cię do `Zlecenie` (możliwe wieloosobowe zlecenia).
- Po zatwierdzeniu udziału przez organizację i oznaczeniu oferty jako ukończona, możesz pobrać certyfikat:
  - z poziomu listy zgłoszonych ofert — przycisk "Pobierz certyfikat" (jeśli spełnione warunki)
  - backend endpoint: `GET /api/offers/{id}/certificate/` lub `GET /api/auth/certificate/`

### Organizacja — publikacja i zarządzanie ofertą
- Tworzenie projektu → tworzenie oferty powiązanej z projektem.
- Możesz przypisać wolontariusza (akceptacja) lub użyć mechanizmu `Zlecenie` do zbiorczego dodawania uczestników.
- Po zakończeniu oferty ustaw `czy_ukonczone=True` (akcja "approve"), co pozwala wystawić recenzję i wygenerować certyfikaty.

### Koordynator — obsługa projektów
- Koordynator ma podobne uprawnienia do zarządzania projektami i ofertami; może też przeglądać listę wolontariuszy i przydzielać uczestników.

### Recenzje i oceny
- Tylko użytkownicy z rolą `organizacja` mogą tworzyć recenzje (`Recenzja`).
- Recenzje powiązane z ofertą muszą odnosić się do wolontariusza uczestniczącego w danej ofercie.
- Ocena musi być liczbą 1–5.

---

## API — przegląd istotnych punktów końcowych

- `POST /api/auth/register/` — rejestracja (pola: `username`, `email`, `password`, `rola`, `nr_telefonu`, i dodatkowo `wiek` dla wolontariusza)
- `POST /api/auth/login/` — logowanie (zwraca `token`)
- `POST /api/auth/logout/` — wylogowanie (usuwa token)
- `GET /api/auth/certificate/` — pobierz zbiorczy certyfikat użytkownika
- `GET /api/projects/`, `POST /api/projects/` — projekty
- `GET /api/offers/`, `POST /api/offers/` — oferty
  - Akcje: `POST /api/offers/{id}/apply/`, `POST /api/offers/{id}/withdraw/`, `POST /api/offers/{id}/assign/`, `GET /api/offers/{id}/certificate/`, `POST /api/offers/{id}/approve/`
- `GET /api/volunteers/` (read-only, szczegóły profilu: `GET /api/volunteers/me/`)
- `GET /api/organizations/` — organizacje
- `GET /api/reviews/`, `POST /api/reviews/` — recenzje (tworzenie z ograniczeniami; see serializer validation)

Uwaga: API używa DRF TokenAuth (nagłówek `Authorization: Token <key>`). Frontend automatycznie ustawia ten nagłówek jeżeli token jest w `localStorage`.

---

## Najczęstsze problemy i ich rozwiązania

- "PDF bez polskich znaków": upewnij się, że czcionki TTF są zainstalowane i że `pdf_utils.py` potrafi je znaleźć; ewentualnie ustaw `PDF_FONT_REGULAR` i `PDF_FONT_BOLD`.
- "Błędy migracji": usuń wolumen bazy (tylko w środowisku dev) i uruchom migracje od nowa albo przywróć dump bazy; sprawdź zgodność migracji.
- "Token wygasł/401": usuń `token` z `localStorage` i zaloguj się ponownie.
- "Brak połączenia z bazą w Dockerze": sprawdź, czy kontener `db` jest uruchomiony i czy `POSTGRES_*` są poprawnie ustawione.

---

## Przydatne pliki i miejsca w repozytorium

- Backend:
  - `backend/wolontariat/settings.py` — konfiguracja Django
  - `backend/wolontariat/models.py` — modele (Uzytkownik, Organizacja, Oferta, Zlecenie, Recenzja)
  - `backend/wolontariat/pdf_utils.py` — obsługa czcionek dla PDF
  - `backend/api/serializers.py`, `backend/api/views.py`, `backend/api/urls.py` — API
  - `backend/wolontariat/seed.py` — skrypt tworzący dane testowe
- Frontend:
  - `frontend/src/api/*` — wrappery API (offers, auth, users…)
  - `frontend/src/hooks/useAuth.tsx` — zarządzanie stanem uwierzytelnienia
  - `frontend/src/pages/*` — widoki użytkownika
  - `frontend/vite.config.ts` — konfiguracja dev serwera

---
