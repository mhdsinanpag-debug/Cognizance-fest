export type LayerCategory = 'sky' | 'cloud' | 'header' | 'dune' | 'subject';

export interface LayerSpec {
  id: string;
  src: string;
  alt: string;
  category: LayerCategory;
  zIndex: number;
  delayMs: number;
  durationMs: number;
  initialTranslateYPercent: number;
}

export interface LayerRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface LayersManifest {
  canvasWidth: number;
  canvasHeight: number;
  layers: Record<string, LayerRect>;
}

/**
 * Choreography timing rules:
 * 1. Page loads: sky, sun, clouds, logo, and menu icon appear immediately (0ms).
 * 2. Clouds gently drift continuously on independent loops.
 * 3. Desert dunes rise one by one from the bottom upward (dune-6 -> dune-1).
 * 4. After all desert dunes rise, trees, cacti, and camel caravan rise up.
 */
export const SCENE_LAYERS: LayerSpec[] = [
  {
    id: 'sky',
    src: '/assets/layers/sky-bg.png',
    alt: 'Warm desert parchment sky',
    category: 'sky',
    zIndex: 1,
    delayMs: 0,
    durationMs: 320,
    initialTranslateYPercent: 0,
  },
  {
    id: 'sun',
    src: '/assets/layers/sun.png',
    alt: 'Golden desert sun',
    category: 'sky',
    zIndex: 2,
    delayMs: 40,
    durationMs: 500,
    initialTranslateYPercent: 6,
  },
  {
    id: 'cloudLeft',
    src: '/assets/layers/cloud-left.png',
    alt: 'Left desert cloud',
    category: 'cloud',
    zIndex: 3,
    delayMs: 80,
    durationMs: 550,
    initialTranslateYPercent: 0,
  },
  {
    id: 'cloudMid',
    src: '/assets/layers/cloud-mid.png',
    alt: 'Cloud drifting across the sun',
    category: 'cloud',
    zIndex: 4,
    delayMs: 110,
    durationMs: 550,
    initialTranslateYPercent: 0,
  },
  {
    id: 'cloudRight',
    src: '/assets/layers/cloud-right.png',
    alt: 'Right desert cloud',
    category: 'cloud',
    zIndex: 5,
    delayMs: 140,
    durationMs: 550,
    initialTranslateYPercent: 0,
  },
  // Desert dunes rising one by one from the bottom (dune-6 -> dune-1)
  {
    id: 'dune-1',
    src: '/assets/layers/dune-1.png',
    alt: 'Distant dark teal desert dune',
    category: 'dune',
    zIndex: 10,
    delayMs: 1100,
    durationMs: 650,
    initialTranslateYPercent: 95,
  },
  {
    id: 'dune-2',
    src: '/assets/layers/dune-2.png',
    alt: 'Burnt orange desert dune',
    category: 'dune',
    zIndex: 12,
    delayMs: 930,
    durationMs: 650,
    initialTranslateYPercent: 250,
  },
  {
    id: 'palm-tree',
    src: '/assets/layers/palm-tree.png',
    alt: 'Date palm tree with orange dates',
    category: 'subject',
    zIndex: 13,
    delayMs: 1580,
    durationMs: 700,
    initialTranslateYPercent: 110,
  },
  {
    id: 'dune-3',
    src: '/assets/layers/dune-3.png',
    alt: 'Pale golden cream desert dune',
    category: 'dune',
    zIndex: 14,
    delayMs: 760,
    durationMs: 650,
    initialTranslateYPercent: 95,
  },
  {
    id: 'camel-caravan',
    src: '/assets/layers/camel-caravan.png',
    alt: 'Traveler leading two camels across the dune',
    category: 'subject',
    zIndex: 15,
    delayMs: 1760,
    durationMs: 740,
    initialTranslateYPercent: 115,
  },
  {
    id: 'cactus-1',
    src: '/assets/layers/cactus-1.png',
    alt: 'Upper desert cactus',
    category: 'subject',
    zIndex: 15,
    delayMs: 1900,
    durationMs: 640,
    initialTranslateYPercent: 120,
  },
  {
    id: 'dune-4',
    src: '/assets/layers/dune-4.png',
    alt: 'Golden amber desert dune',
    category: 'dune',
    zIndex: 16,
    delayMs: 590,
    durationMs: 650,
    initialTranslateYPercent: 95,
  },
  {
    id: 'dry-tree',
    src: '/assets/layers/dry-tree.png',
    alt: 'Desert dry branching tree',
    category: 'subject',
    zIndex: 17,
    delayMs: 2140,
    durationMs: 640,
    initialTranslateYPercent: 120,
  },
  {
    id: 'dune-5',
    src: '/assets/layers/dune-5.png',
    alt: 'Crimson desert dune',
    category: 'dune',
    zIndex: 18,
    delayMs: 420,
    durationMs: 650,
    initialTranslateYPercent: 95,
  },
  {
    id: 'cactus-2',
    src: '/assets/layers/cactus-2.png',
    alt: 'Foreground desert cactus',
    category: 'subject',
    zIndex: 19,
    delayMs: 2020,
    durationMs: 640,
    initialTranslateYPercent: 120,
  },
  {
    id: 'dune-6',
    src: '/assets/layers/dune-6.png',
    alt: 'Foreground dark teal desert dune',
    category: 'dune',
    zIndex: 20,
    delayMs: 250,
    durationMs: 650,
    initialTranslateYPercent: 100,
  },
  {
    id: 'logo',
    src: '/assets/layers/logo.png',
    alt: "Cognizance Students Arts Feast '26",
    category: 'header',
    zIndex: 30,
    delayMs: 0,
    durationMs: 420,
    initialTranslateYPercent: 0,
  },
  {
    id: 'menuBtn',
    src: '/assets/layers/menu-btn.png',
    alt: 'Menu button',
    category: 'header',
    zIndex: 31,
    delayMs: 0,
    durationMs: 420,
    initialTranslateYPercent: 0,
  },
];

export function computePercentBounds(rect: LayerRect, canvasWidth: number, canvasHeight: number) {
  return {
    left: `${(rect.x / canvasWidth) * 100}%`,
    top: `${(rect.y / canvasHeight) * 100}%`,
    width: `${(rect.width / canvasWidth) * 100}%`,
    height: `${(rect.height / canvasHeight) * 100}%`,
  };
}

export function getTotalEntranceDurationMs(layers: LayerSpec[] = SCENE_LAYERS): number {
  return layers.reduce((max, layer) => Math.max(max, layer.delayMs + layer.durationMs), 0);
}

export function validateChoreographyOrder(layers: LayerSpec[] = SCENE_LAYERS): {
  dunesRiseBeforeSubjects: boolean;
  bottomDuneStartsFirst: boolean;
  cloudsLoadWithSky: boolean;
} {
  const dunes = layers.filter((l) => l.category === 'dune');
  const subjects = layers.filter((l) => l.category === 'subject');
  const clouds = layers.filter((l) => l.category === 'cloud');

  const maxDuneStart = Math.max(...dunes.map((d) => d.delayMs));
  const minSubjectStart = Math.min(...subjects.map((s) => s.delayMs));
  const dune6 = dunes.find((d) => d.id === 'dune-6');
  const dune1 = dunes.find((d) => d.id === 'dune-1');

  return {
    dunesRiseBeforeSubjects: minSubjectStart > maxDuneStart,
    bottomDuneStartsFirst: Boolean(dune6 && dune1 && dune6.delayMs < dune1.delayMs),
    cloudsLoadWithSky: clouds.every((c) => c.delayMs < (dune6?.delayMs ?? 999)),
  };
}
