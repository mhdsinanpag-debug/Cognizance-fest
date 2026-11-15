import { useEffect, useState } from 'react';
import { Calendar, MapPin, Pause, Play, RotateCcw, Sparkles, X } from 'lucide-react';

interface MenuDrawerProps {
  open: boolean;
  onClose: () => void;
  onReplay: () => void;
  motionPaused: boolean;
  onToggleMotion: () => void;
}

type DrawerTab = 'events' | 'schedule' | 'venue';

const EVENTS_LIST = [
  { title: 'Mirage Canvas — Live Mural & Sand Art', category: 'Visual Arts', time: 'Day 1 · 10:00 AM' },
  { title: 'Dune Echoes — Classical & Folk Fusion', category: 'Music', time: 'Day 1 · 04:30 PM' },
  { title: 'Caravan Chronicles — Street Theatre', category: 'Dramatics', time: 'Day 2 · 02:00 PM' },
  { title: 'Oasis Lens — Documentary Photography', category: 'Film & Photo', time: 'Day 2 · 05:30 PM' },
];

const SCHEDULE_LIST = [
  { slot: '09:30 AM', title: 'Inaugural Procession & Art Pavilion Opening' },
  { slot: '11:30 AM', title: 'On-Spot Painting, Calligraphy & Clay Sculpture' },
  { slot: '03:00 PM', title: 'Literary Symposium & Poetry Slam' },
  { slot: '06:30 PM', title: 'Twilight Stage Finale & Cultural Ensemble' },
];

export function MenuDrawer({
  open,
  onClose,
  onReplay,
  motionPaused,
  onToggleMotion,
}: MenuDrawerProps) {
  const [activeTab, setActiveTab] = useState<DrawerTab>('events');

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-[#012935]/50 transition-opacity"
      role="dialog"
      aria-modal="true"
      aria-label="Cognizance '26 Navigation Menu"
      onClick={onClose}
    >
      <aside
        className="relative flex h-full w-full max-w-sm flex-col bg-[#FDF1C4] text-[#1A2A2D] shadow-2xl border-l border-[#D8BE7A]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#E5CF91] px-6 py-5">
          <div>
            <h2
              className="text-xl font-bold tracking-tight text-[#5E2C12]"
              style={{ fontFamily: 'var(--font-display)' }}
            >
              Cognizance &rsquo;26
            </h2>
            <p className="text-xs font-medium text-[#7A4B2A]">Students Arts Feast</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close menu"
            className="flex h-11 w-11 items-center justify-center rounded-xl border border-[#D8BE7A] bg-[#F7E5A8] text-[#5E2C12] transition-colors hover:bg-[#EED587] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#013A49]"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="border-b border-[#E5CF91] px-6 py-4">
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => {
                onClose();
                onReplay();
              }}
              className="inline-flex min-h-[42px] items-center gap-2 rounded-xl bg-[#013F50] px-4 py-2 text-xs font-semibold text-[#FDF1C4] transition-colors hover:bg-[#025166] whitespace-nowrap shrink-0"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Replay Entrance
            </button>
            <button
              type="button"
              onClick={onToggleMotion}
              className="inline-flex min-h-[42px] items-center gap-2 rounded-xl border border-[#C7A65C] bg-[#F7E5A8] px-4 py-2 text-xs font-semibold text-[#4B2813] transition-colors hover:bg-[#EED587] whitespace-nowrap shrink-0"
            >
              {motionPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
              {motionPaused ? 'Resume Sky Motion' : 'Pause Sky Motion'}
            </button>
          </div>
        </div>

        <div className="px-6 pt-4">
          <div className="grid grid-cols-3 gap-1 rounded-xl bg-[#EFE0A8] p-1" role="tablist">
            {(
              [
                { id: 'events', label: 'Events' },
                { id: 'schedule', label: 'Schedule' },
                { id: 'venue', label: 'Venue' },
              ] as const
            ).map((tab) => (
              <button
                key={tab.id}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`min-h-[38px] rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-[#FDF6D8] text-[#013F50] shadow-xs'
                    : 'text-[#6A4A2E] hover:text-[#3A2210]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {activeTab === 'events' && (
            <ul className="space-y-4">
              {EVENTS_LIST.map((ev) => (
                <li key={ev.title} className="border-b border-[#E5CF91] pb-4 last:border-b-0">
                  <p className="text-sm font-semibold text-[#182C32]">{ev.title}</p>
                  <p className="mt-1 text-xs text-[#6B4A2E]">
                    <span>{ev.category}</span>
                    <span className="mx-1.5" aria-hidden="true">·</span>
                    <span>{ev.time}</span>
                  </p>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'schedule' && (
            <ul className="space-y-4">
              {SCHEDULE_LIST.map((item) => (
                <li key={item.slot} className="flex items-start gap-3 border-b border-[#E5CF91] pb-4 last:border-b-0">
                  <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#EED68C] text-[#5E2C12]">
                    <Calendar className="h-3.5 w-3.5" />
                  </span>
                  <div>
                    <p className="text-xs font-semibold tabular-nums text-[#8B4318]">{item.slot}</p>
                    <p className="mt-0.5 text-sm font-medium text-[#182C32]">{item.title}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {activeTab === 'venue' && (
            <div className="space-y-4 text-sm text-[#2F3D3F]">
              <div className="flex items-start gap-3">
                <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-[#B44B0A]" />
                <div>
                  <p className="font-semibold text-[#182C32]">Main Courtyard &amp; Open Amphitheatre</p>
                  <p className="mt-1 text-xs leading-relaxed text-[#6B4A2E]">
                    Four outdoor stages inspired by desert dunes, sunlit murals, and handcrafted art pavilions.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3 border-t border-[#E5CF91] pt-4">
                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-[#B44B0A]" />
                <p className="text-xs leading-relaxed text-[#6B4A2E]">
                  Crafted directly from the official Cognizance &rsquo;26 artwork layers with live ambient cloud drift and staggered dune reveal.
                </p>
              </div>
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}
