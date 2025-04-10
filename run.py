# run.py
from app_instance import app
from servicio_clima import ServicioOpenWeatherMap, GestorClima

# Inicializa gestor clima global
clima_gestor = GestorClima(ServicioOpenWeatherMap())

import api  # carga los endpoints

if __name__ == "__main__":
    app.run(debug=True, port=8000)
