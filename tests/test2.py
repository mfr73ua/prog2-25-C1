import requests

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Registro de usuario
print("📌 1. Registrando usuario...")
registro_data = {
    "nombre": "Carla",
    "apellido": "Méndez",
    "email": "carla@example.com",
    "username": "carla_mendez",
    "telefono": "600999999",
    "fecha_nacimiento": "1992-04-10",
    "ciudad": "Alicante",
    "password": "carla456"
}
resp = requests.post(f"{BASE_URL}/registro", json=registro_data)
print("✅ Registro:", resp.status_code, resp.json())

# 2. Login
print("\n🔐 2. Iniciando sesión...")
login_data = {"username": "carla_mendez", "password": "carla456"}
resp = requests.post(f"{BASE_URL}/login", json=login_data)
print("✅ Login:", resp.status_code, resp.json())
assert resp.status_code == 200, "Login fallido, no se puede continuar."

# 3. Crear ruta manual
print("\n🛤️ 3. Creando ruta manual...")
ruta_manual_data = {
    "username": "carla_mendez",
    "password": "carla456",
    "origen": "Museo de Arte Contemporáneo",
    "intermedios": [str(i) for i in ["Concatedral de San Nicolás", "Ayuntamiento de Alicante"]],
    "destino": "Castillo de Santa Bárbara",
    "modo": "walk",
    "nombre": "ruta_valencia_carla"
}
resp = requests.post(f"{BASE_URL}/ruta_manual", json=ruta_manual_data)
print("✅ Ruta manual:", resp.status_code, resp.json())

# 4. Crear rutas automáticas
print("\n⚙️ 4. Generando rutas automáticas...")
rutas_auto_data = {
    "username": "carla_mendez",
    "password": "carla456",
    "direcciones": [
        "Parque El Palmeral",
        "Explanada de España",
        "Puerto de Alicante",
        "Plaza de Toros de Alicante"
    ],
    "cantidad": 3
}
resp = requests.post(f"{BASE_URL}/ruta_auto", json=rutas_auto_data)
print("✅ Rutas automáticas:", resp.status_code)
for linea in resp.json().get("rutas", []):
    print("🔹", linea)

# 5. Consultar clima
print("\n☁️ 5. Consultando clima en Alicante...")
resp = requests.get(f"{BASE_URL}/clima", params={"ciudad": "Alicante"})
print("✅ Clima:", resp.status_code)
for k, v in resp.json().items():
    print(f"{k.capitalize()}: {v}")

# 6. Obtener rutas del usuario
print("\n📦 6. Obteniendo rutas del usuario 'carla_mendez'...")
resp = requests.get(f"{BASE_URL}/usuarios/carla_mendez/rutas")
print("✅ Rutas del usuario:", resp.status_code, resp.json())

# 7. Listar todas las rutas del sistema
print("\n🌍 7. Listando todas las rutas del sistema...")
resp = requests.get(f"{BASE_URL}/rutas")
print("✅ Total rutas:", resp.status_code, len(resp.json().get("rutas", [])))

# 8. Filtrar rutas del sistema
print("\n🔎 8. Filtrando rutas por dificultad='bajo', modo='walk', max_distancia=5...")
resp = requests.get(f"{BASE_URL}/rutas", params={
    "dificultad": "bajo",
    "modo": "walk",
    "distancia_max": 5
})
print("✅ Rutas filtradas:", resp.status_code, len(resp.json().get("rutas", [])))
for r in resp.json().get("rutas", [])[:2]:
    print("🔹", r["nombre"])

# 9. Descargar PDF
print("\n📄 9. Descargando PDF de la ruta 'ruta_valencia_carla'...")
resp = requests.get(f"{BASE_URL}/rutas/ruta_valencia_carla/pdf")
if resp.status_code == 200:
    with open("test2.pdf", "wb") as f:
        f.write(resp.content)
    print("✅ PDF descargado como 'test2.pdf'")
else:
    print("⚠️ No se encontró el PDF:", resp.status_code)

# 10. Descargar HTML
print("\n🌐 10. Descargando HTML de la ruta 'ruta_valencia_carla'...")
resp = requests.get(f"{BASE_URL}/rutas/ruta_valencia_carla/html")
if resp.status_code == 200:
    with open("test2.html", "wb") as f:
        f.write(resp.content)
    print("✅ HTML descargado como 'test2.html'")
else:
    print("⚠️ No se encontró el HTML:", resp.status_code)
