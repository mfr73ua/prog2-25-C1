# api/usuarios.py

from flask import request, jsonify
from usuario import Usuario
from app_instance import app

# Registro de un nuevo usuario
@app.route("/api/registro", methods=["POST"])
def registro():
    data = request.json
    success = Usuario.registrar_usuario(
        data["nombre"], data["apellido"], data["email"], data["username"],
        data["telefono"], data["fecha_nacimiento"], data["ciudad"], data["password"]
    )
    if success:
        return jsonify({"mensaje": "Usuario registrado correctamente"})
    return jsonify({"error": "El nombre de usuario ya existe"}), 400

# Inicio de sesión
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if usuario:
        return jsonify({"mensaje": "Login correcto", "usuario": usuario.username})
    return jsonify({"error": "Credenciales incorrectas"}), 401

# Obtener rutas de un usuario
@app.route("/api/usuarios/<username>/rutas", methods=["GET"])
def obtener_rutas_usuario(username):
    usuarios = Usuario.cargar_usuarios()
    for u in usuarios:
        if u["username"] == username:
            return jsonify({"rutas": u["rutas"]})
    return jsonify({"error": "Usuario no encontrado"}), 404

# Actualizar datos personales del usuario
@app.route("/api/usuarios/<username>", methods=["PUT"])
def actualizar_usuario(username):
    data = request.json
    usuarios = Usuario.cargar_usuarios()

    for u in usuarios:
        if u["username"] == username:
            u["nombre"] = data.get("nombre", u["nombre"])
            u["apellido"] = data.get("apellido", u["apellido"])
            u["email"] = data.get("email", u["email"])
            u["telefono"] = data.get("telefono", u["telefono"])
            u["fecha_nacimiento"] = data.get("fecha_nacimiento", u["fecha_nacimiento"])
            u["ciudad"] = data.get("ciudad", u["ciudad"])
            Usuario.actualizar_usuarios(usuarios)
            return jsonify({"mensaje": "Usuario actualizado correctamente"})

    return jsonify({"error": "Usuario no encontrado"}), 404

# Obtener rutas comunes entre dos usuarios
@app.route("/api/usuarios/<username1>/rutas_comunes/<username2>", methods=["GET"])
def rutas_comunes(username1, username2):
    usuarios = Usuario.cargar_usuarios()
    usuario1 = None
    usuario2 = None

    for u in usuarios:
        if u["username"] == username1:
            usuario1 = u
        if u["username"] == username2:
            usuario2 = u

    if not usuario1 or not usuario2:
        return jsonify({"error": "Uno de los usuarios no existe"}), 404

    rutas_comunes = list(set(usuario1["rutas"]).intersection(usuario2["rutas"]))
    return jsonify({"rutas_comunes": rutas_comunes})

# Eliminar un usuario y sus rutas asociadas
@app.route("/api/usuarios/<username>", methods=["DELETE"])
def eliminar_usuario(username):
    import os
    usuarios = Usuario.cargar_usuarios()
    for i, u in enumerate(usuarios):
        if u["username"] == username:
            for ruta in u["rutas"]:
                ruta_path = os.path.join("rutas", f"{ruta}.json")
                if os.path.exists(ruta_path):
                    os.remove(ruta_path)
                pdf_path = os.path.join("static", f"{ruta}.pdf")
                html_path = os.path.join("static", f"rutas_{ruta}.html")
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                if os.path.exists(html_path):
                    os.remove(html_path)

            usuarios.pop(i)
            Usuario.actualizar_usuarios(usuarios)
            return jsonify({"mensaje": "Usuario y rutas eliminados correctamente"})

    return jsonify({"error": "Usuario no encontrado"}), 404
