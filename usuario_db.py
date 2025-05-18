import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Usuario:
    """
    Clase que representa a un usuario del sistema y gestiona operaciones sobre la base de datos relacionadas.

    Atributos
    ----------
    nombre : str
        Nombre del usuario.
    apellido : str
        Apellido del usuario.
    email : str
        Correo electrónico.
    username : str
        Nombre de usuario único.
    telefono : str
        Número de teléfono.
    fecha_nacimiento : str
        Fecha de nacimiento (en formato ISO o similar).
    ciudad : str
        Ciudad de residencia.
    password : str
        Contraseña del usuario (sin hash).
    fecha_registro : str
        Fecha y hora de registro del usuario.
    """

    def __init__(self, nombre: str, apellido: str, email: str, username: str, telefono: str, 
                 fecha_nacimiento: str, ciudad: str, password: str, fecha_registro: Optional[str] = None) -> None:
        """
        Inicializa una instancia de Usuario.

        Parameters
        ----------
        nombre : str
        apellido : str
        email : str
        username : str
        telefono : str
        fecha_nacimiento : str
        ciudad : str
        password : str
        fecha_registro : Optional[str], optional
            Fecha de registro, por defecto es la fecha actual.
        """
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.username = username
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self.ciudad = ciudad
        self.password = password
        self.fecha_registro = fecha_registro or datetime.now().isoformat()

    @staticmethod
    def get_db_connection():
        """
        Establece una conexión a la base de datos SQLite.

        Returns
        -------
        sqlite3.Connection
            Objeto de conexión a la base de datos.
        """
        conn = sqlite3.connect('miapp.db')
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def registrar_usuario(nombre: str, apellido: str, email: str, username: str, telefono: str, 
                         fecha_nacimiento: str, ciudad: str, password: str) -> bool:
        """
        Registra un nuevo usuario en la base de datos.

        Parameters
        ----------
        nombre : str
        apellido : str
        email : str
        username : str
        telefono : str
        fecha_nacimiento : str
        ciudad : str
        password : str

        Returns
        -------
        bool
            True si el registro fue exitoso, False si el usuario ya existe o hay un error.
        """
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, username, telefono, 
                                  fecha_nacimiento, ciudad, password, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, apellido, email, username, telefono, fecha_nacimiento, 
                  ciudad, password, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def iniciar_sesion(username: str, password: str) -> Optional['Usuario']:
        """
        Verifica las credenciales del usuario y retorna una instancia si son correctas.

        Parameters
        ----------
        username : str
        password : str

        Returns
        -------
        Optional[Usuario]
            Instancia del usuario si las credenciales son válidas, None si no lo son.
        """
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM usuarios WHERE username = ? AND password = ?
            ''', (username, password))
            usuario_data = cursor.fetchone()
            conn.close()
            if usuario_data:
                return Usuario(
                    nombre=usuario_data['nombre'],
                    apellido=usuario_data['apellido'],
                    email=usuario_data['email'],
                    username=usuario_data['username'],
                    telefono=usuario_data['telefono'],
                    fecha_nacimiento=usuario_data['fecha_nacimiento'],
                    ciudad=usuario_data['ciudad'],
                    password=usuario_data['password'],
                    fecha_registro=usuario_data['fecha_registro']
                )
            return None
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return None

    @staticmethod
    def obtener_rutas(username: str) -> List[str]:
        """
        Obtiene una lista de nombres de rutas asociadas al usuario.

        Parameters
        ----------
        username : str
            Nombre de usuario.

        Returns
        -------
        List[str]
            Lista de nombres de rutas asociadas.
        """
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
            SELECT r.nombre 
            FROM rutas r
            JOIN rutas_usuario ru ON r.id = ru.ruta_id
            JOIN usuarios u ON ru.usuario_id = u.id
            WHERE u.username = ?
            ''', (username,))
            rutas = [row['nombre'] for row in cursor.fetchall()]
            conn.close()
            return rutas
        except Exception as e:
            print(f"Error al obtener rutas: {e}")
            return []

    @staticmethod
    def obtener_amigos(username: str) -> Dict[str, List[str]]:
        """
        Obtiene un diccionario de amigos y las rutas que tienen en común con el usuario.

        Parameters
        ----------
        username : str
            Nombre de usuario.

        Returns
        -------
        Dict[str, List[str]]
            Diccionario con nombres de usuario como claves y listas de rutas comunes como valores.
        """
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            if not usuario:
                return {}

            cursor.execute('''
            SELECT u.username, GROUP_CONCAT(r.nombre) as rutas_comunes
            FROM usuarios u
            JOIN amistades a ON (a.amigo_id = u.id)
            JOIN usuarios u2 ON (a.usuario_id = u2.id)
            LEFT JOIN rutas_usuario ru1 ON (ru1.usuario_id = u.id)
            LEFT JOIN rutas_usuario ru2 ON (ru2.usuario_id = u2.id)
            LEFT JOIN rutas r ON (ru1.ruta_id = r.id AND ru2.ruta_id = r.id)
            WHERE u2.username = ?
            GROUP BY u.username
            ''', (username,))
            amigos = {}
            for row in cursor.fetchall():
                rutas = row['rutas_comunes'].split(',') if row['rutas_comunes'] else []
                amigos[row['username']] = rutas
            conn.close()
            return amigos
        except Exception as e:
            print(f"Error al obtener amigos: {e}")
            return {}

    @staticmethod
    def agregar_ruta(username: str, nombre_ruta: str) -> bool:
        """
        Asocia una ruta existente o nueva a un usuario dado.

        Si la ruta no existe, se crea una nueva con datos por defecto.

        Parameters
        ----------
        username : str
            Nombre de usuario.
        nombre_ruta : str
            Nombre de la ruta a asociar.

        Returns
        -------
        bool
            True si se asoció correctamente, False en caso de error.
        """
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            if not usuario:
                return False

            cursor.execute('SELECT id FROM rutas WHERE nombre = ?', (nombre_ruta,))
            ruta = cursor.fetchone()
            if not ruta:
                cursor.execute('''
                INSERT INTO rutas (nombre, descripcion, distancia, duracion, 
                                   dificultad, puntos_interes, origen, destino, modo_transporte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (nombre_ruta, f"Descripción de {nombre_ruta}", 0.0, 0, 
                      'media', '[]', 'Origen', 'Destino', 'walk'))
                ruta_id = cursor.lastrowid
            else:
                ruta_id = ruta['id']

            cursor.execute('''
            INSERT OR IGNORE INTO rutas_usuario (usuario_id, ruta_id)
            VALUES (?, ?)
            ''', (usuario['id'], ruta_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar ruta: {e}")
            return False

