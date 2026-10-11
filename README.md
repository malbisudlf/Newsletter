# Newsletter
Solo un documento para guardar el historial de mis newsletters

- `historial-briefings.json` — historial de todos los briefings enviados, una entrada por
  fecha. La rutina lo actualiza directamente en `main` después de cada envío.
- `.claude/skills/briefing-diario/` — la skill con todas las instrucciones del briefing
  diario (`SKILL.md`) y el script del radar de novedades (`radar.py`). Es la única copia:
  para cambiar el briefing se cambia aquí, y la rutina usa siempre lo que haya en `main`.

## Prompt de la rutina

La rutina programada solo necesita este texto; todo lo demás está en la skill:

```
Ejecuta la skill `briefing-diario` de este repositorio y sigue sus instrucciones al pie de
la letra, empezando por la condición de arranque. Si la skill no aparece en tu lista de
skills, lee `.claude/skills/briefing-diario/SKILL.md` directamente y síguelo igual.
```
