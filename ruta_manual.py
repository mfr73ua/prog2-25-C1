import random
from ruta import Ruta
from utils import *
import json 

class RutaManual:
    @staticmethod
    def crear_ruta_desde_datos(origen, puntos_intermedios, destino, modo, nombre=None, usuario=None):
        """
        Crea una ruta desde los datos proporcionados y actualiza el archivo de usuarios.
        
        Parámetros:
        -----------
        origen : str
            El origen de la ruta.
        puntos_intermedios : List[str]
            Lista de puntos intermedios en la ruta.
        destino : str
            El destino de la ruta.
        modo : str
            El modo de transporte (caminar, bicicleta, coche).
        nombre : str
            El nombre de la ruta (opcional, se genera aleatoriamente si no se proporciona).
        usuario : Usuario
            El usuario que está creando la ruta.
        
        Devuelve:
        ---------
        tuple
            Archivos generados en formato PDF, GPX y HTML.
        """
        
        # Asegurarse de que los valores de origen, destino y puntos intermedios son cadenas
        if not isinstance(origen, str):
            raise ValueError("El origen debe ser una cadena de texto.")
        if not isinstance(destino, str):
            raise ValueError("El destino debe ser una cadena de texto.")
        
        # Asegurarse de que los puntos intermedios sean cadenas de texto
        puntos_intermedios = [str(p) for p in puntos_intermedios]
        
        # Validación para nombre de la ruta
        if not nombre:
            nombre = f"ruta_manual_{random.randint(1000, 9999)}"
        
        # Crear objeto Ruta
        ruta = Ruta(
            nombre=nombre,
            ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),
            distancia=0.0,
            duracion=0.0,
            dificultad="bajo",
            alt_max=0,
            alt_min=0,
            origen=origen,  # Aquí se pasa el nombre de origen como cadena
            puntos_intermedios=puntos_intermedios,  # Lista de puntos intermedios como cadenas
            destino=destino,  # Aquí se pasa el destino como cadena
            modo_transporte=modo
        )
        
        # Guardar la ruta en formato JSON
        ruta.guardar_en_json()

        # Añadir la nueva ruta al archivo de usuarios (solo si el usuario existe)
        if usuario:
            # Asegurarse de que el usuario exista
            if usuario.username:
                usuario.rutas.append(ruta.nombre)
                with open("usuarios.json", "r+") as f:
                    usuarios = json.load(f)
                    for user in usuarios:
                        if user["username"] == usuario.username:
                            user["rutas"] = usuario.rutas
                            break
                    f.seek(0)
                    json.dump(usuarios, f, indent=4, ensure_ascii=False)

        # Exportar a PDF, GPX y HTML
        try:
            pdf_filename = exportar_pdf(ruta.distancias, ruta.tiempos_estimados, ruta.modo_transporte, ruta.nombre, ruta.origen, ruta.puntos_intermedios, ruta.destino)
            gpx_filename = exportar_gpx(ruta.rutas, ruta.grafo, ruta.timestamp)
            html_filename = generar_mapa(ruta.origen, ruta.puntos_intermedios, ruta.destino, ruta.rutas, ruta.grafo, ruta.timestamp)
        except Exception as e:
            raise RuntimeError(f"Error al exportar archivos: {e}")

        # Verificación de éxito
        if not all([pdf_filename, gpx_filename, html_filename]):
            raise ValueError("No se pudieron generar todos los archivos correctamente.")

        # Regresar las rutas generadas
        return pdf_filename, gpx_filename, html_filename
