# Reglas del proyecto (lab 4)

- Los datos son ficticios. El personaje lo inventa cada mesa.
- El modelo base es Qwen/Qwen3-4B-Instruct-2507, en modelos/Qwen3-4B-Instruct-2507.
- El entorno de LLaMA Factory está en factoryEnv/. Antes de usar llamafactory-cli o los scripts que usan torch: source factoryEnv/bin/activate.
- El modelo del Spark para generar el dataset lo sirve llama-server en http://127.0.0.1:8080/v1, con el formato de la API de OpenAI.
- La configuración del entrenamiento está en config/. El dataset va en datos/ y todo lo que se produce va en salidas/.
- No se sube nada de salidas/, datos/personaje.json ni modelos/ a ningún repositorio.
- No envíes correos ni publiques nada.
