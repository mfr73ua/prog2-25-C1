import json
from datetime import datetime
from typing import List, Optional
import osmnx as ox
import networkx as nx
import time
from geocodificador import Geocodificador
from utils import *

class Ruta:
    """
    Clase que representa una ruta geográfica compuesta por un origen, puntos intermedios y un destino,
    junto con propiedades como distancia, duración, dificultad y exportaciones en varios formatos.

    Attributes
    ----------
    nombre : str
        Nombre de la ruta.
    ubicacion : tuple
        Coordenadas aproximadas de la ubicación central de la ruta.
    distancia : float
        Distancia total de la ruta (en km).
    duracion : float
        Duración estimada de la ruta (en horas).
    dificultad : str
        Nivel de dificultad ("bajo", "medio" o "alto").
    alt_max : int
        Altitud máxima (placeholder, no se calcula).
    alt_min : int
        Altitud mínima (placeholder, no se calcula).
    origen : tuple
        Coordenadas del punto de inicio.
    destino : tuple
        Coordenadas del punto de destino.
    puntos_intermedios : list
        Lista de coordenadas de puntos intermedios.
    modo_transporte : str
        Modo de transporte: "walk", "bike" o "drive".
    fecha_registro : datetime
        Fecha y hora de creación de la ruta.
    grafo : nx.MultiDiGraph
        Grafo de calles generado por OSMnx.
    rutas : list
        Lista de subrutas (cada una una lista de nodos).
    distancias : list
        Lista de distancias por tramo (en km).
    tiempos_estimados : list
        Lista de tiempos estimados por tramo (en horas).
    
    Methods
    -------
    calcular_distancia()
        Calcula la distancia total en km de la ruta.
    calcular_dificultad()
        Asigna una dificultad basada en la distancia.
    calcular_duracion()
        Calcula el tiempo estimado de recorrido.
    guardar_en_json()
        Exporta la ruta a distintos formatos incluyendo JSON, GPX, PDF y HTML.
    listar_rutas()
        Devuelve una lista de rutas almacenadas localmente.
    to_dict()
        Convierte la ruta en un diccionario de datos exportables.
    """

    def __init__(self, nombre: str, ubicacion: tuple, distancia: float, duracion: float,
                 dificultad: str, alt_max: int, alt_min: int,
                 origen, puntos_intermedios, destino, modo_transporte: str) -> None:
        """
        Inicializa una nueva instancia de Ruta, obteniendo coordenadas y preparando atributos.
        Puede recibir strings (direcciones) o tuplas (lat, lon) para origen, destino y puntos intermedios.

        Parameters
        ----------
        nombre : str
            Nombre de la ruta.
        ubicacion : tuple
            Coordenadas iniciales aproximadas.
        distancia : float
            Distancia inicial (se recalcula después).
        duracion : float
            Duración inicial (se recalcula después).
        dificultad : str
            Nivel de dificultad (se recalcula después).
        alt_max : int
            Altitud máxima (no se usa actualmente).
        alt_min : int
            Altitud mínima (no se usa actualmente).
        origen : str or tuple
            Dirección de inicio o coordenadas del punto de inicio.
        puntos_intermedios : list of str or tuple
            Lista de direcciones intermedias o coordenadas de puntos intermedios.
        destino : str or tuple
            Dirección final o coordenadas del punto de destino.
        modo_transporte : str
            "walk", "bike" o "drive".
            
        Raises
        ------
        ValueError
            Si alguno de los puntos (origen, destino o intermedios) no puede ser geocodificado correctamente.
        """
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.distancia = distancia
        self.duracion = duracion
        self.dificultad = dificultad
        self.alt_max = alt_max
        self.alt_min = alt_min
        self.fecha_registro = datetime.now()
        self.modo_transporte = modo_transporte
        self.geocodificador: Geocodificador = Geocodificador()

        # Función auxiliar local para obtener un nombre legible de una ubicación
        def extraer_nombre(p):
            if isinstance(p, dict):
                return p.get('direccion') or str((p.get('lat'), p.get('lng')))
            elif isinstance(p, str):
                return p
            elif isinstance(p, tuple) and len(p) == 2:
                return str(p)
            return str(p)
        # Guardar los nombres legibles para origen, destino e intermedios
        self.origen_nombre = extraer_nombre(origen)
        self.destino_nombre = extraer_nombre(destino)
        self.puntos_intermedios_nombres = [extraer_nombre(p) for p in puntos_intermedios]
        
        # Función auxiliar local para obtener coordenadas a partir de diferentes formatos de entrada
        def obtener_coord(p):
            if isinstance(p, tuple) and len(p) == 2 and all(isinstance(x, (float, int)) for x in p):
                return p
            elif isinstance(p, dict):
                if 'lat' in p and 'lng' in p:
                    return (float(p['lat']), float(p['lng']))
                elif 'direccion' in p:
                    return self.geocodificador.obtener_coordenadas(p['direccion'])
            elif isinstance(p, str):
                return self.geocodificador.obtener_coordenadas(p)
            return None
        
        # Obtener coordenadas geográficas del origen, destino y puntos intermedios
        self.origen = obtener_coord(origen)
        self.destino = obtener_coord(destino)
        self.puntos_intermedios = [obtener_coord(p) for p in puntos_intermedios]

        # Validar que ningún punto sea None
        if self.origen is None or self.destino is None or any(p is None for p in self.puntos_intermedios):
            raise ValueError("No se pudieron geocodificar todas las direcciones o las coordenadas no son válidas. Verifica los nombres de las calles o las coordenadas.")
        
        # Inicializar estructuras auxiliares y temporales
        self.timestamp = int(time.time())
        self.grafo: Optional[nx.MultiDiGraph] = None
        self.nodos: List[int] = []
        self.rutas: List[List[int]] = []
        self.distancias: List[float] = []
        self.tiempos_estimados: List[float] = []

    def calcular_distancia(self) -> float:
        """
        Calcula la distancia total de la ruta usando el camino más corto entre cada par de puntos.

        Returns
        -------
        float
            Distancia total en kilómetros.
        """
        self.grafo = ox.graph_from_point(self.origen, dist=5000, network_type=self.modo_transporte)

        nodo_origen = ox.nearest_nodes(self.grafo, self.origen[1], self.origen[0])
        nodo_destino = ox.nearest_nodes(self.grafo, self.destino[1], self.destino[0])
        nodos_intermedios = [ox.nearest_nodes(self.grafo, p[1], p[0]) for p in self.puntos_intermedios]

        ruta_nodos = [nodo_origen] + nodos_intermedios + [nodo_destino]

        distancia_total = 0
        for i in range(len(ruta_nodos) - 1):
            distancia_total += nx.shortest_path_length(self.grafo, ruta_nodos[i], ruta_nodos[i + 1], weight='length')

        return distancia_total / 1000

    def calcular_dificultad(self) -> str:
        """
        Asigna una dificultad según la distancia total.

        Returns
        -------
        str
            "bajo", "medio" o "alto"
        """
        if self.distancia < 10:
            return 'bajo'
        elif self.distancia < 20:
            return 'medio'
        else:
            return 'alto'

    def calcular_duracion(self) -> float:
        """
        Estima el tiempo de recorrido total según la velocidad del modo de transporte.

        Returns
        -------
        float
            Tiempo estimado en horas.

        Raises
        ------
        ValueError
            Si el modo de transporte no es válido.
        """
        velocidad = {'walk': 5, 'bike': 15, 'drive': 30}
        if self.modo_transporte not in velocidad:
            raise ValueError("Modo de transporte no válido. Usa 'walk', 'bike' o 'drive'.")
        return self.distancia / velocidad[self.modo_transporte]

    def guardar_en_json(self) -> None:
        """
        Calcula propiedades de la ruta y guarda los datos en un archivo JSON.
        Además, genera los archivos GPX, HTML, PDF y PNG correspondientes.
        """
        self.distancia = self.calcular_distancia()
        self.dificultad = self.calcular_dificultad()
        self.duracion = self.calcular_duracion()

        distancia_str = f"{self.distancia:.2f} km"
        horas = int(self.duracion)
        minutos = int((self.duracion - horas) * 60)
        duracion_str = f"{horas} h {minutos} min" if horas > 0 else f"{minutos} min"

        datos_ruta = {
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "distancia": distancia_str,
            "duracion": duracion_str,
            "dificultad": self.dificultad,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
            "origen": self.origen_nombre,
            "puntos_intermedios": self.puntos_intermedios_nombres,
            "destino": self.destino_nombre,
            "modo_transporte": self.modo_transporte
        }

        with open(f"rutas/{self.nombre}.json", "w") as archivo:
            json.dump(datos_ruta, archivo, indent=4, ensure_ascii=False)

        # Cálculo de subrutas
        nodo_origen = ox.nearest_nodes(self.grafo, self.origen[1], self.origen[0])
        nodo_destino = ox.nearest_nodes(self.grafo, self.destino[1], self.destino[0])
        nodos_intermedios = [ox.nearest_nodes(self.grafo, p[1], p[0]) for p in self.puntos_intermedios]
        ruta_nodos = [nodo_origen] + nodos_intermedios + [nodo_destino]

        self.rutas = []
        self.distancias = []
        self.tiempos_estimados = []

        for i in range(len(ruta_nodos) - 1):
            try:
                subruta = nx.shortest_path(self.grafo, ruta_nodos[i], ruta_nodos[i + 1], weight='length')
                self.rutas.append(subruta)

                distancia_km = nx.shortest_path_length(self.grafo, ruta_nodos[i], ruta_nodos[i + 1], weight='length') / 1000
                self.distancias.append(distancia_km)

                velocidad = {'walk': 5, 'bike': 15, 'drive': 60}
                tiempo_horas = distancia_km / velocidad[self.modo_transporte]
                self.tiempos_estimados.append(tiempo_horas)
            except Exception as e:
                print(f" Error al calcular subruta: {e}")

        # Exportaciones
        exportar_gpx(self.rutas, self.grafo, self.nombre)
        ruta_html = generar_mapa(self.origen, self.puntos_intermedios, self.destino, self.rutas, self.grafo, self.nombre)
        exportar_pdf(self.distancias, self.tiempos_estimados, self.modo_transporte, self.nombre, self.origen_nombre, self.puntos_intermedios_nombres, self.destino_nombre)


    @staticmethod
    def listar_rutas() -> List[dict]:
        """
        Lista todas las rutas almacenadas en formato JSON dentro del directorio 'rutas/'.

        Recorre todos los archivos `.json` de la carpeta `rutas`, los carga como diccionarios
        y los agrega a una lista que es devuelta al final.

        Returns
        -------
        List[dict]
            Lista de rutas representadas como diccionarios.
            Si no existe la carpeta o no hay archivos válidos, devuelve una lista vacía.
        """
        rutas = []
        if not os.path.exists("rutas"):
            return rutas
        for filename in os.listdir("rutas"):
            if filename.endswith(".json"):
                with open(os.path.join("rutas", filename), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        rutas.append(data)
                    except Exception:
                        continue
        return rutas
    
    def to_dict(self):
        """
        Convierte la instancia de la clase `Ruta` en un diccionario con sus atributos relevantes.

        Este método crea un diccionario con los valores de los atributos de la ruta, incluyendo
        el nombre, modo de transporte, distancia, duración y dificultad. Los métodos `distancia_str()` 
        y `duracion_str()` son utilizados para obtener las representaciones en cadena de los atributos 
        `distancia` y `duracion`.

        Returns
        -------
        dict
            Un diccionario con los siguientes campos:
            - "nombre" (str): Nombre de la ruta.
            - "modo_transporte" (str): Modo de transporte utilizado en la ruta.
            - "distancia" (str): Distancia de la ruta, representada como cadena.
            - "duracion" (str): Duración estimada de la ruta, representada como cadena.
            - "dificultad" (str): Nivel de dificultad de la ruta.
        """
        return {
            "nombre": self.nombre,
            "modo_transporte": self.modo_transporte,
            "distancia": self.distancia_str(),
            "duracion": self.duracion_str(),
            "dificultad": self.dificultad
        }


