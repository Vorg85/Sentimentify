from fastapi import APIRouter, HTTPException, BackgroundTasks
import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from textblob import TextBlob
from deep_translator import GoogleTranslator
from langdetect import detect

from src.models import SentimentRequest, PredictionResponse, ConfirmRequest

router = APIRouter()

custom_model = None
training_result = None

def train_model_task():
    global custom_model, training_result
    print("Inizio task di addestramento del modello")
    csv_path = "src/sample.csv"
    if not os.path.exists(csv_path):
        training_result = {"error": "Il file CSV non esiste nel percorso specificato."}
        print(training_result["error"])
        return
    try:
        df = pd.read_csv(csv_path)
        print("File CSV letto con successo")
    except Exception as e:
        training_result = {"error": f"Errore durante la lettura del file CSV: {e}"}
        print(training_result["error"])
        return
    if "text" not in df.columns or "sentiment" not in df.columns:
        training_result = {"error": "Il file CSV deve contenere le colonne 'text' e 'sentiment'."}
        print(training_result["error"])
        return
    df = df.dropna(subset=["text", "sentiment"])
    X = df["text"]
    y = df["sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Dati suddivisi in train e test")
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    print("Modello addestrato")
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    custom_model = pipeline
    training_result = {"message": "Modello addestrato con successo", "accuracy": accuracy}
    print(f"Addestramento completato con accuratezza: {accuracy}")

@router.get("/train_local_bg")
async def train_local_bg(background_tasks: BackgroundTasks):
    print("Richiesta di addestramento in background ricevuta")
    background_tasks.add_task(train_model_task)
    return {"message": "Addestramento in background avviato. Controlla lo stato tramite /train_status"}

@router.get("/train_status")
async def train_status():
    print("Richiesta di stato dell'addestramento ricevuta")
    if training_result is None:
        return {"status": "Addestramento in corso o non ancora avviato"}
    return training_result

@router.post("/predict_custom", response_model=PredictionResponse)
async def predict_custom(request: SentimentRequest):
    global custom_model
    if custom_model is None:
        raise HTTPException(status_code=400, detail="Il modello non è stato addestrato. Esegui /train_local_bg prima di fare previsioni.")
    
    # Rileva la lingua
    try:
        detected_lang = detect(request.text)
    except:
        detected_lang = "unknown"

    # Traduci in inglese se necessario
    if detected_lang != "en":
        text_for_prediction = GoogleTranslator(source='auto', target='en').translate(request.text)
    else:
        text_for_prediction = request.text

    # Esegui la predizione con il modello personalizzato
    prediction = custom_model.predict([text_for_prediction])[0]
    
    # Ottieni il vettore dei conteggi dal CountVectorizer del modello
    vectorizer = custom_model.named_steps["vect"]
    vector = vectorizer.transform([text_for_prediction])
    count_array = vector.toarray()[0]
    feature_names = vectorizer.get_feature_names_out()
    count_dict = dict(zip(feature_names, count_array))
    
    return {
        "text": request.text,
        "translated_text": text_for_prediction,
        "predicted_sentiment": prediction,
        "confirm_message": "Scegli se la predizione è corretta o errata. Se errata, indica il sentimento atteso e invia i dati a /confirm.",
        "count_vector": count_dict
    }
    
@router.post("/confirm")
async def confirm_record(confirm_req: ConfirmRequest):
    # Log per il debug
    print(f"Richiesta di conferma ricevuta: {confirm_req}")

    # Verifica che il campo 'user_feedback' sia valido
    if confirm_req.user_feedback not in ["correct", "incorrect"]:
        raise HTTPException(status_code=400, detail="Il campo 'user_feedback' deve essere 'correct' o 'incorrect'.")

    # Determina il sentimento finale: se il feedback è 'correct', usa actual_sentiment;
    # se 'incorrect', controlla che expected_sentiment sia fornito e usalo.
    final_sentiment = confirm_req.actual_sentiment
    if confirm_req.user_feedback == "incorrect":
        if not confirm_req.expected_sentiment:
            raise HTTPException(status_code=400, detail="Specificare 'expected_sentiment' se la predizione è errata.")
        final_sentiment = confirm_req.expected_sentiment

    # Definisci il percorso del file CSV
    csv_path = "src/sample.csv"

    # Crea il record da salvare usando il testo tradotto (in inglese)
    new_record = pd.DataFrame({
        "text": [confirm_req.translated_text],
        "sentiment": [final_sentiment]
    })

    # Se il file non esiste, è necessario includere l'header
    header_needed = not os.path.exists(csv_path)

    # Prova ad appendere il record al file CSV
    try:
        new_record.to_csv(csv_path, mode='a', header=header_needed, index=False)
        print(f"Record aggiunto: {new_record}")
    except Exception as e:
        print(f"Errore durante l'aggiunta del record: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nell'aggiunta del record: {e}")

    return {"message": f"Record aggiunto con successo al dataset con sentimento '{final_sentiment}'."}
