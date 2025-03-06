import streamlit as st
import requests

# Imposta l'URL dell'API FastAPI (modifica con il tuo URL se deployato)
API_URL = "https://tuo-fastapi-app.do.app"

st.title("Sentimentify - Interfaccia per Analisi del Sentiment")

# Sezione per l'analisi standard con TextBlob
st.header("Analisi Standard (TextBlob)")
text_input = st.text_area("Inserisci il testo da analizzare:")

if st.button("Analizza con TextBlob"):
    if text_input.strip():
        with st.spinner("Analisi in corso..."):
            response = requests.post(f"{API_URL}/sentiment", json={"text": text_input})
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Sentiment:** {result['sentiment']} (Polarity: {result['polarity']:.2f})")
            st.write(f"**Lingua Rilevata:** {result.get('detected_language', 'N/A')}")
            st.info(result['confirm_message'])
        else:
            st.error("Errore durante l'analisi del testo.")
    else:
        st.warning("Inserisci un testo prima di analizzare!")

# Sezione per l'analisi con il modello personalizzato
st.header("Analisi con il Modello Personalizzato")
if st.button("Analizza con il Modello Personalizzato"):
    if text_input.strip():
        with st.spinner("Predizione in corso..."):
            response = requests.post(f"{API_URL}/predict_custom", json={"text": text_input})
        if response.status_code == 200:
            result = response.json()
            st.write(f"**Predizione:** {result['predicted_sentiment']}")
            st.info(result['confirm_message'])
            # Mostra le opzioni per confermare il risultato
            choice = st.radio("Il risultato è corretto?", ("Predizione esatta", "Predizione errata"))
            expected = None
            if choice == "Predizione errata":
                expected = st.selectbox("Qual è il sentimento atteso?", ("positivo", "negativo", "neutro"))
            if st.button("Invia Conferma"):
                payload = {
                    "text": text_input,  # puoi mantenere anche il testo originale se vuoi mostrarlo
                    "translated_text": result["translated_text"],
                    "actual_sentiment": result["predicted_sentiment"],
                    "user_feedback": "correct" if choice == "Predizione esatta" else "incorrect",
                    "expected_sentiment": expected
                }
                conf_response = requests.post(f"{API_URL}/confirm", json=payload)
                if conf_response.status_code == 200:
                    st.success(conf_response.json()["message"])
                else:
                    st.error("Errore nell'invio della conferma.")
        else:
            st.error("Errore durante la predizione.")
    else:
        st.warning("Inserisci un testo prima di analizzare!")

# Sezione per il training in background
st.header("Training del Modello Personalizzato")
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
