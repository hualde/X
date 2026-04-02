import json
from datetime import datetime, timedelta
from pathlib import Path

def build_plan():
    prompts_file = Path('prompts.json')
    img_prompts_file = Path('image_generation_prompts.json')
    
    if not prompts_file.exists() or not img_prompts_file.exists():
        print("❌ Error: Faltan archivos de configuración (prompts.json o image_generation_prompts.json).")
        return

    with open(prompts_file, 'r', encoding='utf-8') as f:
        ai = json.load(f)
    with open(img_prompts_file, 'r', encoding='utf-8') as f:
        img = json.load(f)
    
    full_plan = {}
    current_date = datetime(2026, 4, 2)
    
    for day_num in range(1, 366):
        is_weekend = current_date.weekday() >= 5 # 5=Sat, 6=Sun
        img_idx = (day_num - 1) % 50
        
        full_plan[f"day_{day_num}"] = {
            "date": current_date.strftime("%Y-%m-%d"),
            "weekday": current_date.strftime("%A"),
            "morning": {
                "image_prompt": img['weekend_50_days'][img_idx] if is_weekend else img['morning_50_days'][img_idx],
                "tweet_text": ai['weekend'] if is_weekend else ai['morning']
            },
            "afternoon": {
                "image_prompt": img['afternoon_50_days'][img_idx],
                "tweet_text": ai['afternoon']
            },
            "night": {
                "image_prompt": img['night_50_days'][img_idx],
                "tweet_text": ai['night']
            }
        }
        current_date += timedelta(days=1)

    with open('COMPLETE_PLAN_365.json', 'w', encoding='utf-8') as f:
        json.dump(full_plan, f, indent=2, ensure_ascii=False)
    
    print("✅ Archivo COMPLETE_PLAN_365.json generado con éxito para los próximos 365 días.")

if __name__ == "__main__":
    build_plan()
