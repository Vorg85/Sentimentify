from fastapi import APIRouter, BackgroundTasks, HTTPException
import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from src.models import SentimentRequest, PredictionResponse, ConfirmRequest

router = APIRouter()

# Variabili globali per memorizzare il modello addestrato e il risultato del training
custom_model = None
training_result = None

def train_model_task():
    """
    Funzione che esegue l'addestramento del modello.
    Viene eseguita in background e aggiorna le variabili globali.
    """
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

    # Elimina le righe in cui 'text' o 'sentiment' sono NaN
    df = df.dropna(subset=["text", "sentiment"])
    X = df["text"]
    y = df["sentiment"]

    # Dividi il dataset in set di training e test (80% training, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Crea una pipeline di classificazione: CountVectorizer + LogisticRegression
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    # Addestra il modello
    pipeline.fit(X_train, y_train)

    # Valuta il modello sul set di test
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Salva il modello addestrato e il risultato
    custom_model = pipeline
    training_result = {"message": "Modello addestrato con successo", "accuracy": accuracy}

@router.get("/train_local_bg")
async def train_local_bg(background_tasks: BackgroundTasks):
    """
    Endpoint che avvia l'addestramento del modello in background.
    Restituisce subito una risposta di conferma.
    """
    background_tasks.add_task(train_model_task)
    return {"message": "Addestramento in background avviato. Controlla lo stato tramite /train_status"}

@router.get("/train_status")
async def train_status():
    """
    Endpoint per controllare lo stato dell'addestramento.
    Restituisce il risultato se l'addestramento è completato o uno stato se ancora in corso.
    """
    if training_result is None:
        return {"status": "Addestramento in corso o non ancora avviato"}
    return training_result

@router.post("/predict_custom", response_model=PredictionResponse)
async def predict_custom(request: SentimentRequest):
    """
    Endpoint per fare predizioni utilizzando il modello addestrato.
    Se il modello non è ancora addestrato, restituisce un errore.
    """
    global custom_model

    if custom_model is None:
        raise HTTPException(status_code=400, detail="Il modello non è stato addestrato. Esegui /train_local_bg prima di fare previsioni.")

    prediction = custom_model.predict([request.text])[0]
    return {"text": request.text, "predicted_sentiment": prediction}

@router.post("/confirm")
async def confirm_record(confirm_req: ConfirmRequest):
    """
    Endpoint per confermare se il risultato (testo e sentimento) è corretto.
    Se confermato, il record viene aggiunto a sample.csv.
    """
    if not confirm_req.confirm:
        return {"message": "Record non aggiunto al dataset."}

    csv_path = "src/sample.csv"
    # Crea una riga da aggiungere al CSV
    new_record = pd.DataFrame({"text": [confirm_req.text], "sentiment": [confirm_req.sentiment]})
    
    # Se il file esiste, aggiungi il record; altrimenti, crealo con le intestazioni
    if os.path.exists(csv_path):
        try:
            new_record.to_csv(csv_path, mode='a', header=False, index=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore nell'aggiunta del record: {e}")
    else:
        try:
            new_record.to_csv(csv_path, mode='w', header=True, index=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore nella creazione del file CSV: {e}")
    
    return {"message": "Record aggiunto con successo al dataset."}