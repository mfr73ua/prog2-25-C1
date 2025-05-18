import requests
import json
from datetime import datetime
import time

# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"

def test_endpoint(endpoint, method="GET", data=None, params=None, expected_status=200):
    """
    Función auxiliar para probar endpoints
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

        print(f"\n🔍 Probando {method} {endpoint}")
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == expected_status:
            print("✅ Test exitoso")
            return True
        else:
            print("❌ Test fallido - Status code incorrecto")
            return False
            
    except Exception as e:
        print(f"❌ Error en {endpoint}: {str(e)}")
        return False

def main():
    print("🚀 Iniciando pruebas completas de endpoints...")
    
    # Direcciones de Alicante para las pruebas
    direcciones_alicante = [
        "Avenida de Maisonnave",
        "Mercado Central de Alicante",
        "Hospital General Universitario de Alicante",
        "Puerto de Alicante",
        "Playa de la Albufereta",
        "Parque de Canalejas",
        "Avenida de la Rambla"
    ]
    
    # 1. Probar endpoint principal
    print("\n1️⃣ Probando endpoint principal")
    test_endpoint("/")
    time.sleep(1)

    # 2. Probar registro de usuario
    print("\n2️⃣ Probando registro de usuario")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuario_prueba = {
        "nombre": "Test",
        "apellido": "Alicante",
        "email": f"test_alicante_{timestamp}@test.com",
        "username": f"test_alicante_{timestamp}",
        "password": "test123",
        "telefono": "987654321",
        "fecha_nacimiento": "1995-01-01",
        "ciudad": "Alicante"
    }
    test_endpoint("/api/usuarios/registro", method="POST", data=usuario_prueba)
    time.sleep(1)

    # 3. Probar login
    print("\n3️⃣ Probando login")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    test_endpoint("/api/usuarios/login", method="POST", data=login_data)
    time.sleep(1)

    # 4. Probar creación de ruta manual
    print("\n4️⃣ Probando creación de ruta manual")
    ruta_data = {
        "origen": {"direccion": direcciones_alicante[0]},
        "destino": {"direccion": direcciones_alicante[1]},
        "modo": "walk",
        "nombre": f"Ruta_Manual_{timestamp}",
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas", method="POST", data=ruta_data)
    time.sleep(2)

    # 5. Probar creación de rutas automáticas
    print("\n5️⃣ Probando creación de rutas automáticas")
    rutas_auto_data = {
        "direcciones": direcciones_alicante[:4],
        "cantidad": 2,
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas/auto", method="POST", data=rutas_auto_data)
    time.sleep(2)

    # 6. Probar obtener rutas del usuario
    print("\n6️⃣ Probando obtener rutas del usuario")
    test_endpoint(f"/api/usuarios/{usuario_prueba['username']}/rutas")
    time.sleep(1)

    # 7. Probar búsqueda de usuarios
    print("\n7️⃣ Probando búsqueda de usuarios")
    test_endpoint("/api/usuarios/buscar", params={"nombre": "test_alicante"})
    time.sleep(1)

    # 8. Probar edición de perfil
    print("\n8️⃣ Probando edición de perfil")
    datos_edicion = {
        "username": usuario_prueba["username"],
        "nombre": "Test Modificado",
        "apellido": "Alicante Modificado",
        "telefono": "987654333",
        "ciudad": "Alicante"
    }
    test_endpoint("/api/usuarios/editar", method="POST", data=datos_edicion)
    time.sleep(1)

    # 9. Probar filtrado de rutas
    print("\n9️⃣ Probando filtrado de rutas")
    filtros = [
        {"dificultad": "bajo"},
        {"max_km": 5},
        {"max_horas": 2},
        {"modo_transporte": "walk"}
    ]
    
    for filtro in filtros:
        test_endpoint("/api/rutas/filtrar", params=filtro)
        time.sleep(1)

    # 10. Probar consulta de clima
    print("\n🔟 Probando consulta de clima")
    test_endpoint("/api/clima", params={"ciudad": "Alicante"})
    time.sleep(1)


    # 12. Probar eliminación de usuario
    print("\n1️⃣1️⃣ Probando eliminación de usuario")
    test_endpoint(
        f"/api/usuarios/{usuario_prueba['username']}", 
        method="POST",
        data={"accion": "eliminar"}
    )

    print("\n✨ Pruebas completadas!")

if __name__ == "__main__":
    main() 