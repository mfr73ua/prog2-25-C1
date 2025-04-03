import requests

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Registro de usuario
print("📌 1. Registrando usuario...")
registro_data = {
    "nombre": "Paula",
    "apellido": "Martín",
    "email": "paula@example.com",
    "username": "paula_martin",
    "telefono": "600111111",
    "fecha_nacimiento": "1990-01-01",
    "ciudad": "Alicante",
    "password": "paula123"
}
resp = requests.post(f"{BASE_URL}/registro", json=registro_data)
print("✅ Registro:", resp.status_code, resp.json())

# 2. Login
print("\n🔐 2. Iniciando sesión...")
login_data = {"username": "paula_martin", "password": "paula123"}
resp = requests.post(f"{BASE_URL}/login", json=login_data)
print("✅ Login:", resp.status_code, resp.json())
assert resp.status_code == 200, "Login fallido, no se puede continuar."

# 3. Crear ruta manual
print("\n🛤️ 3. Creando ruta manual...")
ruta_manual_data = {
    "username": "paula_martin",
    "password": "paula123",
    "origen": "Explanada de España",
    "intermedios": [str(i) for i in ['Concatedral de San Nicolás', 'Ayuntamiento de Alicante']],
    "destino": "Castillo de Santa Bárbara",
    "modo": "walk",
    "nombre": "alicante_ruta_paula"
}
resp = requests.post(f"{BASE_URL}/ruta_manual", json=ruta_manual_data)
print("✅ Ruta manual:", resp.status_code, resp.json())

# 4. Crear rutas automáticas
print("\n⚙️ 4. Generando rutas automáticas...")
rutas_auto_data = {
    "username": "paula_martin",
    "password": "paula123",
    "direcciones": [
        "Parque de Canalejas",
        "Museo de Arte Contemporáneo",
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
print("\n📦 6. Obteniendo rutas del usuario 'paula_martin'...")
resp = requests.get(f"{BASE_URL}/usuarios/paula_martin/rutas")
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
print("\n📄 9. Descargando PDF de la ruta 'alicante_ruta_paula'...")
resp = requests.get(f"{BASE_URL}/rutas/alicante_ruta_paula/pdf")
if resp.status_code == 200:
    with open("test3.pdf", "wb") as f:
        f.write(resp.content)
    print("✅ PDF descargado como 'test3.pdf'")
else:
    print("⚠️ No se encontró el PDF:", resp.status_code)

# 10. Descargar HTML
print("\n🌐 10. Descargando HTML de la ruta 'alicante_ruta_paula'...")
resp = requests.get(f"{BASE_URL}/rutas/alicante_ruta_paula/html")
if resp.status_code == 200:
    with open("test3.html", "wb") as f:
        f.write(resp.content)
    print("✅ HTML descargado como 'test3.html'")
else:
    print("⚠️ No se encontró el HTML:", resp.status_code)
