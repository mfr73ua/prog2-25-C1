from interfaz import Interfaz
import tkinter as tk

if __name__ == '__main__':
    """
    Función principal que inicializa la interfaz gráfica y arranca la aplicación de gestión de rutas.

    Esta función crea una ventana de Tkinter, inicializa la clase `Interfaz`, y entra en el bucle principal de eventos de Tkinter.

    """
    root = tk.Tk()  # Crea una instancia de la ventana principal de Tkinter.
    app = Interfaz(root)  # Inicializa la clase Interfaz con la ventana principal.
    root.mainloop()  # Ejecuta el bucle principal de eventos de Tkinter, lo que mantiene la ventana abierta y en espera de interacciones.
