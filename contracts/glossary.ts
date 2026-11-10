// Contrato del glosario: una entrada por término en src/glossary/*.json. Lo valida tools/glossary.py y lo escribe en data/glossary.js.
export type Lang = 'es' | 'en';
export type GlossaryCat = 'campo' | 'turno' | 'invocacion' | 'efectos' | 'cartas' | 'formatos' | 'jerga';

export interface GlossaryEntry {
  slug: string;                         // kebab-case, único; es la URL ?mode=glossary&term=<slug>
  cat: GlossaryCat;
  es: { term: string; def: string };    // término hasta 60 caracteres; definición de 15 a 80 palabras
  en: { term: string; def: string };    // no puede ser igual a la española
  see: string[];                        // 1 o más slugs de otros términos (ver también)
  cards: string[];                      // 0 o más cartas de ejemplo, con el nombre exacto de src/ygo_all.json
}

// Reglas del texto: sin rayas largas, en español "desterrar" (nunca banish ni banear), texto propio (no copiado de otras wikis).
