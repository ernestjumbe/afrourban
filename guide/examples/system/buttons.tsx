import { ArrowRight, ArrowUpRight, Loader2, Plus, Search } from "lucide-react";

export function ButtonExamples() {
    return (
        <div className="space-y-4 bg-[#0e0e0e] p-8 text-white">
            <div className="flex flex-wrap gap-3">
                <button className="h-11 rounded-full bg-[var(--color-gold)] px-6 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a] transition-colors hover:bg-[var(--color-gold-light)]">
                    Primary
                </button>
                <button className="h-11 rounded-full border border-white/15 bg-transparent px-5 text-[12px] font-bold uppercase tracking-[1.5px] text-white transition-colors hover:border-[var(--color-gold)]/50">
                    Secondary
                </button>
                <button className="h-11 rounded-full border border-[var(--color-terracotta)]/60 bg-transparent px-5 text-[12px] font-bold uppercase tracking-[1.5px] text-[var(--color-terracotta)] transition-colors hover:bg-[var(--color-terracotta)] hover:text-white">
                    Delete account
                </button>
            </div>
            <div className="flex flex-wrap gap-3">
                <button className="inline-flex h-11 items-center gap-2 rounded-full bg-[var(--color-gold)] px-6 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">
                    <Plus className="h-4 w-4" />
                    New event
                </button>
                <button className="inline-flex h-11 items-center gap-2 rounded-full border border-white/15 bg-transparent px-5 text-[12px] font-bold uppercase tracking-[1.5px] text-white">
                    Open
                    <ArrowUpRight className="h-3.5 w-3.5" />
                </button>
                <button aria-label="Search" className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-transparent text-white">
                    <Search className="h-4 w-4" />
                </button>
            </div>
            <div className="flex flex-wrap gap-3">
                <button disabled className="h-11 cursor-not-allowed rounded-full bg-[var(--color-gold)] px-6 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a] opacity-40">
                    Disabled
                </button>
                <button className="inline-flex h-11 cursor-progress items-center gap-2 rounded-full bg-[var(--color-gold)] px-6 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Saving…
                </button>
            </div>
            <a href="#" className="inline-flex items-center gap-1.5 text-[12px] font-bold uppercase tracking-[1.5px] text-[var(--color-gold)] underline-offset-4 hover:underline">
                Read more
                <ArrowRight className="h-3.5 w-3.5" />
            </a>
        </div>
    );
}