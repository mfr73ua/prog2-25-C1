"""
Aplicación Flask para la gestión de rutas geográficas.

Esta aplicación implementa una API RESTful para gestionar rutas geográficas,
usuarios y servicios relacionados como el clima. Está adaptada para despliegue
en PythonAnywhere.

Atributos
---------
BASE_DIR : str
    Directorio base de la aplicación
DB_PATH : str
    Ruta a la base de datos SQLite
STATIC_DIR : str
    Directorio para archivos estáticos
RUTAS_DIR : str
    Directorio para almacenar rutas

"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime
import sqlite3
import requests
from flask_cors import CORS
from ruta import Ruta
from utils import exportar_pdf, exportar_gpx, generar_mapa, exportar_png_desde_html
import logging
from servicio_clima import ServicioOpenWeatherMap, GestorClima

# Configuración de rutas 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'usuarios.db')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
RUTAS_DIR = os.path.join(BASE_DIR, 'rutas')

# Crear directorios necesarios si no existen
for directory in [STATIC_DIR, RUTAS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Inicialización de la aplicación Flask
app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)  

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'timeout': 30}
}
db = SQLAlchemy(app)

# Modelos de base de datos
class Usuario(db.Model):
    """Modelo de usuario para la base de datos.

    Esta clase representa a un usuario en el sistema, almacenando su información
    personal y credenciales.

    Atributos
    ---------
    id : int
        Identificador único del usuario
    nombre : str
        Nombre del usuario
    apellido : str
        Apellido del usuario
    email : str
        Correo electrónico del usuario
    username : str
        Nombre de usuario único
    password_hash : str
        Hash de la contraseña
    telefono : str, opcional
        Número de teléfono
    fecha_nacimiento : str, opcional
        Fecha de nacimiento
    ciudad : str, opcional
        Ciudad de residencia

    Métodos
    -------
    iniciar_sesion(username, password)
        Verifica las credenciales del usuario
    registrar_usuario(nombre, apellido, email, username, password, ...)
        Registra un nuevo usuario
    obtener_rutas(username)
        Obtiene las rutas asociadas al usuario
    agregar_ruta(username, nombre_ruta)
        Asocia una ruta al usuario
    obtener_amigos(username)
        Obtiene los amigos del usuario basado en rutas compartidas
    """

    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.String(20))
    ciudad = db.Column(db.String(100))

    def __repr__(self):
        return f'<Usuario {self.username}>'

    @staticmethod
    def iniciar_sesion(username, password):
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.password_hash == password:
            return usuario
        return None

    @staticmethod
    def registrar_usuario(nombre, apellido, email, username, password, telefono=None, fecha_nacimiento=None, ciudad=None):
        if Usuario.query.filter_by(username=username).first() or Usuario.query.filter_by(email=email).first():
            return False

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            username=username,
            password_hash=password,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            ciudad=ciudad
        )

        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_rutas(username):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return []

        rutas = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        nombres_rutas = [ur.nombre_ruta for ur in rutas]

        resultado = []
        for nombre_ruta in nombres_rutas:
            ruta_path = os.path.join(RUTAS_DIR, f"{nombre_ruta}.json")
            if os.path.exists(ruta_path):
                try:
                    with open(ruta_path, 'r', encoding='utf-8') as f:
                        datos_ruta = json.load(f)
                        resultado.append(datos_ruta)
                except Exception as e:
                    print(f"Error al cargar la ruta {nombre_ruta}: {str(e)}")

        return resultado

    @staticmethod
    def agregar_ruta(username, nombre_ruta):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return False

        relacion = UsuarioRuta.query.filter_by(usuario_id=usuario.id, nombre_ruta=nombre_ruta).first()
        if relacion:
            return True

        nueva_relacion = UsuarioRuta(
            usuario_id=usuario.id,
            nombre_ruta=nombre_ruta,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        db.session.add(nueva_relacion)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_amigos(username):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return {}

        rutas_usuario = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        nombres_rutas = [ur.nombre_ruta for ur in rutas_usuario]

        amigos = {}
        for nombre_ruta in nombres_rutas:
            relaciones = UsuarioRuta.query.filter_by(nombre_ruta=nombre_ruta).all()
            for rel in relaciones:
                if rel.usuario_id != usuario.id:
                    amigo = Usuario.query.get(rel.usuario_id)
                    if amigo:
                        if amigo.username not in amigos:
                            amigos[amigo.username] = {
                                "nombre": amigo.nombre,
                                "apellido": amigo.apellido,
                                "rutas_comunes": []
                            }
                        amigos[amigo.username]["rutas_comunes"].append(nombre_ruta)

        return amigos

class UsuarioRuta(db.Model):
    """Modelo para la relación entre usuarios y rutas.

    Esta clase representa la relación muchos a muchos entre usuarios y rutas,
    permitiendo que múltiples usuarios puedan compartir rutas.

    Atributos
    ---------
    id : int
        Identificador único de la relación
    usuario_id : int
        ID del usuario asociado
    nombre_ruta : str
        Nombre de la ruta asociada
    created_at : str
        Fecha y hora de creación de la relación
    """

    __tablename__ = 'usuario_rutas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre_ruta = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<UsuarioRuta {self.usuario_id}:{self.nombre_ruta}>'

class GestorRutas:
    """Gestor de rutas geográficas.

    Esta clase maneja la carga y filtrado de rutas geográficas desde archivos
    JSON almacenados en el sistema.

    Atributos
    ---------
    rutas : list
        Lista de rutas cargadas
    rutas_dir : str
        Directorio donde se almacenan las rutas

    Métodos
    -------
    cargar_rutas_desde_carpeta()
        Carga todas las rutas desde archivos JSON
    filtrar_por_dificultad(dificultad)
        Filtra rutas por nivel de dificultad
    filtrar_por_distancia(max_km)
        Filtra rutas por distancia máxima
    filtrar_por_duracion(max_horas)
        Filtra rutas por duración máxima
    filtrar_por_transporte(modo)
        Filtra rutas por modo de transporte
    """

    def __init__(self):
        self.rutas = []
        self.rutas_dir = RUTAS_DIR

    def cargar_rutas_desde_carpeta(self):
        rutas = []
        if os.path.exists(self.rutas_dir):
            for archivo in os.listdir(self.rutas_dir):
                if archivo.endswith('.json'):
                    ruta_path = os.path.join(self.rutas_dir, archivo)
                    try:
                        with open(ruta_path, 'r', encoding='utf-8') as f:
                            datos_ruta = json.load(f)
                            rutas.append(datos_ruta)
                    except Exception as e:
                        print(f"Error al cargar la ruta {archivo}: {str(e)}")

        self.rutas = rutas
        return rutas

    def filtrar_por_dificultad(self, dificultad):
        return [ruta for ruta in self.rutas if ruta.get('dificultad', '').lower() == dificultad.lower()]

    def filtrar_por_distancia(self, max_km):
        return [ruta for ruta in self.rutas if float(ruta.get('distancia_km', 0)) <= max_km]

    def filtrar_por_duracion(self, max_horas):
        return [ruta for ruta in self.rutas if float(ruta.get('duracion_horas', 0)) <= max_horas]

    def filtrar_por_transporte(self, modo):
        return [ruta for ruta in self.rutas if ruta.get('modo', '').lower() == modo.lower()]

class RutaManual:
    """Gestor de creación manual de rutas.

    Esta clase proporciona métodos para crear rutas geográficas de forma manual,
    incluyendo la generación de archivos PDF, GPX y mapas HTML.

    Métodos
    -------
    crear_ruta_desde_datos(origen, destino, modo='walk', nombre=None, puntos_intermedios=None, username=None)
        Crea una nueva ruta a partir de puntos geográficos
    """

    @staticmethod
    def crear_ruta_desde_datos(origen, destino, modo='walk', nombre=None, puntos_intermedios=None, username=None):
        if puntos_intermedios is None:
            puntos_intermedios = []

        if not nombre:
            nombre = f"ruta_manual_{int(datetime.now().timestamp())}"

        # Crear objeto Ruta (usa geocodificador, OSMnx, etc.)
        ruta = Ruta(
            nombre=nombre,
            ubicacion=(38.35, -0.48),
            distancia=0.0,
            duracion=0.0,
            dificultad="bajo",
            alt_max=0,
            alt_min=0,
            origen=origen,
            puntos_intermedios=puntos_intermedios,
            destino=destino,
            modo_transporte=modo
        )

        # Validar geocodificación
        if ruta.origen is None or ruta.destino is None or any(p is None for p in ruta.puntos_intermedios):
            logging.error(f"Geocodificación fallida: origen={ruta.origen}, destino={ruta.destino}, intermedios={ruta.puntos_intermedios}")
            raise ValueError("No se pudieron geocodificar todas las direcciones o las coordenadas no son válidas. Verifica los nombres de las calles o las coordenadas.")

        ruta.guardar_en_json()

        # Exportar archivos
        try:
            pdf_filename = exportar_pdf(ruta.distancias, ruta.tiempos_estimados, ruta.modo_transporte, ruta.nombre, ruta.origen, ruta.puntos_intermedios, ruta.destino)
            if not pdf_filename:
                raise RuntimeError("No se generó el archivo PDF")
            gpx_filename = exportar_gpx(ruta.rutas, ruta.grafo, ruta.timestamp)
            if not gpx_filename:
                raise RuntimeError("No se generó el archivo GPX")
            html_filename = generar_mapa(ruta.origen, ruta.puntos_intermedios, ruta.destino, ruta.rutas, ruta.grafo, ruta.timestamp)
            if not html_filename:
                raise RuntimeError("No se generó el archivo HTML")
            exportar_png_desde_html(html_filename, f"static/{ruta.nombre}.png")
        except Exception as e:
            logging.error(f"Error al exportar archivos: {e}")
            raise RuntimeError(f"Error al exportar archivos: {e}")

        # Devuelve un diccionario con la información de la ruta y los archivos generados
        return {
            "nombre": nombre,
            "origen": origen,
            "destino": destino,
            "modo": modo,
            "puntos_intermedios": puntos_intermedios,
            "archivos": {
                "pdf": pdf_filename,
                "gpx": gpx_filename,
                "html": html_filename
            }
        }

class RutaAuto:
    """Gestor de creación automática de rutas.

    Esta clase proporciona métodos para generar rutas automáticamente a partir
    de una lista de direcciones.

    Métodos
    -------
    generar_rutas_desde_direcciones(direcciones, cantidad=5, username=None)
        Genera múltiples rutas a partir de una lista de direcciones
    """

    def generar_rutas_desde_direcciones(self, direcciones, cantidad=5, username=None):
        if not direcciones or len(direcciones) < 2:
            return ["Se requieren al menos dos direcciones"]

        rutas_generadas = []

        for i in range(min(cantidad, len(direcciones) - 1)):
            try:
                # Permitir strings, tuplas o diccionarios
                origen = direcciones[i]
                destino = direcciones[i+1]
                # Si hay más de 2 direcciones, usar como puntos intermedios
                puntos_intermedios = []
                if len(direcciones) > 2:
                    puntos_intermedios = [d for j, d in enumerate(direcciones) if j not in (i, i+1)]
                nombre = f"RutaAuto_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
                modo = 'walk'
                ruta = RutaManual.crear_ruta_desde_datos(
                    origen=origen,
                    destino=destino,
                    puntos_intermedios=puntos_intermedios,
                    modo=modo,
                    nombre=nombre,
                    username=username
                )
                rutas_generadas.append(f"Ruta '{nombre}' creada exitosamente")
            except Exception as e:
                rutas_generadas.append(f"❌ Error al crear la ruta '{nombre}': {str(e)}")
        return rutas_generadas

# Configuración de CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Instancia del gestor de rutas
gestor = GestorRutas()

# Instancia del servicio de clima
servicio_clima = ServicioOpenWeatherMap()
gestor_clima = GestorClima(servicio_clima)

# Ruta principal
@app.route('/')
def home():
    """Endpoint principal de la API.

    Returns
    -------
    JSON
        Diccionario con el estado de la API y su versión
    """
    return jsonify({
        "status": "success",
        "message": "API funcionando correctamente en PythonAnywhere",
        "version": "1.1.0"
    })

# Endpoint para servir archivos estáticos 
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

# Endpoint para servir archivos HTML desde la carpeta 'static'
@app.route('/html/<path:filename>')
def serve_html(filename):
    return send_from_directory(STATIC_DIR, filename)

# Endpoints de Usuarios
@app.route('/api/usuarios/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión de usuarios.

    Parameters
    ----------
    request : JSON
        Debe contener username y password

    Returns
    -------
    JSON
        Datos del usuario si la autenticación es exitosa

    Raises
    ------
    400
        Si faltan campos obligatorios
    401
        Si las credenciales son incorrectas
    500
        Si ocurre un error interno
    """
    try:
        datos = request.get_json(force=True)
        username = datos.get('username', '').strip()
        password = datos.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Usuario y contraseña son obligatorios"
            }), 400
            
        usuario = Usuario.iniciar_sesion(username, password)
        if usuario:
            return jsonify({
                "status": "success",
                "data": {
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "email": usuario.email,
                    "username": usuario.username,
                    "telefono": usuario.telefono,
                    "fecha_nacimiento": usuario.fecha_nacimiento,
                    "ciudad": usuario.ciudad
                }
            })
        return jsonify({
            "status": "error",
            "message": "Usuario o contraseña incorrectos"
        }), 401
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en login: {str(e)}"
        }), 500

@app.route('/api/usuarios/registro', methods=['POST'])
def registro():
    try:
        datos = request.get_json(force=True)
        campos = ['nombre', 'apellido', 'email', 'username', 'password']
        for campo in campos:
            if not datos.get(campo, '').strip():
                return jsonify({
                    "status": "error",
                    "message": f"El campo '{campo}' es obligatorio"
                }), 400
                
        if Usuario.registrar_usuario(
            nombre=datos['nombre'].strip(),
            apellido=datos['apellido'].strip(),
            email=datos['email'].strip(),
            username=datos['username'].strip(),
            password=datos['password'].strip(),
            telefono=datos.get('telefono', '').strip(),
            fecha_nacimiento=datos.get('fecha_nacimiento', '').strip(),
            ciudad=datos.get('ciudad', '').strip()
        ):
            return jsonify({
                "status": "success",
                "message": "Usuario registrado exitosamente"
            })
        return jsonify({
            "status": "error",
            "message": "El usuario ya existe"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en registro: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>', methods=['DELETE', 'POST'])
def eliminar_usuario(username):
    try:
        if request.method == 'POST':
            datos = request.get_json(force=True)
            if not datos or datos.get('accion') != 'eliminar':
                return jsonify({
                    "status": "error",
                    "message": "Acción no permitida"
                }), 400
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
        # Eliminar todas las rutas asociadas
        rutas = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        for ruta in rutas:
            ruta_path = os.path.join(RUTAS_DIR, f"{ruta.nombre_ruta}.json")
            if os.path.exists(ruta_path):
                os.remove(ruta_path)
            db.session.delete(ruta)
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Usuario eliminado correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar usuario: {str(e)}"
        }), 500

@app.route('/api/usuarios/editar', methods=['PUT', 'POST'])
def editar_usuario():
    try:
        datos = request.get_json(force=True)
        username = datos.get('username')
        if not username:
            return jsonify({
                "status": "error",
                "message": "Se requiere el username"
            }), 400
            
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
            
        # Actualizar campos
        campos = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'ciudad']
        for campo in campos:
            if campo in datos:
                setattr(usuario, campo, datos[campo].strip())
                
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Usuario actualizado correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al actualizar usuario: {str(e)}"
        }), 500

@app.route('/api/usuarios/buscar', methods=['GET'])
def buscar_usuarios():
    try:
        nombre = request.args.get('nombre', '').strip()
        if not nombre:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'nombre'"
            }), 400
            
        usuarios = Usuario.query.filter(Usuario.username.like(f'%{nombre}%')).all()
        resultados = [usuario.username for usuario in usuarios]
        
        return jsonify({
            "status": "success",
            "resultados": resultados
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al buscar usuarios: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>/rutas/<nombre_ruta>', methods=['DELETE'])
def eliminar_ruta_usuario(username, nombre_ruta):
    try:
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
            
        relacion = UsuarioRuta.query.filter_by(
            usuario_id=usuario.id,
            nombre_ruta=nombre_ruta
        ).first()
        
        if not relacion:
            return jsonify({
                "status": "error",
                "message": "Ruta no encontrada para este usuario"
            }), 404
            
        # Eliminar archivos asociados
        ruta_path = os.path.join(RUTAS_DIR, f"{nombre_ruta}.json")
        if os.path.exists(ruta_path):
            os.remove(ruta_path)
            
        # Eliminar archivos PDF y HTML si existen
        pdf_path = os.path.join(STATIC_DIR, f"{nombre_ruta}.pdf")
        html_path = os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html")
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(html_path):
            os.remove(html_path)
            
        # Eliminar la relación
        db.session.delete(relacion)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Ruta eliminada correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar ruta: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>/rutas', methods=['GET'])
def obtener_rutas_usuario(username):
    try:
        rutas = []
        usuario = Usuario.query.filter_by(username=username.strip()).first()
        if usuario:
            relaciones = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
            for rel in relaciones:
                ruta_path = os.path.join(RUTAS_DIR, f"{rel.nombre_ruta}.json")
                if os.path.exists(ruta_path):
                    try:
                        with open(ruta_path, 'r', encoding='utf-8') as f:
                            datos_ruta = json.load(f)
                            if isinstance(datos_ruta, dict):
                                # Adaptar origen y destino si son string
                                if isinstance(datos_ruta.get('origen'), str):
                                    datos_ruta['origen'] = {"direccion": datos_ruta['origen']}
                                if isinstance(datos_ruta.get('destino'), str):
                                    datos_ruta['destino'] = {"direccion": datos_ruta['destino']}
                                # Adaptar puntos_intermedios si es lista de strings
                                if 'puntos_intermedios' in datos_ruta and isinstance(datos_ruta['puntos_intermedios'], list):
                                    if datos_ruta['puntos_intermedios'] and isinstance(datos_ruta['puntos_intermedios'][0], str):
                                        datos_ruta['puntos_intermedios'] = [{"direccion": p} for p in datos_ruta['puntos_intermedios']]
                                # Adaptar distancia y duración
                                if 'distancia' in datos_ruta and 'distancia_km' not in datos_ruta:
                                    try:
                                        datos_ruta['distancia_km'] = float(str(datos_ruta['distancia']).replace('km','').strip())
                                    except:
                                        datos_ruta['distancia_km'] = 0
                                if 'duracion' in datos_ruta and 'duracion_horas' not in datos_ruta:
                                    try:
                                        minutos = 0
                                        if 'h' in datos_ruta['duracion']:
                                            partes = datos_ruta['duracion'].split('h')
                                            horas = int(partes[0].strip())
                                            minutos = int(partes[1].replace('min','').strip()) if 'min' in partes[1] else 0
                                            datos_ruta['duracion_horas'] = horas + minutos/60
                                        else:
                                            datos_ruta['duracion_horas'] = float(str(datos_ruta['duracion']).replace('min','').strip())/60
                                    except:
                                        datos_ruta['duracion_horas'] = 0
                                # Adaptar modo
                                if 'modo_transporte' in datos_ruta and 'modo' not in datos_ruta:
                                    datos_ruta['modo'] = datos_ruta['modo_transporte']
                                rutas.append(datos_ruta)
                    except Exception as e:
                        print(f"Error al cargar la ruta {rel.nombre_ruta}: {str(e)}")
        return jsonify({"status": "success", "data": rutas})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener rutas: {str(e)}"}), 500

@app.route('/api/usuarios/amigos', methods=['GET'])
def obtener_amigos():
    try:
        username = request.args.get('username', '').strip()
        if not username:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro username"
            }), 400
        amigos = Usuario.obtener_amigos(username)
        return jsonify({
            "status": "success",
            "data": amigos
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener amigos: {str(e)}"
        }), 500

# Endpoints de Rutas
@app.route('/api/rutas', methods=['GET'])
def obtener_rutas():
    try:
        rutas = gestor.cargar_rutas_desde_carpeta()
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener rutas: {str(e)}"
        }), 500

@app.route('/api/rutas/filtrar', methods=['GET'])
def filtrar_rutas():
    try:
        dificultad = request.args.get('dificultad')
        max_km = request.args.get('max_km', type=float)
        max_horas = request.args.get('max_horas', type=float)
        modo_transporte = request.args.get('modo_transporte')
        
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
            "message": f"Error al filtrar rutas: {str(e)}"
        }), 500

@app.route('/api/rutas', methods=['POST'])
def crear_ruta():
    try:
        datos = request.get_json(force=True)
        ruta = RutaManual.crear_ruta_desde_datos(
            origen=datos['origen'],
            puntos_intermedios=datos.get('puntos_intermedios', []),
            destino=datos['destino'],
            modo=datos.get('modo', 'walk'),
            nombre=datos.get('nombre'),
            username=datos.get('username')
        )
        
        if ruta and datos.get('username'):
            Usuario.agregar_ruta(datos['username'], ruta['nombre'])
            
        return jsonify({
            "status": "success",
            "data": ruta
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al crear ruta: {str(e)}"
        }), 500

@app.route('/api/rutas/auto', methods=['POST'])
def crear_rutas_automaticas():
    try:
        datos = request.get_json(force=True)
        ruta_auto = RutaAuto()
        rutas = []
        nombres_creadas = []
        resultados = ruta_auto.generar_rutas_desde_direcciones(
            direcciones=datos['direcciones'],
            cantidad=datos.get('cantidad', 1),
            username=datos.get('username')
        )
        for resultado in resultados:
            rutas.append(resultado)
            # Extraer el nombre de la ruta si fue creada exitosamente
            if isinstance(resultado, str) and "creada" in resultado:
                nombre = resultado.split("'")[1]
                nombres_creadas.append(nombre)
        # Asociar cada ruta al usuario
        if datos.get('username'):
            for nombre in nombres_creadas:
                Usuario.agregar_ruta(datos['username'], nombre)
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al crear rutas automáticas: {str(e)}"
        }), 500

# Endpoint de Clima
@app.route('/api/clima', methods=['GET'])
def consultar_clima():
    try:
        ciudad = request.args.get('ciudad', '').strip()
        if not ciudad:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'ciudad'"
            }), 400
            
        # Obtener datos del clima usando el servicio
        datos_clima = gestor_clima.consultar_clima(ciudad)
        
        # Formatear la respuesta
        clima = {
            "ciudad": datos_clima.ciudad,
            "temperatura": datos_clima.temperatura,
            "humedad": datos_clima.humedad,
            "descripcion": datos_clima.descripcion,
            "viento": datos_clima.viento,
            "fecha": datos_clima.fecha.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify({
            "status": "success",
            "data": clima
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al consultar clima: {str(e)}"
        }), 500

# Crear las tablas en la base de datos si no existen
def inicializar_db():
    """Inicializa la base de datos creando todas las tablas necesarias.

    Esta función crea la base de datos SQLite si no existe y genera todas
    las tablas definidas en los modelos.

    Notas
    -----
    La función verifica la existencia de la base de datos y crea las tablas
    necesarias usando SQLAlchemy. También imprime información sobre el proceso
    de inicialización.

    Raises
    ------
    Exception
        Si ocurre algún error durante la inicialización de la base de datos
    """
    with app.app_context():
        try:
            if not os.path.exists('usuarios.db'):
                print("📝 Creando nueva base de datos...")
            
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"📊 Tablas creadas: {', '.join(tablas)}")
            
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {str(e)}")
            raise


if __name__ == '__main__':
    inicializar_db()
    #Ejecución local (descomentar)
    #app.run(debug=True, port=5000)
else:
    inicializar_db()