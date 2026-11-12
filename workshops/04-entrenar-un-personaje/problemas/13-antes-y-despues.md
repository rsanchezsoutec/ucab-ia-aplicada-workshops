# Problema 13 · Antes y después

La prueba de que el entrenamiento sirvió: los mismos 10 prompts de prueba, que el modelo nunca vio, a tres versiones del modelo.

1. El modelo base, sin ninguna instrucción.
2. El modelo base, con la ficha del personaje como instrucción.
3. El modelo con el adaptador LoRA, sin ninguna instrucción.

La segunda columna es la importante: si con la ficha ya habla igual, el LoRA no hacía falta.

**Entregable:** `salidas/13-comparacion.html`, la página que la mesa proyecta para presentar su personaje. Por cada prompt, las tres respuestas lado a lado; arriba, el prompt donde más se nota el cambio y el prompt donde el personaje se rompió; abajo, las curvas de loss del problema 12. Que se abra sin internet.

**Condiciones de la mesa:**

- Las tres versiones responden en las mismas condiciones: el mismo prompt, la misma forma de generar y sin muestreo al azar.
- El modelo con LoRA no recibe la ficha ni ningún mensaje de sistema.
- Las respuestas se generan con el mismo formato de chat con el que se entrenó.

**Cada mesa tiene tres minutos para presentarla:** el personaje en una frase, el prompt donde más se nota el cambio y el que lo rompió.
