import requests
import logging
from bs4 import BeautifulSoup

def get_ipa(text, dialect='br'):
    """Gets the api for phonetic transcriptions 'to phonetics' that enables automatic transcriptions
    
    :param text: text to transcribe

    :param dialect: default 'br' = 'british', also 'am' = American"""
    URL = "https://tophonetics.com/"
    session = requests.Session()
    session.get(URL)

    data = {
        "text_to_transcribe": text,
        "submit": "Show transcription",
        "dialect": dialect,
        "output_mode": "ipa",
        "weak_forms": "off",
        "pre_positions": "off",
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
            logging.info("Transcription failed. The site might be blocking the request.")
            print("Transcription failed. The site might be blocking the request.")
            raise Exception("Transcription failed. The site might be blocking the request.")
    except Exception as e:
        logging.info(f"Error in transcription: {e}")
        print(f"Error in transcription: {e}")
    
        raise e