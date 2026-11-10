// Contrato de la sección Lore: una entrada por arquetipo, carta o personaje en src/lore/<slug>.json.
// tools/lore.py la valida (cartas que existen, 50-110 palabras por párrafo, fuentes https directas, ES y EN en todo)
// y la escribe en data/lore.js, que la página carga bajo demanda.

type Bi = { es: string; en: string };          // todo texto va en los dos idiomas

interface LoreBlock {
  h: Bi;                                        // título, hasta 60 caracteres
  p: Bi;                                        // 50 a 110 palabras por idioma, redacción propia (nada copiado de la wiki)
  cards: string[];                              // 1 a 3 cartas que ilustran ESTE bloque (nombres exactos de src/ygo_all.json)
}

interface LoreCreator {                         // 0 a 2, solo si existe y se verificó una pieza concreta sobre este lore
  author: string;                               // canal o persona
  title: string;                                // título exacto publicado
  url: string;                                  // https directo al video o artículo (YouTube: watch?v=...)
  platform: string;
  checked: string;                              // AAAA-MM-DD
  why: Bi;                                      // puntero neutro, sin describir contenido no verificado
}

interface LoreSource { name: string; url: string; checked: string }   // 1 a 4 páginas de wiki realmente leídas

export interface LoreEntry {
  slug: string;                                 // = nombre del archivo
  kind: 'archetype' | 'character';          // de qué es la historia: un arquetipo/carta o un personaje (filtro de la página)
  name: string;
  badge: Bi;                                    // gancho de una línea, hasta 90 caracteres
  origin: Bi;                                   // de dónde viene (serie, manga, juego), hasta 120 caracteres
  blocks: LoreBlock[];                          // 3 a 8
  creators: LoreCreator[];
  sources: LoreSource[];                        // 1 a 12, todas las páginas realmente usadas
  notes: Bi;                                    // aclaración opcional (cadenas vacías si no hay)
}
