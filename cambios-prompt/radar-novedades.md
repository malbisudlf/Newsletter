# Cambio al prompt de la rutina «Briefing diario»: radar de novedades

Pega cada bloque en el sitio que indica su título. Probado el 2026-10-11:
GitHub Trending, Hacker News (API de Algolia) y Hugging Face (su API pública)
responden desde el sandbox de Composio (`COMPOSIO_REMOTE_WORKBENCH`). Desde el
entorno de la rutina, Hacker News y Hugging Face están bloqueados (403 / DNS) y
GitHub Trending sí abre con WebFetch.

---

## 1. En la Fase 1 (Recopilación), añadir como tarea 10

10. **Radar de novedades — GitHub Trending, Hacker News y Hugging Face.** Se
    hace **todos los días, fines de semana incluidos**: no depende de ninguna
    newsletter. Ejecuta esta celda en `COMPOSIO_REMOTE_WORKBENCH` (desde el
    entorno de la rutina, Hacker News y Hugging Face no son accesibles; desde
    el sandbox de Composio sí):

    ```python
    import requests, re, json, time
    out = {}
    try:  # Hacker News: portada actual, con puntos y comentarios
        r = requests.get('https://hn.algolia.com/api/v1/search',
                         params={'tags': 'front_page', 'hitsPerPage': 30}, timeout=20).json()
        out['hn'] = [{'t': h['title'], 'pts': h['points'], 'com': h.get('num_comments'),
                      'url': h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}",
                      'hn': f"https://news.ycombinator.com/item?id={h['objectID']}",
                      'h': round((time.time() - h['created_at_i']) / 3600, 1)} for h in r['hits']
                     if time.time() - h['created_at_i'] < 36 * 3600]  # misma ventana de 36 h
    except Exception as e: out['hn'] = f'ERROR {e}'
    try:  # Hugging Face: modelos en tendencia
        r = requests.get('https://huggingface.co/api/models',
                         params={'sort': 'trendingScore', 'limit': 15}, timeout=20).json()
        out['hf_models'] = [{'id': m['id'], 'likes': m.get('likes'), 'dl': m.get('downloads'),
                             'created': m.get('createdAt', '')[:10], 'tags': m.get('pipeline_tag')} for m in r]
    except Exception as e: out['hf_models'] = f'ERROR {e}'
    try:  # Hugging Face: papers del día más votados
        r = requests.get('https://huggingface.co/api/daily_papers', params={'limit': 30}, timeout=20).json()
        ps = sorted(r, key=lambda p: -(p['paper'].get('upvotes') or 0))[:10]
        out['hf_papers'] = [{'t': p['paper']['title'], 'up': p['paper'].get('upvotes'),
                             'url': f"https://huggingface.co/papers/{p['paper']['id']}"} for p in ps]
    except Exception as e: out['hf_papers'] = f'ERROR {e}'
    try:  # GitHub Trending del día
        h = requests.get('https://github.com/trending?since=daily', timeout=20).text
        repos = []
        for art in h.split('<article')[1:16]:
            name = re.search(r'<h2[^>]*>\s*<a[^>]*href="/([^"/]+/[^"/]+)"', art)
            desc = re.search(r'<p class="col-9[^"]*"[^>]*>\s*(.*?)\s*</p>', art, re.S)
            today = re.search(r'([\d,]+) stars today', art)
            lang = re.search(r'itemprop="programmingLanguage">([^<]+)<', art)
            if name:
                repos.append({'repo': name.group(1),
                              'desc': re.sub(r'<[^>]+>|\s+', ' ', desc.group(1)).strip() if desc else '',
                              'hoy': today.group(1) if today else '?',
                              'lang': lang.group(1) if lang else '',
                              'url': f'https://github.com/{name.group(1)}'})
        out['gh'] = repos
    except Exception as e: out['gh'] = f'ERROR {e}'
    print(json.dumps(out, ensure_ascii=False, indent=1))
    ```

    Si el sandbox de Composio falla, GitHub Trending se puede abrir con WebFetch
    como respaldo. Para Hacker News y Hugging Face no hay respaldo: anota la
    caída en incidencias y sigue. Una fuente que devuelva `ERROR` es una
    incidencia, no un día tranquilo.

## 2. En la Fase 2 (Redacción), añadir antes de «Cuándo una ausencia es una ausencia»

### Qué hacer con el radar de novedades

Este bloque existe para que Mikel se entere de lo nuevo **antes de que llegue a
LinkedIn**. Aquí el criterio general de la Fase 2 se invierte: **manda la
novedad, no el tamaño**. Una herramienta recién publicada, un repo que se
dispara o un término que empieza a repetirse vale más que una ronda de
financiación que ya sale en todos los medios.

- **Cruza las tres fuentes.** Lo que aparece en dos a la vez (un repo en
  Trending que también está en la portada de HN, un modelo de HF del que se
  habla en HN) es la señal más fuerte del día: va primero.
- **GitHub Trending:** descarta los repos clásicos que siempre están (pytorch,
  listas «awesome», código histórico como Apollo-11) y quédate con los nuevos o
  con los que se disparan: miles de estrellas en un día es la señal.
- **Hacker News:** la portada mezcla de todo. Solo entran tecnología e IA con
  algo nuevo detrás (un lanzamiento, una herramienta, un incidente técnico, un
  paper). Fuera los juegos curiosos, la nostalgia y los debates de opinión.
  Cita el enlace original, y el hilo de HN solo si la discusión aporta (por
  ejemplo, si alguien que lo ha probado desmonta el anuncio).
- **Hugging Face:** la lista de tendencia arrastra modelos de hace semanas.
  Prioriza los creados en los últimos 7 días (campo `created`) y los de laboratorios conocidos o con un salto claro (tamaño, licencia
  abierta, capacidad nueva). Descarta las variantes cuantizadas o «uncensored»
  de modelos ya conocidos: son repaquetes, no novedades. De los papers, solo
  los que tengan muchos votos o encajen con una tendencia del día.
- **Detecta conceptos nuevos.** Si un término se repite en varias fuentes y no
  ha salido en briefings anteriores («harness engineering», «context
  engineering»…), explícalo en una frase: suele ser lo que en dos semanas está
  en todas partes.
- **Escepticismo:** muchas estrellas no significa que funcione. Si el repo es de
  hace dos días y nadie lo ha probado en serio, dilo.
- Anti-repetición: ningún repo, modelo o tema que ya haya salido en los últimos
  5 briefings. Si algo que salió aquí después explota (llega a prensa, lo compra
  alguien, lo adopta una grande), vuelve como `🔁 Seguimiento:`.

## 3. En la plantilla de salida, dentro de la sección 2, después de «Nuevos lanzamientos y actualizaciones»

**🔭 Antes de que sea tendencia** (3-4 viñetas, todos los días)

- **[Qué es, en una frase]** — la señal (p. ej. «25.000 estrellas en 24 h en
  GitHub», «500 puntos en Hacker News», «1.600 likes en Hugging Face en su
  primera semana»), por qué podría importar o por qué puede ser humo.
  [fuente primaria](url) (GitHub Trending / Hacker News / Hugging Face)

## 4. En «Cuándo una ausencia es una ausencia», añadir a la tabla de cadencias

| GitHub Trending / Hacker News / Hugging Face | **diaria, también fin de semana** | siempre disponibles |

Y la consecuencia: **la sección 2 ya no se omite entera el fin de semana**. Si
no hay TLDR AI, se omiten «IA General» y «Nuevos lanzamientos», pero «Antes de
que sea tendencia» sale igual.
