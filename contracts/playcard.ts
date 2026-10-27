/**
 * Contrato de la ficha táctica de un mazo (data/play.js, construido por tools/playcards.py desde src/playcards.json).
 * Una ficha por mazo y formato.  Las 4 secciones son obligatorias y siempre van en este orden.
 * tools/playcards.py valida esto mismo contra las cartas reales: si una carta no existe, no está en la lista del mazo o no es legal en el formato, el build falla.
 */

/** Texto en los dos idiomas de la página. */
export interface L10n { es: string; en: string }

export type PlayFormat = 'adv' | 'ocg' | 'edison' | 'goat' | 'hat' | 'gen' | 'dl';

/** Claves de la ficha: `${format}/${slug del nombre del mazo}`, p. ej. "edison/blackwing". */
export type PlaycardKey = `${PlayFormat}/${string}`;

export type Plan = 'control' | 'otk' | 'grind' | 'tempo' | 'combo' | 'burn' | 'stun';
export type Pace = 'fast' | 'medium' | 'slow';

/** 1. Objetivo y Ritmo (Win Condition). */
export interface WinCondition {
  plan: Plan;                // la etiqueta corta del plan de juego
  pace: Pace;                // cuánto tarda en ganar: fast = gana en 1-2 turnos, slow = partida larga
  bullets: L10n[];           // 2 a 4 viñetas directas, una idea por viñeta
}

/** 2. Iniciadores clave (Starters): ruta de 1 o 2 cartas. */
export interface Starter {
  cards: string[];           // 1 o 2 nombres EN INGLÉS (como en la base); deben estar en la lista del mazo
  route: L10n;               // qué hace esa ruta, en una línea
}

/** Momento exacto de la cadena donde duele más. */
export type ChainStep =
  | 'summon'                 // al invocar (se puede responder a la invocación)
  | 'activation'             // al activar un efecto, antes de que entre en la cadena
  | 'resolution'             // al resolverse el efecto
  | 'attack'                 // en la declaración de ataque
  | 'main'                   // durante una Main Phase
  | 'end';                   // End Phase / Standby

/** 3. Puntos de interrupción (Chokepoints): contra qué pierde. */
export interface Chokepoint {
  card: string;              // la carta del rival (inglés); debe ser legal en el formato
  step: ChainStep;
  stepText: L10n;            // en qué paso exacto duele más, en una línea
  loss: L10n;                // qué se pierde y cómo se juega alrededor
}

export interface SideMove { card: string; qty: number; why: L10n }
export interface SideSwap { in: SideMove[]; out: SideMove[] }

/** 4. Plan de Side Deck: qué entra y qué sale yendo primero y yendo segundo. */
export interface SidePlan {
  first: SideSwap;
  second: SideSwap;
  basis: 'editorial' | 'tournament';   // «editorial» = criterio de la redacción, no estadística de torneos
}

/** Solo Duel Links (clave "dl/..."): el Skill que se lleva y por qué.  Duel Links no tiene Side Deck, así que su cuarto bloque es «Skill y ajustes»:
 *  `side.first` / `side.second` pasan a ser los ajustes del Main Deck al ir primero o segundo (entra cualquier carta de Duel Links, sale una del mazo). */
export interface Skill { name: string; why: L10n }

export interface DeckPlaycard {
  win: WinCondition;
  starters: Starter[];       // 1 a 3 rutas
  chokepoints: Chokepoint[]; // 1 a 5
  side: SidePlan;
  skills?: Skill[];          // obligatorio en Duel Links (1 a 3), prohibido en el resto
  updated: string;           // AAAA-MM-DD de la última revisión
}

/** El archivo completo. */
export type PlaycardFile = Record<PlaycardKey, DeckPlaycard>;
