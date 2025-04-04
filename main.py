
# CODIGO COMENTADO UTILIZADO PARA PRUEBAS Y GENERAR DATOS SOBRE LOS QUE PROBAR LAS FUNCIONALIDADES DEL PROYECTO
# AL FINAL DEL FICHERO SE ENCUENTRA LA EJECUCION REAL DEL PROYECTO

'''
import requests
import os
import random
from ruta import Ruta
from itertools import product
from utils import exportar_pdf, exportar_gpx, generar_mapa, exportar_png_desde_html

# Crear el directorio de rutas si no existe
directorio = "rutas"
if not os.path.exists(directorio):
    os.makedirs(directorio)

# Posibles orígenes y destinos reales
origen_destino_data = [
    ("Castillo de Santa Bárbara", "Playa del Postiguet"),
    ("Playa del Postiguet", "Parque El Palmeral"),
    ("Centro Comercial Gran Vía Alicante", "Plaza Mar 2"),
    ("Mercado Central de Alicante", "Hospital General Universitario de Alicante"),
    ("Plaza de los Luceros", "Playa de San Juan"),
    ("Puerto de Alicante", "Museo de Arte Contemporáneo de Alicante"),
    ("Parque de Canalejas", "Plaza de Toros de Alicante"),
    ("La Explanada de España", "Playa de la Albufereta"),
    ("Museo Arqueológico de Alicante", "Parque de la Ereta"),
    ("Centro Comercial Plaza Mar 2", "El Corte Inglés")
]

# Puntos intermedios reales
puntos_intermedios_data = [
    "Calle de Ciriaco", "Avenida de la Constitución", "Calle del Teatro", "Plaza de los Luceros",
    "Avenida de la Rambla", "Calle San Vicente", "Plaza Mar 2", "Avenida de Alicante",
    "Hospital General Universitario de Alicante", "Mercado Central"
]

# Crear combinaciones de origen y destino (cruzadas)
combinaciones_origen_destino = list(product(
    [o[0] for o in origen_destino_data],
    [d[1] for d in origen_destino_data]
))

# Función para generar las rutas
def generar_rutas():
    for i in range(50):
        origen, destino = random.choice(combinaciones_origen_destino)
        puntos_intermedios = random.sample(puntos_intermedios_data, 2)
        modo_transporte = random.choice(["walk", "bike", "drive"])

        try:
            # Crear la ruta
            ruta = Ruta(
                nombre=f"Ruta_{i+1}",
                ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),  # Coordenadas aleatorias en Alicante
                distancia=0.0,
                duracion=0.0,
                dificultad="bajo",
                alt_max=0,
                alt_min=0,
                origen=origen,
                puntos_intermedios=puntos_intermedios,
                destino=destino,
                modo_transporte=modo_transporte
            )

            # Guardar la ruta en el archivo JSON
            ruta.guardar_en_json()

            # Exportar el PDF y otros archivos (GPX, HTML, PNG) asociados
            pdf_path = exportar_pdf(
                ruta.distancias, ruta.tiempos_estimados, ruta.modo_transporte, ruta.nombre,
                ruta.origen_nombre, ruta.puntos_intermedios_nombres, ruta.destino_nombre
            )

            # Exportar GPX
            gpx_path = exportar_gpx(ruta.rutas, ruta.grafo, ruta.timestamp)

            # Generar el mapa en HTML y exportar el PNG desde HTML
            ruta_html = generar_mapa(
                ruta.origen, ruta.puntos_intermedios, ruta.destino, ruta.rutas, ruta.grafo, ruta.timestamp
            )
            exportar_png_desde_html(ruta_html, f"static/{ruta.nombre}.png")

            print(f"Ruta {i+1} guardada en {directorio}/Ruta_{i+1}.json, PDF: {pdf_path}, GPX: {gpx_path}")

        except Exception as e:
            print(f"⚠️ Error al generar la ruta {i+1}: {e}")

# Ejecutar la generación de rutas
generar_rutas()

'''
'''
url = "http://127.0.0.1:5000/procesar_ruta"

respuesta = requests.post(url)

if respuesta.status_code == 200:
    print("✅ Rutas procesadas correctamente:")
    resultados = respuesta.json()
    for ruta in resultados:
        if "error" in ruta:
            print(f"\n⚠️ Error en ruta: {ruta['error']}")
        else:
            print(f"\n🔹 Ruta generada:")
            print(f"GPX: {ruta['gpx_file']}")
            print(f"PDF: {ruta['pdf_file']}")
            print(f"HTML: {ruta['html_file']}")
else:
    print("❌ Error al procesar rutas:", respuesta.json())
'''
###################################################################
'''
from gestor_rutas import GestorRutas  

# Ejecución de gestor de rutas (filtrado):
gestor = GestorRutas()

    todas = gestor.lista_rutas()
    print(f"\n📦 Total de rutas: {len(todas)}")

    # Filtros básicos
    faciles = gestor.filtrar_por_dificultad("bajo")
    cortas = gestor.filtrar_por_distancia(5)
    rapidas = gestor.filtrar_por_duracion(0.5)
    combinadas = gestor.filtrar_combinado("bajo", 5, 0.5)

    gestor.mostrar_rutas(faciles, "Rutas fáciles")
    gestor.mostrar_rutas(cortas, "Rutas cortas (<5 km)")
    gestor.mostrar_rutas(rapidas, "Rutas rápidas (<30 min)")
    gestor.mostrar_rutas(combinadas, "Rutas fáciles, cortas y rápidas")

    # Extras
    destino_deseado = "Playa del Postiguet"
    rutas_al_destino = [r for r in todas if r["destino"] == destino_deseado]
    gestor.mostrar_rutas(rutas_al_destino, f"Rutas que terminan en {destino_deseado}")

    origen_deseado = "Castillo de Santa Bárbara"
    rutas_desde_origen = [r for r in todas if r["origen"] == origen_deseado]
    gestor.mostrar_rutas(rutas_desde_origen, f"Rutas que empiezan en {origen_deseado}")

    rutas_bici = [r for r in todas if r["modo_transporte"] == "bike"]
    gestor.mostrar_rutas(rutas_bici, "Rutas en bicicleta")

    rutas_largas = [
        r for r in todas
        if gestor._distancia_km(r) > 10 and gestor._duracion_horas(r) > 1
    ]
    gestor.mostrar_rutas(rutas_largas, "Rutas largas (>10 km y >1 h)")

    punto_intermedio = "Plaza Mar 2"
    rutas_con_punto = [r for r in todas if punto_intermedio in r.get("puntos_intermedios", [])]
    gestor.mostrar_rutas(rutas_con_punto, f"Rutas que pasan por {punto_intermedio}")

    print("\n📊 Estadísticas:")
    print(f"- Total: {len(todas)} rutas")
    print(f"- Fáciles: {len(faciles)}")
    print(f"- Cortas: {len(cortas)}")
    print(f"- Rápidas: {len(rapidas)}")
    print(f"- Combinadas (bajo, <5km, <30min): {len(combinadas)}")

    rutas_ordenadas = sorted(todas, key=lambda r: gestor._distancia_km(r))
    gestor.mostrar_rutas(rutas_ordenadas[:3], "🏁 Las 3 rutas más cortas")

    rutas_largas_top = sorted(todas, key=lambda r: gestor._distancia_km(r), reverse=True)
    gestor.mostrar_rutas(rutas_largas_top[:3], "🚩 Las 3 rutas más largas")

    rutas_1h = [r for r in todas if abs(gestor._duracion_horas(r) - 1.0) < 0.01]
    gestor.mostrar_rutas(rutas_1h, "🕐 Rutas con duración exacta de 1 hora")
'''
#############################################
'''
# Crear ruta manual con paso de puntos
from ruta_manual import RutaManual
RutaManual.crear_ruta_desde_terminal()

'''
#🛤️ CREAR RUTA MANUAL
#📍 Origen: Plaza de los Luceros
#📌 Intermedios (separados por coma, opcional): 
#🏁 Destino: Playa del Postiguet
#🚶‍♂️🚴‍♀️🚗 Modo (walk, bike, drive): walk
#📝 Nombre para la ruta y archivos exportados (opcional, ENTER para autogenerar): ruta_prueba

#✅ Ruta 'ruta_prueba' creada y exportada con éxito.
'''
'''
#######################################################
'''
# Generador automatico rutas entre puntos a elegir
from ruta_auto import RutaAuto

print("\n📌 GENERADOR DE RUTAS AUTOMÁTICAS")
entradas = input("Ingrese direcciones separadas por coma (mínimo 3):\n> ")
direcciones = [d.strip() for d in entradas.split(',') if d.strip()]

generador = RutaAuto()
generador.generar_rutas_desde_direcciones(direcciones, cantidad=5)
'''
'''
############################################################
# Para probar la api del clima:
from servicio_clima import *
# Clave API de OpenWeatherMap
clave_api: str = "5ead714f2ad83f23daf51c47124fd500"

servicio: ServicioClimaInterface = ServicioOpenWeatherMap(clave_api)
gestor: GestorClima = GestorClima(servicio)

while True:
    print("\n🌤️ CONSULTA DE CLIMA")
    ciudad: str = input("Ingresa el nombre de la ciudad (o 'salir' para terminar): ")
    
    if ciudad.lower() == 'salir':
        break
        
    try:
        resultado: DatosClima = gestor.consultar_clima(ciudad)
        print("\n📊 Información del clima:")
        print(f"📍 Ciudad: {resultado.ciudad}")
        print(f"🌡️ Temperatura: {resultado.temperatura}°C")
        print(f"💧 Humedad: {resultado.humedad}%")
        print(f"☁️ Descripción: {resultado.descripcion}")
        print(f"💨 Viento: {resultado.viento} m/s")
        print(f"📅 Fecha: {resultado.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"❌ {str(e)}")
'''

from interfaz import Interfaz
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    app = Interfaz(root)
    root.mainloop()
