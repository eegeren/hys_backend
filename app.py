from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List
import requests
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = FastAPI()

# Firebase FCM bilgileri
FCM_URL = "https://fcm.googleapis.com/fcm/send"
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")

# Hafızada token listesi (geçici)
registered_tokens: List[str] = []

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "FastAPI servisi çalışıyor ✅"}

# FCM token kaydı (mobil uygulamadan gelen)
@app.post("/token")
def register_token(token: str = Body(...)):
    if token not in registered_tokens:
        registered_tokens.append(token)
        print("✅ Yeni token kaydedildi:", token)
    else:
        print("ℹ️ Token zaten kayıtlı:", token)
    return {"status": "Token kaydedildi"}

# Duyuru modelimiz
class Notification(BaseModel):
    title: str
    body: str

# Duyuru gönderme endpoint'i
@app.post("/ik/send_announcement")
def send_announcement(data: Notification):
    if not registered_tokens:
        return {"status": "❌ Kayıtlı FCM token bulunamadı"}

    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    success, failed = 0, 0

    for token in registered_tokens:
        payload = {
            "to": token,
            "notification": {
                "title": data.title,
                "body": data.body
            }
        }

        res = requests.post(FCM_URL, json=payload, headers=headers)

        if res.status_code == 200:
            print(f"✅ Bildirim gönderildi → {token}")
            success += 1
        else:
            print(f"❌ Hata → {token}: {res.text}")
            failed += 1

    return {
        "status": "Duyuru tamamlandı",
        "başarılı": success,
        "başarısız": failed
    }

# --- LOCAL TEST KISMI ---
if __name__ == "__main__":
    try:
        import uvicorn
        print("✅ uvicorn bulundu. Sunucu başlatılıyor...")
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        print("❌ uvicorn modülü yüklü değil. Lütfen requirements.txt dosyasına ekleyin.")
