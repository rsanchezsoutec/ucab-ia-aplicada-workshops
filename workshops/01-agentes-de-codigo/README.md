# Workshop 1 · Agentes de código en el trabajo

Cinco problemas de una empresa ficticia de compras, para resolver en equipos de tres con OpenCode y un modelo local servido por llama-server en un DGX Spark. Se resuelven con lo que se vio en la charla "Agentes de código en el entorno laboral".

No hay pasos guiados. Cada problema dice qué hay que entregar y qué condición tiene que cumplir, y cómo llegar ahí lo decide el equipo. Discutan entre los tres antes de escribirle al agente.

## Antes de empezar

1. Entra al Spark de tu equipo por SSH.
2. Copia esta carpeta en tu usuario y entra en ella.
3. Ejecuta `bash preparar.sh` una sola vez.
4. Abre OpenCode con `opencode`. Ya viene configurado para usar el modelo local que sirve llama-server en el Spark. Si no responde, avisa al facilitador.

## Cómo se entrega

Cada problema termina en una página HTML en `salidas/` que un jefe pueda abrir y usar en una reunión sin que nadie se la explique. Tiene que verse bien proyectada, con lo importante arriba, y abrirse sin internet. Las cinco páginas son para la misma empresa, así que deberían parecer de la misma empresa.

Para verlas desde tu laptop, abre otra terminal en el Spark, entra en `salidas/` y ejecuta `python3 -m http.server 8000`. Luego abre `http://<ip-del-spark>:8000` en tu navegador. Si la red no lo permite, cópialas con `scp`.

## Los problemas

Se resuelven en orden y en la misma carpeta. El equipo pasa al siguiente cuando lo anuncia el facilitador.

| # | Problema |
| --- | --- |
| 1 | [La reunión con proveedores](problemas/1-la-reunion-con-proveedores.md) |
| 2 | [El informe de cada lunes](problemas/2-el-informe-de-cada-lunes.md) |
| 3 | [La auditoría](problemas/3-la-auditoria.md) |
| 4 | [Finanzas no se fía](problemas/4-finanzas-no-se-fia.md) |
| 5 | [El tablero del gerente](problemas/5-el-tablero-del-gerente.md) |

## Qué hay en la carpeta

- `pedidos.csv`: 352 pedidos de 2026 a seis proveedores, con sede, categoría, fechas y estado.
- `proveedores.csv`: los seis proveedores y sus correos.
- `AGENTS.md` y `CLAUDE.md`: las reglas del proyecto.
- `opencode.json`: la configuración de OpenCode del proyecto.
- `.env` y `secretos/`: una clave y un contrato falsos.
- `.claude/skills/`: carpeta vacía.

Todos los datos son ficticios.
