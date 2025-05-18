import requests
import time

API = "http://127.0.0.1:8000/api"

def imprimir_respuesta(r):
    try:
        print("Respuesta:", r.status_code, r.json())
    except Exception:
        print("Respuesta (no JSON):", r.status_code, r.text)

usuario = {
    "nombre": "Ejemplo",
    "apellido": "Tester",
    "email": "ejemplo@test.com",
    "username": "test_user123",
    "telefono": "666666666",
    "fecha_nacimiento": "2000-01-01",
    "ciudad": "Alicante",
    "password": "test1234"
}

# Registro correcto
print("📤 Registrando usuario...")
r = requests.post(f"{API}/usuarios/registro", json=usuario)
imprimir_respuesta(r)

# Login
print("🔐 Iniciando sesión...")
r = requests.post(f"{API}/login", json={"username": usuario["username"], "password": usuario["password"]})
imprimir_respuesta(r)

# Crear rutas (enviar directamente la ruta)
print("🚣️ Añadiendo rutas de prueba...")
rutas = [
    {
        "nombre": "ruta_test_123",
        "origen": "Alicante",
        "destino": "Castillo Santa Bárbara",
        "modo_transporte": "walk",
        "distancia": "5.2 km",
        "duracion": "1 h",
        "dificultad": "fácil",
        "fecha_registro": "2025-05-06",
        "puntos_intermedios": ["Parque Canalejas", "Puerto de Alicante"],
        "ubicacion": [38.3452, -0.4810]
    },
    {
        "nombre": "ruta_test_124",
        "origen": "Playa Postiguet",
        "destino": "Museo Arqueológico",
        "modo_transporte": "bike",
        "distancia": "3.1 km",
        "duracion": "30 min",
        "dificultad": "medio",
        "fecha_registro": "2025-05-06",
        "puntos_intermedios": ["Explanada", "Mercado Central"],
        "ubicacion": [38.3461, -0.4783]
    }
]

for ruta in rutas:
    r = requests.post(f"{API}/usuarios/{usuario['username']}/rutas", json=ruta)
    print("Ruta:", ruta["nombre"])
    imprimir_respuesta(r)

# Ver rutas del usuario
print("📁 Listando rutas...")
r = requests.get(f"{API}/usuarios/{usuario['username']}/rutas")
imprimir_respuesta(r)

# Buscar usuarios
print("🔎 Buscando usuarios por nombre 'test'...")
r = requests.get(f"{API}/usuarios/buscar", params={"nombre": "test"})
imprimir_respuesta(r)

# Actualizar perfil
print("✏️ Actualizando perfil del usuario...")
actualizacion = {"ciudad": "Elche", "telefono": "699999999"}
r = requests.put(f"{API}/usuarios/{usuario['username']}", json=actualizacion)
imprimir_respuesta(r)

# Ver estadísticas
print("📊 Consultando estadísticas del usuario...")
r = requests.get(f"{API}/usuarios/{usuario['username']}/estadisticas")
imprimir_respuesta(r)

# Ver rutas PDF/HTML
print("🌐 Verificamos generación de archivos PDF/HTML para rutas...")
for ruta in rutas:
    nombre = ruta["nombre"]
    r_pdf = requests.get(f"{API}/rutas/{nombre}/pdf")
    r_html = requests.get(f"{API}/rutas/{nombre}/html")
    print(f"PDF {nombre}: {r_pdf.status_code} | HTML {nombre}: {r_html.status_code}")

# Ver rutas comunes con amigos
print("🧑‍🤝‍🧑 Viendo rutas compartidas con amigos...")
r = requests.get(f"{API}/usuarios/{usuario['username']}/amigos_comunes")
imprimir_respuesta(r)

# Borrar rutas añadidas
print("❌ Borrando rutas de prueba...")
for ruta in rutas:
    r = requests.delete(f"{API}/usuarios/{usuario['username']}/rutas/{ruta['nombre']}")
    print("Borrada:", ruta["nombre"], "=>", r.status_code)

# Borrar usuario
print("🗑️ Borrando cuenta de prueba...")
r = requests.delete(f"{API}/usuarios/{usuario['username']}")
imprimir_respuesta(r)
