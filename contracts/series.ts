// Contrato de las series: una entrada por serie del anime en src/series/series.json. Lo valida tools/series.py y lo escribe en data/series.js.
// Los duelistas y sus mazos NO van acá: salen de data/roulette.js (la ruleta de decks), una sola fuente.
export type Lang = 'es' | 'en';
export type SeriesId = 'dm' | 'gx' | '5d' | 'zx' | 'av' | 'vr';   // los mismos ids que ROU_SERIES de src.html

export interface Series {
  id: SeriesId;
  year: number;                          // año de estreno en Japón
  protagonist: string;                   // nombre del protagonista, igual que en la ruleta (para enlazarlo)
  who: string;                           // cómo se muestra; contiene al protagonista (ej. "Yusaku Fujiki (Playmaker)")
  era: '' | 'goat' | 'edison' | 'hat';   // formato retro de la época (src/formats.json); vacío si no hay
  mech: Record<Lang, string>;            // mecánica que define la serie, 5 a 30 palabras
  blurb: Record<Lang, string>;           // presentación, 25 a 70 palabras; no puede ser igual en los dos idiomas
}

// Reglas del texto: sin rayas largas, en español "desterrar" (nunca banish ni banear), solo datos que se puedan comprobar.
