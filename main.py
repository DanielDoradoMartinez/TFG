import tkinter as tk
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
from deep_translator import GoogleTranslator
from PIL import Image, ImageTk
from itertools import cycle
import threading
import webbrowser
# Textos por defecto para cada campo
textos_defecto = [
    """La plataforma estará basada en la filosofía MOOC y adaptada a las necesidades de aprendizaje de chicos y chicas entre 8 y 13 años. Una vez finalice el periodo de pruebas estará a disposición de todos los donantes de la campaña, que podrán realizar los primeros cursos en cuanto estén disponibles. Una vez completados los cursos de QUÍMICA 1, ELECTRICIDAD 1, CRIMINALÍSTICA y MICROSCOPÍA: Tinción será de acceso gratuito para todo el mundo. La dinámica de aprendizaje es muy sencilla. En primer lugar, el alumno observará una demostración en vídeo, donde se detallarán los materiales necesarios, herramientas, duración y pasos a seguir para la realización del experimento (IMAGEN 1). Tras ver el vídeo, realizará el experimento por sí mismo y analizará los resultados, asimilando los conceptos adquiridos durante el curso (IMAGEN 2) Finalmente, y para asegurar que el alumno ha comprendido todos los conceptos clave, realizará un test con preguntas relacionadas. Si tuviese alguna duda relacionada con el curso, podrá consultarla en un espacio dedicado para ello (IMAGEN 3). A medida que se vayan completando experimentos y cursos, se acumularán puntos para subir de nivel y obtener recompensas y premios.""",

    """El modelo educativo actual está diseñado para optimizar la enseñanza en lugar del aprendizaje, con un acceso a la información masivo y saturado. En los últimos años se ha intentado resolver esta situación con juguetes educativos, digitalización de contenidos y creación de cursos masivos gratuitos online (MOOC). ROCTAR propone un modelo combinado en el que los niños puedan jugar y aprender con la ayuda de tutoriales en vídeo paso por paso y realizar seguimiento activo del progreso. En cada curso se realizarán experimentos específicos en los que el alumno podrá comprender y asimilar los conocimientos de una forma práctica y divertida. Todos los materiales necesarios se podrán adquirir por cuenta propia o mediante uno de los kits preparados que ofrecemos. ROCTAR, no se trata de enseñar sino de aprender.""",

    """El proyecto surge como una iniciativa para aprender ciencias de una forma divertida y dinámica, haciendo de la experiencia educativa un juego. El modelo propuesto está pensado para padres que quieran promover en sus hijos el espíritu científico y despertar inquietud por la experimentación y el conocimiento del mundo.""",

    """El objetivo principal de la campaña de crowdfunding es crear la plataforma web y los primeros cursos, que servirán de base para el futuro desarrollo del proyecto. Se ha escogido GOTEO como plataforma de crowdfunding dado el carácter social del proyecto, y para crear una comunidad activa de usuarios con los que compartir las novedades y recibir feedback para futuras mejoras."""
]

# --- Funciones de preprocesado y traducción ---
def quitarURL(text):
    return re.sub(r'http\S+', '', text)

def quitarPar(text):
    return re.sub(r'\(\s*\)', '', text)

def remove_chars(text):
    return re.sub(r'!\[\]\(', '', str(text))

def remove_extra_chars(text):
    text = re.sub(r'[\n\r\t]', ' ', str(text))
    text = re.sub(r'[\*\#\@\%\&\$\^\=\+\~\<\>\|\[\]\{\}]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_asterisks(text):
    return re.sub(r'\*', '', str(text))

def traducir_si_no_es_espanol(text):
    try:
        return GoogleTranslator(source='auto', target='es').translate(text)
    except Exception as e:
        print(f"[!] Error al traducir: {e}")
        return text

def preprocesar_texto(text):
    text = quitarURL(text)
    text = quitarPar(text)
    text = remove_chars(text)
    text = remove_extra_chars(text)
    text = remove_asterisks(text)
    text = traducir_si_no_es_espanol(text)
    return text

# Nombres de campos
nombres_campos = ["About", "Description", "Motivation", "Goal"]

# Rutas de modelos por campo
grupos_modelos = [
    ["./Rb/RbB0-M1", "./Rb/RbB1-M1", "./Rb/RbB2-M1"],
    ["./Rb/RbB0-M2", "./Rb/RbB1-M2", "./Rb/RbB2-M2"],
    ["./Rb/RbB0-M3", "./Rb/RbB1-M3", "./Rb/RbB2-M3"],
    ["./Rb/RbB0-M4", "./Rb/RbB1-M4", "./Rb/RbB2-M4"]
]

# Cargar modelos y tokenizers
todos_los_modelos = []
for grupo in grupos_modelos:
    modelos_del_grupo = []
    for ruta in grupo:
        tokenizer = AutoTokenizer.from_pretrained(ruta)
        modelo = AutoModelForSequenceClassification.from_pretrained(ruta)
        modelo.eval()
        modelos_del_grupo.append((tokenizer, modelo))
    todos_los_modelos.append(modelos_del_grupo)

# Ventana principal
ventana = tk.Tk()
ventana.title("Predictor de éxito Goteo")
ventana.geometry("800x850")
ventana.resizable(False, False)

# Icono de la app
icon_app = ImageTk.PhotoImage(Image.open("goteo-white.png").resize((32, 32)))
ventana.iconphoto(False, icon_app)

# Botón de enlace a Goteo en esquina superior derecha (icono más grande)

# Botón de enlace a Goteo en esquina superior derecha usando el logo
link_icon = ImageTk.PhotoImage(Image.open("Logos_Goteo.png").resize((120, 36), Image.Resampling.LANCZOS))
def abrir_url():
    webbrowser.open("https://www.goteo.org")
tk.Button(
    ventana,
    image=link_icon,
    command=abrir_url,
    borderwidth=0,
    bg=ventana.cget("bg"),
    activebackground=ventana.cget("bg"),
    cursor="hand2"
).place(x=670, y=10)


# Iconos de campos
icon_brain = ImageTk.PhotoImage(Image.open("brainstorm.png").resize((24, 24)))
icon_pencil = ImageTk.PhotoImage(Image.open("contract.png").resize((24, 24)))
icon_fire = ImageTk.PhotoImage(Image.open("fire.png").resize((24, 24)))
icon_target = ImageTk.PhotoImage(Image.open("target.png").resize((24, 24)))
icon_check = ImageTk.PhotoImage(Image.open("check.png").resize((16, 16)))
icon_x = ImageTk.PhotoImage(Image.open("X.png").resize((16, 16)))
iconos = [icon_brain, icon_pencil, icon_fire, icon_target]

# Iconos del botón y animación
icon_predict = ImageTk.PhotoImage(Image.open("predictive-models.png").resize((24, 24)))
sandclock_base = Image.open("sandclock.png").resize((24, 24))
sandclock_frames = cycle([
    ImageTk.PhotoImage(sandclock_base.rotate(0)),
    ImageTk.PhotoImage(sandclock_base.rotate(90)),
    ImageTk.PhotoImage(sandclock_base.rotate(180)),
    ImageTk.PhotoImage(sandclock_base.rotate(270)),
])

animacion_activa = False

# Etiquetas
cajas_texto = []
def verificar_campos():
    for caja in cajas_texto:
        if not caja.get("1.0", "end").strip():
            boton.config(state="disabled")
            return
    boton.config(state="normal")

for i in range(4):
    etiqueta = tk.Label(
        ventana,
        text=f" {nombres_campos[i]}",
        font=("Arial", 12, "bold"),
        image=iconos[i],
        compound="left",
        anchor="w",
        bg=ventana.cget("bg")
    )
    etiqueta.grid(row=i * 2, column=0, sticky="w", padx=20, pady=(10, 0))

    texto = tk.Text(ventana, width=80, height=5)
    texto.grid(row=i * 2 + 1, column=0, padx=20, pady=(0, 10))

    # 👇 Insertar el texto por defecto aquí
    texto.insert("1.0", textos_defecto[i])

    texto.bind("<KeyRelease>", lambda e: verificar_campos())
    cajas_texto.append(texto)
    

# Frame para resultado y animación
frame_resultado = tk.Frame(ventana, bg=ventana.cget("bg"))
frame_resultado.grid(row=9, column=0, sticky="w", padx=20, pady=10)

etiqueta_resultado_icono = tk.Label(frame_resultado, bg=ventana.cget("bg"))
etiqueta_resultado_icono.pack(side="left", padx=(0, 10), anchor="n")

frame_resultado_texto = tk.Frame(frame_resultado, bg=ventana.cget("bg"))
frame_resultado_texto.pack(side="left", anchor="n")

# Animar reloj
def animar_reloj():
    if not animacion_activa:
        return
    frame = next(sandclock_frames)
    etiqueta_resultado_icono.config(image=frame)
    etiqueta_resultado_icono.image = frame
    ventana.after(100, animar_reloj)

# Lógica pesada en hilo
def hacer_prediccion():
    global animacion_activa
    predicciones_finales = []

    for widget in frame_resultado_texto.winfo_children():
        widget.destroy()

    encabezado = tk.Label(frame_resultado_texto, text="Predicciones por campo:", font=("Arial", 14, "bold"), bg=ventana.cget("bg"))
    encabezado.pack(anchor="w")

    for i in range(4):
        texto = cajas_texto[i].get("1.0", "end").strip() or "vacío"
        texto = preprocesar_texto(texto)
        predicciones = []
        for tokenizer, modelo in todos_los_modelos[i]:
            inputs = tokenizer(texto, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                outputs = modelo(**inputs)
                pred = torch.argmax(outputs.logits, dim=1).item()
                predicciones.append(pred)
        suma = sum(predicciones)
        voto_mayoritario = 1 if suma >= 2 else 0
        predicciones_finales.append(voto_mayoritario)

        icon = icon_check if voto_mayoritario == 1 else icon_x
        fila = tk.Frame(frame_resultado_texto, bg=ventana.cget("bg"))
        tk.Label(fila, image=icon, bg=ventana.cget("bg")).pack(side="left")
        tk.Label(fila, text=f" {nombres_campos[i]}: {'SI' if voto_mayoritario == 1 else 'NO'}", bg=ventana.cget("bg"), font=("Arial", 12)).pack(side="left")
        fila.pack(anchor="w")

    votos_1 = predicciones_finales.count(1)
    votos_0 = predicciones_finales.count(0)
    if votos_1 == votos_0:
        voto_extra = predicciones_finales[3]
        votos_1 += voto_extra
        votos_0 += (1 - voto_extra)
    resultado_final = 1 if votos_1 > votos_0 else 0

    icon = icon_check if resultado_final == 1 else icon_x
    final_row = tk.Frame(frame_resultado_texto, bg=ventana.cget("bg"))
    tk.Label(final_row, image=icon, bg=ventana.cget("bg")).pack(side="left")
    tk.Label(final_row, text=f" Resultado final: {'SI' if resultado_final == 1 else 'NO'}", bg=ventana.cget("bg"), font=("Arial", 14, "bold")).pack(side="left")
    final_row.pack(anchor="w", pady=(10, 0))

    animacion_activa = False
    etiqueta_resultado_icono.config(image="")
    boton.config(state="normal", text=" Predecir", image=icon_predict)

# Al pulsar el botón
def predecir():
    global animacion_activa
    animacion_activa = True
    for widget in frame_resultado_texto.winfo_children():
        widget.destroy()
    tk.Label(frame_resultado_texto, text=" Realizando predicciones...", bg="lightgray", font=("Arial", 14)).pack(anchor="w")
    animar_reloj()
    boton.config(state="disabled", text=" Cargando...", image=icon_predict)
    threading.Thread(target=hacer_prediccion).start()

# Botón
boton = tk.Button(ventana, text=" Predecir", font=("Arial", 14), command=predecir, image=icon_predict, compound="left", state="disabled")
boton.grid(row=8, column=0, pady=15)
verificar_campos()
# Iniciar app
ventana.mainloop()
