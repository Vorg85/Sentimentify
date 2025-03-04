from textblob import TextBlob

def analyze_text(text: str) -> dict:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    # Classifica il sentiment in base alla polarità
    if polarity > 0:
        sentiment = "positivo"
    elif polarity < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"
    
    return {"sentiment": sentiment, "polarity": polarity}
