"""
Aplicación Flask para la gestión de rutas geográficas.

Este módulo implementa una API RESTful para gestionar rutas geográficas,
usuarios y servicios relacionados como el clima.
"""

from flask import Flask, jsonify, request, send_from_directory
from gestor_rutas import GestorRutas
from usuario import Usuario
from ruta_manual import RutaManual
from ruta_auto import RutaAuto

# Importación condicional del servicio de clima
try:
    from servicio_clima import ServicioOpenWeatherMap as ServicioClima
    servicio_clima_disponible = True
except ImportError:
    servicio_clima_disponible = False

app = Flask(__name__, static_folder='static')
gestor = GestorRutas()

# Configuración de CORS para permitir peticiones desde cualquier origen
@app.after_request
def after_request(response):
    """
    Configura los encabezados CORS para permitir peticiones desde cualquier origen.

    Parameters
    ----------
    response : Response
        Objeto de respuesta Flask.

    Returns
    -------
    Response
        Objeto de respuesta modificado con los encabezados CORS.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Ruta principal
@app.route('/')
def home():
    """
    Ruta principal que verifica que la API está funcionando.

    Returns
    -------
    Response
        Respuesta JSON con información sobre el estado de la API.
    """
    return jsonify({
        "status": "success",
        "message": "API funcionando correctamente",
        "version": "1.0.0"
    })

# Endpoints estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Sirve archivos estáticos (HTML, PDF, GPX, PNG).

    Parameters
    ----------
    filename : str
        Nombre del archivo a servir.

    Returns
    -------
    Response
        Archivo estático solicitado.
    """
    return send_from_directory('static', filename)

# Endpoints de Usuarios
@app.route('/api/usuarios/login', methods=['POST'])
def login():
    """
    Endpoint para autenticar a un usuario.

    Requiere un JSON con username y password.

    Returns
    -------
    Response
        Datos del usuario si la autenticación es exitosa.
    """
    try:
        datos = request.json
        username = datos.get('username')
        password = datos.get('password')

        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Se requieren username y password"
            }), 400

        usuario = Usuario.iniciar_sesion(username, password)

        if usuario:
            return jsonify({
                "status": "success",
                "data": {
                    "username": usuario.username,
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "email": usuario.email,
                    "ciudad": usuario.ciudad
                }
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Credenciales inválidas"
            }), 401

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/usuarios/registro', methods=['POST'])
def registro():
    """
    Endpoint para registrar un nuevo usuario.

    Requiere un JSON con todos los campos del usuario.

    Returns
    -------
    Response
        Confirmación del registro o error.
    """
    try:
        datos = request.json
        required_fields = ['nombre', 'apellido', 'email', 'username', 'telefono',
                         'fecha_nacimiento', 'ciudad', 'password']

        for field in required_fields:
            if field not in datos:
                return jsonify({
                    "status": "error",
                    "message": f"Falta el campo requerido: {field}"
                }), 400

        success = Usuario.registrar_usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            username=datos['username'],
            telefono=datos['telefono'],
            fecha_nacimiento=datos['fecha_nacimiento'],
            ciudad=datos['ciudad'],
            password=datos['password']
        )

        if success:
            return jsonify({
                "status": "success",
                "message": "Usuario registrado correctamente"
            })
        else:
            return jsonify({
                "status": "error",
                "message": "El nombre de usuario ya existe"
            }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/usuarios/amigos', methods=['GET'])
def obtener_amigos():
    """
    Endpoint para obtener las relaciones de amistad entre usuarios.

    La amistad se determina por rutas en común.

    Returns
    -------
    Response
        Diccionario de relaciones de amistad.
    """
    try:
        amigos_dict = Usuario.amigos()

        # Asegurar que cada usuario tenga un diccionario de amigos, no una lista
        for usuario, amigos in amigos_dict.items():
            # Si amigos es una lista, convertirla a diccionario
            if isinstance(amigos, list):
                # Crear un diccionario donde cada amigo tiene una lista vacía de rutas
                amigos_dict[usuario] = {amigo: [] for amigo in amigos}

        return jsonify({
            "status": "success",
            "data": amigos_dict
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/usuarios/<username>/rutas', methods=['GET'])
def obtener_rutas_usuario(username):
    """
    Endpoint para obtener las rutas asociadas a un usuario específico.

    Parameters
    ----------
    username : str
        Nombre de usuario.

    Returns
    -------
    Response
        Lista de rutas del usuario.
    """
    try:
        usuarios = Usuario.cargar_usuarios()
        usuario = next((u for u in usuarios if u['username'] == username), None)

        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404

        return jsonify({
            "status": "success",
            "data": usuario.get('rutas', [])
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Endpoints de Rutas
@app.route('/api/rutas', methods=['GET'])
def obtener_rutas():
    """
    Endpoint para obtener todas las rutas disponibles.

    Returns
    -------
    Response
        Lista de todas las rutas.
    """
    try:
        rutas = gestor.cargar_rutas_desde_carpeta()
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/rutas/filtrar', methods=['GET'])
def filtrar_rutas():
    """
    Endpoint para filtrar rutas según diversos criterios.

    Parámetros de filtrado (query):
    - dificultad: bajo, medio, alto
    - max_km: distancia máxima en kilómetros
    - max_horas: duración máxima en horas
    - modo_transporte: walk, bike, drive

    Returns
    -------
    Response
        Lista de rutas filtradas.
    """
    try:
        dificultad = request.args.get('dificultad')
        max_km = request.args.get('max_km', type=float)
        max_horas = request.args.get('max_horas', type=float)
        modo_transporte = request.args.get('modo_transporte')

        # Recargamos las rutas para asegurar que estamos trabajando con los datos más recientes
        gestor.rutas = gestor.cargar_rutas_desde_carpeta()
        rutas = gestor.rutas

        if dificultad:
            rutas = gestor.filtrar_por_dificultad(dificultad)
        if max_km:
            rutas = gestor.filtrar_por_distancia(max_km)
        if max_horas:
            rutas = gestor.filtrar_por_duracion(max_horas)
        if modo_transporte:
            rutas = gestor.filtrar_por_transporte(modo_transporte)

        return jsonify({
            "status": "success",
            "data": rutas
        })
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/rutas', methods=['POST'])
def crear_ruta():
    """
    Endpoint para crear una nueva ruta manual.

    Requiere un JSON con origen, destino y opcionalmente:
    - puntos_intermedios: lista de puntos intermedios
    - modo: modo de transporte (walk, bike, drive)
    - nombre: nombre de la ruta
    - username: usuario al que asociar la ruta

    Returns
    -------
    Response
        Detalles de la ruta creada.
    """
    try:
        datos = request.json
        origen = datos.get('origen')
        destino = datos.get('destino')
        modo = datos.get('modo', 'walk')  # Por defecto, modo a pie
        puntos_intermedios = datos.get('puntos_intermedios', [])
        nombre = datos.get('nombre')
        username = datos.get('username')

        if not origen or not destino:
            return jsonify({
                "status": "error",
                "message": "Se requieren origen y destino"
            }), 400

        # Obtener usuario si se proporciona username
        usuario = None
        if username:
            usuarios = Usuario.cargar_usuarios()
            for user_data in usuarios:
                if user_data['username'] == username:
                    usuario = Usuario(**user_data)
                    break

        # Crear la ruta manual
        pdf_path, gpx_path, html_path = RutaManual.crear_ruta_desde_datos(
            origen=origen,
            puntos_intermedios=puntos_intermedios,
            destino=destino,
            modo=modo,
            nombre=nombre,
            usuario=usuario
        )

        # Si hay un usuario, asociar la ruta
        if usuario:
            if 'rutas' not in usuario.__dict__:
                usuario.rutas = []
            if nombre:
                usuario.rutas.append(nombre)
            Usuario.guardar_usuarios(usuarios)

        return jsonify({
            "status": "success",
            "data": {
                "nombre": nombre,
                "origen": origen,
                "destino": destino,
                "modo": modo,
                "puntos_intermedios": puntos_intermedios,
                "archivos": {
                    "pdf": pdf_path,
                    "gpx": gpx_path,
                    "html": html_path
                }
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/rutas/auto', methods=['POST'])
def crear_rutas_automaticas():
    """
    Endpoint para crear rutas automáticas a partir de una lista de direcciones.

    Requiere un JSON con:
    - direcciones: lista de direcciones para crear rutas
    - cantidad (opcional): número de rutas a crear
    - username (opcional): usuario al que asociar las rutas

    Returns
    -------
    Response
        Lista de nombres de las rutas creadas.
    """
    try:
        datos = request.json
        direcciones = datos.get('direcciones', [])
        cantidad = int(datos.get('cantidad', 5))
        username = datos.get('username')

        if not direcciones or len(direcciones) < 2:
            return jsonify({
                "status": "error",
                "message": "Se requieren al menos dos direcciones"
            }), 400

        # Obtener usuario si se proporciona username
        usuario = None
        if username:
            usuarios = Usuario.cargar_usuarios()
            for user_data in usuarios:
                if user_data['username'] == username:
                    usuario = Usuario(**user_data)
                    break

        # Crear rutas automáticas
        ruta_auto = RutaAuto()
        resultado = ruta_auto.generar_rutas_desde_direcciones(direcciones, cantidad)

        # Si hay un usuario, asociar las rutas
        if usuario:
            if 'rutas' not in usuario.__dict__:
                usuario.rutas = []
            for ruta_msg in resultado:
                if "creada" in ruta_msg:
                    nombre_ruta = ruta_msg.split("'")[1]
                    usuario.rutas.append(nombre_ruta)
            Usuario.guardar_usuarios(usuarios)

        return jsonify({
            "status": "success",
            "data": resultado
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/rutas/<nombre>/pdf', methods=['GET'])
def descargar_pdf(nombre):
    """
    Endpoint para descargar el archivo PDF de una ruta específica.

    Parameters
    ----------
    nombre : str
        Nombre de la ruta.

    Returns
    -------
    Response
        Archivo PDF de la ruta.
    """
    try:
        path = f"{nombre}.pdf"
        return send_from_directory("static", path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"No se pudo descargar el PDF: {str(e)}"
        }), 404

@app.route('/api/rutas/<nombre>/html', methods=['GET'])
def descargar_html(nombre):
    """
    Endpoint para descargar el archivo HTML de una ruta específica.

    Parameters
    ----------
    nombre : str
        Nombre de la ruta.

    Returns
    -------
    Response
        Archivo HTML de la ruta.
    """
    try:
        path = f"rutas_{nombre}.html"
        return send_from_directory("static", path, as_attachment=True)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"No se pudo descargar el HTML: {str(e)}"
        }), 404

# Endpoint de Clima
@app.route('/api/clima', methods=['GET'])
def consultar_clima():
    """
    Endpoint para consultar el clima de una ciudad.

    Requiere el parámetro de consulta 'ciudad'.

    Returns
    -------
    Response
        Datos del clima para la ciudad especificada.
    """
    try:
        if not servicio_clima_disponible:
            return jsonify({
                "status": "error",
                "message": "Servicio de clima no disponible"
            }), 503

        ciudad = request.args.get('ciudad')
        if not ciudad:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'ciudad'"
            }), 400

        servicio = ServicioClima()
        clima = servicio.obtener_clima(ciudad)
        return jsonify({
            "status": "success",
            "data": clima
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

