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

@app.post("/sentiment", response_model=SentimentResponse)
async def sentiment_endpoint(request: SentimentRequest):
    # Verifica che il testo non sia vuoto
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Il campo 'text' non può essere vuoto")
    
    result = analyze_text(request.text)
    return result

@app.get("/")
async def read_root():
    logger.info("Endpoint root chiamato")
    return {"message": "Benvenuto in Sentimentify!"}

# Include il router per il training personalizzato
app.include_router(training_router)
