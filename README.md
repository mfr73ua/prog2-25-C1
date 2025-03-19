# Rutas turísticas en Alicante
## Autores

* (Coordinador) [Marcos Francés Requena](https://github.com/mfr73ua)
* [Rares Andrei Mocanu](https://github.com/ra-and5)
* [Marta López Martos](https://github.com/martalopez6)
* [Germán Hurtado Rodríguez](https://github.com/ghr8)
* [David González Fernández](https://github.com/Gallego-DavidGonzalez)

## Profesor
[Cristina Cachero](https://github.com/ccacheroc)

## Requisitos
* Gestión rutas, listado de ellas y filtrado por ubicación, dificultad o distancia. -> Germán
* Rutas exportadas en diferentes formatos (gpx, pdf y html) -> Marcos
* Opción de calificar las rutas añadiendo una puntuación (mediante estrellas) y la posibilidad de subir fotos.
* Registro de actividad de cada usuario, almacenando las rutas completadas por cada usuario. -> Marta
* Generación de informes mensuales en formato pdf con estadísticas personales, km recorridos, tiempo total de actividad... -> Marta
* Integración de mapas, con alguna API para mostrar las rutas en un formato útil y visual. -> Marcos
* Obtención a su vez de información meteorológica de las rutas en tiempo real mediante otra API.
* Posibilidad de exportar rutas para dispositivos GPS en formato gpx, ya sean relojes deportivos, ciclocomputadores o apps de senderismo para seguir las rutas mediante su realización con indicaciones. -> Marcos
* Creación de una interfaz básica mediante la librería `tkinter` para la ejecución del proyecto. -> Marcos

## Instrucciones de instalación y ejecución
Para la instalación de las librerías necesarias para la ejecución del proyecto ejecute el siguiente comando:
   ```bash
   pip install -r requeriments.txt
```

## Resumen de la API
[//]: # (Cuando tengáis la API, añadiréis aquí la descripción de las diferentes llamadas.)
[//]: # (Para la evaluación por pares, indicaréis aquí las diferentes opciones de vuestro menú textual, especificando para qué sirve cada una de ellas)
El proyecto consiste en una aplicación para gestionar, calcular y exportar rutas utilizando datos geográficos proporcionados por OpenStreetMap mediante la biblioteca osmnx y la herramienta de geocodificación geopy. El sistema permite definir rutas manualmente (crear_rutas_manual.py) o de manera automática desde archivos JSON (crear_rutas_auto.py), almacenándolas y recuperándolas posteriormente (gestor_rutas.py).

Para cada ruta definida, la aplicación puede calcular la trayectoria óptima con NetworkX (ruta.py y calcular_ruta.py). Estos cálculos consideran puntos intermedios, origen y destino, así como modos de transporte específicos como caminar, bicicleta o coche. Los resultados incluyen la distancia total y el tiempo estimado.

Además, se generan reportes detallados en diferentes formatos: GPX (para sistemas GPS), PDF (para reportes impresos) y HTML interactivo (mapas generados con Folium) mediante funciones auxiliares implementadas en utils.py. Finalmente, la aplicación cuenta con una interfaz gráfica construida en Tkinter (interfaz.py), lo que facilita la interacción con el usuario y la integración con otros sistemas.

El conjunto completo de dependencias necesarias para ejecutar el proyecto está especificado claramente en el archivo requirements.txt.
