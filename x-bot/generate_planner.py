import csv
import json
from pathlib import Path
from datetime import datetime, timedelta

def generate_365_csv():
    # Cargar prompts existentes
    with open('prompts.json', 'r', encoding='utf-8') as f:
        ai_themes = json.load(f)
    
    with open('image_generation_prompts.json', 'r', encoding='utf-8') as f:
        img_prompts = json.load(f)
    
    # Preparar el archivo CSV
    output_path = 'DAILY_PLANNER_365.csv'
    
    # Categorías de imágenes
    mornings = img_prompts['morning_50_days']
    afternoons = img_prompts['afternoon_50_days']
    nights = img_prompts['night_50_days']
    weekends = img_prompts['weekend_50_days']
    
    start_date = datetime(2026, 4, 2) # Hoy
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        # Cabecera
        writer.writerow(['Day', 'Date', 'Weekday', 'Slot', 'AI Tweet Theme (DeepSeek)', 'Image AI Prompt (Midjourney/Flux)'])
        
        for i in range(365):
            curr_date = start_date + timedelta(days=i)
            day_num = i + 1
            wkday_name = curr_date.strftime('%A')
            is_weekend = curr_date.weekday() >= 5 # 5=Sat, 6=Sun
            
            # 1. MORNING
            img_idx = i % 50
            if is_weekend:
                theme = ai_themes['weekend']
                img_p = weekends[img_idx]
            else:
                theme = ai_themes['morning']
                img_p = mornings[img_idx]
            writer.writerow([day_num, curr_date.strftime('%Y-%m-%d'), wkday_name, 'Morning (9-11 AM)', theme, img_p])
            
            # 2. AFTERNOON
            theme = ai_themes['afternoon']
            img_p = afternoons[img_idx]
            writer.writerow([day_num, curr_date.strftime('%Y-%m-%d'), wkday_name, 'Afternoon (2-4 PM)', theme, img_p])
            
            # 3. NIGHT
            theme = ai_themes['night']
            img_p = nights[img_idx]
            writer.writerow([day_num, curr_date.strftime('%Y-%m-%d'), wkday_name, 'Night (7-9 PM)', theme, img_p])

    print(f"✅ Archivo {output_path} generado con éxito.")

if __name__ == "__main__":
    generate_365_csv()
