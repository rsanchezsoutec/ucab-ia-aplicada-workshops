# Lab 4 · Entrenar un personaje

Hasta ahora le cambiamos al modelo lo que lee: instrucciones en el prompt y documentos con RAG. Hoy le cambiamos cómo habla. Cada mesa inventa un personaje, genera un dataset con el modelo que ya sirve su Spark y entrena un adaptador LoRA sobre Qwen3-4B con LLaMA Factory. Al final, los mismos 10 prompts van al modelo sin ajustar, al modelo con la ficha como instrucción y al modelo con LoRA, y cada mesa presenta su comparación.

A diferencia de los labs anteriores, este sí es paso a paso: lo nuevo es la herramienta y el proceso.

## El plan de la sesión

| Hora | Bloque | Quién |
| --- | --- | --- |
| 0:00 | Teoría: fine-tuning, LoRA y cuándo usarlo | Todos |
| 0:30 | Arranque en paralelo, cada uno con su rol | A, B y C |
| 1:30 | Entrenamiento | La mesa |
| 2:00 | Antes y después | La mesa |
| 2:20 | Cada mesa presenta su personaje | Todos |
| 2:45 | Margen para fallas de instalación o descarga | |

## Antes de empezar (los tres)

1. Entra al Spark de tu mesa por SSH. Los tres trabajan en la misma carpeta, cada uno en su propia terminal.
2. Copia esta carpeta en tu usuario y entra en ella.
3. Ejecuta `bash preparar.sh`. Si algo dice FALTA, avisa al facilitador antes de seguir.
4. Repártanse los roles: A instala, B genera el dataset y C escribe el personaje.

## Arranque en paralelo (60 minutos)

### Alumno A · Instala LLaMA Factory y baja el modelo base

Son los pasos del playbook oficial de NVIDIA para LLaMA Factory en DGX Spark. Todo se hace dentro de la carpeta del lab.

1. Crea el entorno de Python y actívalo:
   ```bash
   python3 -m venv factoryEnv
   source factoryEnv/bin/activate
   pip install -U pip huggingface_hub
   ```
2. Abre una segunda terminal en el Spark, entra a la carpeta del lab, activa el entorno y empieza a bajar el modelo base (unos 8 GB). Déjala corriendo mientras sigues:
   ```bash
   source factoryEnv/bin/activate
   hf download Qwen/Qwen3-4B-Instruct-2507 --local-dir modelos/Qwen3-4B-Instruct-2507
   ```
   Si el facilitador ya dejó el modelo en el Spark, no lo bajes: enlázalo con `ln -s <ruta-que-te-den> modelos/Qwen3-4B-Instruct-2507`.
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
5. Cuando termine la descarga del modelo, avísale a C: ya puede probar el modelo base.

**Listo cuando:** `CUDA: True`, `llamafactory-cli version` responde y la carpeta `modelos/Qwen3-4B-Instruct-2507` tiene los archivos `.safetensors`.

### Alumno B · Genera el dataset

El script `scripts/generar_dataset.py` le pide al modelo del Spark preguntas variadas sobre los temas de `temas.txt` y después las respuestas como el personaje. No necesita el entorno de A: usa solo Python.

1. Mientras C escribe la ficha, prueba el script con el personaje de ejemplo. Genera 5 ejemplos, los muestra y no guarda nada:
   ```bash
   python3 scripts/generar_dataset.py --ficha personaje_ejemplo.md --prueba
   ```
2. Revisa `temas.txt` con la mesa: agreguen temas que le queden bien a su personaje y quiten los que no.
3. Cuando C tenga lista la ficha (`personaje.md`) y los 10 prompts de prueba (`prompts_de_prueba.txt`), genera el dataset completo:
   ```bash
   python3 scripts/generar_dataset.py --cantidad 400
   ```
   Tarda unos minutos. Si se corta, vuelve a ejecutar lo mismo y sigue donde quedó. Los prompts de prueba quedan fuera del dataset a propósito: si el modelo los viera en el entrenamiento, la comparación del final no diría nada.
4. Lee el resumen que imprime al final y abre `datos/personaje.json`. Lean juntos unos 20 ejemplos. Borren los que estén mal: respuestas que se salen del personaje, que inventan datos o que repiten siempre la misma frase. El modelo va a aprender exactamente lo que haya en ese archivo.

Si el Spark sirve el modelo con Ollama y no con llama-server, agrega `--url http://127.0.0.1:11434/v1 --modelo <nombre-del-modelo>`.

**Listo cuando:** `datos/personaje.json` tiene entre 300 y 500 ejemplos revisados.

### Alumno C · Escribe el personaje y prueba el modelo base

1. Inventen el personaje entre los tres, en cinco minutos. Después C completa la ficha en `personaje.md`: quién es, cómo habla, sus expresiones, lo que nunca hace y tres respuestas de ejemplo. `personaje_ejemplo.md` sirve de modelo.
2. Escribe los 10 prompts de prueba en `prompts_de_prueba.txt`, uno por línea. Mezcla preguntas normales, dos sobre temas que el personaje no sabría y una que intente sacarlo del personaje. Escríbelos antes de que B genere el dataset completo.
3. Cuando A tenga el modelo, prueba el modelo base sin ajustar con tres de tus prompts:
   ```bash
   source factoryEnv/bin/activate
   llamafactory-cli chat config/chat_base.yaml
   ```
   Escribe `exit` para salir. Anota cómo responde: eso es el «antes».

**Listo cuando:** la ficha y los 10 prompts están escritos y la mesa vio cómo responde el modelo base.

**Punto de control a la hora 1:30:** entorno con `CUDA: True`, modelo bajado, dataset revisado, ficha y prompts listos.

## Entrenamiento (30 minutos)

1. Abran `config/entrenar.yaml` y lean juntos qué hace cada línea. Los valores que importan hoy son `lora_rank`, `learning_rate`, `num_train_epochs` y `gradient_accumulation_steps`.
2. Entrenen:
   ```bash
   source factoryEnv/bin/activate
   llamafactory-cli train config/entrenar.yaml
   ```
   Con 400 ejemplos y 3 épocas debería tardar entre 5 y 10 minutos en el Spark. La primera vez tarda un poco más en arrancar.
3. Sigan el `loss` que imprime cada 5 pasos y el `eval_loss` cada 20. El de entrenamiento tiene que bajar. Si el de evaluación sube mientras el otro sigue bajando, el modelo está memorizando.
4. Al terminar, el adaptador queda en `salidas/adaptador/`, con las curvas `training_loss.png` y `training_eval_loss.png`.

Si el personaje casi no se nota al final, prueben de nuevo con más épocas (`num_train_epochs=5`) o un paso más grande (`learning_rate=2.0e-4`). Se pueden cambiar sin editar el archivo:
```bash
llamafactory-cli train config/entrenar.yaml num_train_epochs=5
```

## Antes y después (20 minutos)

1. Generen la comparación con los 10 prompts de prueba:
   ```bash
   source factoryEnv/bin/activate
   python scripts/comparar.py
   ```
   Deja `salidas/comparacion.html` con tres columnas por prompt: el modelo base, el modelo base con la ficha como instrucción y el modelo con LoRA sin instrucciones. Abajo van las curvas de loss.
2. Para verla desde la laptop, en otra terminal del Spark entra a `salidas/` y ejecuta `python3 -m http.server 8000`. Luego abre `http://<ip-del-spark>:8000/comparacion.html`. Si la red no deja pasar el puerto, copia el archivo con `scp`.
3. Conversen con el personaje para probarlo fuera de la lista:
   ```bash
   llamafactory-cli chat config/chat_lora.yaml
   ```
4. Preparen la presentación: el personaje en una frase, el prompt donde más se nota el cambio, el prompt donde el personaje se rompió y qué cambiarían del dataset.

## Cierre (25 minutos)

Cada mesa tiene tres minutos para presentar su personaje con su comparación. Después, entre todos: ¿qué logra LoRA que no logra la ficha como instrucción?, ¿qué costó? y ¿para qué lo usarían en el proyecto final?

## Extra, fuera de las 3 horas: usar el personaje fuera de LLaMA Factory

Esto no se probó en el Spark: tómenlo como punto de partida.

1. Fusionen el adaptador con el modelo base en un modelo nuevo:
   ```bash
   llamafactory-cli export config/exportar.yaml
   ```
   Queda en `salidas/modelo_fusionado/`, con un `Modelfile` de Ollama que LLaMA Factory genera solo.
2. Para servirlo con llama-server, conviértanlo a GGUF con el `llama.cpp` del Spark (si falta algún paquete, instálenlo en `factoryEnv`) y levántenlo en otro puerto:
   ```bash
   python ~/llama.cpp/convert_hf_to_gguf.py salidas/modelo_fusionado --outfile salidas/personaje-q8_0.gguf --outtype q8_0
   ~/llama.cpp/build/bin/llama-server -m salidas/personaje-q8_0.gguf --port 8090 --jinja
   ```

## Qué hay en la carpeta

- `personaje.md`: la ficha del personaje, para completar.
- `personaje_ejemplo.md`: un personaje de ejemplo, para probar el script.
- `prompts_de_prueba.txt`: los 10 prompts de prueba, para completar.
- `temas.txt`: los temas de las preguntas del dataset.
- `scripts/generar_dataset.py`: genera el dataset con el modelo del Spark. Solo usa Python.
- `scripts/comparar.py`: la comparación del final. Necesita el entorno de LLaMA Factory.
- `config/`: la configuración de entrenamiento, de chat y de exportación de LLaMA Factory.
- `datos/dataset_info.json`: le dice a LLaMA Factory dónde está el dataset del personaje.
- `modelos/` y `salidas/`: el modelo base y todo lo que produzca la mesa. Nada de eso se sube al repo.
- `AGENTS.md` y `CLAUDE.md`: las reglas del proyecto, por si usan OpenCode para ayudarse.

Todos los datos son ficticios.
