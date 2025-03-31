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

Este proyecto consiste en una aplicación completa para la **creación, gestión, visualización y exportación de rutas geográficas**. Diseñado con un enfoque modular y extensible, el sistema ofrece una experiencia amigable al usuario gracias a su **interfaz gráfica construida con Tkinter**. Su funcionalidad se centra en generar rutas dentro de la provincia de Alicante, aprovechando los datos de OpenStreetMap y la API de OpenWeatherMap para enriquecer la experiencia del usuario.

---

#### 🧭 Estructura del sistema de rutas

El corazón del sistema es la clase `Ruta`, encargada de representar una ruta geográfica con todos sus metadatos: coordenadas, distancia, duración estimada, dificultad, y puntos relevantes. Internamente, se utiliza la biblioteca `osmnx` para construir un **grafo urbano basado en la red vial** de la ciudad, lo que permite calcular caminos óptimos entre origen, puntos intermedios y destino.

Cada ruta generada se exporta automáticamente en cuatro formatos distintos:

- **HTML interactivo** con el mapa visual y marcadores (vía Folium).
- **Archivo GPX** compatible con dispositivos GPS.
- **Informe PDF** con detalles como tramos, distancias y tiempo estimado.
- **Imagen PNG** del mapa generado (usando Selenium para captura del HTML).

Además, se clasifica automáticamente cada ruta según su **nivel de dificultad** (bajo, medio, alto) dependiendo de la distancia, y se estima la duración en función del medio de transporte elegido: caminar, bicicleta o coche.

---

#### 🛠️ Rutas manuales y automáticas

El sistema ofrece dos formas principales de crear rutas:

1. **Ruta Manual**: El usuario introduce el origen, puntos intermedios y destino de forma explícita, junto al modo de transporte y un nombre para la ruta. Esta opción brinda un control total sobre el recorrido y permite guardar la ruta directamente asociada al perfil del usuario.

2. **Ruta Automática**: A partir de una lista de direcciones dadas, el sistema genera múltiples rutas aleatorias entre pares de puntos, seleccionando también al azar los puntos intermedios y el medio de transporte. Esta funcionalidad es útil para descubrir nuevos recorridos de manera rápida y sin esfuerzo.

Todas las rutas creadas quedan almacenadas como archivos `.json` y se asocian al usuario correspondiente dentro de una base de datos persistente en `usuarios.json`.

---

#### 👤 Gestión de usuarios y relaciones sociales

El sistema incluye un **módulo completo de autenticación** que permite a los usuarios registrarse, iniciar sesión y almacenar sus rutas. Los datos personales (nombre, email, ciudad, etc.) se guardan junto con una lista de rutas creadas y una lista de amigos.

La lógica de amistad se basa en la detección automática de **rutas compartidas**: si dos usuarios tienen al menos una ruta en común, se consideran amigos. La interfaz permite consultar las rutas en común con cada amigo y acceder a sus archivos exportados.

Cada usuario puede visualizar sus rutas guardadas, abrir el archivo PDF o HTML asociado directamente desde la interfaz, y consultar información básica como origen, destino, y modo de transporte.

---

#### ☁️ Consulta meteorológica integrada

Una de las funcionalidades destacadas es la **consulta del clima** usando la API de OpenWeatherMap. El usuario puede introducir cualquier ciudad (por defecto, se espera que sea en España) y obtener información actualizada sobre:

- Temperatura
- Humedad
- Descripción del clima
- Velocidad del viento
- Fecha y hora de la medición

Esto permite planificar rutas de forma más informada, anticipando posibles condiciones meteorológicas adversas.

---

#### 🧩 Modularidad y código organizado

El proyecto está dividido en módulos altamente cohesivos y con responsabilidades bien definidas:

- `ruta.py`, `ruta_auto.py`, `ruta_manual.py`: gestión de rutas.
- `utils.py`: funciones de exportación.
- `usuario.py`: clase para manejar usuarios.
- `gestor_rutas.py`: carga, filtrado y análisis de rutas.
- `geocodificador.py`: conversión de direcciones en coordenadas.
- `servicio_clima.py`: consulta del clima mediante API.
- `interfaz.py`: interfaz gráfica completa con menús y formularios.
- `main.py`: punto de entrada para ejecutar la app o generar rutas masivas.

La estructura del código está pensada para facilitar **la extensión futura** (por ejemplo, añadir nuevas formas de filtrado de rutas o integración con APIs de cualquier otro tipo).


## Instrucciones de instalación y ejecución
Para la instalación de las librerías necesarias para la ejecución del proyecto ejecute el siguiente comando:
   ```bash
   pip install -r requeriments.txt
```
A continuación con la simple ejecución del fichero `main.py` bastaría para probar nuestro proyecto.

## Resumen de la API
[//]: # (Cuando tengáis la API, añadiréis aquí la descripción de las diferentes llamadas.)
[//]: # (Para la evaluación por pares, indicaréis aquí las diferentes opciones de vuestro menú textual, especificando para qué sirve cada una de ellas)

Actualmente, el sistema cuenta con una API sencilla que permite procesar rutas desde el backend. Esta API está pensada como punto de entrada para automatizar la generación de rutas y obtener archivos exportados como GPX, PDF y HTML sin necesidad de usar la interfaz gráfica. El endpoint principal disponible es `/procesar_ruta`, accesible mediante una petición POST.

Al enviar una solicitud a esta ruta, el sistema genera automáticamente una o varias rutas utilizando combinaciones predefinidas de direcciones reales en Alicante. Internamente, se calcula el grafo de calles, se buscan los caminos más cortos y se exportan los archivos asociados para cada ruta. La respuesta de la API devuelve un resumen de los archivos generados o un mensaje de error si algo falla en el proceso.

Aunque actualmente no se reciben parámetros personalizados en la petición (es decir, no puedes indicar tus propios puntos aún), el sistema está preparado para crecer fácilmente. En el futuro, se podría ampliar esta API para aceptar datos como origen, destino, puntos intermedios, modo de transporte o usuario asociado, haciendo que el sistema sea totalmente interactivo desde cualquier frontend o sistema externo.

En resumen, esta API sirve como una base funcional para automatizar la creación de rutas. Es ideal para pruebas, generación masiva de rutas o integración inicial con otros servicios. Puedes probarla localmente enviando una petición POST a `http://127.0.0.1:5000/procesar_ruta`.

