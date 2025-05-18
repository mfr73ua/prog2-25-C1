"""
Clase para manejar la geocodificación de direcciones usando Nominatim de OpenStreetMap.

Esta clase permite convertir direcciones en coordenadas geográficas
específicamente para la ciudad de Alicante, España.


"""

import time
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.location import Location

class Geocodificador:
    """
    Convierte direcciones en coordenadas geográficas.

    Esta clase utiliza el servicio Nominatim de OpenStreetMap para
    convertir direcciones en coordenadas (latitud, longitud).

    Attributes
    ----------
    geolocator : Nominatim
        Instancia del geocodificador Nominatim configurada
    """

    def __init__(self, user_agent: str = "PII_UA", timeout: int = 10) -> None:
        """
        Inicializa el geocodificador.

        Parameters
        ----------
        user_agent : str, optional
            Nombre para las peticiones a Nominatim, por defecto "PII_UA"
        timeout : int, optional
            Tiempo máximo de espera en segundos, por defecto 10
        """
        self.geolocator: Nominatim = Nominatim(user_agent=user_agent, timeout=timeout)

    def obtener_coordenadas(self, direccion: str) -> Optional[Tuple[float, float]]:
        """
        Obtiene las coordenadas de una dirección en Alicante.

        Parameters
        ----------
        direccion : str
            Dirección a geocodificar

        Returns
        -------
        Optional[Tuple[float, float]]
            Tupla (latitud, longitud) o None si no se encuentra

        Raises
        ------
        Exception
            Si hay un error en la geocodificación
        """
        query: str = f"{direccion}, Alicante, Spain"
        try:
            ubicacion: Optional[Location] = self.geolocator.geocode(query)
            time.sleep(1)  # Evita bloqueos por exceso de peticiones

            if ubicacion:
                lat: float = ubicacion.latitude
                lon: float = ubicacion.longitude

                if 38.22 <= lat <= 38.40 and -0.51 <= lon <= -0.43:
                    return (lat, lon)

        except Exception as e:
            print(f"Error en la geocodificación de '{direccion}': {e}")

        return None
