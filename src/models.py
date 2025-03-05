from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    polarity: float
    
class PredictionResponse(BaseModel):
    text: str
    predicted_sentiment: str
