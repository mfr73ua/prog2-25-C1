import requests
import json
from datetime import datetime
import time

BASE_URL = "https://ra55.pythonanywhere.com"

def test_endpoint(endpoint, method="GET", data=None, params=None, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url, json=data)
        else:
            raise ValueError(f"Método no soportado: {method}")

        print(f"\nProbando {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == expected_status:
            print("Test exitoso")
            return True
        else:
            print("Test fallido - Status code incorrecto")
            return False

    except Exception as e:
        print(f"Error en {endpoint}: {str(e)}")
        return False

def main():
    print("Iniciando pruebas completas de endpoints para Madrid...")

    direcciones_madrid = [
        "Puerta del Sol",
        "Parque del Retiro",
        "Museo del Prado",
        "Estadio Santiago Bernabéu",
        "Plaza Mayor",
        "Palacio Real",
        "Gran Vía"
    ]

    print("\n1. Probando endpoint principal")
    test_endpoint("/")
    time.sleep(1)

    print("\n2. Probando registro de usuario")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuario_prueba = {
        "nombre": "Test",
        "apellido": "Madrid",
        "email": f"test_madrid_{timestamp}@test.com",
        "username": f"test_madrid_{timestamp}",
        "password": "test123",
        "telefono": "912345678",
        "fecha_nacimiento": "1990-05-20",
        "ciudad": "Madrid"
    }
    test_endpoint("/api/usuarios/registro", method="POST", data=usuario_prueba)
    time.sleep(1)

    print("\n3. Probando login")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    test_endpoint("/api/usuarios/login", method="POST", data=login_data)
    time.sleep(1)

    print("\n4. Probando creación de ruta manual")
    ruta_data = {
        "origen": {"direccion": direcciones_madrid[0]},
        "destino": {"direccion": direcciones_madrid[1]},
        "modo": "car",
        "nombre": f"Ruta_Manual_{timestamp}",
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas", method="POST", data=ruta_data)
    time.sleep(2)

    print("\n5. Probando creación de rutas automáticas")
    rutas_auto_data = {
        "direcciones": direcciones_madrid[:4],
        "cantidad": 3,
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas/auto", method="POST", data=rutas_auto_data)
    time.sleep(2)

    print("\n6. Probando obtener rutas del usuario")
    test_endpoint(f"/api/usuarios/{usuario_prueba['username']}/rutas")
    time.sleep(1)

    print("\n7. Probando búsqueda de usuarios")
    test_endpoint("/api/usuarios/buscar", params={"nombre": "test_madrid"})
    time.sleep(1)

    print("\n8. Probando edición de perfil")
    datos_edicion = {
        "username": usuario_prueba["username"],
        "nombre": "Test Modificado",
        "apellido": "Madrid Modificado",
        "telefono": "912340000",
        "ciudad": "Madrid"
    }
    test_endpoint("/api/usuarios/editar", method="POST", data=datos_edicion)
    time.sleep(1)

    print("\n9. Probando filtrado de rutas")
    filtros = [
        {"dificultad": "medio"},
        {"max_km": 8},
        {"max_horas": 3},
        {"modo_transporte": "car"}
    ]

    for filtro in filtros:
        test_endpoint("/api/rutas/filtrar", params=filtro)
        time.sleep(1)

    print("\n10. Probando consulta de clima")
    test_endpoint("/api/clima", params={"ciudad": "Madrid"})
    time.sleep(1)

    print("\n11. Probando eliminación de usuario")
    test_endpoint(
        f"/api/usuarios/{usuario_prueba['username']}",
        method="POST",
        data={"accion": "eliminar"}
    )

    print("\nPruebas completadas para Madrid!")

if __name__ == "__main__":
    main()