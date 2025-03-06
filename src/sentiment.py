from textblob import TextBlob
from deep_translator import GoogleTranslator
from langdetect import detect

def analyze_text(text: str) -> dict:
    # Rileva la lingua con langdetect
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "unknown"

    # Se la lingua non è inglese, traducila
    if detected_lang != "en":
        translated_text = GoogleTranslator(source='auto', target='en').translate(text)
    else:
        translated_text = text

    # Analizza con TextBlob il testo tradotto
    analysis = TextBlob(translated_text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        sentiment = "positivo"
    elif polarity < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"

    return {
        "sentiment": sentiment,
        "polarity": polarity,
        "detected_language": detected_lang
    }
