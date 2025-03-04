from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Benvenuto in Sentimentify!"}

def test_sentiment_positive():
    # Test con un testo che dovrebbe avere sentiment positivo
    response = client.post("/sentiment", json={"text": "I love this amazing project!"})
    assert response.status_code == 200
    data = response.json()
    # Controlla che il sentiment restituito sia "positivo" e che la polarità sia maggiore di 0
    assert data["sentiment"] == "positivo"
    assert data["polarity"] > 0

def test_sentiment_negative():
    # Test con un testo che dovrebbe avere sentiment negativo
    response = client.post("/sentiment", json={"text": "I hate this terrible experience."})
    assert response.status_code == 200
    data = response.json()
    # Controlla che il sentiment restituito sia "negativo" e che la polarità sia minore di 0
    assert data["sentiment"] == "negativo"
    assert data["polarity"] < 0

def test_sentiment_empty():
    # Testa l'endpoint con un testo vuoto, dovrebbe ritornare un errore 400
    response = client.post("/sentiment", json={"text": ""})
    assert response.status_code == 400
    assert "Il campo 'text' non può essere vuoto" in response.json()["detail"]
