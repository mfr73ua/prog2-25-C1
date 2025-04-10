import os
import tkinter as tk
from tkinter import messagebox
import webbrowser
import json
import requests

class Interfaz:
    """
    Clase principal de la interfaz gráfica para el gestor de rutas.

    Esta clase gestiona la autenticación del usuario, el menú principal,
    la creación de rutas manuales y automáticas, la consulta del clima,
    y la visualización de rutas propias y de amigos.

    Parameters
    ----------
    root : tkinter.Tk
        Ventana principal de la aplicación.
    """
    
    # URL base de la API
    API_URL = "https://ra55.pythonanywhere.com"

    def __init__(self, root):
        """Inicializa la interfaz y muestra la pantalla de login."""
        self.root = root
        self.root.title("Gestor de Rutas - Login")
        self.usuario = None
        self.datos_usuario = None

        self.pantalla_login()
        
    def hacer_peticion(self, endpoint, metodo="GET", datos=None, params=None):
        """
        Realiza una petición a la API.
        
        Parameters
        ----------
        endpoint : str
            Ruta del endpoint a consultar.
        metodo : str, optional
            Método HTTP a utilizar (GET, POST, etc.)
        datos : dict, optional
            Datos a enviar en formato JSON.
        params : dict, optional
            Parámetros de consulta.
            
        Returns
        -------
        dict
            Respuesta de la API en formato JSON.
        """
        url = f"{self.API_URL}{endpoint}"
        
        try:
            if metodo == "GET":
                respuesta = requests.get(url, params=params)
            elif metodo == "POST":
                respuesta = requests.post(url, json=datos)
            else:
                raise ValueError(f"Método HTTP no soportado: {metodo}")
                
            if respuesta.status_code >= 400:
                error_msg = respuesta.json().get("message", "Error desconocido")
                raise Exception(f"Error en la API (código {respuesta.status_code}): {error_msg}")
                
            return respuesta.json()
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")

    def pantalla_login(self):
        """Muestra la pantalla de inicio de sesión con campos de usuario y contraseña."""
        self.limpiar_pantalla()

        tk.Label(self.root, text="Iniciar Sesión", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Usuario:").pack()
        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack()

        tk.Label(self.root, text="Contraseña:").pack()
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack()

        tk.Button(self.root, text="Entrar", command=self.verificar_login).pack(pady=10)
        tk.Button(self.root, text="¿No tienes cuenta? Regístrate", command=self.abrir_ventana_registro).pack()

    def verificar_login(self):
        """
        Verifica las credenciales ingresadas por el usuario a través de la API.

        Si las credenciales son válidas, redirige a la pantalla principal.
        Si no, muestra un mensaje de error.
        """
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        try:
            datos = {
                "username": username,
                "password": password
            }
            respuesta = self.hacer_peticion("/api/usuarios/login", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                self.datos_usuario = respuesta["data"]
                self.usuario = self.datos_usuario["username"]
                messagebox.showinfo("Bienvenido", f"Hola {self.datos_usuario['nombre']}, ¡has iniciado sesión!")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_ventana_registro(self):
        """Muestra el formulario de registro para nuevos usuarios."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Registrar Usuario", font=("Arial", 16)).pack(pady=10)

        campos = ["Nombre", "Apellido", "Email", "Usuario", "Teléfono", "Fecha de nacimiento (YYYY-MM-DD)", "Ciudad", "Contraseña"]
        self.entries_registro = []

        for campo in campos:
            tk.Label(self.root, text=f"{campo}:").pack()
            entry = tk.Entry(self.root, show="*" if campo == "Contraseña" else None)
            entry.pack()
            self.entries_registro.append(entry)

        tk.Button(self.root, text="Registrar", command=self.registrar_usuario).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.pantalla_login).pack(pady=5)

    def registrar_usuario(self):
        """
        Registra al usuario con los datos ingresados en el formulario a través de la API.

        Si los campos están completos y el nombre de usuario no existe, se registra correctamente.
        """
        datos = [e.get().strip() for e in self.entries_registro]

        if not all(datos):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        nombre, apellido, email, username, telefono, fecha_nacimiento, ciudad, password = datos

        try:
            datos_registro = {
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "username": username,
                "telefono": telefono,
                "fecha_nacimiento": fecha_nacimiento,
                "ciudad": ciudad,
                "password": password
            }
            
            respuesta = self.hacer_peticion("/api/usuarios/registro", metodo="POST", datos=datos_registro)
            
            if respuesta["status"] == "success":
                messagebox.showinfo("Registro exitoso", "¡Te has registrado correctamente!")
                self.pantalla_login()
            else:
                messagebox.showerror("Error", respuesta.get("message", "Error desconocido durante el registro"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pantalla_principal(self):
        """Muestra el menú principal con botones para cada funcionalidad del sistema."""
        
        self.limpiar_pantalla()
        self.root.title(f"Bienvenido {self.datos_usuario['nombre']}")

        tk.Label(self.root, text=f"👋 Hola, {self.datos_usuario['nombre']}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="📍 Ver mis rutas", width=25, command=self.ver_rutas).pack(pady=5)
        tk.Button(self.root, text="👥 Ver mis amigos", width=25, command=self.ver_amigos).pack(pady=5)
        tk.Button(self.root, text="☁️ Consultar el clima", width=25, command=self.ver_clima).pack(pady=5)
        tk.Button(self.root, text="🛠 Crear ruta manual", width=25, command=self.pantalla_crear_ruta_manual).pack(pady=5)
        tk.Button(self.root, text="⚙️ Crear rutas automáticas", width=25, command=self.pantalla_crear_ruta_auto).pack(pady=5)
        tk.Button(self.root, text="🔍 Ver todas las rutas", width=25, command=self.ver_todas_las_rutas).pack(pady=5)
        tk.Button(self.root, text="🔒 Cerrar sesión", width=25, command=self.cerrar_sesion).pack(pady=15)

    def pantalla_crear_ruta_manual(self):
        """Muestra un formulario para crear rutas manualmente con campos de entrada."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Crear Ruta Manual", font=("Arial", 16)).pack(pady=10)

        labels = [
            "Origen:",
            "Puntos intermedios (separados por comas):",
            "Destino:",
            "Modo de transporte (walk/bike/drive):",
            "Nombre de la ruta (opcional):"
        ]
        self.entries_ruta_manual = []

        for texto in labels:
            tk.Label(self.root, text=texto).pack()
            entry = tk.Entry(self.root, width=50)
            entry.pack(pady=2)
            self.entries_ruta_manual.append(entry)

        tk.Button(self.root, text="Crear Ruta", command=self.crear_ruta_manual).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=5)

    def crear_ruta_manual(self):
        """Recoge los datos del formulario y crea una ruta manual a través de la API."""
        origen = self.entries_ruta_manual[0].get().strip()
        intermedios_texto = self.entries_ruta_manual[1].get().strip()
        intermedios = [p.strip() for p in intermedios_texto.split(",") if p.strip()] if intermedios_texto else []
        destino = self.entries_ruta_manual[2].get().strip()
        modo = self.entries_ruta_manual[3].get().strip().lower()
        nombre = self.entries_ruta_manual[4].get().strip() or None

        if not (origen and destino and modo):
            messagebox.showerror("Error", "Origen, destino y modo de transporte son obligatorios.")
            return

        try:
            datos = {
                "origen": origen,
                "puntos_intermedios": intermedios,
                "destino": destino,
                "modo": modo,
                "nombre": nombre,
                "username": self.usuario
            }
            
            respuesta = self.hacer_peticion("/api/rutas", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                archivos = respuesta["data"]["archivos"]
                mensaje = f"Ruta creada con éxito.\nPDF: {archivos['pdf']}\nGPX: {archivos['gpx']}\nHTML: {archivos['html']}"
                messagebox.showinfo("Ruta creada", mensaje)
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudo crear la ruta"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la ruta: {str(e)}")

    def pantalla_crear_ruta_auto(self):
        """Muestra un formulario para crear múltiples rutas automáticas."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Crear Rutas Automáticas", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Direcciones (separadas por comas):").pack()
        self.entry_direcciones_auto = tk.Entry(self.root, width=60)
        self.entry_direcciones_auto.pack(pady=5)

        tk.Label(self.root, text="Cantidad de rutas a generar:").pack()
        self.entry_cantidad_auto = tk.Entry(self.root, width=10)
        self.entry_cantidad_auto.insert(0, "5")
        self.entry_cantidad_auto.pack(pady=5)

        tk.Button(self.root, text="Generar Rutas", command=self.crear_rutas_automaticas).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=5)

    def crear_rutas_automaticas(self):
        """Genera rutas automáticas basadas en direcciones introducidas por el usuario."""
        direcciones_texto = self.entry_direcciones_auto.get().strip()
        direcciones = [d.strip() for d in direcciones_texto.split(",") if d.strip()]
        cantidad_texto = self.entry_cantidad_auto.get().strip()

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        if len(direcciones) < 2:
            messagebox.showerror("Error", "Introduce al menos dos direcciones válidas.")
            return

        try:
            datos = {
                "direcciones": direcciones,
                "cantidad": cantidad,
                "username": self.usuario
            }
            
            respuesta = self.hacer_peticion("/api/rutas/auto", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                resultados = respuesta["data"]
                if isinstance(resultados, list):
                    messagebox.showinfo("Rutas creadas", "\n".join(resultados))
                else:
                    messagebox.showinfo("Rutas creadas", "Las rutas se han creado correctamente.")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron generar las rutas"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar las rutas: {str(e)}")

    def ver_rutas(self):
        """Muestra todas las rutas asociadas al usuario con opciones para visualizar archivos."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Mis Rutas", font=("Arial", 16)).pack(pady=10)

        try:
            respuesta = self.hacer_peticion(f"/api/usuarios/{self.usuario}/rutas")
            
            if respuesta["status"] == "success":
                rutas = respuesta["data"]
                
                if rutas:
                    for ruta in rutas:
                        frame = tk.Frame(self.root)
                        frame.pack(pady=5)

                        tk.Label(frame, text=ruta, font=("Arial", 12)).pack(side="left", padx=10)

                        pdf_url = f"{self.API_URL}/static/{ruta}.pdf"
                        html_url = f"{self.API_URL}/static/rutas_{ruta}.html"

                        tk.Button(frame, text="📄 Ver PDF", command=lambda p=pdf_url: webbrowser.open(p)).pack(side="left", padx=5)
                        tk.Button(frame, text="🌐 Ver HTML", command=lambda h=html_url: webbrowser.open(h)).pack(side="left", padx=5)
                else:
                    tk.Label(self.root, text="No tienes rutas asignadas aún.").pack(pady=5)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener las rutas"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las rutas: {str(e)}")

        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def ver_amigos(self):
        """Muestra los amigos del usuario y las rutas en común con ellos."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Rutas en común con amigos", font=("Arial", 16)).pack(pady=10)

        try:
            respuesta = self.hacer_peticion("/api/usuarios/amigos")
            
            if respuesta["status"] == "success":
                amigos_data = respuesta["data"]
                usuario_amigos = amigos_data.get(self.usuario, {})
                
                if usuario_amigos:
                    for amigo, rutas_comunes in usuario_amigos.items():
                        tk.Label(self.root, text=f"Amigo: {amigo}", font=("Arial", 12, "bold")).pack(pady=5)
                        
                        if rutas_comunes:
                            for ruta in rutas_comunes:
                                frame = tk.Frame(self.root)
                                frame.pack(pady=5)
                                
                                tk.Label(frame, text=f"Ruta en común: {ruta}").pack(side="left", padx=10)
                                
                                pdf_url = f"{self.API_URL}/static/{ruta}.pdf"
                                html_url = f"{self.API_URL}/static/rutas_{ruta}.html"
                                
                                tk.Button(frame, text="📄 Ver PDF", command=lambda p=pdf_url: webbrowser.open(p)).pack(side="left", padx=5)
                                tk.Button(frame, text="🌐 Ver HTML", command=lambda h=html_url: webbrowser.open(h)).pack(side="left", padx=5)
                        else:
                            tk.Label(self.root, text="No tienen rutas en común.").pack(pady=5)
                else:
                    tk.Label(self.root, text="No tienes amigos registrados.").pack(pady=5)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener los amigos"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los amigos: {str(e)}")

        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def ver_clima(self):
        """Muestra un formulario para consultar el clima en una ciudad específica."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Ingresa la ciudad para consultar el clima", font=("Arial", 14)).pack(pady=10)

        self.entry_ciudad_clima = tk.Entry(self.root)
        self.entry_ciudad_clima.pack(pady=5)

        tk.Button(self.root, text="Consultar Clima", command=self.consultar_clima).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def consultar_clima(self):
        """Consulta el clima actual para la ciudad ingresada por el usuario a través de la API."""
        ciudad = self.entry_ciudad_clima.get().strip()

        if not ciudad:
            messagebox.showerror("Error", "Por favor, ingresa el nombre de una ciudad.")
            return

        try:
            respuesta = self.hacer_peticion("/api/clima", params={"ciudad": ciudad})
            
            if respuesta["status"] == "success":
                clima = respuesta["data"]
                clima_info = f"Ciudad: {clima.get('ciudad', 'N/A')}\n" \
                             f"Temperatura: {clima.get('temperatura', 'N/A')}°C\n" \
                             f"Humedad: {clima.get('humedad', 'N/A')}%\n" \
                             f"Descripción: {clima.get('descripcion', 'N/A')}\n" \
                             f"Viento: {clima.get('viento', 'N/A')} m/s\n" \
                             f"Fecha: {clima.get('fecha', 'N/A')}"
                messagebox.showinfo("Clima", clima_info)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudo obtener el clima"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el clima: {str(e)}")

    def ver_todas_las_rutas(self):
        """
        Muestra todas las rutas del sistema con filtros aplicables.

        Permite filtrar por dificultad, distancia, duración y modo de transporte.
        Las rutas se muestran en un panel scrollable con botones para ver PDF y HTML.
        """
        self.limpiar_pantalla()

        tk.Label(self.root, text="🧭 Filtrar Rutas del Sistema", font=("Arial", 16)).pack(pady=10)

        # Filtros
        filtro_frame = tk.Frame(self.root)
        filtro_frame.pack()

        tk.Label(filtro_frame, text="Dificultad (bajo, medio, alto):").grid(row=0, column=0, sticky="w")
        self.filtro_dificultad = tk.Entry(filtro_frame)
        self.filtro_dificultad.grid(row=0, column=1, padx=10)

        tk.Label(filtro_frame, text="Distancia máx (km):").grid(row=1, column=0, sticky="w")
        self.filtro_distancia = tk.Entry(filtro_frame)
        self.filtro_distancia.grid(row=1, column=1, padx=10)

        tk.Label(filtro_frame, text="Duración máx (h):").grid(row=2, column=0, sticky="w")
        self.filtro_duracion = tk.Entry(filtro_frame)
        self.filtro_duracion.grid(row=2, column=1, padx=10)

        tk.Label(filtro_frame, text="Medio de transporte (walk, bike, drive):").grid(row=3, column=0, sticky="w")
        self.filtro_modo = tk.Entry(filtro_frame)
        self.filtro_modo.grid(row=3, column=1, padx=10)

        # Botones de control
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Aplicar filtros", command=lambda: self.aplicar_filtros_rutas()).pack(side="left", padx=10)
        tk.Button(control_frame, text="Volver", command=self.pantalla_principal).pack(side="left", padx=10)

        # Scroll
        canvas = tk.Canvas(self.root, height=350)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas)

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cargar todas las rutas al inicio
        self.aplicar_filtros_rutas()

    def aplicar_filtros_rutas(self):
        """
        Aplica los filtros introducidos por el usuario a las rutas a través de la API.

        Usa dificultad, distancia, duración y modo de transporte como filtros.
        """
        dificultad = self.filtro_dificultad.get().strip().lower()
        distancia = self.filtro_distancia.get().strip()
        duracion = self.filtro_duracion.get().strip()
        modo = self.filtro_modo.get().strip().lower()

        # Limpiar el panel de rutas
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        try:
            params = {}
            if dificultad:
                params["dificultad"] = dificultad
            if distancia:
                params["max_km"] = float(distancia)
            if duracion:
                params["max_horas"] = float(duracion)
            if modo:
                params["modo_transporte"] = modo
                
            respuesta = self.hacer_peticion("/api/rutas/filtrar", params=params)
            
            if respuesta["status"] == "success":
                self.mostrar_rutas(respuesta["data"])
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron filtrar las rutas"))
        except ValueError as e:
            messagebox.showerror("Error de formato", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las rutas: {str(e)}")

    def mostrar_rutas(self, rutas):
        """
        Muestra visualmente las rutas en el panel scrollable.

        Parameters
        ----------
        rutas : list
            Lista de rutas en formato diccionario.
        """
        if not rutas:
            tk.Label(self.scroll_frame, text="No se encontraron rutas con los filtros aplicados.").pack(pady=10)
            return

        for r in rutas:
            frame = tk.Frame(self.scroll_frame, bd=1, relief="solid", padx=5, pady=5)
            frame.pack(padx=10, pady=5, fill="x")

            texto = f"📍 {r.get('nombre', 'Sin nombre')} | {r.get('distancia', 'N/A')} | {r.get('duracion', 'N/A')} | Dificultad: {r.get('dificultad', 'N/A')}\n{r.get('origen', 'N/A')} → {r.get('destino', 'N/A')} ({r.get('modo_transporte', 'N/A')})"
            tk.Label(frame, text=texto, font=("Arial", 10), justify="left", anchor="w").pack(anchor="w")

            # Botones de exportación
            nombre_archivo = r.get("nombre", "")
            btn_frame = tk.Frame(frame)
            btn_frame.pack(anchor="e", pady=5)

            pdf_url = f"{self.API_URL}/static/{nombre_archivo}.pdf"
            html_url = f"{self.API_URL}/static/rutas_{nombre_archivo}.html"

            tk.Button(btn_frame, text="📄 Ver PDF", command=lambda p=pdf_url: webbrowser.open(p)).pack(side="left", padx=5)
            tk.Button(btn_frame, text="🌐 Ver HTML", command=lambda h=html_url: webbrowser.open(h)).pack(side="left", padx=5)

    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual y vuelve al login."""
        self.usuario = None
        self.datos_usuario = None
        self.root.title("Gestor de Rutas - Login")
        self.pantalla_login()

    def limpiar_pantalla(self):
        """Elimina todos los elementos visibles de la ventana actual."""
        for widget in self.root.winfo_children():
            widget.destroy()
