import os
import tkinter as tk
from tkinter import messagebox
import webbrowser
import json

from servicio_clima import GestorClima, ServicioOpenWeatherMap
from usuario import Usuario
from ruta_manual import RutaManual
from ruta_auto import RutaAuto
from gestor_rutas import GestorRutas

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

    def __init__(self, root):
        """Inicializa la interfaz, el servicio de clima y muestra la pantalla de login."""
        self.root = root
        self.root.title("Gestor de Rutas - Login")
        self.usuario = None

        self.servicio_clima = ServicioOpenWeatherMap(clave_api="5ead714f2ad83f23daf51c47124fd500")
        self.gestor_clima = GestorClima(self.servicio_clima)

        self.pantalla_login()

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
        Verifica las credenciales ingresadas por el usuario.

        Si las credenciales son válidas, redirige a la pantalla principal.
        Si no, muestra un mensaje de error.
        """
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        usuario = Usuario.iniciar_sesion(username, password)
        if usuario:
            self.usuario = usuario
            messagebox.showinfo("Bienvenido", f"Hola {usuario.nombre}, ¡has iniciado sesión!")
            self.pantalla_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

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

    def registrar_usuario(self):
        """
        Registra al usuario con los datos ingresados en el formulario.

        Si los campos están completos y el nombre de usuario no existe, se registra correctamente.
        """
        datos = [e.get().strip() for e in self.entries_registro]

        if not all(datos):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        nombre, apellido, email, username, telefono, fecha_nacimiento, ciudad, password = datos

        if Usuario.registrar_usuario(nombre, apellido, email, username, telefono, fecha_nacimiento, ciudad, password):
            messagebox.showinfo("Registro exitoso", "¡Te has registrado correctamente!")
            self.pantalla_login()
        else:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")

    def pantalla_principal(self):
        """Muestra el menú principal con botones para cada funcionalidad del sistema."""
        
        self.limpiar_pantalla()
        self.root.title(f"Bienvenido {self.usuario.nombre}")

        tk.Label(self.root, text=f"👋 Hola, {self.usuario.nombre}", font=("Arial", 14)).pack(pady=10)
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
            "Modo de transporte (caminar/bicicleta/coche):",
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
        """Recoge los datos del formulario y crea una ruta manual para el usuario."""
        origen = self.entries_ruta_manual[0].get().strip()
        intermedios = self.entries_ruta_manual[1].get().strip().split(",") if self.entries_ruta_manual[1].get().strip() else []
        destino = self.entries_ruta_manual[2].get().strip()
        modo = self.entries_ruta_manual[3].get().strip().lower()
        nombre = self.entries_ruta_manual[4].get().strip() or None

        if not (origen and destino and modo):
            messagebox.showerror("Error", "Origen, destino y modo de transporte son obligatorios.")
            return

        try:
            pdf, gpx, html = RutaManual.crear_ruta_desde_datos(origen, intermedios, destino, modo, nombre, self.usuario)
            messagebox.showinfo("Ruta creada", f"Ruta creada con éxito.\nPDF: {pdf}\nGPX: {gpx}\nHTML: {html}")
            self.pantalla_principal()
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
        direcciones = self.entry_direcciones_auto.get().strip().split(",")
        cantidad_texto = self.entry_cantidad_auto.get().strip()

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        direcciones = [d.strip() for d in direcciones if d.strip()]

        if len(direcciones) < 2:
            messagebox.showerror("Error", "Introduce al menos dos direcciones válidas.")
            return

        try:
            generador = RutaAuto()
            resultados = generador.generar_rutas_desde_direcciones(direcciones, cantidad)

            for linea in resultados:
                nombre = linea.split("'")[1]
                if nombre not in self.usuario.rutas:
                    self.usuario.rutas.append(nombre)

            Usuario.actualizar_rutas_usuario(self.usuario)
            messagebox.showinfo("Rutas creadas", "\n".join(resultados))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar las rutas: {str(e)}")

    def ver_rutas(self):
        """Muestra todas las rutas asociadas al usuario con opciones para visualizar archivos."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Mis Rutas", font=("Arial", 16)).pack(pady=10)

        if self.usuario.rutas:
            for ruta in self.usuario.rutas:
                frame = tk.Frame(self.root)
                frame.pack(pady=5)

                tk.Label(frame, text=ruta, font=("Arial", 12)).pack(side="left", padx=10)

                pdf_path = f"static/{ruta}.pdf"
                html_path = f"static/rutas_{ruta}.html"

                if os.path.exists(pdf_path):
                    tk.Button(frame, text="📄 Ver PDF", command=lambda p=pdf_path: self.abrir_archivo(p)).pack(side="left", padx=5)

                if os.path.exists(html_path):
                    tk.Button(frame, text="🌐 Ver HTML", command=lambda h=html_path: self.abrir_archivo(h)).pack(side="left", padx=5)
        else:
            tk.Label(self.root, text="No tienes rutas asignadas aún.").pack(pady=5)

        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def ver_amigos(self):
        """Muestra los amigos del usuario y las rutas en común con ellos."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Rutas en común con amigos", font=("Arial", 16)).pack(pady=10)

        for amigo in self.usuario.amigos:
            tk.Label(self.root, text=f"Amigo: {amigo}").pack(pady=5)

            rutas_comunes = set(self.usuario.rutas).intersection(set(self.get_rutas_amigo(amigo)))
            for ruta in rutas_comunes:
                tk.Label(self.root, text=f"Ruta en común: {ruta}").pack(pady=5)

                ruta_path = f"rutas/{ruta}.json"
                if os.path.exists(ruta_path):
                    with open(ruta_path, "r") as f:
                        ruta_data = json.load(f)
                        origen = ruta_data.get("origen", "Desconocido")
                        destino = ruta_data.get("destino", "Desconocido")
                        tk.Label(self.root, text=f"Origen: {origen} → Destino: {destino}", font=("Arial", 12)).pack(pady=5)

                pdf_path = f"static/{ruta}.pdf"
                html_path = f"static/rutas_{ruta}.html"

                if os.path.exists(pdf_path):
                    tk.Button(self.root, text=f"Ver PDF de {ruta}", command=lambda r=pdf_path: self.abrir_archivo(r)).pack(pady=5)
                if os.path.exists(html_path):
                    tk.Button(self.root, text=f"Ver HTML de {ruta}", command=lambda r=html_path: self.abrir_archivo(r)).pack(pady=5)

        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def get_rutas_amigo(self, amigo_username):
        """Devuelve las rutas asociadas a un amigo dado su nombre de usuario."""
        for usuario in Usuario.cargar_usuarios():
            if usuario['username'] == amigo_username:
                return usuario['rutas']
        return []

    def ver_clima(self):
        """Muestra un formulario para consultar el clima en una ciudad específica."""
        self.limpiar_pantalla()
        tk.Label(self.root, text="Ingresa la ciudad para consultar el clima", font=("Arial", 14)).pack(pady=10)

        self.entry_ciudad_clima = tk.Entry(self.root)
        self.entry_ciudad_clima.pack(pady=5)

        tk.Button(self.root, text="Consultar Clima", command=self.consultar_clima).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.pantalla_principal).pack(pady=10)

    def consultar_clima(self):
        """Consulta el clima actual para la ciudad ingresada por el usuario."""
        ciudad = self.entry_ciudad_clima.get().strip()

        if not ciudad:
            messagebox.showerror("Error", "Por favor, ingresa el nombre de una ciudad.")
            return

        try:
            clima = self.gestor_clima.consultar_clima(ciudad)
            clima_info = f"Ciudad: {clima.ciudad}\nTemperatura: {clima.temperatura}°C\nHumedad: {clima.humedad}%\n" \
                         f"Descripción: {clima.descripcion}\nViento: {clima.viento} m/s\nFecha: {clima.fecha.strftime('%Y-%m-%d %H:%M:%S')}"
            messagebox.showinfo("Clima", clima_info)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el clima. {str(e)}")

    def ver_todas_las_rutas(self):
        """
        Muestra todas las rutas del sistema con filtros aplicables.

        Permite filtrar por dificultad, distancia, duración y modo de transporte.
        Las rutas se muestran en un panel scrollable con botones para ver PDF y HTML.
        """

        self.limpiar_pantalla()
        gestor = GestorRutas()

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
        tk.Button(control_frame, text="Aplicar filtros", command=lambda: aplicar_filtros()).pack(side="left", padx=10)
        tk.Button(control_frame, text="Volver", command=self.pantalla_principal).pack(side="left", padx=10)

        # Scroll
        canvas = tk.Canvas(self.root, height=350)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def extraer_numero(valor: str) -> float:
            """
            Extrae el primer número flotante de una cadena.

            Parameters
            ----------
            valor : str
                Cadena que contiene un número al inicio.

            Returns
            -------
            float
                Número extraído o infinito si no es válido.
            """

            try:
                return float(valor.split()[0])
            except:
                return float('inf')

        def mostrar_rutas(rutas):
            """
            Muestra visualmente las rutas en el panel scrollable.

            Parameters
            ----------
            rutas : list
                Lista de rutas en formato diccionario.
            """

            for widget in scroll_frame.winfo_children():
                widget.destroy()

            for r in rutas:
                frame = tk.Frame(scroll_frame, bd=1, relief="solid", padx=5, pady=5)
                frame.pack(padx=10, pady=5, fill="x")

                texto = f"📍 {r['nombre']} | {r['distancia']} | {r['duracion']} | Dificultad: {r['dificultad']}\n{r['origen']} → {r['destino']} ({r['modo_transporte']})"
                tk.Label(frame, text=texto, font=("Arial", 10), justify="left", anchor="w").pack(anchor="w")

                # Botones de exportación
                nombre_archivo = r["nombre"]
                pdf_path = os.path.join("static", f"{nombre_archivo}.pdf")
                html_path = os.path.join("static", f"rutas_{nombre_archivo}.html")

                btn_frame = tk.Frame(frame)
                btn_frame.pack(anchor="e", pady=5)

                if os.path.exists(pdf_path):
                    tk.Button(btn_frame, text="📄 Ver PDF", command=lambda p=pdf_path: self.abrir_archivo(p)).pack(side="left", padx=5)
                if os.path.exists(html_path):
                    tk.Button(btn_frame, text="🌐 Ver HTML", command=lambda h=html_path: self.abrir_archivo(h)).pack(side="left", padx=5)

        def aplicar_filtros():
            """
            Aplica los filtros introducidos por el usuario a las rutas.

            Usa dificultad, distancia, duración y modo de transporte como filtros.
            """

            dificultad = self.filtro_dificultad.get().strip().lower()
            distancia = self.filtro_distancia.get().strip()
            duracion = self.filtro_duracion.get().strip()
            modo = self.filtro_modo.get().strip().lower()

            try:
                max_km = float(distancia) if distancia else float('inf')
            except:
                max_km = float('inf')
            try:
                max_h = float(duracion) if duracion else float('inf')
            except:
                max_h = float('inf')

            try:
                rutas_filtradas = gestor.lista_rutas()
                if modo:
                    rutas_filtradas = gestor.filtrar_por_transporte(modo)
                if dificultad:
                    rutas_filtradas = [r for r in rutas_filtradas if r["dificultad"].lower() == dificultad]
                rutas_filtradas = [
                    r for r in rutas_filtradas
                    if extraer_numero(r["distancia"]) <= max_km and extraer_numero(r["duracion"]) <= max_h
                ]
                mostrar_rutas(rutas_filtradas)
            except ValueError as e:
                messagebox.showerror("Modo de transporte no válido", str(e))

        # Mostrar todas al inicio
        mostrar_rutas(gestor.lista_rutas())


    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual y vuelve al login."""
        self.usuario = None
        self.root.title("Gestor de Rutas - Login")
        self.pantalla_login()

    def abrir_archivo(self, archivo_path):
        """Abre un archivo local (PDF o HTML) en el navegador predeterminado."""
        try:
            webbrowser.open(archivo_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo. {str(e)}")

    def limpiar_pantalla(self):
        """Elimina todos los elementos visibles de la ventana actual."""
        for widget in self.root.winfo_children():
            widget.destroy()

