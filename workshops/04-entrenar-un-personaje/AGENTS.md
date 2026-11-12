# Reglas del proyecto (lab 4)

- Los datos son ficticios. El personaje lo inventa cada mesa.
- El modelo base que se entrena es Qwen/Qwen3-4B-Instruct-2507, en modelos/Qwen3-4B-Instruct-2507.
- LLaMA Factory está instalado en el entorno factoryEnv/ de esta carpeta. Todo lo que use llamafactory-cli, torch, transformers o peft corre con ese entorno: source factoryEnv/bin/activate.
- La carpeta LLaMA-Factory/ es el código de la herramienta: se lee para ver ejemplos, pero no se edita. Las configuraciones de la mesa van en config/.
- El modelo del Spark lo sirve llama-server en http://127.0.0.1:8080/v1, con el formato de la API de OpenAI y el modelo qwen3-coder. Es el que genera el dataset y el que mueve a OpenCode. No se detiene ni se reinicia.
- El programa que genera el dataset usa solo la biblioteca estándar de Python.
- Los comandos largos (generar el dataset, entrenar, comparar) corren en segundo plano con nohup y dejan su log en salidas/. Se revisan con tail.
- No instales paquetes fuera de factoryEnv y no uses sudo.
- La carpeta plan-b/ es el respaldo del facilitador: no se lee ni se usa.
- El dataset va en datos/ y todo lo que se produce va en salidas/. Las páginas se abren sin internet.
- No envíes correos ni publiques nada.
