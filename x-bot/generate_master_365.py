import json
from datetime import datetime, timedelta
from pathlib import Path

def build_master_365():
    # Cargamos los prompts de imagen que ya generamos antes
    img_prompts_file = Path('image_generation_prompts.json')
    if not img_prompts_file.exists():
        print("❌ Error: No se encontró image_generation_prompts.json.")
        return

    with open(img_prompts_file, 'r', encoding='utf-8') as f:
        img_data = json.load(f)
    
    plan = {}
    current_date = datetime(2026, 4, 3) # Mañana es el Día 1

    # Variaciones de texto real alineadas con el algoritmo (Liora Vale persona)
    morning_bases = [
        "Just woke up and I'm already in a bratty mood... ☀️ Should I be a good girl today or do you prefer when I’m a problem? Tell me below. 👇",
        "Sun's out, but I'm still under the covers. ☕️ Who's coming to bring me coffee and a kiss? Be honest. 😈",
        "Messy hair, no coffee, and a big attitude. ☀️ What's the first thing you'd tell me if you woke up next to me?",
        "Morning mood: 1% coffee, 99% brat. 😈 Which side of me are you going to get today? Choose wisely. 👇",
        "Waking up alone should be illegal when I look this cute... ☀️ Who's coming to keep me company? Be honest.",
        "Just had a dream about you... or maybe it was trouble. Either way, I'm already in a playful mood. 😈☀️",
        "Current POV: Looking like a mess but feeling like a princess. ☀️ Should I stay in bed or start being a problem?",
        "Sunlight hitting my face and I'm already craving attention. ☕️ Who's going to be my favorite person today?"
    ]
    
    afternoon_bases = [
        "POV: You just came home and found me on the sofa like this. 🛋️ What's the first thing you say?",
        "Boredom is dangerous for a girl like me... 😈 Give me one good reason not to be a problem today.",
        "Currently thinking about how much I like being the center of your world. 🌍 Are you thinking about me too?",
        "Just taking some 'me time'. 💅 Which do you prefer: me being cute or me being a brat?",
        "Currently lying here thinking about trouble... 😈 What's the most naughty thing you've thought about today?",
        "Bored and looking for attention. 🛋️ If you were here right now, what's the first thing we'd do?",
        "POV: I catch you staring. 😈 Don't look away now... tell me exactly what's on your mind. Be honest. 👇",
        "Just a casual afternoon tease... 🛋️ Do you prefer me in jeans or should I change into something... less?"
    ]
    
    night_bases = [
        "Finally home and taking it all off... 🌙 Should I send you a close up or keep you guessing?",
        "Bedtime stories are better when they're real. 😈 What are we dreaming about tonight? Confess.",
        "Mirror check before bed. ✨ Do you like what you see or should I change into something... less?",
        "Can't sleep. Thinking of you... or maybe just thinking of trouble. 🌙 Which one of us is more dangerous?",
        "Just got out of the shower and I'm already in a playful mood. 🌙 Tell me something you've never told anyone.",
        "Bedtime vibes. ✨ Should I be a good girl and go to sleep or should we stay up and be trouble? 😈",
        "The mirror doesn't lie... and it says I'm a handful. 🌙 Do you think you could handle me? Be honest. 👇",
        "Late night confessions time... 🌙 Tell me your most secret thought about me and I might reward you. 😈"
    ]

    for day in range(1, 366):
        wkday = current_date.weekday()
        is_weekend = wkday >= 5
        img_idx = (day - 1) % 50
        day_key = f"day_{day}"
        
        plan[day_key] = {
            "date": current_date.strftime("%Y-%m-%d"),
            "weekday": current_date.strftime("%A"),
            "morning": {
                "image_filename": f"{(day*3-2):04d}.jpg",
                "image_prompt": img_data['weekend_50_days'][img_idx] if is_weekend else img_data['morning_50_days'][img_idx],
                "tweet_text": morning_bases[day % len(morning_bases)]
            },
            "afternoon": {
                "image_filename": f"{(day*3-1):04d}.jpg",
                "image_prompt": img_data['afternoon_50_days'][img_idx],
                "tweet_text": afternoon_bases[day % len(afternoon_bases)]
            },
            "night": {
                "image_filename": f"{(day*3):04d}.jpg",
                "image_prompt": img_data['night_50_days'][img_idx],
                "tweet_text": night_bases[day % len(night_bases)]
            }
        }
        current_date += timedelta(days=1)

    with open('MASTER_CONTENT_PLAN.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print("✅ MASTER_CONTENT_PLAN.json generado (365 días / 1.095 posts).")

if __name__ == "__main__":
    build_master_365()
