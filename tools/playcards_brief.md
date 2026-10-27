# Cómo redactar las fichas tácticas de un formato

Trabajás en `F:\pepo\Aleister-s-Codex-main\Aleister-s-Codex-main` (no es un repo git; Python con `PYTHONIOENCODING=utf-8`). Tu trabajo: escribir **un solo archivo**, `src/playcards/<FORMATO>.json`, con una ficha táctica por cada mazo de tier 1 a 3 de tu formato. No toques ningún otro archivo (otros redactores escriben los suyos al mismo tiempo).

## Qué leer primero (en este orden)
1. `contracts/playcard.ts`: el contrato exacto (4 secciones: win, starters, chokepoints, side + updated). Todo texto lleva `{es, en}`.
2. `src/playcards.json`: la ficha ya escrita `edison/blackwing`. Es el ejemplo de tono, largo y nivel de detalle: viñetas directas, una idea por viñeta, escaneables en celular.
3. `python tools/playcards_decks.py <FORMATO>`: lista tus mazos con la **clave** que debés usar (`formato/slug`), la receta (main, extra, side) y el tier.

## De dónde sale la información
Investigá **en línea** (WebSearch y WebFetch): guías de mazo de Yugipedia, YGOPRODeck (artículos y deck pages), Format Library (formatlibrary.com), Dueling Book, Duelist Saga/ygoprodeck "how to play", reportes de torneos, sitios de formatos retro (Goat: goatformat/ygopro, Edison: edisonformat.com, HAT) y videos transcriptos si los hay. Cruzá al menos dos fuentes para cada afirmación táctica. Parafraseá con tus palabras: no copies frases de las fuentes ni listas enteras.

## Reglas duras (el validador las hace cumplir; si fallan, no hay ficha)
- Nombres de carta en **inglés exacto** como están en `src/ygo_all.json`. Todas las cartas deben existir y, en Edison, Goat y HAT, ser legales en ese formato (el pool está en `src/formats.json`). Un mazo retro no usa Ash Blossom ni Nibiru: en retro las interrupciones son trampas, Effect Veiler y cartas de la época, las que existan en el pool.
- `starters`: 1 a 3 rutas, de 1 o 2 cartas que estén en la lista (main o extra) del mazo.
- `chokepoints`: 1 a 5 cartas del rival (legales en el formato) contra las que el mazo pierde, con `step` ∈ summon | activation | resolution | attack | main | end y en `stepText` el paso exacto de la cadena o de la fase donde duele más. En formatos modernos (adv, ocg, gen) incluí los handtraps que de verdad importen (Ash Blossom & Joyous Spring, Droll & Lock Bird, Nibiru, the Primal Being, Infinite Impermanence, Effect Veiler, Maxx "C", Mulcharmy Fuwalos, etc.) solo si afectan a ese mazo, y decí en qué eslabón de su cadena rompen la jugada.
- `side`: `first` e `in`/`out` con la **misma cantidad total** de copias entrando y saliendo; las cartas que entran deben estar en el Side de la lista de ejemplo del mazo y las que salen en su Main/Extra, con `qty` que no pase de lo que la lista juega. `basis`: `"tournament"` solo si una fuente muestra listas reales de side o una guía explícita de ir primero/segundo; si es criterio tuyo, `"editorial"`.
- `win.plan` ∈ control | otk | grind | tempo | combo | burn | stun; `win.pace` ∈ fast | medium | slow; 2 a 4 viñetas.
- Cada texto de 3 a 400 caracteres, español rioplatense neutro (vos), directo, sin relleno, y el inglés equivalente. Sin guiones largos (— ni –).
- `updated`: `2026-10-26`.

## Honestidad
- No inventes. Si no conseguís información suficiente y confiable de un mazo, **no escribas su ficha**: es mejor que falte a que esté inventada. Un mazo con una ficha floja o dudosa se omite.
- Verificá lo que dice cada carta contra `src/ygo_all.json` (campo `desc`, `level`, `type`) antes de afirmar qué hace o su nivel. Los textos de efectos de las cartas están ahí.
- Para el OCG y los mazos de 2026, las fuentes pueden ser pocas: usá lo que encuentres y omití lo que no puedas respaldar.

## Cómo validar (obligatorio antes de terminar)
`python tools/playcards.py src/playcards/<FORMATO>.json` valida solo tu archivo contra las cartas y las listas reales. Corregí hasta que diga `OK`. No corras `python tools/playcards.py` sin argumentos (escribe `data/play.js` y lo hace quien te encargó la tarea).

## Qué devolver
Un informe corto: cuántas fichas escribiste, cuáles omitiste y por qué, y las 3 o 4 fuentes principales que usaste (URL). Nada más.
