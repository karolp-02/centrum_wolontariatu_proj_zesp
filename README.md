# Centrum wolontariatu
Projekt zespołowy - Karol Przybyłowski, Maksym Kovalchuk, Szymon Drdzeń

# Setup
#### 1. Clone the repository
```bash
git clone https://github.com/karolp-02/centrum_wolontariatu_proj_zesp.git wolontariat
cd wolontariat
```
#### 2. Copy the environment config
```bash
cp .env.example .env
```
#### 3. Edit `.env` with your own values

#### 4. Start the application
```bash
docker-compose up -d
```

#### 5. Open http://localhost:8000 in your browser

# Test data

*Testowe konta z różnymi rolami*
#### Wolontariusz

Email: jan.kowalski@example.com Hasło: haslo123
#### Koordynator

Email: anna.nowak@szkola.pl Hasło: haslo123
#### Organizacja

Email: piotr@fundacja.pl Hasło: haslo123
