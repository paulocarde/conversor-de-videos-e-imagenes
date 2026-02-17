import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import os
import threading
import subprocess

class AppConversora(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MyTube Multi-Converter Pro")
        self.geometry("700x650")
        ctk.set_appearance_mode("dark")
        
        self.archivos_rutas = [] # Lista para múltiples archivos
        self.carpeta_destino = ""

        # UI - Título
        self.label = ctk.CTkLabel(self, text="Conversor por Lotes (Batch)", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        # SECCIÓN DE SELECCIÓN
        self.f_sel = ctk.CTkFrame(self)
        self.f_sel.pack(pady=10, padx=20, fill="x")

        self.btn_sel = ctk.CTkButton(self.f_sel, text="1. Seleccionar Archivos", command=self.seleccionar_archivos)
        self.btn_sel.grid(row=0, column=0, padx=10, pady=10)

        self.btn_dest = ctk.CTkButton(self.f_sel, text="2. Carpeta de Destino", command=self.seleccionar_destino, fg_color="#e67e22")
        self.btn_dest.grid(row=0, column=1, padx=10, pady=10)

        self.lbl_info = ctk.CTkLabel(self, text="Archivos: 0 | Destino: Original", text_color="gray")
        self.lbl_info.pack(pady=5)

        # Barra de Progreso
        self.progress = ctk.CTkProgressBar(self, width=500)
        self.progress.set(0)
        self.progress.pack(pady=20)

        # CONTENEDORES DE OPCIONES
        self.setup_ui_options()

        self.status = ctk.CTkLabel(self, text="Listo para empezar", font=("Roboto", 14))
        self.status.pack(pady=20)

    def setup_ui_options(self):
        # Frame Video
        self.f_video = ctk.CTkFrame(self)
        self.f_video.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.f_video, text="VIDEO/AUDIO:").pack(side="left", padx=10)
        self.menu_video = ctk.CTkOptionMenu(self.f_video, values=["mp4", "mkv", "mp3", "wav"])
        self.menu_video.pack(side="left", padx=10, pady=10)
        self.btn_v = ctk.CTkButton(self.f_video, text="Convertir Todo", command=lambda: self.iniciar_hilo("video"), state="disabled")
        self.btn_v.pack(side="right", padx=10)

        # Frame Imagen
        self.f_img = ctk.CTkFrame(self)
        self.f_img.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.f_img, text="IMAGENES:").pack(side="left", padx=10)
        self.menu_img = ctk.CTkOptionMenu(self.f_img, values=["webp", "png", "jpg"], fg_color="#2ecc71", button_color="#27ae60")
        self.menu_img.pack(side="left", padx=10, pady=10)
        self.btn_i = ctk.CTkButton(self.f_img, text="Convertir Todo", command=lambda: self.iniciar_hilo("imagen"), state="disabled", fg_color="#27ae60")
        self.btn_i.pack(side="right", padx=10)

    def seleccionar_archivos(self):
        # askopenfilenames (en plural) permite selección múltiple
        self.archivos_rutas = list(filedialog.askopenfilenames())
        if self.archivos_rutas:
            self.actualizar_info()
            self.btn_v.configure(state="normal")
            self.btn_i.configure(state="normal")

    def seleccionar_destino(self):
        self.carpeta_destino = filedialog.askdirectory()
        self.actualizar_info()

    def actualizar_info(self):
        dest = self.carpeta_destino if self.carpeta_destino else "Original"
        self.lbl_info.configure(text=f"Archivos: {len(self.archivos_rutas)} | Destino: {os.path.basename(dest)}")

    def iniciar_hilo(self, tipo):
        self.progress.set(0)
        threading.Thread(target=self.procesar_lote, args=(tipo,), daemon=True).start()

    def procesar_lote(self, tipo):
        total = len(self.archivos_rutas)
        for i, ruta in enumerate(self.archivos_rutas):
            nombre_base = os.path.basename(ruta)
            self.status.configure(text=f"Procesando ({i+1}/{total}): {nombre_base}")
            
            # Definir ruta de salida
            nombre_sin_ext = os.path.splitext(nombre_base)[0]
            extension = self.menu_video.get() if tipo == "video" else self.menu_img.get()
            
            directorio = self.carpeta_destino if self.carpeta_destino else os.path.dirname(ruta)
            ruta_salida = os.path.join(directorio, f"{nombre_sin_ext}_conv.{extension}")

            if tipo == "video":
                self.convertir_video_logic(ruta, ruta_salida, extension)
            else:
                self.convertir_imagen_logic(ruta, ruta_salida, extension)
            
            # Actualizar barra de progreso (determinado)
            self.progress.set((i + 1) / total)

        self.status.configure(text="¡Conversión por lotes finalizada!", text_color="#2ecc71")

    def convertir_video_logic(self, entrada, salida, fmt):
        cmd = f'ffmpeg -i "{entrada}" -c:v libx264 -preset superfast "{salida}" -y'
        if fmt in ["mp3", "wav"]:
            cmd = f'ffmpeg -i "{entrada}" -vn -ab 192k "{salida}" -y'
        subprocess.run(cmd, shell=True)

    def convertir_imagen_logic(self, entrada, salida, fmt):
        try:
            img = Image.open(entrada)
            img.save(salida, "JPEG" if fmt=="jpg" else fmt.upper())
        except Exception as e:
            print(f"Error en imagen: {e}")

if __name__ == "__main__":
    app = AppConversora()
    app.mainloop()