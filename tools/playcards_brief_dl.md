# Anexo para las fichas de Duel Links

Leé primero `tools/playcards_brief.md` (reglas generales, honestidad, validación) y `contracts/playcard.ts`. Esto es lo que cambia en Duel Links:

- Las claves son `dl/<slug>` con el nombre del mazo tal como lo muestra la página (los de Rush terminan en "(Rush)", p. ej. `dl/wyrms-rush`). `python tools/playcards_decks.py dl` las lista con receta, Skill más usado y tier.
- **No hay Side Deck ni handtraps de mano en el mismo sentido que el TCG.** Duel Links tiene reglas propias: Main de 20 a 30 cartas, Extra de hasta 9, el Skill del duelista, el límite de copias propio del juego, y el orden de turno (quien va primero no ataca en su primer turno). Escribí la ficha para ese juego, no para el TCG.
- El objeto lleva un campo extra `skills` (1 a 3): los Skills que conviene llevar con el mazo (el más usado primero; los demás son alternativas), con `name` en inglés tal como figura en el juego y `why` en es y en. El Skill más usado de cada mazo está en la lista de `playcards_decks.py`.
- `side.first` y `side.second` aquí son los **ajustes del Main Deck** al ir primero o segundo: `in` es cualquier carta que exista en Duel Links (validada contra `dl/cards.json`), `out` es una carta del Main o Extra de la lista. Entran y salen las mismas copias en total. `basis: "editorial"` salvo que una fuente lo diga.
- `chokepoints`: las cartas del rival que más duelen en Duel Links (trampas y cartas de interrupción que existan en el juego, p. ej. Solemn Judgment, Mirror Force, Ash Blossom & Joyous Spring, Nibiru si están; verificá que existan), con el paso exacto de la cadena.
- Fuentes: Duel Links Meta (duellinksmeta.com), Yugipedia/Fandom de Duel Links, YGOPRODeck Duel Links, DLM deck guides, canales/guías de la comunidad. Cruzá al menos dos fuentes y omití los mazos que no puedas respaldar.
- El Skill lo da el juego: describí qué hace el Skill con tus palabras y por qué sirve a ese mazo.
- Fecha `updated`: la de hoy (2026-10-27).
