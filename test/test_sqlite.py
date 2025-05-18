import requests
import json
from datetime import datetime
import sqlite3
import os
import time


# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"


def test_completo():
    """
        Ejecuta una prueba integral del sistema, incluyendo:

        - Registro y login de usuarios
        - Creación de rutas (manuales y automáticas)
        - Consulta y filtrado de rutas
        - Edición de perfiles
        - Consulta de clima
        - Eliminación de usuarios
    """
    print("\nIniciando test completo del sistema...")

    # 1. Crear usuarios de prueba
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuarios_prueba = [
        {
            "nombre": "Test",
            "apellido": "Alicante",
            "email": f"test_alicante_{timestamp}@test.com",
            "username": f"test_alicante_{timestamp}",
            "password": "test123",
            "telefono": "987654321",
            "fecha_nacimiento": "1995-01-01",
            "ciudad": "Alicante"
        },
        {
            "nombre": "Test2",
            "apellido": "Alicante2",
            "email": f"test_alicante2_{timestamp}@test.com",
            "username": f"test_alicante2_{timestamp}",
            "password": "test123",
            "telefono": "987654322",
            "fecha_nacimiento": "1995-01-02",
            "ciudad": "Alicante"
        }
    ]

    # Direcciones de Alicante para las rutas
    direcciones_alicante = [
        "Avenida de Maisonnave",
        "Mercado Central de Alicante",
        "Hospital General Universitario de Alicante",
        "Puerto de Alicante",
        "Playa de la Albufereta",
        "Parque de Canalejas",
        "Avenida de la Rambla"
    ]

    print("\nRegistrando usuarios de prueba...")
    for usuario in usuarios_prueba:
        response = requests.post(f"{BASE_URL}/api/usuarios/registro", json=usuario)
        print(f"Registro de {usuario['username']}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 2. Probar login de usuarios
    print("\nProbando login de usuarios...")
    for usuario in usuarios_prueba:
        login_data = {
            "username": usuario["username"],
            "password": usuario["password"]
        }
        response = requests.post(f"{BASE_URL}/api/usuarios/login", json=login_data)
        print(f"Login de {usuario['username']}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 3. Crear rutas manuales
    print("\nCreando rutas manuales...")
    rutas_manuales = [
        {
            "origen": {"direccion": direcciones_alicante[0]},
            "destino": {"direccion": direcciones_alicante[1]},
            "modo": "walk",
            "nombre": f"Ruta_Manual_1_{timestamp}",
            "username": usuarios_prueba[0]["username"]
        },
        {
            "origen": {"direccion": direcciones_alicante[2]},
            "destino": {"direccion": direcciones_alicante[3]},
            "modo": "drive",
            "nombre": f"Ruta_Manual_2_{timestamp}",
            "username": usuarios_prueba[0]["username"]
        }
    ]

    for ruta in rutas_manuales:
        response = requests.post(f"{BASE_URL}/api/rutas", json=ruta)
        print(f"Creación de ruta {ruta['nombre']}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        time.sleep(2)  # Esperar entre peticiones para no sobrecargar la API

    # 4. Crear rutas automáticas
    print("\nCreando rutas automáticas...")
    ruta_auto = {
        "direcciones": direcciones_alicante[:4],  # Usar las primeras 4 direcciones
        "cantidad": 2,
        "username": usuarios_prueba[1]["username"]
    }

    response = requests.post(f"{BASE_URL}/api/rutas/auto", json=ruta_auto)
    print("Creación de rutas automáticas:")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    time.sleep(2)

    # 5. Verificar rutas de usuarios
    print("\nVerificando rutas de usuarios...")
    for usuario in usuarios_prueba:
        response = requests.get(f"{BASE_URL}/api/usuarios/{usuario['username']}/rutas")
        print(f"Rutas de {usuario['username']}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 6. Probar búsqueda de usuarios
    print("\nProbando búsqueda de usuarios...")
    search_term = "test_alicante"
    response = requests.get(f"{BASE_URL}/api/usuarios/buscar", params={"nombre": search_term})
    print(f"Búsqueda de usuarios con término '{search_term}':")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 7. Probar consulta de clima
    print("\nProbando consulta de clima...")
    response = requests.get(f"{BASE_URL}/api/clima", params={"ciudad": "Alicante"})
    print("Consulta de clima en Alicante:")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 8. Probar filtrado de rutas
    print("\nProbando filtrado de rutas...")
    filtros = [
        {"dificultad": "bajo"},
        {"max_km": 5},
        {"max_horas": 2},
        {"modo_transporte": "walk"}
    ]

    for filtro in filtros:
        response = requests.get(f"{BASE_URL}/api/rutas/filtrar", params=filtro)
        print(f"Filtrado con {filtro}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        time.sleep(1)

    # 9. Probar edición de perfil
    print("\nProbando edición de perfil...")
    datos_edicion = {
        "username": usuarios_prueba[0]["username"],
        "nombre": "Test Modificado",
        "apellido": "Alicante Modificado",
        "telefono": "987654333",
        "ciudad": "Alicante"
    }

    response = requests.post(f"{BASE_URL}/api/usuarios/editar", json=datos_edicion)
    print("Edición de perfil:")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    # 10. Probar eliminación de usuario
    print("\nProbando eliminación de usuario...")
    for usuario in usuarios_prueba:
        response = requests.post(
            f"{BASE_URL}/api/usuarios/{usuario['username']}",
            json={"accion": "eliminar"}
        )
        print(f"Eliminación de {usuario['username']}:")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        time.sleep(1)


if __name__ == "__main__":
    test_completo()
