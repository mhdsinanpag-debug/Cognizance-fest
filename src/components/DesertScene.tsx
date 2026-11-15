import { useEffect, useState, type CSSProperties } from 'react';
import rawManifest from '../data/layersManifest.json';
import {
  SCENE_LAYERS,
  computePercentBounds,
  getTotalEntranceDurationMs,
  type LayerSpec,
  type LayersManifest,
} from '../utils/choreography';

const manifest = rawManifest as LayersManifest;

interface DesertSceneProps {
  replayKey: number;
  motionPaused: boolean;
  menuOpen: boolean;
  onOpenMenu: () => void;
}

type SceneStage = 'loading' | 'dunes' | 'subjects' | 'live';

const IDLE_CLASS_BY_ID: Record<string, string> = {
  cloudLeft: 'anim-cloud-left',
  cloudRight: 'anim-cloud-right',
  'palm-tree': 'anim-palm-breeze',
  'camel-caravan': 'anim-camel-breathe',
};

function renderSceneLayer(
  layer: LayerSpec,
  replayKey: number,
  onOpenMenu: () => void,
  menuOpen: boolean,
) {
  const rect = manifest.layers[layer.id];
  if (!rect) return null;

  const bounds = computePercentBounds(rect, manifest.canvasWidth, manifest.canvasHeight);
  const idleClass = IDLE_CLASS_BY_ID[layer.id] ?? '';

  const isSubject = layer.category === 'subject';
  const isDune = layer.category === 'dune';
  const startOpacity = isDune ? 0.96 : 0;
  const opacityDurationMs = isSubject ? 160 : isDune ? 180 : layer.durationMs;
  const easing = isSubject
    ? 'cubic-bezier(0.16, 1, 0.3, 1)'
    : isDune
      ? 'cubic-bezier(0.2, 0.9, 0.25, 1)'
      : 'cubic-bezier(0.22, 1, 0.36, 1)';

  const entranceStyle = {
    ...bounds,
    zIndex: layer.zIndex,
    '--start-y': `${layer.initialTranslateYPercent}%`,
    '--start-opacity': `${startOpacity}`,
    animation: `riseTranslate ${layer.durationMs}ms ${easing} ${layer.delayMs}ms both, riseOpacity ${opacityDurationMs}ms ease-out ${layer.delayMs}ms both`,
    willChange: 'transform, opacity',
  } as CSSProperties;

  if (layer.id === 'menuBtn') {
    return (
      <div key={`${replayKey}-${layer.id}`} style={entranceStyle} className="absolute">
        <button
          type="button"
          onClick={onOpenMenu}
          aria-label="Open Cognizance menu"
          aria-expanded={menuOpen}
          className="group relative block h-full w-full cursor-pointer rounded-xl transition-transform duration-150 hover:scale-[1.04] active:scale-[0.96] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#013F50]"
        >
          <img
            src={layer.src}
            alt=""
            draggable={false}
            className="h-full w-full object-contain drop-shadow-sm select-none"
          />
        </button>
      </div>
    );
  }

  return (
    <div
      key={`${replayKey}-${layer.id}`}
      style={entranceStyle}
      className="pointer-events-none absolute"
    >
      <img
        src={layer.src}
        alt={layer.alt}
        draggable={false}
        className={`h-full w-full object-fill select-none ${idleClass}`}
      />
    </div>
  );
}

export function DesertScene({
  replayKey,
  motionPaused,
  menuOpen,
  onOpenMenu,
}: DesertSceneProps) {
  const [stage, setStage] = useState<SceneStage>('loading');

  useEffect(() => {
    setStage('loading');
    const tDunes = window.setTimeout(() => setStage('dunes'), 250);
    const tSubjects = window.setTimeout(() => setStage('subjects'), 1550);
    const tLive = window.setTimeout(() => setStage('live'), getTotalEntranceDurationMs(SCENE_LAYERS));
    return () => {
      window.clearTimeout(tDunes);
      window.clearTimeout(tSubjects);
      window.clearTimeout(tLive);
    };
  }, [replayKey]);

  return (
    <div
      data-testid="desert-scene"
      data-stage={stage}
      className={`relative aspect-[773/1507] w-full overflow-hidden bg-[#FDEFB2] select-none ${
        motionPaused ? 'motion-paused' : ''
      }`}
    >
      {SCENE_LAYERS.map((layer) => renderSceneLayer(layer, replayKey, onOpenMenu, menuOpen))}
    </div>
  );
}
