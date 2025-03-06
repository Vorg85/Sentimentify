from textblob import TextBlob
from googletrans import Translator
from langdetect import detect

translator = Translator()

def analyze_text(text: str) -> dict:
    # Usa langdetect per rilevare la lingua
    try:
        detected_lang = detect(text)
    except Exception as e:
        detected_lang = "unknown"

    # Se il testo non è in inglese, traducilo in inglese
    if detected_lang != "en":
        translation = translator.translate(text, dest="en")
        text_for_analysis = translation.text
    else:
        text_for_analysis = text

    # Analizza il testo (tradotto se necessario) con TextBlob
    analysis = TextBlob(text_for_analysis)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        sentiment = "positivo"
    elif polarity < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"
    
    return {"sentiment": sentiment, "polarity": polarity, "detected_language": detected_lang}
