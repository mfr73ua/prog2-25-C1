import json
import sqlite3
import os
from datetime import datetime

# Rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'usuarios.db')
JSON_PATH = os.path.join(BASE_DIR, 'usuarios.json')

def crear_tablas():
    """
    Crea las tablas necesarias en la base de datos SQLite.

    Se eliminan las tablas existentes `usuario_rutas`, `rutas` y `usuarios` (si existen) 
    y se crean nuevamente con su estructura correspondiente.

    Returns
    -------
    sqlite3.Connection
        Conexión activa a la base de datos con las tablas creadas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS usuario_rutas')
    cursor.execute('DROP TABLE IF EXISTS rutas')
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            telefono TEXT,
            fecha_nacimiento TEXT,
            ciudad TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            origen TEXT NOT NULL,
            destino TEXT NOT NULL,
            puntos_intermedios TEXT,
            modo TEXT DEFAULT 'walk',
            distancia_km REAL,
            duracion_horas REAL,
            dificultad TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            creador TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_rutas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nombre_ruta TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            UNIQUE(usuario_id, nombre_ruta)
        )
    ''')
    conn.commit()
    print("Tablas creadas correctamente")
    return conn

def migrar_datos():
    """
    Migra los datos de usuarios y rutas desde el archivo JSON a la base de datos SQLite.

    El archivo JSON debe contener una lista de usuarios con sus respectivos campos y 
    rutas asociadas. Por cada usuario se insertan sus datos personales y se crean 
    relaciones con las rutas indicadas.

    Returns
    -------
    bool
        True si la migración fue exitosa, False si hubo algún error (como archivo no encontrado).
    """
    if not os.path.exists(JSON_PATH):
        print(f"No se encontró el archivo {JSON_PATH}")
        return False

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        usuarios = json.load(f)

    conn = crear_tablas()
    cursor = conn.cursor()
    usuarios_migrados = 0
    rutas_migradas = 0

    for usuario in usuarios:
        datos_usuario = (
            usuario.get('nombre', ''),
            usuario.get('apellido', ''),
            usuario.get('email', ''),
            usuario.get('username', ''),
            usuario.get('password', ''),
            usuario.get('telefono', ''),
            usuario.get('fecha_nacimiento', ''),
            usuario.get('ciudad', ''),
            datetime.now().isoformat()
        )
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (
                nombre, apellido, email, username, password_hash,
                telefono, fecha_nacimiento, ciudad, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', datos_usuario)
        user_id = cursor.lastrowid
        usuarios_migrados += 1

        rutas = usuario.get('rutas', [])
        if isinstance(rutas, list):
            for nombre_ruta in rutas:
                cursor.execute('''
                    INSERT OR REPLACE INTO rutas (
                        nombre, origen, destino, puntos_intermedios,
                        modo, distancia_km, duracion_horas, dificultad,
                        created_at, creador
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nombre_ruta,
                    json.dumps({"lat": 0, "lng": 0}),
                    json.dumps({"lat": 0, "lng": 0}),
                    json.dumps([]),
                    'walk',
                    0.0,
                    0.0,
                    'media',
                    datetime.now().isoformat(),
                    usuario.get('username', '')
                ))
                cursor.execute('''
                    INSERT OR REPLACE INTO usuario_rutas (
                        usuario_id, nombre_ruta, created_at
                    ) VALUES (?, ?, ?)
                ''', (
                    user_id,
                    nombre_ruta,
                    datetime.now().isoformat()
                ))
                rutas_migradas += 1
        print(f"Usuario {usuario.get('username', '')} migrado correctamente")

    conn.commit()
    conn.close()
    print(f"\nResumen de la migración:")
    print(f"Usuarios migrados: {usuarios_migrados}")
    print(f"Rutas migradas: {rutas_migradas}")
    print("Migración completada exitosamente!")
    return True

if __name__ == "__main__":
    """
    Punto de entrada del script.

    Ejecuta el proceso de migración de datos desde un archivo JSON a una base de datos SQLite.
    Imprime en consola información sobre el estado del proceso y resumen final.

    Examples
    --------
    $ python script.py
    Iniciando proceso de migración...
    Ruta de la base de datos: /ruta/absoluta/usuarios.db
    Ruta del archivo JSON: /ruta/absoluta/usuarios.json
    ...
    """
    print("Iniciando proceso de migración...")
    print(f"Ruta de la base de datos: {DB_PATH}")
    print(f"Ruta del archivo JSON: {JSON_PATH}")
    if migrar_datos():
        print("Migración completada con éxito")
    else:
        print("La migración no se completó correctamente")

