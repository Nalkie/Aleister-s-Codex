# Traducción al inglés de Aleister's Codex: instrucciones y glosario

La página es un sitio de análisis competitivo de Yu-Gi-Oh! (meta de torneos, recetas de mazos, banlist, cartas, Duel Links) escrito en español rioplatense
informal (voseo: "tocá", "abrí", "mirá"). La versión en inglés debe sonar como la habría escrito un jugador competitivo de habla inglesa:
clara, directa, sin frases de relleno, mismo nivel de formalidad que el original (cercano, no corporativo). Segunda persona neutra ("tap", "open", "see").

## Reglas obligatorias (un validador automático las comprueba)
1. Conservá los marcadores `{0}`, `{1}`, ... exactamente: mismos números, misma cantidad. Podés cambiar su orden dentro de la frase.
   Cada marcador es un valor que la página rellena (un número, un nombre, otro texto): el campo `ctx` del lote dice qué es cada uno.
2. Conservá las etiquetas HTML y sus atributos tal cual (`<b>`, `<span class="chip">`, `<small>`, `<em>`, `<a href=...>`...). Solo se traduce el texto
   visible y el valor de `title`, `placeholder`, `aria-label` y `alt`. No agregues ni quites etiquetas. Conservá las entidades (`&amp;`, `&nbsp;`).
3. Conservá los espacios del principio y del final de cada texto (muchos son fragmentos que se pegan a otros: " Límite " -> " Limit ").
4. No uses `${`, comillas invertidas, ni saltos de línea nuevos.
5. No traduzcas nombres propios: cartas (Ash Blossom & Joyous Spring), arquetipos (Elfnote, Branded), formatos (Genesys, Duel Links, Speed Duel,
   Rush Duel, OCG, TCG, Edison, Goat, HAT), sitios (YuGiOh Meta, YGOPRODeck, TCGplayer, Cardmarket), "tier", "Top 4", "Staple", "Engines".
6. Si un texto ya está en inglés o es un nombre propio, devolvelo igual.
7. Los textos son fragmentos de pantalla: una frase puede continuar en otro fragmento. Respetá el sentido de cada fragmento por separado y su puntuación
   (si termina en ":" o en "(", la traducción también).

## Glosario (usalo siempre igual)
| Español | Inglés |
|---|---|
| mazo / deck | deck |
| receta (lista de referencia de un mazo) | decklist ("Reference decklist"); "receta más usual" = "most common decklist" |
| arquetipo | archetype |
| carta(s) | card(s) |
| banlist | banlist |
| prohibida / limitada / semi-limitada | Forbidden / Limited / Semi-Limited |
| Límite 1/2/3 (Duel Links) | Limit 1/2/3 |
| libre / hasta 3 copias | unlimited / up to 3 copies |
| copia(s) | copy / copies |
| puntos (Genesys) | points |
| tope de 100 puntos | 100-point cap |
| ajuste de puntos | points update |
| Receta con banlist anterior | Decklist from the previous banlist |
| Banlist actual / anterior | Current banlist / Previous banlist |
| Puntos actuales / anteriores | Current points / Previous points |
| Formato en transición | Format in transition |
| caja / expansión / set | box / set (TCG: "set" or "expansion") |
| Cajas y sets | Boxes & sets |
| estructura / mazo de estructura | structure deck |
| sobre | booster pack |
| Buscador de cartas | Card search |
| Constructor (de mazos) | Deck builder |
| Guía | Guide |
| Eventos | Events |
| Obtención en Duel Links | Getting cards in Duel Links |
| cómo conseguirla | how to get it |
| Cómo se calcula | How it's calculated |
| Cómo se juega | How to play |
| victoria(s) | win(s) |
| torneo(s) | tournament(s) |
| puesto (1.º, 2.º) | place (1st, 2nd) |
| muestra | sample |
| peso de resultados | results weight |
| Ganadores fuera del meta | Winners outside the meta |
| Poco resultado | Low results |
| Sin tier | No tier |
| el más fuerte | the strongest |
| top cut frecuente | frequent top cut |
| Más jugado | Most played |
| Staple | Staple |
| Main Deck / Extra Deck / Side Deck | Main Deck / Extra Deck / Side Deck |
| Invocación Normal / Especial | Normal Summon / Special Summon |
| Sincro / Fusión / Xyz / Link / Péndulo / Ritual | Synchro / Fusion / Xyz / Link / Pendulum / Ritual |
| Tuner | Tuner |
| Nivel / Rango / Escala | Level / Rank / Scale |
| Atributo / Tipo | Attribute / Type |
| ATK / DEF | ATK / DEF |
| Cementerio | Graveyard (GY) |
| desterrar | banish |
| negar | negate |
| mano (cartas) | hand |
| cadena | chain |
| Hechizo / Trampa / Monstruo | Spell / Trap / Monster |
| Gemas, dinero real | Gems, real money |
| personaje | character |
| Subiendo de nivel | Leveling up |
| Canje con tickets | Ticket exchange |
| ticket | ticket |
| Card Trader | Card Trader |
| rareza | rarity |
| Común / Rara / Súper / Ultra / Secreta | Common / Rare / Super / Ultra / Secret |
| copia de seguridad | backup |
| Mi mazo / Mis mazos | My deck / My decks |
| Guardar / Cargar / Importar / Exportar / Eliminar / Cerrar | Save / Load / Import / Export / Delete / Close |
| Ver menos / Mostrar más | Show less / Show more |
| Todos / Todas | All |
| Cargando… | Loading… |
| Sin datos | No data |
| Fuentes y límites | Sources and limits |

## Formato de entrega
Un archivo JSON `{ "<key del lote>": "<traducción>", ... }` con TODAS las claves del lote y ninguna más. La clave es el campo `key` del lote, tal cual.
Validalo con `python tools/i18n_check.py <in_NN.json> <out_NN.json>` y corregí hasta que diga "0 con problemas".
