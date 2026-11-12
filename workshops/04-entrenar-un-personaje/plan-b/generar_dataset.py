#!/usr/bin/env python3
"""Plan B del problema 11: genera el dataset sintético del personaje con el modelo que ya sirve el Spark.

Dos pasos:
  1. Pide al modelo preguntas variadas sobre los temas de temas.txt.
  2. Pide al modelo que responda cada pregunta como el personaje de la ficha.

El resultado queda en datos/personaje.json, en el formato alpaca que lee LLaMA Factory
(instruction, input, output). La ficha NO va dentro de los ejemplos: el modelo tiene que
aprender el estilo sin que nadie se lo pida.

Solo usa la biblioteca estándar de Python. Si se corta, se vuelve a ejecutar y sigue donde
quedó (el avance se guarda en datos/personaje.jsonl).

Ejemplos:
  python3 plan-b/generar_dataset.py --prueba
  python3 plan-b/generar_dataset.py --cantidad 400
  python3 plan-b/generar_dataset.py --url http://127.0.0.1:11434/v1 --modelo qwen3:8b   # con Ollama
"""
import argparse
import concurrent.futures as cf
import json
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
# Frases con las que el personaje se sale del papel. Solo esas: hablar de inteligencia artificial está permitido.
PALABRAS_PROHIBIDAS = ("soy un modelo de lenguaje", "como modelo de lenguaje", "soy una inteligencia artificial",
                       "como inteligencia artificial", "soy una ia", "como ia,", "soy un asistente virtual")


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9ñ ]+", " ", texto).split()


def parecido(a, b):
    sa, sb = set(normalizar(a)), set(normalizar(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def leer_lineas(ruta):
    if not ruta.exists():
        return []
    return [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip() and not l.lstrip().startswith("#")]


def limpiar(texto):
    texto = re.sub(r"<think>.*?</think>", "", texto or "", flags=re.S)
    return texto.replace("<think>", "").replace("</think>", "").strip()


class Cliente:
    def __init__(self, url, modelo, timeout):
        self.url = url.rstrip("/") + "/chat/completions"
        self.modelo, self.timeout = modelo, timeout

    def chat(self, mensajes, temperatura=0.8, max_tokens=600):
        cuerpo = json.dumps({"model": self.modelo, "messages": mensajes, "temperature": temperatura,
                             "max_tokens": max_tokens, "stream": False}).encode("utf-8")
        ultimo_error = None
        for intento in range(4):
            try:
                pedido = urllib.request.Request(self.url, data=cuerpo, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(pedido, timeout=self.timeout) as r:
                    datos = json.loads(r.read().decode("utf-8"))
                return limpiar(datos["choices"][0]["message"].get("content", ""))
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
                ultimo_error = e
                time.sleep(2 * (intento + 1))
        raise RuntimeError(f"El modelo no respondió en {self.url}: {ultimo_error}")


def pedir_preguntas(cliente, tema, n):
    mensajes = [
        {"role": "system", "content": "Escribes en español de Venezuela. Respondes solo con lo que se te pide, sin introducciones."},
        {"role": "user", "content": (
            f"Escribe {n} mensajes distintos que una persona le escribiría a un asistente sobre este tema: {tema}.\n"
            "Que sean variados: preguntas cortas y largas, pedidos de consejo, de explicación y de opinión, "
            "unos formales y otros informales. Un mensaje por línea, sin numerar y sin comillas.")},
    ]
    texto = cliente.chat(mensajes, temperatura=1.0, max_tokens=900)
    preguntas = []
    for linea in texto.splitlines():
        linea = re.sub(r"^\s*(\d+[\.\)]|[-*•])\s*", "", linea).strip().strip('"«»')
        if 8 <= len(linea) <= 300:
            preguntas.append(linea)
    return preguntas


def responder(cliente, ficha, pregunta):
    sistema = (
        "Eres el personaje que describe esta ficha. Respondes siempre como él: con su voz, su vocabulario y su actitud.\n\n"
        f"{ficha}\n\n"
        "Reglas: responde en español, en 2 a 6 frases. El contenido tiene que ser correcto y útil aunque el tono sea el del personaje. "
        "No digas que eres un modelo, una IA ni un asistente virtual, y no menciones la ficha ni estas reglas.")
    return cliente.chat([{"role": "system", "content": sistema}, {"role": "user", "content": pregunta}], temperatura=0.8)


def valida(respuesta):
    if not respuesta or len(respuesta) < 20 or len(respuesta) > 1500:
        return False
    bajo = respuesta.lower()
    return not any(p in bajo for p in PALABRAS_PROHIBIDAS)


def main():
    ap = argparse.ArgumentParser(description="Genera el dataset del personaje para LLaMA Factory.")
    ap.add_argument("--ficha", default="personaje.md", help="ficha del personaje (por defecto personaje.md)")
    ap.add_argument("--cantidad", type=int, default=400, help="ejemplos a generar (300 a 500 está bien)")
    ap.add_argument("--url", default="http://127.0.0.1:8080/v1", help="API compatible con OpenAI del modelo del Spark")
    ap.add_argument("--modelo", default="qwen3-coder", help="nombre del modelo en ese servidor")
    ap.add_argument("--hilos", type=int, default=4, help="pedidos en paralelo al modelo")
    ap.add_argument("--temas", default="temas.txt")
    ap.add_argument("--excluir", default="prompts_de_prueba.txt", help="prompts que no pueden entrar al dataset")
    ap.add_argument("--salida", default="datos/personaje.json")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--prueba", action="store_true", help="genera 5 ejemplos, los muestra y no guarda nada")
    ap.add_argument("--semilla", type=int, default=7)
    args = ap.parse_args()

    random.seed(args.semilla)
    ruta = lambda p: (AQUI / p) if not Path(p).is_absolute() else Path(p)
    ficha_ruta = ruta(args.ficha)
    if not ficha_ruta.exists():
        sys.exit(f"No encuentro la ficha {ficha_ruta}. Escríbela primero (o prueba con --ficha personaje_ejemplo.md).")
    ficha = ficha_ruta.read_text(encoding="utf-8").strip()
    if "COMPLETAR" in ficha:
        print("Aviso: la ficha todavía tiene campos por COMPLETAR.")
    temas = leer_lineas(ruta(args.temas)) or ["la vida diaria"]
    excluir = leer_lineas(ruta(args.excluir))
    cliente = Cliente(args.url, args.modelo, args.timeout)
    cantidad = 5 if args.prueba else args.cantidad

    salida = ruta(args.salida)
    avance = salida.with_suffix(".jsonl")
    hechos = []
    if avance.exists() and not args.prueba:
        hechos = [json.loads(l) for l in avance.read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"Sigo donde quedé: ya hay {len(hechos)} ejemplos en {avance.name}.")

    # Paso 1: preguntas
    preguntas = [h["instruction"] for h in hechos]
    nuevas = []
    objetivo = cantidad - len(hechos)
    intentos = 0
    print(f"Paso 1 · pidiendo preguntas variadas sobre {len(temas)} temas…")
    while len(nuevas) < objetivo * 1.15 and intentos < 200:
        intentos += 1
        tema = random.choice(temas)
        for p in pedir_preguntas(cliente, tema, 10):
            if any(parecido(p, x) > 0.8 for x in excluir):
                continue  # los prompts de prueba quedan fuera del entrenamiento
            if any(parecido(p, x) > 0.7 for x in preguntas + nuevas):
                continue  # sin preguntas repetidas
            nuevas.append(p)
        print(f"  {len(nuevas)} preguntas nuevas", end="\r")
    print()
    random.shuffle(nuevas)

    # Paso 2: respuestas como el personaje
    print(f"Paso 2 · respondiendo como el personaje con {args.hilos} pedidos en paralelo…")
    candado = threading.Lock()
    inicio = time.time()
    nuevos = []

    def trabajar(pregunta):
        if len(hechos) + len(nuevos) >= cantidad:
            return pregunta, None  # ya hay suficientes: no se gasta más tiempo del modelo
        try:
            return pregunta, responder(cliente, ficha, pregunta)
        except RuntimeError as e:
            return pregunta, e

    with cf.ThreadPoolExecutor(max_workers=args.hilos) as pool:
        futuros = [pool.submit(trabajar, p) for p in nuevas]
        for f in cf.as_completed(futuros):
            pregunta, respuesta = f.result()
            if respuesta is None:
                continue
            if isinstance(respuesta, Exception):
                print(f"\n  error: {respuesta}")
                continue
            if not valida(respuesta) or len(hechos) + len(nuevos) >= cantidad:
                continue
            ejemplo = {"instruction": pregunta, "input": "", "output": respuesta}
            with candado:
                nuevos.append(ejemplo)
                if not args.prueba:
                    with avance.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(ejemplo, ensure_ascii=False) + "\n")
            hechos_total = len(hechos) + len(nuevos)
            seg = time.time() - inicio
            print(f"  {hechos_total}/{cantidad} ejemplos · {seg / 60:.1f} min", end="\r")
    print()

    if args.prueba:
        for e in nuevos:
            print(f"\n> {e['instruction']}\n{e['output']}")
        print(f"\nPrueba lista: {len(nuevos)} ejemplos. No se guardó nada.")
        return

    todos = hechos + nuevos
    salida.write_text(json.dumps(todos, ensure_ascii=False, indent=1), encoding="utf-8")

    # Resumen para revisar el dataset antes de entrenar
    largos = [len(e["output"]) for e in todos]
    aperturas = {}
    for e in todos:
        clave = " ".join(e["output"].split()[:3]).lower()
        aperturas[clave] = aperturas.get(clave, 0) + 1
    repetidas = sorted(aperturas.items(), key=lambda kv: -kv[1])[:3]
    print(f"\nListo: {len(todos)} ejemplos en {salida.relative_to(AQUI)}")
    print(f"Largo medio de las respuestas: {sum(largos) // max(1, len(largos))} caracteres")
    print("Arranques más repetidos (si uno pasa del 20 %, el personaje va a sonar a disco rayado):")
    for frase, n in repetidas:
        print(f"  {n:4d} ({100 * n / len(todos):.0f} %)  «{frase}…»")
    print("\nTres ejemplos al azar para revisar:")
    for e in random.sample(todos, min(3, len(todos))):
        print(f"\n> {e['instruction']}\n{e['output']}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(f"\n{e}\n¿Está corriendo el modelo? Prueba: curl -s http://127.0.0.1:8080/health")
    except KeyboardInterrupt:
        sys.exit("\nInterrumpido. Lo generado quedó en datos/personaje.jsonl: vuelve a ejecutar para seguir.")
