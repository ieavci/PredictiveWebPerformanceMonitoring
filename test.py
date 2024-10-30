import requests
import json

# Flask uygulamanızın çalıştığı URL
url = 'http://127.0.0.1:5000/predict'

# Göndereceğiniz örnek veriler
data = {
    "grpThreads": [10],
    "allThreads": [5],
    "Latency": [200],
    "bytes": [500],
    "sentBytes": [450],
    "success": ["true"]
}

# JSON formatında POST isteği gönderme
response = requests.post(url, json=data)

# Gelen yanıtı kontrol etme
if response.status_code == 200:
    print('Tahmin:', response.json())
else:
    print('Hata:', response.status_code, response.text)
