import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuración de DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

logger = logging.getLogger(__name__)

def generate_tweet_text(prompt):
    """
    Usa la API de DeepSeek para generar el texto de un tweet basado en un prompt dado.
    """
    if not DEEPSEEK_API_KEY:
        logger.error("Falta DEEPSEEK_API_KEY en el archivo .env.")
        return "⚠️ Error: Falta la API Key de DeepSeek."

    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en redactar tweets virales y atractivos. Tu respuesta DEBE ser un único tweet de menos de 260 caracteres (para dejar espacio a tags o imágenes). No uses hashtags excesivos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        tweet_content = response.choices[0].message.content.strip()
        
        # Limpiar posibles comillas que a veces añaden las LLM
        if tweet_content.startswith('"') and tweet_content.endswith('"'):
            tweet_content = tweet_content[1:-1]

        logger.info(f"✅ Texto generado por AI: {tweet_content[:50]}...")
        return tweet_content

    except Exception as e:
        logger.error(f"❌ Error al llamar a la API de DeepSeek: {e}")
        return None
