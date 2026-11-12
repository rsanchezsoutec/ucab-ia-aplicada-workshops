# Plan B

Programas y configuraciones listos para una mesa que se atrasó. Se usan solo si el facilitador lo dice: el lab es resolver los problemas con OpenCode. El agente no puede leer esta carpeta (lo impide `opencode.json`), así que se ejecutan a mano, desde la carpeta del lab y con el entorno activado (`source factoryEnv/bin/activate`).

| Problema | Comando |
| --- | --- |
| 11 · El dataset | `python3 plan-b/generar_dataset.py --cantidad 400` y después `cp plan-b/dataset_info.json datos/` |
| 12 · Entrenar | `nohup llamafactory-cli train plan-b/entrenar.yaml > salidas/entrenamiento.log 2>&1 &` y seguirlo con `tail -f salidas/entrenamiento.log` |
| 13 · Antes y después | `python plan-b/comparar.py` |
| Para conversar con el personaje | `llamafactory-cli chat plan-b/chat_lora.yaml` |
| 14 · Fusionar el adaptador | `llamafactory-cli export plan-b/exportar.yaml` |

`generar_dataset.py` solo usa Python y el modelo del Spark en `http://127.0.0.1:8080/v1`. Con Ollama, agrega `--url http://127.0.0.1:11434/v1 --modelo <nombre-del-modelo>`. Para probarlo sin guardar nada: `python3 plan-b/generar_dataset.py --ficha personaje_ejemplo.md --prueba`.
