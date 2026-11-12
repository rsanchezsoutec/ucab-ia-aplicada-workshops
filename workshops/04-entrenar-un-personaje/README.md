# Lab 4 · Entrenar un personaje

Hasta ahora le cambiamos al modelo lo que lee: instrucciones en el prompt y documentos con RAG. Hoy le cambiamos cómo habla. Cada mesa inventa un personaje, genera un dataset con el modelo que ya sirve su Spark y entrena un adaptador LoRA sobre Qwen3-4B con LLaMA Factory. Al final, los mismos 10 prompts van al modelo sin ajustar, al modelo con la ficha como instrucción y al modelo con LoRA.

La instalación de LLaMA Factory se hace a mano, paso a paso, porque es parte de lo que se aprende hoy. Lo demás es igual que en los labs anteriores: cada problema dice qué hay que entregar y qué condición tiene que cumplir, y la mesa lo resuelve con OpenCode. Discutan entre los tres antes de escribirle al agente.

## El plan de la sesión

| Hora | Bloque | Quién |
| --- | --- | --- |
| 0:00 | Teoría: fine-tuning, LoRA y cuándo usarlo | Todos |
| 0:30 | A instala a mano; B y C resuelven el problema 11 con OpenCode | A, B y C |
| 1:30 | Problema 12 · Entrenar el adaptador | La mesa |
| 2:00 | Problema 13 · Antes y después | La mesa |
| 2:20 | Cada mesa presenta su personaje | Todos |
| 2:45 | Margen para fallas de instalación o descarga | |

## Antes de empezar (los tres)

1. Entra al Spark de tu mesa por SSH. Los tres trabajan en la misma carpeta, cada uno en su propia terminal.
2. Copia esta carpeta en tu usuario y entra en ella.
3. Ejecuta `bash preparar.sh`. Si algo dice FALTA, avisa al facilitador antes de seguir.
4. Repártanse los roles: A instala; B y C empiezan el problema 11.

## La instalación, a mano (alumno A, hasta 60 minutos)

Son los pasos del playbook oficial de NVIDIA para LLaMA Factory en DGX Spark. Todo se hace dentro de la carpeta del lab.

1. Crea el entorno de Python, actívalo e instala la herramienta de Hugging Face:
   ```bash
   python3 -m venv factoryEnv
   source factoryEnv/bin/activate
   pip install -U pip huggingface_hub
   ```
   Al principio de la línea tiene que aparecer `(factoryEnv)`.
2. Abre una segunda terminal en el Spark, entra a la carpeta del lab, activa el entorno y baja el modelo base (unos 8 GB). Déjala corriendo mientras sigues:
   ```bash
   source factoryEnv/bin/activate
   hf download Qwen/Qwen3-4B-Instruct-2507 --local-dir modelos/Qwen3-4B-Instruct-2507
   ```
   Si el facilitador ya dejó el modelo en el Spark, no lo bajes: enlázalo con `ln -s /srv/models/Qwen3-4B-Instruct-2507 modelos/Qwen3-4B-Instruct-2507`.
3. En la primera terminal, instala PyTorch para CUDA 13 y comprueba que ve la GPU:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
   python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
   ```
   Tiene que decir `CUDA: True`. Si dice `False`, no sigas: avisa al facilitador.
4. Baja LLaMA Factory e instálalo:
   ```bash
   git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
   pip install -e ./LLaMA-Factory
   llamafactory-cli version
   ```
   El playbook de NVIDIA escribe `pip install -e ".[metrics]"`. La versión actual de LLaMA Factory ya no tiene ese extra, y las métricas no hacen falta para entrenar.
5. Cuando termine la descarga, comprueba que el modelo está completo (tres archivos `.safetensors`) y pruébalo. Escribe «hola», espera la respuesta y sal con `exit`:
   ```bash
   ls -lh modelos/Qwen3-4B-Instruct-2507/
   llamafactory-cli chat config/chat_base.yaml
   ```
6. Avísale a la mesa: el entorno está listo. Desde ahora, A se suma a los problemas.

**Listo cuando:** `CUDA: True`, `llamafactory-cli version` responde y el modelo base contesta en el chat.

## Los problemas, con OpenCode

Abre OpenCode en la carpeta del lab con `opencode`. Las reglas del proyecto están en `AGENTS.md`: ahí dice dónde está el modelo, cómo se activa el entorno y que los comandos largos corren en segundo plano.

| # | Problema | Cuándo |
| --- | --- | --- |
| 11 | [El dataset del personaje](problemas/11-el-dataset-del-personaje.md) | B y C, mientras A instala |
| 12 | [Entrenar el adaptador](problemas/12-entrenar-el-adaptador.md) | La mesa, desde la hora 1:30 |
| 13 | [Antes y después](problemas/13-antes-y-despues.md) | La mesa, desde la hora 2:00 |
| 14 | [El personaje fuera del lab](problemas/14-el-personaje-fuera-del-lab.md) | Para quien termine el 13 |

**Punto de control a la hora 1:30:** entorno con `CUDA: True`, modelo base en su carpeta y el dataset del problema 11 revisado por la mesa. Si una mesa va muy atrasada, el facilitador le habilita la carpeta `plan-b/`.

## Cómo ver las páginas

Cada problema deja una página HTML en `salidas/`. Para verla desde la laptop, en otra terminal del Spark entra a `salidas/` y ejecuta `python3 -m http.server 8000`. Luego abre `http://<ip-del-spark>:8000`. Si la red no deja pasar el puerto, copia el archivo con `scp`.

## Cierre (25 minutos)

Cada mesa tiene tres minutos para presentar su personaje con la página del problema 13. Después, entre todos: ¿qué logra LoRA que no logra la ficha como instrucción?, ¿qué costó? y ¿para qué lo usarían en el proyecto final?

## Qué hay en la carpeta

- `problemas/`: los enunciados de los problemas 11 a 14.
- `personaje.md`: la ficha del personaje, para completar.
- `personaje_ejemplo.md`: un personaje de ejemplo.
- `prompts_de_prueba.txt`: los 10 prompts de prueba, para completar.
- `temas.txt`: temas para que las preguntas del dataset sean variadas.
- `config/chat_base.yaml`: para probar el modelo base al terminar la instalación. Las configuraciones de la mesa también van en `config/`.
- `datos/`: aquí va el dataset del problema 11.
- `modelos/` y `salidas/`: el modelo base y todo lo que produzca la mesa. Nada de eso se sube al repo.
- `plan-b/`: el respaldo del facilitador, solo si él lo habilita. OpenCode no puede leerla.
- `AGENTS.md`, `CLAUDE.md` y `opencode.json`: las reglas y la configuración del proyecto.

Todos los datos son ficticios.
