#!/usr/bin/env python3
"""Antes y después: los mismos prompts de prueba a tres versiones del modelo.

  1. Base: el modelo sin ajustar, sin instrucciones.
  2. Base + ficha: el modelo sin ajustar, con la ficha del personaje como mensaje de sistema.
  3. LoRA: el modelo con el adaptador entrenado, sin instrucciones.

Deja salidas/comparacion.html (y comparacion.json) con las tres respuestas lado a lado
y la curva de loss del entrenamiento.

Necesita el entorno de LLaMA Factory (torch, transformers y peft):
  source factoryEnv/bin/activate
  python scripts/comparar.py
"""
import argparse
import base64
import html
import json
import re
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent


def leer_prompts(ruta):
    return [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip() and not l.lstrip().startswith("#")]


def nombre_del_personaje(ficha):
    m = re.search(r"##\s*Nombre\s*\n+(.+)", ficha)
    return m.group(1).strip() if m else "el personaje"


def prompt_chatml(usuario, sistema=None):
    # El mismo formato que la plantilla qwen3_nothink con la que se entrenó: sin bloque de razonamiento.
    texto = f"<|im_start|>system\n{sistema}<|im_end|>\n" if sistema else ""
    return texto + f"<|im_start|>user\n{usuario}<|im_end|>\n<|im_start|>assistant\n"


def main():
    ap = argparse.ArgumentParser(description="Compara el modelo base, el base con la ficha y el modelo con LoRA.")
    ap.add_argument("--modelo", default="modelos/Qwen3-4B-Instruct-2507")
    ap.add_argument("--adaptador", default="salidas/adaptador")
    ap.add_argument("--prompts", default="prompts_de_prueba.txt")
    ap.add_argument("--ficha", default="personaje.md")
    ap.add_argument("--salida", default="salidas/comparacion.html")
    ap.add_argument("--max-tokens", type=int, default=300)
    args = ap.parse_args()
    ruta = lambda p: (AQUI / p) if not Path(p).is_absolute() else Path(p)

    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        sys.exit("Falta el entorno de LLaMA Factory. Actívalo primero: source factoryEnv/bin/activate")

    prompts = leer_prompts(ruta(args.prompts))
    if not prompts:
        sys.exit(f"No hay prompts en {args.prompts}. Escribe los 10 prompts de prueba, uno por línea.")
    ficha = ruta(args.ficha).read_text(encoding="utf-8").strip()
    adaptador = ruta(args.adaptador)
    if not (adaptador / "adapter_config.json").exists():
        sys.exit(f"No encuentro el adaptador en {adaptador}. ¿Terminó el entrenamiento?")

    if torch.cuda.is_available():
        dispositivo, tipo = "cuda", torch.bfloat16
    else:
        dispositivo, tipo = "cpu", torch.float32
        print("Aviso: no hay GPU visible, esto va a ser lento.")

    print("Cargando el modelo base y el adaptador…")
    modelo_ruta = ruta(args.modelo) if ruta(args.modelo).exists() else args.modelo
    tok = AutoTokenizer.from_pretrained(modelo_ruta, trust_remote_code=True)
    try:
        base = AutoModelForCausalLM.from_pretrained(modelo_ruta, dtype=tipo, trust_remote_code=True)
    except TypeError:  # versiones viejas de transformers
        base = AutoModelForCausalLM.from_pretrained(modelo_ruta, torch_dtype=tipo, trust_remote_code=True)
    base = base.to(dispositivo)
    modelo = PeftModel.from_pretrained(base, str(adaptador)).to(dispositivo)
    modelo.eval()
    fin = tok.convert_tokens_to_ids("<|im_end|>")

    def generar(texto, con_lora):
        entradas = tok(texto, return_tensors="pt").to(dispositivo)
        opciones = dict(max_new_tokens=args.max_tokens, do_sample=False, repetition_penalty=1.05,
                        eos_token_id=[fin, tok.eos_token_id], pad_token_id=tok.pad_token_id or tok.eos_token_id)
        with torch.no_grad():
            if con_lora:
                salida = modelo.generate(**entradas, **opciones)
            else:
                with modelo.disable_adapter():
                    salida = modelo.generate(**entradas, **opciones)
        nuevo = salida[0][entradas["input_ids"].shape[1]:]
        return re.sub(r"<think>.*?</think>", "", tok.decode(nuevo, skip_special_tokens=True), flags=re.S).strip()

    filas = []
    inicio = time.time()
    for i, p in enumerate(prompts, 1):
        print(f"  prompt {i}/{len(prompts)}: {p[:60]}")
        filas.append({
            "prompt": p,
            "base": generar(prompt_chatml(p), con_lora=False),
            "base_con_ficha": generar(prompt_chatml(p, sistema=ficha), con_lora=False),
            "lora": generar(prompt_chatml(p), con_lora=True),
        })
    print(f"Listo en {(time.time() - inicio) / 60:.1f} min.")

    salida = ruta(args.salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.with_suffix(".json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")

    img = ""
    for nombre, texto in (("training_loss.png", "Loss de entrenamiento"), ("training_eval_loss.png", "Loss de evaluación")):
        curva = adaptador / nombre
        if curva.exists():
            img += f'<img alt="{texto}" src="data:image/png;base64,{base64.b64encode(curva.read_bytes()).decode()}">'
    e = html.escape
    cuerpo = "".join(
        f"<tr><th scope='row'>{e(f['prompt'])}</th><td>{e(f['base'])}</td><td>{e(f['base_con_ficha'])}</td><td class='lora'>{e(f['lora'])}</td></tr>"
        for f in filas)
    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Antes y después · {e(nombre_del_personaje(ficha))}</title>
<style>
:root {{ --fondo:#06222C; --panel:#0C303D; --panel2:#123E4D; --acento:#36C6D9; --texto:#E8F1F4; --gris:#9BB2BA; --amarillo:#F2D13F; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--fondo); color:var(--texto); font:16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
header {{ padding:32px 24px 8px; max-width:1400px; margin:auto; }}
.kicker {{ color:var(--acento); letter-spacing:.25em; font-size:12px; font-weight:700; text-transform:uppercase; }}
h1 {{ margin:6px 0 4px; font-size:30px; }} h1 span {{ color:var(--acento); }}
p.nota {{ color:var(--gris); margin:0 0 16px; }}
main {{ padding:0 24px 40px; max-width:1400px; margin:auto; }}
.tabla {{ overflow-x:auto; }}
table {{ border-collapse:separate; border-spacing:0 8px; width:100%; min-width:900px; }}
thead th {{ text-align:left; color:var(--acento); font-size:12px; letter-spacing:.15em; text-transform:uppercase; padding:4px 12px; }}
tbody th, tbody td {{ background:var(--panel); padding:12px; vertical-align:top; text-align:left; white-space:pre-wrap; font-weight:400; }}
tbody th {{ color:var(--amarillo); font-weight:600; width:18%; border-radius:6px 0 0 6px; }}
tbody td.lora {{ background:var(--panel2); border-left:3px solid var(--acento); border-radius:0 6px 6px 0; }}
figure {{ background:var(--panel); padding:16px; border-radius:6px; margin:24px 0 0; }}
figure img {{ max-width:100%; width:600px; background:#fff; border-radius:4px; margin:0 12px 12px 0; }}
figcaption {{ color:var(--gris); font-size:14px; margin-top:8px; }}
</style></head><body>
<header><div class="kicker">Lab 4 · Antes y después</div>
<h1>El modelo habla como <span>{e(nombre_del_personaje(ficha))}</span></h1>
<p class="nota">Los mismos {len(filas)} prompts de prueba, que no estaban en el dataset. Respuestas sin muestreo, para que la comparación sea justa.</p></header>
<main><div class="tabla"><table><thead><tr><th>Prompt</th><th>Modelo base</th><th>Base con la ficha como instrucción</th><th>Con LoRA, sin instrucciones</th></tr></thead>
<tbody>{cuerpo}</tbody></table></div>
{f'<figure>{img}<figcaption>Curvas de loss. Si la de evaluación sube mientras la de entrenamiento sigue bajando, el modelo está memorizando el dataset.</figcaption></figure>' if img else ''}
</main></body></html>"""
    salida.write_text(pagina, encoding="utf-8")
    print(f"Página: {salida.relative_to(AQUI) if salida.is_relative_to(AQUI) else salida}")


if __name__ == "__main__":
    main()
