from ruta import Ruta
import random
import os
from typing import List
from ruta_manual import RutaManual
import sqlite3
from datetime import datetime



class RutaAuto:
    
    
    def __init__(self, directorio: str = "rutas") -> None:
        
        """
        Se comprueba que exista el directorio de rutas.
        Dependiendo de si lo hace o no lo crea en caso negativo.
        """
        
        self.directorio = directorio
        if not os.path.exists(self.directorio):
            os.makedirs(self.directorio)


    def generar_rutas_desde_direcciones(self, direcciones: List[str], cantidad: int = 5, username: str = None) -> list:
        
        """
        Genera rutas aleatorias entre las direcciones proporcionadas y las exporta en varios formatos.

        Parámetros:
        -----------
        direcciones : List[str]
            Lista de direcciones reales introducidas por el usuario.
        cantidad : int
            Número de rutas aleatorias a generar (por defecto 5).
        username : str
            Usuario al que asociar la ruta (opcional).
        """
        
        # Se valida que haya al menos 2 direcciones
        if len(direcciones) < 2:
            return ["Se necesitan al menos dos direcciones para generar rutas."]


        rutas_generadas = []
        
        for i in range(min(cantidad, len(direcciones) - 1)):
            
            try:
                
                # Seleccionar aleatoriamente origen, destino y puntos intermedios
                origen, destino = random.sample(direcciones, 2)
                
                # Selección de hasta dos puntos intermedios distintos de origen y destino
                puntos_intermedios = random.sample(
                    [d for d in direcciones if d != origen and d != destino],
                    k=min(2, len(direcciones) - 2)
                ) if len(direcciones) > 2 else []
                
                
                # Se selecciona de forma aleatoria el modo de transporte
                modo = random.choice(["walk", "bike", "drive"])
                
                nombre = f"ruta_auto_{int(datetime.now().timestamp())}_{i+1}"

                # Crear la ruta usando RutaManual
                try:
                    ruta = RutaManual.crear_ruta_desde_datos(
                        origen=origen,
                        puntos_intermedios=puntos_intermedios,
                        destino=destino,
                        modo=modo,
                        nombre=nombre,
                        username=username
                    )
                    
                except Exception as e:
                    rutas_generadas.append(f"Error al crear la ruta '{nombre}': {str(e)}")
                    continue

                # Asociar la ruta al usuario en la base de datos SQLite (en caso de que no lo haga la RutaManual)
                if username:
                    try:
                        # Se gestiona conexión y operación con la base de datos.
                        conn = sqlite3.connect('usuarios.db')
                        cursor = conn.cursor()
                        
                        # Buscar el ID del usuario por su nombre de usuario
                        cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
                        usuario = cursor.fetchone()
                        
                        if usuario:
                            # Insertar la relación entre usuario y ruta si no existe
                            cursor.execute('''
                                INSERT OR IGNORE INTO usuario_rutas (
                                    usuario_id, nombre_ruta, created_at
                                ) VALUES (?, ?, ?)
                            ''', (
                                usuario[0],
                                nombre,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ))
                            conn.commit()
                        conn.close()
                    except Exception as e:
                        # Si hay un error al asociar la ruta con el usuario, se registra
                        rutas_generadas.append(f"Ruta creada pero error al asociar al usuario: {str(e)}")
                        
                        
                rutas_generadas.append(f"Ruta '{nombre}' creada y exportada exitosamente.")
            except Exception as e:
                # Si ocurre cualquier otro error general, se captura y se registra
                rutas_generadas.append(f"Error general: {str(e)}")
        return rutas_generadas