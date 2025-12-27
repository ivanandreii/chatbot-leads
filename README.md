# Chatbot Leads

Un proiect simplu de chatbot pentru o afacere mică. Oferă răspunsuri rapide despre program, locație, servicii și prețuri și colectează lead-uri atunci când utilizatorul dorește o programare.

## Structura proiectului
- `app/main.py` – aplicația FastAPI: definește endpointul `/chat`, logica chatbotului și salvarea lead-urilor.
- `data/leads.json` – fișierul în care se salvează lead-urile (format JSON). Se creează automat dacă lipsește.
- `static/index.html` – un widget web simplu pentru a testa chatbotul direct din browser.
- `requirements.txt` – dependențele Python necesare pentru a rula proiectul.

## Cum rulezi local
1. Creează și activează un mediu virtual (opțional dar recomandat):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Instalează dependențele:
   ```bash
   pip install -r requirements.txt
   ```
3. Pornește serverul FastAPI cu Uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Deschide interfața web la `http://localhost:8000/static/index.html` dacă servești fișierele statice sau folosește direct endpointul `/chat` cu un client HTTP (ex: curl, Postman).

> Notă: Pentru a servi fișierele statice, poți porni un server simplu din directorul `static` (ex: `python -m http.server 8000`) sau configura FastAPI să expună fișierele statice. În timpul dezvoltării, deschiderea directă a fișierului `static/index.html` în browser este suficientă.

## Cum funcționează chatbotul
- Caută cuvinte cheie în mesaj pentru a răspunde despre:
  - **program**: programul de lucru.
  - **locatie**: adresa afacerii.
  - **servicii**: lista de servicii oferite.
  - **preturi**: exemple de prețuri.
- Pentru intenția de **programare** (cuvinte precum „programare”, „rezervare”, „book”):
  - Cere nume, telefon și serviciu dorit dacă lipsesc.
  - Când primește toate câmpurile, salvează lead-ul în `data/leads.json` și confirmă programarea.

## Exemplu de apel API
```
POST /chat
Content-Type: application/json

{
  "message": "Vreau o programare",
  "name": "Ana Pop",
  "phone": "0712345678",
  "service": "Tuns"
}
```

Răspuns:
```
{
  "reply": "Mulțumim! Am înregistrat programarea pentru serviciul Tuns pe numele Ana Pop. Te vom contacta la 0712345678.",
  "intent": "booking",
  "requested_fields": []
}
```

## Explicație pe scurt pentru începători
- **FastAPI**: framework web în Python care permite crearea rapidă de endpointuri HTTP.
- **Endpoint `/chat`**: primește un mesaj și, opțional, detalii pentru programare. Răspunde cu un text și informații despre ce a înțeles (intent).
- **Lead-uri**: când utilizatorul oferă nume, telefon și serviciu dorit, datele se salvează în `data/leads.json` pentru a putea fi contactat ulterior.
- **Interfața HTML**: `static/index.html` face un request AJAX la `/chat` și afișează dialogul în pagină.
