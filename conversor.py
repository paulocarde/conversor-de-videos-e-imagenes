import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import threading
import subprocess

class AppMaster(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Media Master Suite v5.0")
        self.geometry("1000x800")
        ctk.set_appearance_mode("dark")
        
        self.archivos_rutas = []
        self.carpeta_destino = ""

        # --- DISEÑO DE PESTAÑAS ---
        self.tabview = ctk.CTkTabview(self, width=950, height=550)
        self.tabview.pack(pady=20, padx=20)
        
        self.tab_video = self.tabview.add("🎥 Video")
        self.tab_audio = self.tabview.add("🎵 Audio")
        self.tab_img = self.tabview.add("🖼️ Imágenes")

        self.setup_tab_pro(self.tab_video, "video", [("Videos", "*.mp4 *.mkv *.avi *.mov *.webm")])
        self.setup_tab_pro(self.tab_audio, "audio", [("Audio/Video", "*.mp3 *.wav *.flac *.mp4 *.mkv")])
        self.setup_tab_pro(self.tab_img, "imagen", [("Imágenes", "*.jpg *.png *.webp *.bmp")])

        # --- BARRA INFERIOR ---
        self.progress = ctk.CTkProgressBar(self, width=850, height=22)
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(self, text="Sistema listo", font=("Roboto", 16))
        self.lbl_status.pack(pady=5)

    def setup_tab_pro(self, tab, tipo, filtros):
        # Frame Principal de la Pestaña
        frame_cuerpo = ctk.CTkFrame(tab, fg_color="transparent")
        frame_cuerpo.pack(fill="both", expand=True, padx=10, pady=10)

        # COLUMNA IZQUIERDA: CONTROLES
        f_left = ctk.CTkFrame(frame_cuerpo, fg_color="transparent")
        f_left.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(f_left, text="CONTROLES", font=("Roboto", 18, "bold")).pack(pady=10)
        
        btn_p = {"height": 55, "width": 220, "font": ("Roboto", 15, "bold")}
        
        ctk.CTkButton(f_left, text="📁 Cargar Archivos", command=lambda: self.seleccionar(filtros), **btn_p).pack(pady=10)
        
        # Selector de Formato
        if tipo == "video": self.m_v = ctk.CTkOptionMenu(f_left, values=["mp4", "mkv", "avi", "webm", "gif"], height=45); self.m_v.pack(pady=10)
        elif tipo == "audio": self.m_a = ctk.CTkOptionMenu(f_left, values=["mp3", "wav", "flac"], height=45); self.m_a.pack(pady=10)
        else: self.m_i = ctk.CTkOptionMenu(f_left, values=["webp", "png", "jpg", "ico"], height=45); self.m_i.pack(pady=10)

        ctk.CTkButton(f_left, text="📂 Carpeta Destino", fg_color="#e67e22", command=self.set_dest, **btn_p).pack(pady=10)
        
        # Botón Eliminar Seleccionado
        ctk.CTkButton(f_left, text="🗑️ Eliminar de Lista", fg_color="#c0392b", hover_color="#a93226", 
                      command=self.eliminar_seleccionado, **btn_p).pack(pady=10)

        ctk.CTkButton(f_left, text="🚀 Iniciar Conversión", fg_color="#27ae60", command=lambda: self.hilo(tipo), **btn_p).pack(pady=20)

        # COLUMNA DERECHA: TABLA DE ARCHIVOS
        f_right = ctk.CTkFrame(frame_cuerpo, fg_color="#1a1a1a", corner_radius=10)
        f_right.pack(side="right", fill="both", expand=True, padx=10)

        # Configuración de Estilo para la Tabla (Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, font=("Roboto", 11))
        style.map("Treeview", background=[('selected', '#3498db')])

        columnas = ("#", "Nombre del Archivo", "Formato")
        tabla = ttk.Treeview(f_right, columns=columnas, show="headings", height=15)
        
        tabla.heading("#", text="#")
        tabla.heading("Nombre del Archivo", text="Nombre del Archivo")
        tabla.heading("Formato", text="Formato")

        tabla.column("#", width=40, anchor="center")
        tabla.column("Nombre del Archivo", width=350, anchor="w")
        tabla.column("Formato", width=80, anchor="center")
        
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
        setattr(self, f"tabla_{tipo}", tabla)

    def seleccionar(self, tipos):
        rutas = filedialog.askopenfilenames(filetypes=tipos)
        if rutas:
            # Evitar duplicados al cargar
            nuevas_rutas = [r for r in rutas if r not in self.archivos_rutas]
            self.archivos_rutas.extend(nuevas_rutas)
            self.actualizar_tablas()

    def actualizar_tablas(self):
        tab_actual = self.tabview.get()
        mapping = {"🎥 Video": "tabla_video", "🎵 Audio": "tabla_audio", "🖼️ Imágenes": "tabla_imagen"}
        tabla = getattr(self, mapping[tab_actual])

        # Limpiar tabla
        for item in tabla.get_children():
            tabla.delete(item)

        # Llenar tabla
        for i, ruta in enumerate(self.archivos_rutas, 1):
            nombre = os.path.basename(ruta)
            ext = os.path.splitext(ruta)[1].upper().replace(".", "")
            tabla.insert("", "end", values=(i, nombre, ext))
        
        self.lbl_status.configure(text=f"Cola: {len(self.archivos_rutas)} archivos.")

    def eliminar_seleccionado(self):
        tab_actual = self.tabview.get()
        mapping = {"🎥 Video": "tabla_video", "🎵 Audio": "tabla_audio", "🖼️ Imágenes": "tabla_imagen"}
        tabla = getattr(self, mapping[tab_actual])
        
        seleccionados = tabla.selection()
        if not seleccionados:
            return

        for item in seleccionados:
            # Obtener el nombre del archivo para buscarlo en la lista de rutas
            valores = tabla.item(item, "values")
            nombre_archivo = valores[1]
            # Eliminar de la lista maestra
            self.archivos_rutas = [r for r in self.archivos_rutas if os.path.basename(r) != nombre_archivo]
        
        self.actualizar_tablas()

    def set_dest(self):
        dest = filedialog.askdirectory()
        if dest: self.carpeta_destino = dest

    def hilo(self, tipo):
        if not self.archivos_rutas:
            messagebox.showwarning("Aviso", "No hay archivos en la lista.")
            return
        threading.Thread(target=self.procesar, args=(tipo,), daemon=True).start()

    def procesar(self, tipo):
        if tipo == "video": target_fmt = self.m_v.get()
        elif tipo == "audio": target_fmt = self.m_a.get()
        else: target_fmt = self.m_i.get()

        omitidos = []
        procesados = 0
        total = len(self.archivos_rutas)

        for i, ruta in enumerate(self.archivos_rutas):
            nombre = os.path.basename(ruta)
            ext_actual = os.path.splitext(ruta)[1].replace(".", "").lower()

            if ext_actual == target_fmt:
                omitidos.append(nombre)
                continue

            self.lbl_status.configure(text=f"Procesando ({i+1}/{total}): {nombre}")
            dir_out = self.carpeta_destino if self.carpeta_destino else os.path.dirname(ruta)
            salida = os.path.join(dir_out, f"{os.path.splitext(nombre)[0]}_ready.{target_fmt}")

            if tipo == "imagen": self.run_pillow(ruta, salida, target_fmt)
            else: self.run_ffmpeg(ruta, salida, target_fmt, tipo)
            
            procesados += 1
            self.progress.set((i + 1) / total)

        self.finalizar_proceso(procesados, omitidos, target_fmt)

    def finalizar_proceso(self, procesados, omitidos, fmt):
        msg = f"✅ ¡Conversión Exitosa!\n\nSe procesaron {procesados} archivos."
        if omitidos:
            msg += f"\n\n⚠️ {len(omitidos)} archivos se omitieron por ya ser {fmt.upper()}."

        # Ventana de pregunta Sí/No
        respuesta = messagebox.askyesno("Tarea Terminada", f"{msg}\n\n¿Deseas abrir la carpeta de los archivos ahora?")
        
        if respuesta:
            ruta_abrir = self.carpeta_destino if self.carpeta_destino else os.path.dirname(self.archivos_rutas[0])
            os.startfile(ruta_abrir) # Solo funciona en Windows
        
        self.progress.set(0)
        self.lbl_status.configure(text="Listo.")

    def run_ffmpeg(self, entrada, salida, fmt, tipo):
        cmd = f'ffmpeg -i "{entrada}" -c:v libx264 -preset ultrafast "{salida}" -y'
        if tipo == "audio": cmd = f'ffmpeg -i "{entrada}" -vn -ab 192k "{salida}" -y'
        subprocess.run(cmd, shell=True)

    def run_pillow(self, entrada, salida, fmt):
        img = Image.open(entrada)
        if fmt == "jpg": img = img.convert("RGB"); fmt = "JPEG"
        img.save(salida, fmt.upper())

if __name__ == "__main__":
    app = AppMaster()
    app.mainloop()