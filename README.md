# Sentimentify

Sentimentify è un'API REST sviluppata con FastAPI che analizza il sentiment di un testo. Il progetto offre due modalità principali di analisi:

## 1. Analisi Standard
Utilizza TextBlob per analizzare il sentiment (positivo, negativo o neutro) e restituire la polarità del testo. Se il testo non è in inglese, viene tradotto in inglese prima dell'analisi.

## 2. Modello Personalizzato
Permette di addestrare un modello personalizzato utilizzando un dataset CSV locale (`src/sample.csv`) e, successivamente, fare predizioni sui testi. Se il testo non è in inglese, viene tradotto in inglese per la predizione.  
Dopo la predizione, l'utente può confermare se il risultato è esatto o errato: se errato, l'utente specifica il sentimento atteso e il record (contenente il testo tradotto e il sentimento definitivo) viene salvato nel file CSV.

## Tecnologie Utilizzate

- **FastAPI:** Framework per la creazione di API veloci e performanti.
- **TextBlob:** Libreria per l'analisi del sentiment e l'elaborazione del linguaggio naturale.
- **deep-translator:** Per tradurre testi in inglese se necessario.
- **langdetect:** Per rilevare la lingua del testo.
- **Pandas:** Per la gestione e l'analisi dei dati.
- **scikit-learn:** Per costruire e addestrare il modello personalizzato (pipeline con CountVectorizer e LogisticRegression).
- **Uvicorn:** Server ASGI per eseguire l'applicazione.
- **Streamlit:** Per creare un'interfaccia utente interattiva per testare le API.

## Funzionalità ed Endpoints

### Analisi Standard con TextBlob
- **Endpoint:** `POST /sentiment`  
  **Descrizione:**  
  Riceve un JSON con il campo `text`. Rileva la lingua del testo e, se necessario, traduce il testo in inglese prima di analizzarlo con TextBlob.  
  **Risposta:**  
  Restituisce:
  - `sentiment`: "positivo", "negativo" o "neutro"
  - `polarity`: il valore della polarità
  - `detected_language`: la lingua rilevata
  - `confirm_message`: invito a confermare il risultato tramite l'endpoint `/confirm`

  **Esempio di richiesta:**
  ```json
  {
    "text": "Sei bellissima!"
  }
  ```

### Modello Personalizzato

#### Addestramento
- **Endpoint:** `GET /train_local_bg`  
  Avvia l'addestramento del modello in background usando il file CSV locale `src/sample.csv`.

- **Endpoint:** `GET /train_status`  
  Restituisce lo stato del training, incluso un messaggio di successo e l'accuratezza del modello addestrato.

#### Predizione
- **Endpoint:** `POST /predict_custom`  
  **Descrizione:**  
  Riceve un JSON con il campo `text`. Rileva la lingua e, se non in inglese, traduce il testo in inglese per eseguire la predizione con il modello personalizzato.
  **Risposta:**  
  Restituisce:
  - `text`: il testo originale
  - `translated_text`: il testo tradotto in inglese
  - `predicted_sentiment`: il sentimento predetto dal modello
  - `confirm_message`: invito a confermare il risultato tramite l'endpoint `/confirm`

  **Esempio di richiesta:**
  ```json
  {
    "text": "Questo prodotto è fantastico!"
  }
  ```

#### Conferma della Predizione e Salvataggio
- **Endpoint:** `POST /confirm`  
  **Descrizione:**  
  Riceve un JSON contenente:
  - `text`: il testo originale (per riferimento)
  - `translated_text`: il testo tradotto in inglese (che verrà salvato)
  - `actual_sentiment`: il sentimento predetto dal modello
  - `user_feedback`: "correct" se la predizione è esatta, "incorrect" se è errata
  - `expected_sentiment`: (obbligatorio se `user_feedback` è "incorrect") il sentimento atteso  
  **Funzione:**  
  Determina il sentimento finale da salvare (usa `actual_sentiment` se il feedback è "correct", altrimenti usa `expected_sentiment`) e appende il record (testo tradotto e sentimento) al file CSV `src/sample.csv`.

  **Esempio di richiesta:**
  ```json
  {
    "text": "Questo prodotto è fantastico!",
    "translated_text": "This product is fantastic!",
    "actual_sentiment": "positivo",
    "user_feedback": "incorrect",
    "expected_sentiment": "negativo"
  }
  ```

### Feedback (Opzionale)
- **Endpoint:** `GET /feedback`  
  Restituisce l'ultimo testo analizzato e il relativo sentimento (utile per debug).

## Interfaccia Utente (Streamlit)
La UI, contenuta in `ui.py` nella root del progetto, permette di:
- Inserire un testo.
- Eseguire l'analisi standard oppure la predizione personalizzata.
- Visualizzare i risultati con indicatori visivi (spinner durante la predizione).
- Confermare il risultato selezionando tra "Predizione esatta" e "Predizione errata". Se errata, è possibile selezionare il sentimento atteso.
- Avviare il training in background e controllarne lo stato.

## Installazione e Esecuzione

### Clona il repository:
```bash
git clone https://github.com/tuo_username/Sentimentify.git
cd Sentimentify
```

### Crea e attiva l'ambiente virtuale:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### Avvia il server FastAPI:
```bash
uvicorn src.main:app --reload
```
L'API sarà disponibile su [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Avvia l'interfaccia Streamlit:
```bash
streamlit run ui.py
```
La UI sarà accessibile all'URL fornito da Streamlit (di solito [http://localhost:8501](http://localhost:8501)).

## Testing
```bash
pytest tests/
```

## Considerazioni sul Deployment
- Su DigitalOcean il filesystem è effimero, quindi usa un database per persistenza.
- Puoi deployare su DigitalOcean con buildpack per Python, configurando API_URL e runtime.txt se necessario.

