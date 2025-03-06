import streamlit as st
import requests

# URL della FastAPI (modifica se è deployata su un server remoto)
API_URL = "http://127.0.0.1:8000"

st.title("Sentimentify - Analisi del Sentiment 📊")

# Input per il testo
text_input = st.text_area("Inserisci il testo da analizzare:", "")

# Pulsante per analizzare con TextBlob
if st.button("Analizza con TextBlob"):
    if text_input.strip():
        response = requests.post(f"{API_URL}/sentiment", json={"text": text_input})
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Sentiment:** {result['sentiment']} (Polarity: {result['polarity']:.2f})")
            st.info(result['confirm_message'])
        else:
            st.error("Errore durante l'analisi del testo.")
    else:
        st.warning("Inserisci un testo prima di analizzare!")

# Pulsante per analizzare con il modello personalizzato
if st.button("Analizza con il Modello Personalizzato"):
    if text_input.strip():
        response = requests.post(f"{API_URL}/predict_custom", json={"text": text_input})
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Sentiment Predetto:** {result['predicted_sentiment']}")
            st.info(result['confirm_message'])
        else:
            st.error("Errore durante la predizione.")
    else:
        st.warning("Inserisci un testo prima di analizzare!")

# Sezione di conferma del risultato
st.subheader("Conferma il Risultato")
sentiment_choice = st.selectbox("Seleziona il sentimento corretto:", ["positivo", "negativo", "neutro"])
confirm = st.checkbox("Confermo che il risultato è corretto")

if st.button("Invia Conferma"):
    if confirm:
        response = requests.post(f"{API_URL}/confirm", json={"text": text_input, "sentiment": sentiment_choice, "confirm": True})
        if response.status_code == 200:
            st.success("Il testo è stato aggiunto con successo al dataset!")
        else:
            st.error("Errore nell'invio della conferma.")
    else:
        st.warning("Spunta la casella di conferma prima di inviare.")

# Sezione di training
st.subheader("Training del Modello")
if st.button("Avvia Training in Background"):
    response = requests.get(f"{API_URL}/train_local_bg")
    if response.status_code == 200:
        st.success(response.json()["message"])
    else:
        st.error("Errore nell'avvio del training.")

if st.button("Controlla Stato del Training"):
    response = requests.get(f"{API_URL}/train_status")
    if response.status_code == 200:
        st.write(response.json())
    else:
        st.error("Errore nel recupero dello stato del training.")
