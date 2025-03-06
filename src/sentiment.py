from textblob import TextBlob
from googletrans import Translator

translator = Translator()

def analyze_text(text: str) -> dict:
    # Rileva la lingua
    blob = TextBlob(text)
    detected_lang = blob.detect_language()
    # Se non è in inglese, traduci
    if detected_lang != "en":
        translation = translator.translate(text, dest="en")
        text_for_analysis = translation.text
    else:
        text_for_analysis = text

    analysis = TextBlob(text_for_analysis)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        sentiment = "positivo"
    elif polarity < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"
    
    return {"sentiment": sentiment, "polarity": polarity, "detected_language": detected_lang}
