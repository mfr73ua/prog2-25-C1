import requests

API_URL = "https://ra55.pythonanywhere.com/api/rutas/auto"
datos = {
    "direcciones": [
        "Avenida de la Estación, Alicante",
        "Plaza de los Luceros, Alicante",
        "Calle San Vicente, Alicante"
    ],
    "cantidad": 2,
    "username": "rare"
}

resp = requests.post(API_URL, json=datos)
print("Status:", resp.status_code)
try:
    print("Respuesta:", resp.json())
except Exception as e:
    print("Error al decodificar JSON:", e)
    print("Texto bruto:", resp.text)