import {
  VIDEO_LOOK_GROUPS,
  VIDEO_LOOK_STYLES,
  VIDEO_STUDENT_NOTE_MAX,
  type VideoLookStyle,
} from './videoLookSheet';

interface VideoLookControlsProps {
  look: VideoLookStyle;
  addPeople: boolean;
  addVehicles: boolean;
  note: string;
  disabled?: boolean;
  onLookChange: (look: VideoLookStyle) => void;
  onAddPeopleChange: (value: boolean) => void;
  onAddVehiclesChange: (value: boolean) => void;
  onNoteChange: (note: string) => void;
}

/** The look sheet: what the finished video should look like. Geometry and the
 * camera are not choices here; they come from the 3D scene and the drawn route. */
export function VideoLookControls({
  look,
  addPeople,
  addVehicles,
  note,
  disabled = false,
  onLookChange,
  onAddPeopleChange,
  onAddVehiclesChange,
  onNoteChange,
}: VideoLookControlsProps) {
  return (
    <div className="space-y-2.5">
      {VIDEO_LOOK_GROUPS.map((group) => (
        <div key={group}>
          <p className="mb-1 text-[8px] font-black uppercase tracking-[0.14em] text-[#151515]/40">{group}</p>
          <div className="grid grid-cols-3 gap-1.5" role="group" aria-label={`${group} looks`}>
            {VIDEO_LOOK_STYLES.filter((option) => option.group === group).map((option) => (
              <button
                key={option.id}
                type="button"
                aria-pressed={look === option.id}
                disabled={disabled}
                onClick={() => onLookChange(option.id)}
                className={`rounded-lg border px-2 py-1.5 text-left transition disabled:cursor-not-allowed disabled:opacity-40 ${look === option.id ? 'border-[#151515] bg-[#fff0bf] shadow-[2px_2px_0_0_#151515]' : 'border-[#151515]/15 bg-white/45 hover:bg-white'}`}
              >
                <span className="block text-[9px] font-black">{option.label}</span>
                <span className="block text-[8px] leading-tight text-[#151515]/45">{option.detail}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
      <div className="grid grid-cols-2 gap-1.5">
        <label className={`flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-[#151515]/15 bg-white/45 px-2 text-[9px] font-bold ${disabled ? 'opacity-40' : ''}`}>
          <input type="checkbox" className="h-4 w-4 accent-[#151515]" checked={addPeople} disabled={disabled}
            onChange={(event) => onAddPeopleChange(event.target.checked)} />
          People on paths
        </label>
        <label className={`flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-[#151515]/15 bg-white/45 px-2 text-[9px] font-bold ${disabled ? 'opacity-40' : ''}`}>
          <input type="checkbox" className="h-4 w-4 accent-[#151515]" checked={addVehicles} disabled={disabled}
            onChange={(event) => onAddVehiclesChange(event.target.checked)} />
          Slow traffic in lanes
        </label>
      </div>
      <div>
        <label htmlFor="video-student-note" className="mb-1 flex items-center justify-between text-[8px] font-black uppercase tracking-[0.14em] text-[#151515]/40">
          <span>Note to the video engine (optional)</span>
          <span aria-live="polite">{note.length}/{VIDEO_STUDENT_NOTE_MAX}</span>
        </label>
        <textarea
          id="video-student-note"
          value={note}
          maxLength={VIDEO_STUDENT_NOTE_MAX}
          rows={2}
          disabled={disabled}
          placeholder="e.g. market stalls along the main street, mist over the wetland"
          onChange={(event) => onNoteChange(event.target.value)}
          className="w-full resize-none rounded-lg border border-[#151515]/15 bg-white/70 px-2 py-1.5 text-[10px] font-semibold text-[#151515] placeholder:text-[#151515]/30 focus:border-[#151515] focus:outline-none disabled:opacity-40"
        />
        <p className="mt-1 text-[8px] font-semibold leading-relaxed text-[#151515]/40">
          Light, weather and finish only. The buildings, parks and streets come from your 3D scene and cannot be changed by the note.
        </p>
      </div>
    </div>
  );
}
