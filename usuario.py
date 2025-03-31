import json
import os
import random
from datetime import datetime
from typing import List, Dict, Optional

class Usuario:
    def __init__(self, nombre: str, apellido: str, email: str, username: str, telefono: str, fecha_nacimiento: str, ciudad: str, password: str, fecha_registro: Optional[str] = None, rutas: Optional[List[str]] = None, amigos: Optional[List[str]] = None) -> None:
        """
        Inicializa un nuevo usuario con los parámetros dados.

        Parámetros
        ----------
        nombre : str
            Nombre del usuario.
        apellido : str
            Apellido del usuario.
        email : str
            Correo electrónico del usuario.
        username : str
            Nombre de usuario único.
        telefono : str
            Número de teléfono del usuario.
        fecha_nacimiento : str
            Fecha de nacimiento del usuario en formato 'YYYY-MM-DD'.
        ciudad : str
            Ciudad del usuario.
        password : str
            Contraseña del usuario.
        fecha_registro : Optional[str]
            Fecha de registro en formato ISO (se asigna la actual si no se proporciona).
        rutas : Optional[List[str]]
            Lista de rutas asociadas al usuario.
        amigos : Optional[List[str]]
            Lista de amigos del usuario.
        """
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.username = username
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self.ciudad = ciudad
        self.password = password
        self.fecha_registro = datetime.fromisoformat(fecha_registro) if isinstance(fecha_registro, str) else datetime.now()
        self.rutas: List[str] = rutas if rutas else []
        self.amigos: List[str] = amigos if amigos else []

    def agregar_ruta_predefinida(self, directorio: str = "rutas", num_rutas: int = 3) -> None:
        """
        Carga y asigna un número aleatorio de rutas predefinidas a la lista de rutas del usuario.

        Parámetros
        ----------
        directorio : str, opcional
            Directorio donde se encuentran las rutas predefinidas (por defecto 'rutas').
        num_rutas : int, opcional
            Número de rutas aleatorias a asignar al usuario (por defecto 3).
        """
        rutas = self.cargar_rutas_predefinidas(directorio)
        rutas_asignadas = random.sample(rutas, min(num_rutas, len(rutas)))  # Asigna un máximo de 'num_rutas' rutas aleatorias
        self.rutas.extend(rutas_asignadas)
        self.guardar_en_json()

    @staticmethod
    def cargar_rutas_predefinidas(directorio: str = "rutas") -> List[str]:
        """
        Carga las rutas predefinidas desde el directorio y las guarda solo con su nombre de archivo.

        Parámetros
        ----------
        directorio : str, opcional
            Directorio donde se encuentran las rutas predefinidas (por defecto 'rutas').

        Devuelve
        ---------
        List[str]
            Lista con los nombres de las rutas predefinidas.
        """
        rutas: List[str] = []
        if os.path.exists(directorio):
            archivos = [f for f in os.listdir(directorio) if f.endswith('.json')]
            for archivo in archivos:
                rutas.append(os.path.splitext(archivo)[0])  # Guardamos el nombre de archivo sin la extensión
        return rutas

    def guardar_en_json(self) -> None:
        """
        Guarda el usuario en el archivo JSON solo con las rutas asociadas.

        Devuelve
        ---------
        None
        """
        usuarios = Usuario.cargar_usuarios()
        # Solo actualizar las rutas del usuario en el JSON
        for usuario_data in usuarios:
            if usuario_data['username'] == self.username:
                usuario_data['rutas'] = self.rutas  # Actualizamos solo las rutas
                break
        Usuario.guardar_usuarios(usuarios)

    @staticmethod
    def cargar_usuarios() -> List[Dict[str, Optional[str]]]:
        """
        Carga todos los usuarios desde el archivo JSON.

        Devuelve
        ---------
        List[Dict[str, Optional[str]]]
            Lista de diccionarios que representan los usuarios.
        """
        try:
            with open("usuarios.json", "r", encoding="utf-8") as archivo:
                usuarios = json.load(archivo)
                # Convertir la cadena de fecha de regreso a datetime
                for usuario_data in usuarios:
                    if 'fecha_registro' in usuario_data:
                        # Verificar si es un string, si no, convertir a datetime
                        if isinstance(usuario_data['fecha_registro'], str):
                            usuario_data['fecha_registro'] = datetime.fromisoformat(usuario_data['fecha_registro'])
                return usuarios
        except FileNotFoundError:
            return []

    @staticmethod
    def guardar_usuarios(usuarios: List[Dict[str, Optional[str]]]) -> None:
        """
        Guarda todos los usuarios en el archivo JSON.

        Parámetros
        ----------
        usuarios : List[Dict[str, Optional[str]]]
            Lista de diccionarios que representan los usuarios que se van a guardar.

        Devuelve
        ---------
        None
        """
        # Convertir la fecha de cada usuario a cadena antes de guardarlo
        for usuario_data in usuarios:
            if 'fecha_registro' in usuario_data:
                # Verificar si es un objeto datetime, si es así convertir a ISO 8601
                if isinstance(usuario_data['fecha_registro'], datetime):
                    usuario_data['fecha_registro'] = usuario_data['fecha_registro'].isoformat()  # Convertir a string ISO 8601
        with open("usuarios.json", "w", encoding="utf-8") as archivo:
            json.dump(usuarios, archivo, indent=4, ensure_ascii=False)

    
    @staticmethod
    def amigos() -> Dict[str, List[str]]:
        """
        Determina qué usuarios tienen rutas en común y los considera amigos.
        
        Devuelve
        --------
        Dict[str, List[str]]
            Un diccionario donde las claves son los nombres de usuario y los valores son listas de amigos.
        """
        usuarios = Usuario.cargar_usuarios()
        amigos_dict = {usuario['username']: [] for usuario in usuarios}

        for i in range(len(usuarios)):
            for j in range(i + 1, len(usuarios)):
                usuario1, usuario2 = usuarios[i], usuarios[j]
                if set(usuario1['rutas']) & set(usuario2['rutas']):  # Verifica intersección de rutas
                    amigos_dict[usuario1['username']].append(usuario2['username'])
                    amigos_dict[usuario2['username']].append(usuario1['username'])
        
        return amigos_dict
    
    @staticmethod
    def registrar_usuario(nombre: str, apellido: str, email: str, username: str, telefono: str, fecha_nacimiento: str, ciudad: str, password: str) -> bool:
        """
        Registra un nuevo usuario si el nombre de usuario no existe ya.
        """
        usuarios = Usuario.cargar_usuarios()
        if any(user['username'] == username for user in usuarios):
            print("El usuario ya existe.")
            return False
        nuevo_usuario = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "username": username,
            "telefono": telefono,
            "fecha_nacimiento": fecha_nacimiento,
            "ciudad": ciudad,
            "password": password,
            "fecha_registro": datetime.now().isoformat(),
            "rutas": []
        }
        usuarios.append(nuevo_usuario)
        Usuario.guardar_usuarios(usuarios)
        return True

    @staticmethod
    def iniciar_sesion(username: str, password: str) -> Optional['Usuario']:
        """
        Inicia sesión verificando el nombre de usuario y la contraseña.
        """
        usuarios = Usuario.cargar_usuarios()
        for usuario_data in usuarios:
            if usuario_data['username'] == username and usuario_data['password'] == password:
                return Usuario(**usuario_data)
        print("Usuario o contraseña incorrectos.")
        return None
