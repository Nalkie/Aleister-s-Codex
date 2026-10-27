"""Traducción de la página al inglés.

Los textos fuente quedan en español.  En cada build, wrap_js() recorre los <script> de la página y envuelve con t() cada texto en español
(cadenas '...' / "..." -> __t('...'), plantillas `...${x}...` -> __t`...${x}...`).  En español __t() devuelve el texto tal cual; en inglés busca la
traducción en el diccionario tools/i18n_en.json (clave = el texto de origen, con las partes dinámicas ${...} como {0}, {1}...).
Si falta una entrada devuelve el español: la página nunca queda rota.

  python tools/i18n.py stats      cuenta los textos que se envolverían
  python tools/i18n.py extract    escribe tools/i18n_todo.json con lo que todavía no está en el diccionario

Usado por tools/page_only.py y tools/build_db.py.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DICT = os.path.join(HERE, 'i18n_en.json')
ACCENT = re.compile(r'[áéíóúñÁÉÍÓÚÑ¿¡ü]')
# palabras que en una frase de varias palabras delatan al español (sin las que también son inglés)
WORDS = set('''de la el los las que con para una del por sin más como esta este estos estas desde hasta entre sobre según cada donde cuando
mazo mazos carta cartas lista listas jugada jugadas formato puntos prohibida prohibidas limitada limitadas receta recetas arquetipo arquetipos
torneo torneos tocá abrí mirá elegí buscá armá guardá pegá copiá importá exportá todavía también solo todos todas ninguna ninguno hay
tiene tienen puede pueden sirve sirven usa usan juega juegan ver verla verlo cómo qué cuál cuáles dónde quién cuánto nuevo nueva nuevos nuevas
vigente actual actuales anterior anteriores resultados resultado victoria victorias puesto puestos copias copia entonces aunque porque
si no ni pero sino además luego antes después ahora siempre nunca algunas algunos otras otros misma mismo mismos mismas'''.split())
# textos cortos de la interfaz que no tienen tilde ni palabras de la lista de arriba
SHORT = set('''Cartas Carta Mazo Mazos Cerrar Buscar Guardar Importar Exportar Nuevo Eventos Evento Banlist Guía Gratis Personaje Fecha Torneo Jugadores
Ganador Comunidad Salida Código Tipo Nivel Rango Escala Atributo Mano Lado Principal Extra Copiar Cargar Eliminar Todos Todas Ninguna
Galería Lista Vista Sí Sin Más Menos Abrir Cancelar Aceptar Volver Siguiente Anterior Inicio Resultado Resultados Precio Precios Valor Total
Fuentes Cajas Caja Estructura Estructuras Personajes Otras Caja principal Mini caja Semana Mes Año Hoy Ayer Nunca Siempre Libre Prohibida
Limitada Semi-limitada Prohibidas Limitadas Genérica Staple Monstruos Monstruo Hechizos Hechizo Trampas Trampa Ritual Fusión Sincro Péndulo
Victoria Victorias Arquetipo Arquetipos Copia Copias Jugada Jugadas Receta Recetas Impresión Impresiones Personaje Personajes Torneos Mazos
Estrategia Estrategias Expansión Expansiones Rareza Rarezas Puntos Punto Gemas Gema Dinero Listo Hecho Aviso
Actual Actuales Anteriores Reciente Recientes Próximo Próximos Nuevo Nueva Nuevos Nuevas Ver Menos Mostrar Ocultar Quitar Agregar Vaciar
Cargando Generando Copiado Pegá Pegar Buscá Elegí Tocá Abrí Mirá Armá'''.split())


_NAMES = None
SKIP_RE = re.compile(r'^\[[^\]]+\]$|^[a-z]+(-[a-z]+)+$')


def card_names():
    """Nombres de cartas (en inglés): algunos llevan palabras en japonés o francés que parecen español."""
    global _NAMES
    if _NAMES is None:
        _NAMES = set()
        for f in ('ids.json',):
            fp = os.path.join(HERE, '..', f)
            if os.path.exists(fp):
                _NAMES |= set(json.load(open(fp, encoding='utf-8')))
        fp = os.path.join(HERE, '..', 'src', 'ygo_all.json')
        if os.path.exists(fp):
            _NAMES |= {c['name'] for c in json.load(open(fp, encoding='utf-8'))}
    return _NAMES


_FORCE = None


def force():
    """Textos que hay que traducir aunque no tengan tildes ni palabras del español (tools/i18n_force.json)."""
    global _FORCE
    if _FORCE is None:
        fp = os.path.join(HERE, 'i18n_force.json')
        _FORCE = set(json.load(open(fp, encoding='utf-8'))) if os.path.exists(fp) else set()
    return _FORCE


_VOCAB = None


def vocab():
    """Palabras que solo existen en español dentro de lo que ya está traducido (tokens de las claves menos los de las traducciones y los nombres de cartas).
    Sirve para encontrar textos sin tildes ni palabras gramaticales («Arte original», «Fuego») que se parecen a los que ya se tradujeron."""
    global _VOCAB
    if _VOCAB is None:
        tok = lambda x: {w.lower() for w in re.findall(r'[A-Za-zÀ-ÿ]{4,}', re.sub(r'<[^>]+>', ' ', x))}
        es, en = set(), set()
        for fn in ('i18n_en.json', 'i18n_static.json'):
            fp = os.path.join(HERE, fn)
            if os.path.exists(fp):
                for k, v in json.load(open(fp, encoding='utf-8')).items():
                    es |= tok(k)
                    en |= tok(v)
        nt = set()
        for n in card_names():
            nt |= tok(n)
        _VOCAB = es - en - nt
    return _VOCAB


_SKIP = None


def skip():
    """Textos que nunca se traducen aunque parezcan españoles: nombres usados como claves en el código (tools/i18n_skip.json)."""
    global _SKIP
    if _SKIP is None:
        fp = os.path.join(HERE, 'i18n_skip.json')
        _SKIP = set(json.load(open(fp, encoding='utf-8'))) if os.path.exists(fp) else set()
    return _SKIP


def is_spanish(text):
    if text in skip():
        return False
    if text in force():
        return True
    t0 = text.strip()
    if t0 in card_names() or SKIP_RE.match(t0) or t0.startswith(('http://', 'https://')):
        return False
    if _is_spanish(text):
        return True
    plain = re.sub(r'<[^>]+>', lambda m: ' ' + ' '.join(re.findall(r'(?:title|placeholder|aria-label|alt)="([^"]*)"', m.group(0))) + ' ', text)
    return any(w.lower() in vocab() for w in re.findall(r'[A-Za-zÀ-ÿ]{4,}', plain))


def _is_spanish(text):
    """¿Este texto fijo es del español de la interfaz?  (HTML de las plantillas incluido: se ignoran nombres de etiquetas y de atributos)."""
    t = re.sub(r'<[^>]+>', lambda m: ' ' + ' '.join(re.findall(r'(?:title|placeholder|aria-label|alt)="([^"]*)"', m.group(0))) + ' ', text)
    t = re.sub(r'\$\{[^}]*\}', ' ', t)
    if ACCENT.search(t):
        return True
    words = re.findall(r"[A-Za-zÀ-ÿ]+", t)
    if not words:
        return False
    low = [w.lower() for w in words]
    if sum(1 for w in low if w in WORDS) >= 1 and len(words) >= 2:
        return True
    # plantilla con marcadores ("{0} de {1}"): basta una palabra suelta del español como "de" o "y"
    if re.search(r'\{\d+\}', text) and any(w in WORDS or w == 'y' for w in low):
        return True
    return len(words) <= 3 and all(w in SHORT or w.capitalize() in SHORT for w in words if len(w) > 2) and any(w in SHORT or w.capitalize() in SHORT for w in words)


# ---------------------------------------------------------------- tokenizador de JS (comentarios, cadenas, plantillas anidadas, regex)
FN = '__t'          # nombre de la función de traducción en la página (un nombre corto como t chocaría con variables locales)
KEYWORDS = {'return', 'typeof', 'case', 'else', 'in', 'of', 'yield', 'await', 'throw', 'void', 'delete', 'do'}
BS = chr(92)       # la barra invertida
NL = chr(10)       # salto de línea
WS = ' ' + chr(9) + chr(13) + chr(10)   # espacio en blanco
REGEX_PREV = set('(,=:[!&|?{};+-*%<>~^') | {'return', 'typeof', 'case', 'in', 'of', 'delete', 'void', 'throw', 'new', 'else', 'do'}


def tokenize(js):
    """Lista de (inicio, fin, 's') por cada cadena y (inicio, fin, 'T', partes, expresiones) por cada plantilla, también las anidadas.
    Una sola pasada: el contenido de cada ${...} se recorre con las mismas reglas (comentarios, cadenas, plantillas, regex)."""
    n = len(js)
    out = []

    def skip_string(i):
        q = js[i]
        j = i + 1
        while j < n:
            if js[j] == BS:
                j += 2
                continue
            if js[j] == q:
                return j + 1
            j += 1
        raise ValueError('cadena sin cerrar en %d' % i)

    def skip_regex(i):
        j = i + 1
        in_class = False
        while j < n:
            c = js[j]
            if c == BS:
                j += 2
                continue
            if c == '[':
                in_class = True
            elif c == ']':
                in_class = False
            elif c == '/' and not in_class:
                j += 1
                while j < n and js[j].isalpha():
                    j += 1
                return j
            elif c == NL:
                return None
            j += 1
        return None

    def template(i):
        """i apunta a la comilla invertida. Devuelve la posición siguiente al cierre."""
        j = i + 1
        parts, exprs = [], []
        a = j
        while j < n:
            c = js[j]
            if c == BS:
                j += 2
                continue
            if c == '`':
                parts.append((a, j))
                out.append((i, j + 1, 'T', parts, exprs))
                return j + 1
            if c == '$' and js[j + 1:j + 2] == '{':
                parts.append((a, j))
                end = scan(j + 2, True)
                exprs.append((j + 2, end))
                j = end + 1
                a = j
                continue
            j += 1
        raise ValueError('plantilla sin cerrar en %d' % i)

    def scan(i, in_expr):
        """Recorre hasta el final (o hasta la } que cierra la expresión). Devuelve la posición de esa }."""
        prev = ''
        depth = 0
        while i < n:
            c = js[i]
            if c in WS:
                i += 1
                continue
            if c == '/' and js[i + 1:i + 2] == '/':
                k = js.find(NL, i)
                i = n if k < 0 else k
                continue
            if c == '/' and js[i + 1:i + 2] == '*':
                i = js.index('*/', i) + 2
                continue
            if c == "'" or c == '"':
                j = skip_string(i)
                out.append((i, j, 's'))
                prev = 'str'
                i = j
                continue
            if c == '`':
                i = template(i)
                prev = 'str'
                continue
            if c == '/':
                if prev in REGEX_PREV or prev == '':
                    j = skip_regex(i)
                    if j:
                        prev = 'regex'
                        i = j
                        continue
                prev = '/'
                i += 1
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                if in_expr and depth == 0:
                    return i
                depth -= 1
            if c.isalnum() or c in '_$':
                j = i
                while j < n and (js[j].isalnum() or js[j] in '_$'):
                    j += 1
                prev = js[i:j]
                i = j
                continue
            prev = c
            i += 1
        return n

    scan(0, False)
    return out


def unescape(lit):
    """Valor de una cadena '...' o "..." de JS."""
    body = lit[1:-1]
    return re.sub(r'\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)', lambda m: {'n': '\n', 't': '\t', 'r': '\r'}.get(m.group(1), chr(int(m.group(1)[1:], 16)) if m.group(1)[0] in 'ux' and len(m.group(1)) > 1 else m.group(1)), body)


def template_key(js, tok):
    """Texto de origen de una plantilla con {0}, {1}... en lugar de cada ${...}."""
    parts, exprs = tok[3], tok[4]
    s = ''
    for k, (a, b) in enumerate(parts):
        s += js[a:b]
        if k < len(exprs):
            s += '{%d}' % k
    return s


def collect(js):
    """[(inicio, fin, clave, tipo)] de lo que hay que envolver."""
    items = []
    toks = tokenize(js)
    toks.sort(key=lambda t: (t[0], -t[1]))
    for tok in toks:
        a, b, kind = tok[0], tok[1], tok[2]
        # una plantilla ya etiquetada (ident`...`) no se toca
        k = a - 1
        while k >= 0 and js[k] in ' \t':
            k -= 1
        if kind == 'T' and k >= 0 and (js[k].isalnum() or js[k] in '_$)]'):
            w = k
            while w >= 0 and (js[w].isalnum() or js[w] in '_$'):
                w -= 1
            if js[k] in ')]' or js[w + 1:k + 1] not in KEYWORDS:    # ident`...` (plantilla etiquetada): no se toca; return`...` sí
                continue
        if kind == 's':
            # clave de objeto {'texto':...} o propiedad: no es un texto de pantalla
            after = js[b:b + 40].lstrip()
            if after.startswith(':') and not after.startswith('::'):
                before = js[max(0, a - 40):a].rstrip()
                if before.endswith('{') or before.endswith(','):
                    # {'clave': valor} o  ,'clave': valor  -> clave (pero ?'a':'b' del ternario no entra: lleva ? antes)
                    continue
            val = unescape(js[a:b])
            if is_spanish(val):
                items.append((a, b, val, 's', []))
        else:
            key = template_key(js, tok)
            if is_spanish(key):
                ctx = [js[x:y][:70] for x, y in tok[4]]
                items.append((a, b, key, 'T', ctx))
    return items


def wrap_js(js):
    """Devuelve el JS con t() alrededor de cada texto en español, y las claves encontradas."""
    items = collect(js)
    items.sort(key=lambda x: (x[0], -x[1]))
    # solo se envuelve lo que no está dentro de otro texto ya envuelto: las plantillas anidadas se envuelven por separado,
    # así que se aplica desde el final para no mover posiciones
    out = js
    for a, b, key, kind, _ in sorted(items, key=lambda x: -x[0]):
        if kind == 's':
            out = out[:a] + FN + '(' + out[a:b] + ')' + out[b:]
        else:
            out = out[:a] + FN + out[a:b] + out[b:]
    info = {}
    for a, b, k, kind, ctx in items:
        info.setdefault(k, {'pos': a, 'ctx': ctx})
    return out, sorted(info), info


def wrap_page(html):
    """Aplica wrap_js a cada <script> sin src."""
    keys, info = set(), {}

    def rep(m):
        js, k, inf = wrap_js(m.group(2))
        keys.update(k)
        for key, v in inf.items():
            info.setdefault(key, {'pos': m.start(2) + v['pos'], 'ctx': v['ctx']})
        return m.group(1) + js + m.group(3)

    out = re.sub(r'(<script\b(?![^>]*\bsrc=)[^>]*>)(.*?)(</script>)', rep, html, flags=re.S)
    return out, sorted(keys), info


def cooked(key):
    """El texto de origen tal como se ve en pantalla (sin las barras de escape de JS): es lo que se le da a quien traduce."""
    return re.sub(r'\\(.)', lambda m: {'n': ' ', 't': ' '}.get(m.group(1), m.group(1)), key)


def load_dict():
    return json.load(open(DICT, encoding='utf-8')) if os.path.exists(DICT) else {}


def apply(html):
    """Para el build: envuelve con t() los textos en español de los scripts y mete los diccionarios.
    Va ANTES de inyectar los datos grandes (YGMDATA, DLDATA...): no hay que recorrerlos."""
    wrapped, keys, _ = wrap_page(html)
    en = load_dict()
    sp = os.path.join(HERE, 'i18n_static.json')
    st = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    missing = [k for k in keys if k not in en]
    print('i18n: %d textos envueltos, %d sin traducción (en inglés se ven en español)' % (len(keys), len(missing)))
    for k in missing[:10]:
        print('   falta:', repr(k[:90]))
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    wrapped = wrapped.replace('/*__I18NEN__*/{}', dump({k: en[k] for k in keys if k in en}))
    wrapped = wrapped.replace('/*__I18NST__*/{}', dump(st))
    return wrapped


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'stats'
    src = open(os.path.join(HERE, '..', 'src.html'), encoding='utf-8').read()
    gx = os.path.join(HERE, 'guide_extra.js')
    if os.path.exists(gx):
        src = src.replace('/*__GUIDEX__*/', open(gx, encoding='utf-8').read())
    wrapped, keys, info = wrap_page(src)
    d = load_dict()
    todo = [k for k in keys if k not in d]
    print('textos únicos en español:', len(keys), '| ya traducidos:', len(keys) - len(todo), '| faltan:', len(todo), '| KB de texto:', sum(len(k) for k in keys) // 1024)
    if cmd == 'extract':
        rows = [{'key': k, 'text': cooked(k), 'ctx': info[k]['ctx']} for k in sorted(todo, key=lambda k: info[k]['pos'])]
        json.dump(rows, open(os.path.join(HERE, 'i18n_todo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('tools/i18n_todo.json escrito')
