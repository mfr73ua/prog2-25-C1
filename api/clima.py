# api/clima.py
from app_instance import app
from flask import request, jsonify
from run import clima_gestor  # importar la instancia desde run.py

# Obtener clima actual
@app.route("/api/clima", methods=["GET"])
def obtener_clima():
    ciudad = request.args.get("ciudad")
    try:
        clima = clima_gestor.consultar_clima(ciudad)
        return jsonify({
            "ciudad": clima.ciudad,
            "temperatura": clima.temperatura,
            "humedad": clima.humedad,
            "descripcion": clima.descripcion,
            "viento": clima.viento,
            "fecha": clima.fecha.isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Forzar actualización de clima
@app.route("/api/clima/<ciudad>", methods=["PUT"])
def actualizar_clima(ciudad):
    try:
        clima = clima_gestor.consultar_clima(ciudad)
        return jsonify({"mensaje": "Clima actualizado", "ciudad": clima.ciudad, "temperatura": clima.temperatura})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
