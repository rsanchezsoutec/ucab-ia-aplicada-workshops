# Problema 11 · El dataset del personaje

Lo resuelven B y C con OpenCode mientras A instala LLaMA Factory.

La mesa inventa un personaje. Para que el modelo aprenda a hablar como él, hacen falta cientos de ejemplos de pregunta y respuesta en su voz, y nadie los va a escribir a mano. El modelo que ya sirve el Spark puede escribirlos.

Primero, C escribe la ficha del personaje en `personaje.md` y los 10 prompts de prueba en `prompts_de_prueba.txt`. `personaje_ejemplo.md` sirve de modelo. Después, la mesa le pide a OpenCode un programa que genere el dataset con el modelo del Spark.

**Material:** `personaje.md`, `prompts_de_prueba.txt` y `temas.txt`, una lista de temas para que las preguntas sean variadas.

**Entregable:** `datos/personaje.json` con entre 300 y 500 ejemplos, en el formato que lee LLaMA Factory y registrado en `datos/dataset_info.json`, y `salidas/11-dataset.html`: cuántos ejemplos hay, de qué temas, cuántas respuestas arrancan igual y 10 ejemplos al azar para leer.

**Condiciones de la mesa:**

- La ficha no va dentro de los ejemplos: el modelo tiene que hablar como el personaje sin que nadie se lo pida.
- Ninguno de los 10 prompts de prueba entra al dataset. Si entra, la comparación del problema 13 no dice nada.
- Si más del 20 % de las respuestas arrancan con las mismas palabras, el dataset no sirve: el personaje va a sonar a disco rayado.
- El programa usa solo la biblioteca estándar de Python y el modelo del Spark. Si se corta, no se pierde lo que ya generó.

**Antes de entrenar, la mesa lee 20 ejemplos y borra los malos.** El modelo va a aprender exactamente lo que haya en ese archivo.
