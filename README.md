# Sentimentify

Sentimentify è un'API REST sviluppata con FastAPI che analizza il sentiment di un testo, classificandolo come positivo, negativo o neutro, e fornisce il valore numerico della polarità. Il progetto utilizza TextBlob per l'analisi del sentiment, Pandas per eventuali operazioni sui dati, e Uvicorn come server ASGI.

## Tecnologie Utilizzate

- **FastAPI:** Framework per la creazione di API veloci e performanti.
- **TextBlob:** Libreria per l'analisi del sentiment e l'elaborazione del linguaggio naturale.
- **Pandas:** Utilizzato per la gestione e l'analisi dei dati.
- **Uvicorn:** Server ASGI per eseguire l'applicazione in modalità sviluppo e produzione.

## Installazione

Segui questi passaggi per configurare l'ambiente di sviluppo e avviare l'applicazione:

1. **Clona il repository:**
```bash
git clone https://github.com/tuo_username/Sentimentify.git
cd Sentimentify
```

2. **Crea e attiva l'ambiente virtuale:**

***Su Linux/macOS:***
```bash
py -m venv venv
source venv/bin/activate
```

***Su Windows:***
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Installa le dipendenze:**
```bash
pip install -r requirements.txt
```

## Esecuzione dell'Applicazione

Avvia l'applicazione con Uvicorn:

```bash
uvicorn src.main:app --reload
```

L'app sarà disponibile su http://127.0.0.1:8000.
Accedi alla documentazione interattiva (Swagger UI) su http://127.0.0.1:8000/docs.

## Testing

Per eseguire i test unitari utilizza ***pytest***:

```bash
pytest tests/
```