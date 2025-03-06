from pydantic import BaseModel
from typing import Optional

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    polarity: float
    confirm_message: str = "Se il risultato è come ti aspettavi, usa /confirm per salvare il record."

class PredictionResponse(BaseModel):
    text: str
    translated_text: str
    predicted_sentiment: str
    confirm_message: str = "Scegli se la predizione è corretta o errata. Se errata, indica il sentimento atteso e invia i dati a /confirm."

class ConfirmRequest(BaseModel):
    # Il testo originale (opzionale, a scopo informativo)
    text: str
    # Il testo tradotto in inglese (questo sarà salvato nel CSV)
    translated_text: str
    actual_sentiment: str     # Il sentimento ottenuto dalla predizione
    user_feedback: str        # "correct" oppure "incorrect"
    expected_sentiment: Optional[str] = None  # Obbligatorio se user_feedback è "incorrect"
