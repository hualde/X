import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Importar la función que ya tenemos hecha en post.py
from post import post_tweet
from ai_generator import generate_tweet_text

# Configuración básica de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

SCHEDULE_FILE = Path(__file__).parent / "schedule.json"
POSTED_IMAGES_FILE = Path(__file__).parent / "posted_images.txt"
PHOTOS_DIR = Path(__file__).parent / "photos"

def get_posted_images():
    """Carga la lista de imágenes ya publicadas desde el archivo de texto."""
    if not POSTED_IMAGES_FILE.exists():
        return set()
    with open(POSTED_IMAGES_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def mark_image_as_posted(image_name):
    """Guarda el nombre de la imagen publicada en el historial."""
    with open(POSTED_IMAGES_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{image_name}\n")

def get_next_available_image():
    """Busca la primera imagen en la carpeta /photos que no esté en el historial."""
    if not PHOTOS_DIR.exists():
        logger.error(f"La carpeta de fotos no existe: {PHOTOS_DIR}")
        return None
    
    posted = get_posted_images()
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # Listar y ordenar imágenes para llevar un orden secuencial (o usar random.shuffle)
    all_photos = sorted([f for f in PHOTOS_DIR.iterdir() if f.suffix.lower() in extensions])
    
    for photo in all_photos:
        if photo.name not in posted:
            return photo
            
    return None

def load_schedule():
    """Carga la configuración de tweets desde el archivo JSON."""
    if not SCHEDULE_FILE.exists():
        logger.error(f"No se encontró el archivo de configuración: {SCHEDULE_FILE}")
        return []
    
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def safe_post_tweet(text_or_prompt, image_path_mode, jitter_minutes=0, use_ai=False):
    """Envoltura para post_tweet que gestiona la selección de imágenes, errores y un retraso aleatorio."""
    
    if jitter_minutes > 0:
        delay_seconds = random.randint(0, jitter_minutes * 60)
        logger.info(f"⏳ Aplicando retraso aleatorio de {delay_seconds // 60} minutos y {delay_seconds % 60} segundos...")
        time.sleep(delay_seconds)

    logger.info("⏰ Preparando tarea programada...")
    
    # Generar texto con AI si está habilitado
    if use_ai:
        logger.info(f"🤖 Generando texto con DeepSeek basado en el prompt: '{text_or_prompt[:30]}...'")
        text_to_post = generate_tweet_text(text_or_prompt)
        if not text_to_post:
            logger.error("❌ Abortando: Falló la generación de texto con AI.")
            return
    else:
        text_to_post = text_or_prompt

    image_to_send = None
    image_name = None
    
    if image_path_mode == "AUTO_POOL":
        photo_path = get_next_available_image()
        if photo_path:
            image_to_send = str(photo_path)
            image_name = photo_path.name
            logger.info(f"📸 Imagen seleccionada del pool: {image_name}")
        else:
            logger.warning("⚠️ No quedan imágenes disponibles por publicar en la carpeta /photos.")
    elif image_path_mode:
        image_to_send = image_path_mode
        image_name = Path(image_path_mode).name

    try:
        post_tweet(text=text_to_post, image_path=image_to_send)
        if image_path_mode == "AUTO_POOL" and image_name:
            mark_image_as_posted(image_name)
        logger.info("✅ Tweet enviado correctamente.")
    except Exception as e:
        logger.error(f"❌ Error al enviar tweet programado: {e}")

def main():
    logger.info("🚀 Iniciando el planificador de tweets para X (Twitter)...")
    
    scheduler = BlockingScheduler()
    jobs_data = load_schedule()
    
    if not jobs_data:
        logger.warning("No hay tweets programados en schedule.json. El programa terminará.")
        return

    for job in jobs_data:
        hour = job.get("hour")
        minute = job.get("minute", 0)
        text = job.get("text") or job.get("prompt")
        image = job.get("image")
        jitter = job.get("jitter_minutes", 0)
        use_ai = job.get("use_ai", False)
        
        if hour is None or not text:
            logger.warning(f"Omitiendo entrada inválida: {job}")
            continue
            
        # Programar para que ocurra cada día a esa hora
        trigger = CronTrigger(hour=hour, minute=minute)
        scheduler.add_job(
            safe_post_tweet,
            trigger=trigger,
            args=[text, image, jitter, use_ai],
            name=f"Tweet_{hour}:{minute:02d}"
        )
        msg = f"📅 Programada tarea a las {hour:02d}:{minute:02d}"
        if use_ai:
            msg += " (via AI)"
        if jitter > 0:
            msg += f" (con hasta {jitter} min de var.)"
        logger.info(f"{msg}")

    # Capturar señales de terminación para cerrar limpiamente
    def signal_handler(sig, frame):
        logger.info("🛑 Deteniendo el planificador...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()
