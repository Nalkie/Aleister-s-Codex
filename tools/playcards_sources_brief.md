# Brief: fuentes y límites de las fichas tácticas

Trabajás sobre UN archivo de fichas tácticas (te lo asigna quien te lanzó). Cada ficha ya tiene su texto escrito (plan, iniciadores, puntos de interrupción, side/skill). Tu trabajo es agregar a **cada ficha de tu archivo**:

- `sources`: de 2 a 6 páginas reales que respaldan lo que dice la ficha.
- `limits` (opcional, 0 a 3): avisos honestos sobre qué desconfiar de esa ficha.

No cambies ningún otro campo. Si ves un error de hecho en una ficha (una carta que no hace lo que dice, un número mal), NO lo corrijas: anotalo en tu informe final con la clave de la ficha y la frase exacta.

## Por qué existe esto

La página muestra al pie de cada ficha un bloque «Fuentes y límites» para que quien la lee sepa de dónde sale cada cosa y hasta dónde confiar. Una fuente inventada o que no dice lo que la ficha dice es peor que no tener fuente. Por eso: **solo entra una página que abriste y leíste**.

## Formato (contracts/playcard.ts)

```json
"sources": [
  {"name": "Snake-Eye Ash", "url": "https://yugipedia.com/wiki/Snake-Eye_Ash", "kind": "cards", "checked": "2026-10-27"},
  {"name": "Snake-Eye Deck | Duel Links Meta", "url": "https://www.duellinksmeta.com/...", "kind": "guide", "checked": "2026-10-27"}
],
"limits": [
  {"es": "…", "en": "…"}
]
```

- `kind`: `cards` (texto oficial de las cartas), `guide` (guía o análisis de estrategia del mazo), `results` (resultados de torneos), `rules` (reglas, rulings, cómo funciona el formato), `list` (banlist, puntos Genesys, lista de cartas del formato).
- `checked`: `2026-10-27`.
- `name`: **copiá el título real de la página** (se puede acortar, pero las palabras propias tienen que estar). El gate compara el `name` con el título que baja el verificador: si le ponés «Snake-Eye Ash» a una página que se titula «Frozen Rose», falla.
- `url`: https, sin parámetros de seguimiento (`utm_*`, `fbclid`). No se aceptan YouTube, Reddit, X/Twitter, Discord, Facebook ni TikTok: no se pueden verificar. Tampoco paywalls.
- Sin URLs repetidas dentro de la misma ficha. Una misma fuente general (la banlist de Konami, una página de formato) sí puede repetirse entre fichas.

## Qué tiene que respaldar cada ficha

Mirá lo que afirma la ficha y buscá, en este orden de prioridad:

1. **El texto de las cartas clave** (iniciadores y puntos de interrupción): Yugipedia (`https://yugipedia.com/wiki/<Nombre>`), YGOPRODeck (`https://ygoprodeck.com/card/<slug>-<id>`, el ID real sale de la API), Duel Links Meta para Duel Links. Una o dos cartas centrales alcanzan, no hace falta una por carta.
2. **Una guía o análisis del mazo** que sustente el plan: YGOrganization, Duel Links Meta (páginas de mazo y artículos), YuGiOh Meta, Format Library para formatos retro, Road of the King y KotaCards para OCG, YGOPRODeck articles, blogs de jugadores reconocidos.
3. **Resultados** si la ficha dice que el mazo gana o se juega (páginas de torneo, top decks).
4. **El formato**: la banlist o las reglas si la ficha depende de ellas (Konami para Advanced, Format Library para Edison/Goat/HAT, Konami/YGOrganization para Genesys, Duel Links Meta para Duel Links).

El Side Deck / «Skill y ajustes» casi siempre es criterio de la redacción: no inventes una fuente para eso. Si ninguna fuente lo respalda, dejalo y decilo en un `limits` (ver abajo).

## Cómo abrir las páginas

- Abrí cada URL con WebFetch (o WebSearch para encontrarla) y **leé que diga lo que la ficha dice**. No armes URLs por intuición: YGOPRODeck ignora el texto antes del ID y devuelve OTRA carta con 200; Yugipedia devuelve 404 si el título no es exacto.
- Yugipedia con WebFetch devuelve 403. Usá su API para leer: `curl -s -A "AleistersCodex/1.0 (briloizzo5@gmail.com)" "https://yugipedia.com/api.php?action=parse&page=Snake-Eye_Ash&prop=wikitext&format=json&redirects=1"`. El enlace que va en la ficha sigue siendo la página normal `https://yugipedia.com/wiki/Snake-Eye_Ash`.
- ID de YGOPRODeck: `https://db.ygoprodeck.com/api/v7/cardinfo.php?name=<Nombre exacto>` → campo `id`; la página es `https://ygoprodeck.com/card/<slug>-<id>`... si dudás del slug, probá con la página y revisá el título.
- Duel Links Meta: `https://www.duellinksmeta.com/api/v1/...` sirve para leer; el enlace público es la página del sitio.

## `limits`: qué escribir

Avisos concretos y verdaderos, en voseo rioplatense como el resto de la página (en español: «desterrar», nunca «banish» ni «banear»). Ejemplos de lo que sí sirve:

- «El Side Deck es criterio de la redacción: no hay una estadística de torneos que lo respalde.»
- «Las guías que encontramos son de antes de la banlist del 19 de octubre de 2026: revisá qué cartas siguen legales.»
- «Hay una sola guía sobre este mazo y es de agosto.»
- «El texto de una carta clave cambió de versión: la ficha usa el texto de la época del formato.» (retro)

No escribas avisos genéricos que valen para cualquier ficha (la página ya agrega sola «criterio editorial» y «Revisada el …»). Si de verdad no hay nada que avisar, `limits` se omite. Máximo 3, cada uno de 3 a 400 caracteres, en `es` y `en`.

## Cómo comprobar tu trabajo (obligatorio antes de terminar)

Desde la raíz del proyecto:

```
python tools/playcards.py <tu archivo>        # el esquema: tiene que decir "OK: N fichas válidas"
python tools/playcards_links.py <tu archivo>  # abre CADA url: tiene que terminar con "sin verificar: 0" y "con el nombre que no corresponde al título: 0"
```

Si una URL falla (404, bloqueo, título de error), buscá otra: no la dejes. Si el verificador marca un `name` que no corresponde al título, corregí el `name` con el título real o cambiá de fuente.

## Si no podés

Si para un mazo no encontrás 2 fuentes reales que puedas abrir, **no inventes**: dejá esa ficha sin tocar, decilo en tu informe como BLOCKED con qué buscaste, y seguí con las demás.

## Informe final (corto)

Por ficha: cuántas fuentes quedaron, de qué tipo, y los `limits` que pusiste. Después, aparte: (1) afirmaciones de la ficha que NO pudiste respaldar con ninguna fuente (clave + frase exacta), (2) errores de hecho que viste, (3) fichas BLOCKED. Terminá con la salida de los dos comandos de comprobación.

No toques otros archivos, no hagas commits, no corras el build de la página.
