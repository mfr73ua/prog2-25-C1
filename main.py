import os
import tkinter as tk
from interfaz import Interfaz
import sqlite3
from PIL import Image, ImageTk
import sys





def main():
    """Función principal que inicia la aplicación."""
  
    # Iniciar la interfaz gráfica principal
    root = tk.Tk()
    
    # Ocultar la ventana principal temporalmente para evitar que aparezca antes de lo necesario
    root.withdraw()
    
    
    # Configurar la ventana principal
    root.deiconify()
    
    # Mostrar la ventana principal con el tamaño ajustado
    root.geometry("800x800")
    app = Interfaz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    