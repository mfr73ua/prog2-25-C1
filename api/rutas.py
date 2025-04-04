# api/rutas.py
from app_instance import app
from flask import request, jsonify, send_from_directory
from ruta_manual import RutaManual
from ruta_auto import RutaAuto
from usuario import Usuario
from ruta import Ruta
import os
import json

# Crear ruta manual
@app.route("/api/ruta_manual", methods=["POST"])
def crear_manual():
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 403
    try:
        pdf, gpx, html = RutaManual.crear_ruta_desde_datos(
            data["origen"], data["intermedios"], data["destino"],
            data["modo"], data.get("nombre"), usuario
        )
        return jsonify({"mensaje": "Ruta creada", "pdf": pdf, "gpx": gpx, "html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Crear rutas automáticas
@app.route("/api/ruta_auto", methods=["POST"])
def crear_auto():
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 403
    try:
        generador = RutaAuto()
        resultado = generador.generar_rutas_desde_direcciones(data["direcciones"], int(data["cantidad"]))
        return jsonify({"mensaje": "Rutas automáticas generadas", "rutas": resultado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Listar rutas con filtros
@app.route("/api/rutas", methods=["GET"])
def listar_rutas():
    rutas = Ruta.listar_rutas()
    dificultad = request.args.get("dificultad")
    modo = request.args.get("modo")
    distancia_max = request.args.get("distancia_max", type=float)
    duracion_max = request.args.get("duracion_max", type=float)

    if dificultad:
        rutas = [r for r in rutas if r.get("dificultad", "").lower() == dificultad.lower()]
    if modo:
        rutas = [r for r in rutas if r.get("modo_transporte", "").lower() == modo.lower()]
    if distancia_max:
        rutas = [r for r in rutas if float(str(r.get("distancia", "0")).split()[0]) <= distancia_max]
    if duracion_max:
        rutas = [r for r in rutas if float(str(r.get("duracion", "0")).split()[0]) <= duracion_max]

    return jsonify({"rutas": rutas})

# Descargar PDF de ruta
@app.route("/api/rutas/<nombre>/pdf", methods=["GET"])
def descargar_pdf(nombre):
    path = f"{nombre}.pdf"
    return send_from_directory("static", path, as_attachment=True)

# Descargar HTML de ruta
@app.route("/api/rutas/<nombre>/html", methods=["GET"])
def descargar_html(nombre):
    path = f"rutas_{nombre}.html"
    return send_from_directory("static", path, as_attachment=True)

# Actualizar datos de una ruta
@app.route("/api/rutas/<nombre>", methods=["PUT"])
def actualizar_ruta(nombre):
    data = request.json
    ruta_path = os.path.join("rutas", f"{nombre}.json")
    if not os.path.exists(ruta_path):
        return jsonify({"error": "Ruta no encontrada"}), 404

    try:
        with open(ruta_path, "r+", encoding="utf-8") as f:
            ruta = json.load(f)
            ruta["origen"] = data.get("origen", ruta["origen"])
            ruta["intermedios"] = data.get("intermedios", ruta["intermedios"])
            ruta["destino"] = data.get("destino", ruta["destino"])
            ruta["modo_transporte"] = data.get("modo", ruta["modo_transporte"])
            ruta["dificultad"] = data.get("dificultad", ruta["dificultad"])
            ruta["duracion"] = data.get("duracion", ruta["duracion"])
            f.seek(0)
            json.dump(ruta, f, ensure_ascii=False, indent=4)
            f.truncate()
        return jsonify({"mensaje": "Ruta actualizada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar una ruta
@app.route("/api/rutas/<nombre>", methods=["DELETE"])
def eliminar_ruta(nombre):
    ruta_path = os.path.join("rutas", f"{nombre}.json")
    if not os.path.exists(ruta_path):
        return jsonify({"error": "Ruta no encontrada"}), 404

    try:
        os.remove(ruta_path)
        pdf_path = os.path.join("static", f"{nombre}.pdf")
        html_path = os.path.join("static", f"rutas_{nombre}.html")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(html_path):
            os.remove(html_path)

        usuarios = Usuario.cargar_usuarios()
        for usuario in usuarios:
            if nombre in usuario.get("rutas", []):
                usuario["rutas"].remove(nombre)
                Usuario.actualizar_usuarios(usuarios)

        return jsonify({"mensaje": "Ruta eliminada correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener detalles de una ruta
@app.route("/api/rutas/<nombre>", methods=["GET"])
def obtener_detalles_ruta(nombre):
    ruta_path = os.path.join("rutas", f"{nombre}.json")
    if not os.path.exists(ruta_path):
        return jsonify({"error": "Ruta no encontrada"}), 404

    try:
        with open(ruta_path, "r", encoding="utf-8") as f:
            ruta = json.load(f)
        return jsonify(ruta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Buscar rutas por nombre
@app.route("/api/rutas/buscar", methods=["GET"])
def buscar_rutas():
    nombre = request.args.get("nombre", "").lower()
    rutas = Ruta.listar_rutas()
    rutas_encontradas = [r for r in rutas if nombre in r["nombre"].lower()]
    return jsonify({"rutas_encontradas": rutas_encontradas})
