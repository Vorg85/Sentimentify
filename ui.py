import streamlit as st
import requests

# Imposta l'URL dell'API FastAPI (modifica con il tuo URL se deployato)
API_URL = "https://sentimentify-app-prttt.ondigitalocean.app/"

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
            # Sezione di conferma, usando uno st.form per garantire il submit insieme
            with st.form("confirm_form"):
                choice = st.radio("Il risultato è corretto?", ("Predizione esatta", "Predizione errata"))
                expected = None
                if choice == "Predizione errata":
                    expected = st.selectbox("Qual è il sentimento atteso?", ("positivo", "negativo", "neutro"))
                submitted = st.form_submit_button("Invia Conferma")
                if submitted:
                    payload = {
                        "text": text_input,
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
        st.write(response.json()["status"])
    else:
        st.error("Errore nel recupero dello stato del training.")

# Sezione informativa sul funzionamento del modello
with st.expander("Come funziona il modello?"):
    st.markdown("""
    **1. Conversione del Testo in Numeri:**
    
    - Il testo viene **tokenizzato**: viene diviso in parole (token).
    - Con il **CountVectorizer**, il testo viene trasformato in un vettore numerico, in cui ogni elemento rappresenta la frequenza di una parola nel testo.
    
    **2. Regressione Logistica per la Classificazione:**
    
    - **Obiettivo:** Assegnare a ciascun testo una probabilità di appartenere a ciascuna classe (positivo, negativo, neutro).
    - **Processo:**
      - Durante l'**addestramento**, il modello impara dei pesi per ogni parola (cioè, quanto è importante quella parola per determinare il sentimento) e un bias.
      - Quando un nuovo testo viene convertito in vettore, il modello calcola una **somma pesata** (prodotto tra i vettori e i pesi) e aggiunge il bias.
      - La somma viene trasformata tramite una **funzione sigmoide** (o softmax, in caso di classificazione multiclasse) per ottenere una probabilità per ogni classe.
      - La classe con la probabilità più alta viene selezionata come **predizione del sentimento**.
      
    **3. Supporto Multilingue:**
    
    - Se il testo non è in inglese, viene rilevata la lingua e tradotto in inglese prima della predizione, assicurando che il modello lavori con dati in una lingua uniforme.
    
    **Conclusione:**
    
    La combinazione di questi processi consente al modello di apprendere dai dati (durante il training) e di fare previsioni accurate sui testi in ingresso. Se la predizione non corrisponde a quanto atteso, puoi fornire un feedback per migliorare il dataset.
    """)
