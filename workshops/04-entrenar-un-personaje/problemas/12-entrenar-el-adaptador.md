# Problema 12 · Entrenar el adaptador

Con el entorno que instaló A y el dataset del problema 11, la mesa entrena un adaptador LoRA sobre Qwen3-4B-Instruct-2507 con LLaMA Factory. LLaMA Factory trae un ejemplo para Qwen3 en `LLaMA-Factory/examples/train_lora/qwen3_lora_sft.yaml`, que es el que usa el playbook de NVIDIA.

Pídanle a OpenCode la configuración y el entrenamiento, y que les explique cada número antes de lanzarlo. Discutan entre los tres si están de acuerdo.

**Entregable:** la configuración en `config/entrenar.yaml`, el adaptador en `salidas/adaptador/` y `salidas/12-entrenamiento.html`: los hiperparámetros que usaron y por qué, cuánto tardó y las curvas de loss de entrenamiento y de evaluación.

**Condiciones de la mesa:**

- Un 10 % del dataset queda aparte para medir si el modelo aprende o memoriza.
- El entrenamiento corre en segundo plano y deja su log en un archivo. Si se corta la conexión o se cierra OpenCode, el entrenamiento sigue.
- La configuración vive en un archivo del proyecto, no en la memoria de nadie.

**Mientras corre, lean la curva:** si el loss de evaluación sube mientras el de entrenamiento sigue bajando, el modelo está memorizando.
