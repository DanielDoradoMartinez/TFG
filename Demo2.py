import tkinter as tk
from tkinter import ttk
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from captum.attr import IntegratedGradients
import re
import unicodedata
from collections import defaultdict
from PIL import Image, ImageTk
from itertools import cycle
import threading
defau="El proyecto surge como una iniciativa para aprender ciencias de una forma divertida y dinámica, haciendo de la experiencia educativa un juego. El modelo propuesto está pensado para padres que quieran promover en sus hijos el espíritu científico y despertar inquietud por la experimentación y el conocimiento del mundo."
def corregir_codificacion(text):
    try:
        text = text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return unicodedata.normalize('NFKC', text)

def score_to_color(score, max_score=0.5):
    score = max(-max_score, min(score, max_score))
    norm = abs(score) / max_score
    intensity = int(255 * (1 - norm))
    hex_val = f"{intensity:02x}"
    if score > 0:
        return f"#{hex_val}ff{hex_val}"
    else:
        return f"#ff{hex_val}{hex_val}"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

ventana = tk.Tk()
ventana.title("Visualizador interpretabilidad")
ventana.geometry("950x650")
ventana.configure(bg="#f5f5f5")

# --- Seleccion de campo ---
campo_var = tk.IntVar(value=2)  # Por defecto: Motivation (M3)

frame_radios = tk.Frame(ventana, bg="#f5f5f5")
frame_radios.pack(anchor="ne", pady=(10, 0), padx=(0, 20))

opciones = [("About", 1), ("Motivation", 2), ("Description", 3), ("Goal", 4)]
for texto, val in opciones:
    tk.Radiobutton(
        frame_radios,
        text=texto,
        variable=campo_var,
        value=val,
        bg="#f5f5f5",
        font=("Arial", 10),
        anchor="w"
    ).pack(side="left", padx=5)

label_instr = tk.Label(ventana, text="Texto:", font=("Arial", 13, "bold"), bg="#f5f5f5")
label_instr.pack(pady=(15, 5))

text_input = tk.Text(ventana, width=100, height=6, font=("Helvetica", 11), relief="groove", bd=2)
text_input.pack(pady=(0, 10))
text_input.insert("1.0", defau)
# --- Boton centrado ---
frame_boton = tk.Frame(ventana, bg="#f5f5f5")
frame_boton.pack()
boton = tk.Button(
    frame_boton,
    text="Visualizar IG",
    font=("Arial", 12),
    bg="#4caf50",
    fg="white",
    relief="raised",
    padx=10,
    pady=5
)
boton.pack()

# --- Frame para barra centrada ---
frame_estado_exterior = tk.Frame(ventana, bg="#f5f5f5")
frame_estado_exterior.pack(pady=(0, 15))
progress_bar = ttk.Progressbar(frame_estado_exterior, length=200, mode="determinate", maximum=3)
progress_bar.pack_forget()  # Oculto al inicio

# --- Reloj animado flotante ---
etiqueta_icono = tk.Label(ventana, bg="#f5f5f5")
etiqueta_icono.place_forget()

sandclock_base = Image.open("sandclock.png").resize((24, 24))
sandclock_frames = cycle([
    ImageTk.PhotoImage(sandclock_base.rotate(deg)) for deg in (0, 90, 180, 270)
])
animacion_activa = False
def animar_reloj():
    if not animacion_activa:
        return
    frame = next(sandclock_frames)
    etiqueta_icono.config(image=frame)
    etiqueta_icono.image = frame
    ventana.after(100, animar_reloj)

# --- Area de resultado ---
frame_resultado = tk.Frame(ventana, bg="#f5f5f5")
frame_resultado.pack(fill="both", expand=True, padx=10, pady=(0, 10))

scrollbar = tk.Scrollbar(frame_resultado)
scrollbar.pack(side="right", fill="y")

text_resultado = tk.Text(
    frame_resultado,
    wrap="word",
    yscrollcommand=scrollbar.set,
    font=("Helvetica", 12),
    relief="groove",
    bd=2
)
text_resultado.pack(fill="both", expand=True)
scrollbar.config(command=text_resultado.yview)

text_resultado.bind("<Key>", lambda e: "break")
text_resultado.bind("<Button-1>", lambda e: "break")
text_resultado.bind("<B1-Motion>", lambda e: "break")

def visualizar_ig_en_hilo():
    global animacion_activa
    texto = text_input.get("1.0", "end").strip()
    if not texto:
        text_resultado.config(state="normal")
        text_resultado.delete("1.0", "end")
        text_resultado.insert("1.0", "⚠️ Ingrese un texto válido.")
        text_resultado.config(state="disabled")
        return

    text_resultado.config(state="normal")
    text_resultado.delete("1.0", "end")
    text_resultado.insert("1.0", "⏳ Calculando...")
    text_resultado.config(state="disabled")
    boton.config(state="disabled")
    progress_bar.pack()
    progress_bar["value"] = 0
    progress_bar.update()
    animacion_activa = True

    ventana.update_idletasks()
    x_bar = progress_bar.winfo_rootx() - ventana.winfo_rootx()
    y_bar = progress_bar.winfo_rooty() - ventana.winfo_rooty()
    etiqueta_icono.place(x=x_bar - 30, y=y_bar, width=24, height=24)
    animar_reloj()

    def tarea():
        global animacion_activa
        try:
            carpeta_modelos = "./Bt"
            prefijo_modelo = "BtB"
            campo = f"M{campo_var.get()}"
            modelos_m3 = [f"{carpeta_modelos}/{prefijo_modelo}{i}-{campo}" for i in range(3)]

            word_scores = defaultdict(float)
            word_counts = defaultdict(int)

            for idx, model_path in enumerate(modelos_m3):
                model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model.eval()

                texto_limpio = corregir_codificacion(texto)
                inputs = tokenizer(texto_limpio, return_tensors='pt', truncation=True, max_length=512, return_offsets_mapping=True)
                input_ids = inputs['input_ids'].to(device)
                attention_mask = inputs['attention_mask'].to(device)

                offset_mapping = tokenizer(texto_limpio, return_offsets_mapping=True, truncation=True, max_length=512)["offset_mapping"]
                ref_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id
                ref_input_ids = torch.full_like(input_ids, ref_token_id)
                input_embeddings = model.bert.embeddings(input_ids)
                ref_embeddings = model.bert.embeddings(ref_input_ids)

                def forward_func(inputs_embeds, attention_mask):
                    logits = model(inputs_embeds=inputs_embeds, attention_mask=attention_mask).logits
                    return torch.softmax(logits, dim=1)[:, 1]

                ig = IntegratedGradients(forward_func)
                attributions, _ = ig.attribute(
                    inputs=input_embeddings,
                    baselines=ref_embeddings,
                    additional_forward_args=(attention_mask,),
                    return_convergence_delta=True
                )

                attributions_sum = attributions.sum(dim=-1).squeeze(0)
                attributions_sum = attributions_sum / torch.norm(attributions_sum)

                for (start, end), score in zip(offset_mapping[1:-1], attributions_sum[1:-1]):
                    if end > start:
                        word = texto_limpio[start:end]
                        word_scores[word] += score.item()
                        word_counts[word] += 1

                progress_bar["value"] += 1
                progress_bar.update()

                del model, tokenizer
                torch.cuda.empty_cache()

            final_scores = {word: word_scores[word] / word_counts[word] for word in word_scores}
            palabras = re.findall(r'\S+|\s+', texto)
            max_score = max(abs(s) for s in final_scores.values()) if final_scores else 1.0

            text_resultado.config(state="normal")
            text_resultado.delete("1.0", "end")

            for i, palabra in enumerate(palabras):
                clean = palabra.strip()
                tag = f"word{i}"
                if clean in final_scores:
                    color = score_to_color(final_scores[clean], max_score)
                    text_resultado.insert("end", palabra, tag)
                    text_resultado.tag_configure(tag, background=color)
                else:
                    text_resultado.insert("end", palabra)

            text_resultado.config(state="disabled")

        except Exception as e:
            text_resultado.config(state="normal")
            text_resultado.delete("1.0", "end")
            text_resultado.insert("1.0", f"❌ Error: {e}")
            text_resultado.config(state="disabled")
        finally:
            animacion_activa = False
            etiqueta_icono.place_forget()
            etiqueta_icono.config(image="")
            progress_bar["value"] = 0
            progress_bar.pack_forget()
            boton.config(state="normal")

    threading.Thread(target=tarea).start()

boton.config(command=visualizar_ig_en_hilo)
ventana.mainloop()
