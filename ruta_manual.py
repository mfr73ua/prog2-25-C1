"""
Módulo para la creación manual de rutas geográficas.

Este módulo permite crear rutas especificando origen, destino
y puntos intermedios, generando los archivos necesarios.

"""

import random
from ruta import Ruta
from utils import exportar_pdf, exportar_gpx, generar_mapa
import json

class RutaManual:
    """
    Clase para crear rutas de forma manual.

    Esta clase permite crear rutas y generar los archivos
    PDF, GPX y HTML correspondientes.

    Methods
    -------
    crear_ruta_desde_datos(origen, puntos_intermedios, destino, modo, nombre, username)
        Crea una ruta con los datos proporcionados
    """

    @staticmethod
    def crear_ruta_desde_datos(origen, puntos_intermedios, destino, modo, nombre=None, username=None):
        """
        Crea una ruta con los datos proporcionados.

        Parameters
        ----------
        origen : str
            Punto de inicio de la ruta
        puntos_intermedios : List[str]
            Lista de puntos intermedios
        destino : str
            Punto final de la ruta
        modo : str
            Modo de transporte (caminar, bicicleta, coche)
        nombre : str, optional
            Nombre de la ruta
        username : str, optional
            Usuario que crea la ruta

        Returns
        -------
        tuple
            Nombres de los archivos generados (PDF, GPX, HTML)

        Raises
        ------
        ValueError
            Si el origen o destino son None
        RuntimeError
            Si hay un error al exportar los archivos
        """
        # Validaciones: solo verifica que no sean None
        if origen is None or destino is None:
            raise ValueError("El origen y el destino no pueden ser None.")
        if puntos_intermedios is None:
            puntos_intermedios = []

        if not nombre:
            nombre = f"ruta_manual_{random.randint(1000, 9999)}"

        ruta = Ruta(
            nombre=nombre,
            ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),
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

        ruta.guardar_en_json()

        # Añadir la nueva ruta al archivo de usuarios
        if username:
            with open("usuarios.json", "r+", encoding="utf-8") as f:
                usuarios = json.load(f)
                for user in usuarios:
                    if user["username"] == username:
                        if "rutas" not in user:
                            user["rutas"] = []
                        user["rutas"].append(ruta.nombre)
                        break
                f.seek(0)
                json.dump(usuarios, f, indent=4, ensure_ascii=False)
                f.truncate()

        try:
            pdf_filename = exportar_pdf(ruta.distancias, ruta.tiempos_estimados, ruta.modo_transporte, ruta.nombre, ruta.origen, ruta.puntos_intermedios, ruta.destino)
            gpx_filename = exportar_gpx(ruta.rutas, ruta.grafo, ruta.timestamp)
            html_filename = generar_mapa(ruta.origen, ruta.puntos_intermedios, ruta.destino, ruta.rutas, ruta.grafo, ruta.timestamp)
        except Exception as e:
            raise RuntimeError(f"Error al exportar archivos: {e}")

        if not all([pdf_filename, gpx_filename, html_filename]):
            raise ValueError("No se pudieron generar todos los archivos correctamente.")

        return pdf_filename, gpx_filename, html_filename