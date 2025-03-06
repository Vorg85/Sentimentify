# Sentimentify

Sentimentify è un'API REST sviluppata con FastAPI che analizza il sentiment di un testo. Il progetto offre due modalità principali di analisi:

## 1. Analisi Standard
Utilizza TextBlob per analizzare il sentiment (positivo, negativo o neutro) e restituire la polarità del testo.

## 2. Modello Personalizzato
Permette di addestrare un modello personalizzato utilizzando un dataset CSV locale (`src/sample.csv`) e successivamente fare previsioni sui testi. Inoltre, il sistema chiede la conferma all'utente se il risultato è come previsto; se confermato, il record (testo e sentimento) viene aggiunto al dataset.

## Tecnologie Utilizzate

- **FastAPI:** Framework per la creazione di API veloci e performanti.
- **TextBlob:** Libreria per l'analisi del sentiment e l'elaborazione del linguaggio naturale.
- **Pandas:** Utilizzato per la gestione e l'analisi dei dati.
- **scikit-learn:** Utilizzato per costruire e addestrare il modello personalizzato (pipeline con CountVectorizer e LogisticRegression).
- **Uvicorn:** Server ASGI per eseguire l'applicazione in modalità sviluppo e produzione.

## Funzionalità e Endpoints

### Analisi Standard con TextBlob

- **Endpoint:** `POST /sentiment`  
  Invia un JSON con il campo `text` e ricevi il sentiment analizzato da TextBlob.  
  **Esempio di richiesta:**
  ```json
  {
    "text": "I love this amazing project!"
  }
  ```
  La risposta include anche un messaggio di conferma che invita l'utente a utilizzare l'endpoint `/confirm` per salvare il record, se il risultato è come previsto.

### Modello Personalizzato

#### Addestramento in Background:

- **Endpoint:** `GET /train_local_bg`  
  Avvia l'addestramento del modello in background, leggendo il file CSV locale `src/sample.csv`.  
  *Nota:* Il processo avvia l'addestramento in background per evitare timeout, ed è possibile controllarne lo stato tramite l'endpoint successivo.

- **Endpoint:** `GET /train_status`  
  Consente di verificare lo stato dell'addestramento (se il training è in corso oppure restituisce il risultato con l'accuratezza sul set di test).

#### Predizione con il Modello Personalizzato:

- **Endpoint:** `POST /predict_custom`  
  Invia un JSON con il campo `text` e ricevi la predizione del sentiment basata sul modello personalizzato addestrato.
  **Esempio di richiesta:**
  ```json
  {
    "text": "Questo prodotto è fantastico!"
  }
  ```
  La risposta include un messaggio di conferma per salvare il record se il risultato è come previsto.

#### Salvataggio dei Record nel Dataset

- **Endpoint:** `POST /confirm`  
  Permette all'utente di confermare che il risultato (testo e sentimento) è corretto. Se confermato (inviando `"confirm": true`), il record viene aggiunto al file CSV locale `src/sample.csv`.
  **Esempio di richiesta:**
  ```json
  {
    "text": "Questo prodotto è fantastico!",
    "sentiment": "positivo",
    "confirm": true
  }
  ```

## Installazione

### Clona il repository:
```bash
git clone https://github.com/tuo_username/Sentimentify.git
cd Sentimentify
```

### Crea e attiva l'ambiente virtuale:

**Su Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Su Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## Esecuzione dell'Applicazione

Avvia l'applicazione con Uvicorn:
```bash
uvicorn src.main:app --reload
```

L'app sarà disponibile su [http://127.0.0.1:8000](http://127.0.0.1:8000).

Accedi alla documentazione interattiva (Swagger UI) su [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Testing

Per eseguire i test unitari utilizza pytest:
```bash
pytest tests/
```

## Considerazioni sul Deployment

- In ambiente locale, le modifiche al file `src/sample.csv` sono persistenti.
- Su piattaforme come DigitalOcean App Platform, il filesystem dei container è effimero, quindi le modifiche al dataset non sono persistenti. Per la persistenza dei dati in produzione, considera l'utilizzo di un database o di uno storage esterno.

