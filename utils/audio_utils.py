import os
import uuid
import requests
from pydub import AudioSegment

# Cria diretório temporário para armazenar áudios
AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def download_audio(url: str, extension: str = "ogg") -> str:
    """
    Baixa um áudio da URL informada, converte para .mp3 e retorna o caminho do arquivo convertido.
    """
    try:
        # 1. Baixa o áudio original (geralmente .ogg)
        original_filename = f"{uuid.uuid4()}.{extension}"
        original_path = os.path.join(AUDIO_DIR, original_filename)

        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        with open(original_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # 2. Converte para mp3
        converted_filename = f"{uuid.uuid4()}.mp3"
        converted_path = os.path.join(AUDIO_DIR, converted_filename)

        audio = AudioSegment.from_file(original_path)
        audio.export(converted_path, format="mp3")

        # 3. Remove o original
        os.remove(original_path)

        return converted_path

    except Exception as e:
        raise RuntimeError(f"Erro ao baixar ou converter áudio: {e}")
