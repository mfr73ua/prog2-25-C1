from flask import request, jsonify
from usuario import Usuario
from app_instance import app
import os
import json

# Registro de un nuevo usuario
@app.route("/api/registro", methods=["POST"])
def registro():
    """
    Registra un nuevo usuario en el sistema.

    Recibe los datos del usuario a través de una solicitud POST, y si el nombre de usuario 
    no está registrado previamente, crea un nuevo usuario. Si el registro es exitoso, 
    devuelve un mensaje de éxito, en caso contrario, devuelve un error indicando que el 
    nombre de usuario ya existe.

    Parameters
    ----------
    None

    Returns
    -------
    Response
        Retorna un mensaje en formato JSON indicando el éxito o el error en el registro.
    """
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
    """
    Inicia sesión de un usuario.

    Recibe las credenciales del usuario (nombre de usuario y contraseña) y verifica si 
    son correctas. Si las credenciales son válidas, devuelve un mensaje de inicio de sesión 
    exitoso, junto con el nombre del usuario. Si las credenciales son incorrectas, 
    devuelve un mensaje de error.

    Parameters
    ----------
    None

    Returns
    -------
    Response
        Retorna un mensaje en formato JSON con el resultado del inicio de sesión.
    """
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if usuario:
        return jsonify({"mensaje": "Login correcto", "usuario": usuario.username})
    return jsonify({"error": "Credenciales incorrectas"}), 401

# Obtener rutas de un usuario
@app.route("/api/usuarios/<username>/rutas", methods=["GET"])
def obtener_rutas_usuario(username):
    """
    Obtiene las rutas de un usuario específico.

    Este endpoint recibe el nombre de usuario y devuelve todas las rutas asociadas a ese usuario. 
    Si el usuario no existe, retorna un error 404.

    Parameters
    ----------
    username : str
        El nombre de usuario para obtener las rutas.

    Returns
    -------
    Response
        Retorna un JSON con las rutas del usuario, o un error 404 si el usuario no existe.
    """
    usuarios = Usuario.cargar_usuarios()
    for u in usuarios:
        if u["username"] == username:
            return jsonify({"rutas": u["rutas"]})
    return jsonify({"error": "Usuario no encontrado"}), 404

# Obtener rutas comunes entre dos usuarios
@app.route("/api/usuarios/<username1>/rutas_comunes/<username2>", methods=["GET"])
def rutas_comunes(username1, username2):
    """
    Obtiene las rutas comunes entre dos usuarios.

    Este endpoint recibe dos nombres de usuario y devuelve las rutas que ambos comparten. 
    Si alguno de los usuarios no existe, retorna un error 404.

    Parameters
    ----------
    username1 : str
        El nombre de usuario del primer usuario.
    username2 : str
        El nombre de usuario del segundo usuario.

    Returns
    -------
    Response
        Retorna un JSON con las rutas comunes entre los dos usuarios.
    """
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

# Obtener amigos con los que se comparten rutas
@app.route("/api/usuarios/<username>/amigos_comunes", methods=["GET"])
def amigos_con_rutas_comunes(username):
    """
    Obtiene los amigos del usuario con los que comparte rutas.

    Este endpoint recibe un nombre de usuario y retorna los amigos con los que comparte al menos 
    una ruta. Si el usuario no existe, retorna un error 404. Para cada amigo, muestra las rutas comunes.

    Parameters
    ----------
    username : str
        El nombre de usuario para obtener los amigos con rutas comunes.

    Returns
    -------
    Response
        Retorna un JSON con los amigos del usuario y las rutas comunes que comparten.
    """
    usuarios = Usuario.cargar_usuarios()
    usuario_principal = None

    for u in usuarios:
        if u["username"] == username:
            usuario_principal = u
            break

    if not usuario_principal:
        return jsonify({"error": "Usuario no encontrado"}), 404

    rutas_usuario = set(usuario_principal.get("rutas", []))
    amigos_con_rutas = {}

    for u in usuarios:
        if u["username"] == username:
            continue  # No compararse consigo mismo
        rutas_otro = set(u.get("rutas", []))
        comunes = rutas_usuario & rutas_otro
        if comunes:
            amigos_con_rutas[u["username"]] = list(comunes)

    return jsonify({"amigos": amigos_con_rutas})

# Eliminar una ruta específica de un usuario
@app.route("/api/usuarios/<username>/rutas/<nombre_ruta>", methods=["DELETE"])
def eliminar_ruta_usuario(username, nombre_ruta):
    """
    Elimina una ruta del listado de rutas de un usuario específico.

    Este endpoint permite a un usuario borrar una ruta que ya no desee conservar.
    También elimina los archivos PDF, GPX y HTML asociados a la ruta si existen.

    Parameters
    ----------
    username : str
        Nombre de usuario que quiere eliminar la ruta.
    nombre_ruta : str
        Nombre de la ruta a eliminar.

    Returns
    -------
    Response
        Un mensaje de éxito si se elimina correctamente, o un error si no se encuentra.
    """

    usuarios = Usuario.cargar_usuarios()
    ruta_borrada = False

    for u in usuarios:
        if u["username"] == username:
            if nombre_ruta in u.get("rutas", []):
                u["rutas"].remove(nombre_ruta)
                ruta_borrada = True
                break

    if not ruta_borrada:
        return jsonify({"error": "Ruta no encontrada o usuario inexistente"}), 404

    Usuario.guardar_usuarios(usuarios)

    # Eliminar archivos asociados si existen
    for ext in ["pdf", "html", "gpx"]:
        path = os.path.join("static", f"{nombre_ruta if ext != 'html' else f'rutas_{nombre_ruta}'}.{ext}")
        if os.path.exists(path):
            os.remove(path)

    return jsonify({"mensaje": f"Ruta '{nombre_ruta}' eliminada exitosamente"})

# Actualizar datos personales de un usuario (nombre, email, ciudad, etc.)
@app.route("/api/usuarios/<username>", methods=["PUT"])
def actualizar_usuario(username):
    """
    Permite actualizar los datos personales de un usuario existente.

    Solo puede actualizar los campos: nombre, apellido, email, teléfono y ciudad.

    Parameters
    ----------
    username : str
        Nombre del usuario a actualizar.

    Returns
    -------
    Response
        Un mensaje de éxito o un error si el usuario no existe.
    """
    data = request.json
    usuarios = Usuario.cargar_usuarios()

    for u in usuarios:
        if u["username"] == username:
            for key in ["nombre", "apellido", "email", "telefono", "ciudad"]:
                if key in data:
                    u[key] = data[key]
            Usuario.guardar_usuarios(usuarios)
            return jsonify({"mensaje": "Datos actualizados correctamente"})

    return jsonify({"error": "Usuario no encontrado"}), 404

# Buscar usuarios por coincidencia parcial en nombre o apellido
@app.route("/api/usuarios/buscar", methods=["GET"])
def buscar_usuarios():
    """
    Busca usuarios por coincidencia parcial en nombre o apellido.

    Este endpoint es útil para añadir funcionalidades sociales, como sugerencias de amigos.

    Query Parameters
    ----------------
    nombre : str
        Cadena parcial a buscar en nombre o apellido.

    Returns
    -------
    Response
        Una lista de usernames que coinciden con la búsqueda.
    """
    nombre = request.args.get("nombre", "").lower()
    usuarios = Usuario.cargar_usuarios()
    resultados = [u["username"] for u in usuarios if nombre in u["username"].lower()]
    return jsonify({"resultados": resultados})

# Elimina totalmente tras el login al usuario de la base de datos
@app.route("/api/usuarios/<username>", methods=["DELETE"])
def eliminar_usuario(username):
    """
    Elimina un usuario del sistema.

    Busca al usuario en la base de datos por su nombre de usuario (`username`)
    y lo elimina si existe. La eliminación se realiza actualizando el archivo
    JSON con el resto de usuarios, sin afectar a rutas ni a otros usuarios.

    Parameters
    ----------
    username : str
        Nombre de usuario del usuario que se desea eliminar.

    Returns
    -------
    flask.Response
        Un mensaje JSON indicando si la eliminación fue exitosa o si el usuario no existe.
    """
    usuarios = Usuario.cargar_usuarios()

    # Filtra todos los usuarios excepto el que se quiere eliminar
    nuevos_usuarios = [u for u in usuarios if u["username"] != username]

    if len(usuarios) == len(nuevos_usuarios):
        return jsonify({"error": "Usuario no encontrado"}), 404

    Usuario.guardar_usuarios(nuevos_usuarios)
    print(f"✅ Usuario {username} eliminado correctamente")
    return jsonify({"mensaje": f"Usuario {username} eliminado correctamente"}), 200
