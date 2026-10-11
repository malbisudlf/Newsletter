# Radar de novedades del briefing diario (tarea 10 de la Fase 1).
# Se ejecuta en COMPOSIO_REMOTE_WORKBENCH: Hacker News y Hugging Face no son
# accesibles desde el entorno de la rutina, pero sí desde el sandbox de Composio.
import requests, re, json, time
out = {}
try:  # Hacker News: portada actual (últimas 36 h), con puntos y comentarios
    r = requests.get('https://hn.algolia.com/api/v1/search',
                     params={'tags': 'front_page', 'hitsPerPage': 30}, timeout=20).json()
    out['hn'] = [{'t': h['title'], 'pts': h['points'], 'com': h.get('num_comments'),
                  'url': h.get('url') or f"https://news.ycombinator.com/item?id={h['objectID']}",
                  'hn': f"https://news.ycombinator.com/item?id={h['objectID']}",
                  'h': round((time.time() - h['created_at_i']) / 3600, 1)} for h in r['hits']
                 if time.time() - h['created_at_i'] < 36 * 3600]
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
