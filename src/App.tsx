import { useState } from 'react';
import { Pause, Play, RotateCcw } from 'lucide-react';
import { DesertScene } from './components/DesertScene';
import { MenuDrawer } from './components/MenuDrawer';

export default function App() {
  const [replayKey, setReplayKey] = useState(0);
  const [motionPaused, setMotionPaused] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleReplay = () => {
    setReplayKey((k) => k + 1);
  };

  return (
    <main className="relative flex min-h-dvh w-full flex-col items-center justify-center overflow-x-hidden bg-gradient-to-b from-[#FDEFB2] via-[#FDEFB2] via-70% to-[#013F50] sm:from-[#FAF0CA] sm:via-[#F7E6AA] sm:to-[#EFD589] sm:px-6 sm:py-5">
      {/* Subtle warm ambient glow behind the living artwork on desktop */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 hidden sm:block bg-[radial-gradient(circle_at_50%_24%,rgba(255,212,112,0.45),transparent_58%)]"
      />

      {/* Primary Live PNG Canvas */}
      <section
        aria-label="Cognizance Students Arts Feast '26 Living Desert Artwork"
        className="relative z-10 w-full sm:w-auto sm:h-[min(92dvh,850px)] sm:aspect-[773/1507] sm:rounded-[28px] sm:border sm:border-[#D9BA73] sm:shadow-[0_24px_70px_-18px_rgba(74,40,12,0.32)] overflow-hidden"
      >
        <DesertScene
          replayKey={replayKey}
          motionPaused={motionPaused}
          menuOpen={menuOpen}
          onOpenMenu={() => setMenuOpen(true)}
        />
      </section>

      {/* Clean desktop/tablet stage controls below or floating subtly */}
      <div className="relative z-10 mt-3 hidden sm:flex items-center gap-2">
        <button
          type="button"
          onClick={handleReplay}
          className="inline-flex min-h-[40px] items-center gap-2 rounded-xl border border-[#D4B46A] bg-[#FDF5D4]/90 px-4 py-2 text-xs font-semibold text-[#4A280E] shadow-xs backdrop-blur-xs transition-colors hover:bg-[#FAF0C4] whitespace-nowrap shrink-0 cursor-pointer"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Replay Animation
        </button>
        <button
          type="button"
          onClick={() => setMotionPaused((p) => !p)}
          className="inline-flex min-h-[40px] items-center gap-2 rounded-xl border border-[#D4B46A] bg-[#FDF5D4]/90 px-4 py-2 text-xs font-semibold text-[#4A280E] shadow-xs backdrop-blur-xs transition-colors hover:bg-[#FAF0C4] whitespace-nowrap shrink-0 cursor-pointer"
        >
          {motionPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
          {motionPaused ? 'Resume Motion' : 'Pause Motion'}
        </button>
      </div>

      <MenuDrawer
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        onReplay={handleReplay}
        motionPaused={motionPaused}
        onToggleMotion={() => setMotionPaused((p) => !p)}
      />
    </main>
  );
}
