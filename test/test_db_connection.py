import requests
import json
from datetime import datetime
import time

# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"


def test_endpoint(endpoint, method="GET", data=None, params=None, expected_status=200):
    """
    Función auxiliar para probar los endpoints de la API.

    Parameters
    ----------
    endpoint : str
        Ruta relativa del endpoint (por ejemplo, '/api/usuarios/login').
    method : str, optional
        Método HTTP: 'GET', 'POST', 'PUT' o 'DELETE'. Por defecto 'GET'.
    data : dict, optional
        Datos enviados en el cuerpo de la petición (para POST, PUT, DELETE).
    params : dict, optional
        Parámetros de consulta (para GET).
    expected_status : int, optional
        Código de estado HTTP esperado. Por defecto 200.

    Returns
    -------
    bool
        True si el código de estado es el esperado, False en caso contrario o excepción.

    """
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


def test_database_operations():
    """
       Ejecuta una batería completa de pruebas sobre la API de usuarios y rutas.

       Incluye operaciones como:
       - Registro y login de usuario
       - Detección de duplicados
       - Creación y verificación de rutas
       - Edición y eliminación de usuario
       - Búsqueda de usuarios

       Cada prueba valida la respuesta esperada y reporta el resultado por consola.
       """
    print("\nIniciando pruebas completas de la base de datos...")

    # 1. Crear usuario de prueba
    print("\nProbando creación de usuario")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuario_prueba = {
        "nombre": "Test",
        "apellido": "DB",
        "email": f"db_test_{timestamp}@test.com",
        "username": f"db_user_{timestamp}",
        "password": "test123",
        "telefono": "123456789",
        "fecha_nacimiento": "1990-01-01",
        "ciudad": "Alicante"
    }
    test_endpoint("/api/usuarios/registro", method="POST", data=usuario_prueba)
    time.sleep(1)

    # 2. Intentar crear usuario duplicado (debe fallar)
    print("\nProbando creación de usuario duplicado")
    test_endpoint("/api/usuarios/registro", method="POST", data=usuario_prueba, expected_status=400)
    time.sleep(1)

    # 3. Login con credenciales correctas
    print("\nProbando login con credenciales correctas")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    test_endpoint("/api/usuarios/login", method="POST", data=login_data)
    time.sleep(1)

    # 4. Login con credenciales incorrectas
    print("\nProbando login con credenciales incorrectas")
    login_data_incorrecto = {
        "username": usuario_prueba["username"],
        "password": "password_incorrecto"
    }
    test_endpoint("/api/usuarios/login", method="POST", data=login_data_incorrecto, expected_status=401)
    time.sleep(1)

    # 5. Crear ruta para el usuario
    print("\nProbando creación de ruta")
    ruta_data = {
        "origen": {"direccion": "Avenida de Maisonnave"},
        "destino": {"direccion": "Mercado Central de Alicante"},
        "modo": "walk",
        "nombre": f"Ruta_DB_Test_{timestamp}",
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas", method="POST", data=ruta_data)
    time.sleep(2)

    # 6. Verificar que la ruta se guardó correctamente
    print("\nVerificando rutas del usuario")
    test_endpoint(f"/api/usuarios/{usuario_prueba['username']}/rutas")
    time.sleep(1)

    # 7. Editar perfil del usuario
    print("\nProbando edición de perfil")
    datos_edicion = {
        "username": usuario_prueba["username"],
        "nombre": "Test Modificado",
        "apellido": "DB Modificado",
        "telefono": "987654321",
        "ciudad": "Alicante"
    }
    test_endpoint("/api/usuarios/editar", method="POST", data=datos_edicion)
    time.sleep(1)

    # 8. Verificar que los cambios se guardaron
    print("\nVerificando cambios en el perfil")
    test_endpoint("/api/usuarios/buscar", params={"nombre": "Test Modificado"})
    time.sleep(1)

    # 9. Probar búsqueda de usuario inexistente
    print("\nProbando búsqueda de usuario inexistente")
    test_endpoint("/api/usuarios/buscar", params={"nombre": "usuario_inexistente"})
    time.sleep(1)

    # 10. Eliminar usuario y sus rutas
    print("\nProbando eliminación de usuario")
    test_endpoint(
        f"/api/usuarios/{usuario_prueba['username']}",
        method="POST",
        data={"accion": "eliminar"}
    )
    time.sleep(1)

    # 11. Verificar que el usuario fue eliminado
    print("\nVerificando eliminación del usuario")
    test_endpoint("/api/usuarios/buscar", params={"nombre": usuario_prueba["username"]})

    print("\nPruebas de base de datos completadas!")


if __name__ == "__main__":
    test_database_operations() 
