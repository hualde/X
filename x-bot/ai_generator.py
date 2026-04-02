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
    Usa la API de DeepSeek para generar el texto de un tweet basado en un prompt dado,
    siguiendo las directrices de engagement de X abril 2026.
    """
    if not DEEPSEEK_API_KEY:
        logger.error("Falta DEEPSEEK_API_KEY en el archivo .env.")
        return "⚠️ Error: Falta la API Key de DeepSeek."

    system_instructions = (
        "You are the official tweet generator for Liora Vale (@lioravale015). "
        "Your goal is to maximize engagement (replies > likes > reposts) following 2026 X algorithm rules.\n\n"
        "STRICT RULES:\n"
        "1. LANGUAGE: You MUST write ONLY in English.\n"
        "2. STYLE: Juguetona, cariñosa, a bit 'bratty' and always 'teasing'. Use modern internet slang if appropriate.\n"
        "3. TONE: Suggestive and provocative but NEVER explicit (no NSFW words, no vulgarity).\n"
        "4. STRUCTURE: Hook (impactful first line) + Tease (suggestion) + Call to Action (strong question or challenge).\n"
        "5. ALGORITHM: Length between 100-180 characters. Max 1-2 emojis. Avoid hashtags.\n"
        "6. OBJECTIVE: Force people to reply. Prioritize POV situations, polls, or asking for opinions."
    )

    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Genera un tweet sobre este tema: {prompt}"}
            ],
            max_tokens=150,
            temperature=0.8
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
