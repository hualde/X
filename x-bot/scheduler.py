import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Importar la lógica de envío de post.py
from post import post_tweet

# --- CONFIGURACIÓN ---
START_DATE = datetime(2026, 4, 2) # Fecha en la que empieza el Día 1 del plan
PLAN_FILE = Path(__file__).parent / "MASTER_CONTENT_PLAN.json"
POSTED_IMAGES_FILE = Path(__file__).parent / "posted_images.txt"

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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

def run_catch_up():
    """Revisa el plan desde el primer día y publica lo que esté pendiente antes de la hora actual."""
    logger.info("🔍 Iniciando revisión de posts pendientes (catch-up)...")
    
    if not PLAN_FILE.exists():
        logger.error(f"❌ No se encontró {PLAN_FILE}. Omite catch-up.")
        return

    try:
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            plan = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error al cargar el plan maestro: {e}")
        return
    
    posted_set = get_posted_images()
    now = datetime.now()
    
    # Horarios base de los slots (momento teórico de publicación)
    slots_config = {
        "morning": 9,
        "afternoon": 14,
        "night": 19
    }

    # Calculamos cuántos días han pasado desde el inicio
    delta = now - START_DATE
    current_day_limit = delta.days + 1
    
    pending_count = 0

    # Recorremos desde el Día 1 hasta el día actual
    for day_num in range(1, current_day_limit + 1):
        day_key = f"day_{day_num}"
        day_data = plan.get(day_key)
        if not day_data: continue
        
        # Fecha correspondiente a este día del plan
        day_date = START_DATE + timedelta(days=day_num-1)
        
        for slot, hour_limit in slots_config.items():
            slot_data = day_data.get(slot)
            if not slot_data: continue
            
            image_name = slot_data['image_filename']
            # Momento en que este post debió haber salido (aprox)
            theoretical_time = day_date.replace(hour=hour_limit, minute=0, second=0, microsecond=0)
            
            # Si la hora ya pasó Y la imagen no está en el registro -> Publicar
            if theoretical_time < now and image_name not in posted_set:
                logger.info(f"⏳ Recuperando post pendiente: {day_key} - {slot} ({image_name})")
                try:
                    post_tweet(text=slot_data['tweet_text'], image_path=f"photos/{image_name}")
                    mark_image_as_posted(image_name)
                    pending_count += 1
                    time.sleep(10) # Pequeña espera entre publicaciones de recuperación
                except Exception as e:
                    logger.error(f"❌ Error al recuperar {day_key} - {slot}: {e}")

    if pending_count > 0:
        logger.info(f"✅ Se han recuperado {pending_count} posts que estaban pendientes.")
    else:
        logger.info("✨ El bot está al día. No se detectaron posts pendientes.")

def post_job(slot):
    """Tarea programada para publicar el post correspondiente al día actual."""
    now = datetime.now()
    delta = now - START_DATE
    day_num = delta.days + 1
    day_key = f"day_{day_num}"

    try:
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        entry = plan.get(day_key, {}).get(slot)
        if not entry:
            logger.warning(f"⚠️ No hay contenido definido para {day_key} - {slot}")
            return

        image_name = entry['image_filename']
        posted_set = get_posted_images()

        if image_name in posted_set:
            logger.info(f"⏭️ El post {day_key} - {slot} ({image_name}) ya fue publicado. Saltando...")
            return

        logger.info(f"🚀 Publicando {day_key} - {slot}...")
        post_tweet(text=entry['tweet_text'], image_path=f"photos/{image_name}")
        mark_image_as_posted(image_name)
        logger.info("✅ Publicación exitosa.")
        
    except Exception as e:
        logger.error(f"❌ Error en la tarea programada ({slot}): {e}")

def main():
    logger.info("🚀 Iniciando el Bot de Liora Vale...")
    logger.info(f"📅 Día 1 del plan establecido el: {START_DATE.strftime('%Y-%m-%d')}")
    
    # 1. Ponerse al día con lo que no se publicó (Catch-up)
    run_catch_up()

    # 2. Configurar la agenda para los próximos posts
    scheduler = BlockingScheduler()
    
    # Programamos las 3 franjas horarias con un jitter de 2h (7200 segundos)
    # Esto significa que el post de las 9:00 saldrá entre las 9:00 y las 11:00
    scheduler.add_job(post_job, CronTrigger(hour=9, minute=0), args=['morning'], jitter=7200, name="morning_task")
    scheduler.add_job(post_job, CronTrigger(hour=14, minute=0), args=['afternoon'], jitter=7200, name="afternoon_task")
    scheduler.add_job(post_job, CronTrigger(hour=19, minute=0), args=['night'], jitter=7200, name="night_task")
    
    # Manejo de señales de cierre
    def signal_handler(sig, frame):
        logger.info("🛑 Deteniendo el bot...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("📅 Tareas programadas. El bot se mantendrá en ejecución.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()
