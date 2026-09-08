from curl_cffi import requests
from datetime import datetime, timedelta, timezone

def get_recent_kick_clips(channel_slug, days=30):
    # A Kick belső API végpontja
    url = f"https://kick.com/api/v2/channels/{channel_slug}/clips"
    
    # Fontos: A böngésző ujjlenyomatának utánzása (impersonate="chrome")
    # Ez segít átjutni a Cloudflare védelmen.
    try:
        response = requests.get(url, impersonate="chrome120", timeout=10)
        
        if response.status_code != 200:
            print(f"Hiba történt: {response.status_code}")
            return []
            
        data = response.json()
        clips = data.get("clips", [])
        
        # Dátum határ kiszámítása (mai nap - 30 nap)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        recent_clips = []
        
        print(f"--- {channel_slug} legfrissebb klippjei (utolsó {days} nap) ---")
        
        for clip in clips:
            # A Kick dátum formátuma: "2023-10-27T14:30:00.000Z"
            created_at_str = clip.get("created_at")
            if not created_at_str:
                continue
                
            # Dátum konvertálása datetime objektummá
            # A Python 3.11+ kezeli a 'Z'-t, régebbinél replace kellhet
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            
            # Szűrés: ha újabb, mint a határdátum
            if created_at > cutoff_date:
                recent_clips.append({
                    "title": clip.get("title"),
                    "url": f"https://kick.com/{channel_slug}?clip={clip.get('id')}",
                    "date": created_at.strftime("%Y-%m-%d %H:%M"),
                    "views": clip.get("views"),
                    "duration": clip.get("duration")
                })

        return recent_clips

    except Exception as e:
        print(f"Kivétel történt: {e}")
        return []

# --- Futtatás ---

channel_name = "alfonsine" 
clips = get_recent_kick_clips(channel_name)

if clips:
    for c in clips:
        print(f"[{c['date']}] {c['title']} | Nézettség: {c['views']}")
        print(f"Link: {c['url']}")
        print("-" * 20)
else:
    print("Nem találtunk 30 napnál frissebb klippet, vagy hiba történt.")