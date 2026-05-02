import { Bookmark, Info } from "lucide-react";

export function TooltipExamples() {
    return (
        <div className="flex flex-wrap gap-8 bg-[#0e0e0e] p-8 text-white">
            <span className="group relative inline-flex">
                <button type="button" aria-label="Save" className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-transparent text-white hover:border-[var(--color-gold)]/50">
                    <Bookmark className="h-4 w-4" />
                </button>
                <span role="tooltip" className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-[#1a1a1a] px-2.5 py-1.5 text-[11px] font-semibold text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
                    Save
                    <span className="absolute left-1/2 top-full h-0 w-0 -translate-x-1/2 border-x-4 border-x-transparent border-t-4 border-t-[#1a1a1a]" />
                </span>
            </span>

            <span className="group relative inline-flex items-center gap-1.5">
                <span className="text-[13px] text-white/60">Privacy</span>
                <button type="button" aria-label="Why is this public?" className="inline-flex h-5 w-5 items-center justify-center rounded-full text-white/40 hover:text-[var(--color-gold)]">
                    <Info className="h-3.5 w-3.5" />
                </button>
                <span role="tooltip" className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-[#1a1a1a] px-2.5 py-1.5 text-[11px] font-semibold text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
                    Visible on your profile
                    <span className="absolute left-1/2 top-full h-0 w-0 -translate-x-1/2 border-x-4 border-x-transparent border-t-4 border-t-[#1a1a1a]" />
                </span>
            </span>
        </div>
    );
}