from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    polarity: float
    confirm_message: str = "Se il risultato è come ti aspettavi, invia una richiesta a /confirm con 'confirm': true per aggiungere il record al dataset."

class PredictionResponse(BaseModel):
    text: str
    predicted_sentiment: str
    confirm_message: str = "Se il risultato è come ti aspettavi, invia una richiesta a /confirm con 'confirm': true per aggiungere il record al dataset."

class ConfirmRequest(BaseModel):
    text: str
    sentiment: str
    confirm: bool