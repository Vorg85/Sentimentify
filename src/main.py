from fastapi import FastAPI, HTTPException
from src.models import SentimentRequest, SentimentResponse
from src.sentiment import analyze_text
import logging
from src.training import router as training_router

# Configurazione base del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentimentify", description="API per analizzare il sentiment di un testo", version="1.0")

last_text = ""  # Variabili globali per memorizzare l'ultimo testo analizzato
last_sentiment = "" # Variabili globali per memorizzare l'ultimo sentiment 

@app.post("/sentiment", response_model=SentimentResponse)
async def sentiment_endpoint(request: SentimentRequest):
    # Verifica che il testo non sia vuoto
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Il campo 'text' non può essere vuoto")
    
    result = analyze_text(request.text)
    global last_text
    global last_sentiment
    last_text = request.text
    last_sentiment = result["sentiment"]
    logger.info(f"Testo analizzato: {request.text}, Sentiment: {result['sentiment']}, Polarità: {result['polarity']}")
    # Aggiungiamo il messaggio di conferma
    result["confirm_message"] = "Se il risultato è come ti aspettavi, invia una richiesta a /confirm con 'confirm': true per aggiungere il record al dataset."
    return result

# Feedback dell'ultimo testo analizzato e del sentiment
@app.get("/feedback")
async def feedback_endpoint():
    if last_text == "":
        raise HTTPException(status_code=404, detail="Nessun testo analizzato")
    
    # Richiede all'utente di fornire un feedback sul sentiment (positivo, negativo, neutro)
    return {"last_text": last_text, "last_sentiment": last_sentiment, "feedback": "Inserisci un feedback (positivo, negativo, neutro)"}


@app.get("/")
async def read_root():
    logger.info("Endpoint root chiamato")
    return {"message": "Benvenuto in Sentimentify!"}

# Include il router per il training personalizzato
app.include_router(training_router)
