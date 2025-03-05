from fastapi import APIRouter, HTTPException
import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from src.models import SentimentRequest, PredictionResponse

router = APIRouter()

# Variabile globale per memorizzare il modello personalizzato addestrato
custom_model = None

@router.get("/train_local")
async def train_local():
    global custom_model

    # Percorso del file CSV locale
    csv_path = "src/sample.csv"

    # Verifica che il file esista
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=400, detail="Il file CSV non esiste nel percorso specificato.")

    # Leggi il file CSV usando Pandas
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore durante la lettura del file CSV: {e}")

    # Verifica che il dataset contenga le colonne richieste
    if "text" not in df.columns or "sentiment" not in df.columns:
        raise HTTPException(
            status_code=400,
            detail="Il file CSV deve contenere le colonne 'text' e 'sentiment'."
        )

    # Rimuovi le righe in cui 'text' o 'sentiment' sono NaN
    df = df.dropna(subset=["text", "sentiment"])

    # Separazione delle feature e delle etichette
    X = df["text"]
    y = df["sentiment"]

    # Dividi il dataset in set di training e test (80% training, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crea una pipeline di classificazione: vettorizzazione e classificatore
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    # Addestra il modello
    pipeline.fit(X_train, y_train)

    # Valuta il modello sul set di test
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Salva il modello addestrato in una variabile globale
    custom_model = pipeline

    return {"message": "Modello addestrato con successo", "accuracy": accuracy}

@router.post("/predict_custom", response_model=PredictionResponse)
async def predict_custom(request: SentimentRequest):
    global custom_model

    # Verifica che il modello sia stato addestrato
    if custom_model is None:
        raise HTTPException(status_code=400, detail="Il modello non è stato addestrato. Esegui /train_local prima di fare previsioni.")

    # Effettua la previsione sul nuovo testo
    prediction = custom_model.predict([request.text])[0]
    return {"text": request.text, "predicted_sentiment": prediction}
