import requests
from bs4 import BeautifulSoup

def get_ipa(text, dialect='br'):
    URL = "https://tophonetics.com/"
    session = requests.Session()
    session.get(URL)

    data = {
        "text_to_transcribe": text,
        "submit": "Show transcription",
        "dialect": dialect,           # 'am' = American, 'br' = British
        "output_mode": "ipa",
        "weak_forms": "on",           # Optional: enables weak forms
        "pre_positions": "off",         # Optional: enables parentheses
        "lines": "one"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://tophonetics.com",
        "Referer": "https://tophonetics.com/"
    }

    try:
        response = session.post(URL, data=data, headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        transcription = soup.find("div", id="transcr_output")
        
        if transcription:
            return transcription.get_text(separator=" ").strip()
        else:
            return "Transcription failed. The site might be blocking the request."

    except Exception as e:
        return f"Error: {e}"