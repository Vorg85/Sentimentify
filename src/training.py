from fastapi import APIRouter, HTTPException, BackgroundTasks
import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from textblob import TextBlob
from googletrans import Translator

from src.models import SentimentRequest, PredictionResponse, ConfirmRequest

router = APIRouter()

custom_model = None
training_result = None

def train_model_task():
    global custom_model, training_result
    csv_path = "src/sample.csv"
    if not os.path.exists(csv_path):
        training_result = {"error": "Il file CSV non esiste nel percorso specificato."}
        return
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        training_result = {"error": f"Errore durante la lettura del file CSV: {e}"}
        return
    if "text" not in df.columns or "sentiment" not in df.columns:
        training_result = {"error": "Il file CSV deve contenere le colonne 'text' e 'sentiment'."}
        return
    df = df.dropna(subset=["text", "sentiment"])
    X = df["text"]
    y = df["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    custom_model = pipeline
    training_result = {"message": "Modello addestrato con successo", "accuracy": accuracy}

@router.get("/train_local_bg")
async def train_local_bg(background_tasks: BackgroundTasks):
    background_tasks.add_task(train_model_task)
    return {"message": "Addestramento in background avviato. Controlla lo stato tramite /train_status"}

@router.get("/train_status")
async def train_status():
    if training_result is None:
        return {"status": "Addestramento in corso o non ancora avviato"}
    return training_result

@router.post("/predict_custom", response_model=PredictionResponse)
async def predict_custom(request: SentimentRequest):
    global custom_model

    if custom_model is None:
        raise HTTPException(status_code=400, detail="Il modello non è stato addestrato. Esegui /train_local_bg prima di fare previsioni.")
    
    # Rileva la lingua e traduci in inglese se necessario
    translator = Translator()
    blob = TextBlob(request.text)
    detected_lang = blob.detect_language()
    if detected_lang != "en":
        translation = translator.translate(request.text, dest="en")
        text_for_prediction = translation.text
    else:
        text_for_prediction = request.text

    # Effettua la predizione utilizzando il testo tradotto
    prediction = custom_model.predict([text_for_prediction])[0]
    return {
        "text": request.text,
        "translated_text": text_for_prediction,
        "predicted_sentiment": prediction,
        "confirm_message": "Scegli se la predizione è corretta o errata. Se errata, indica il sentimento atteso e invia i dati a /confirm."
    }

@router.post("/confirm")
async def confirm_record(confirm_req: ConfirmRequest):
    """
    Se user_feedback è "correct", usa actual_sentiment; se "incorrect", usa expected_sentiment per aggiornare il CSV.
    Il record verrà salvato usando il campo translated_text, in modo da avere il dato in inglese.
    """
    if confirm_req.user_feedback not in ["correct", "incorrect"]:
        raise HTTPException(status_code=400, detail="user_feedback deve essere 'correct' o 'incorrect'.")
    final_sentiment = confirm_req.actual_sentiment
    if confirm_req.user_feedback == "incorrect":
        if not confirm_req.expected_sentiment:
            raise HTTPException(status_code=400, detail="Specificare expected_sentiment se la predizione è errata.")
        final_sentiment = confirm_req.expected_sentiment
    csv_path = "src/sample.csv"
    # Salva il testo tradotto anziché il testo originale
    new_record = pd.DataFrame({"text": [confirm_req.translated_text], "sentiment": [final_sentiment]})
    header_needed = not os.path.exists(csv_path)
    try:
        new_record.to_csv(csv_path, mode='a', header=header_needed, index=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nell'aggiunta del record: {e}")
    return {"message": f"Record aggiunto con successo al dataset con sentimento '{final_sentiment}'."}

