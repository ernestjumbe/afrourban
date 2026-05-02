import { ChevronDown, Search } from "lucide-react";

export function DirectoryFiltersExample() {
    return (
        <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-4 md:p-5">
            <div className="flex flex-col gap-3 lg:flex-row">
                <div className="relative min-w-0 flex-1">
                    <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/35" />
                    <input
                        type="text"
                        placeholder="Search by name, description, or address"
                        className="h-11 w-full rounded-full border border-white/[0.08] bg-white/[0.04] pl-11 pr-10 text-[14px] text-white outline-none placeholder:text-white/30 focus:border-[var(--color-gold)]/50"
                    />
                </div>

                <button className="inline-flex h-11 items-center justify-between gap-2 rounded-full border border-white/15 px-4 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50">
                    Type
                    <ChevronDown className="h-4 w-4" />
                </button>

                <div className="inline-flex h-11 rounded-full border border-white/15 p-1">
                    <button className="rounded-full bg-[var(--color-gold)] px-4 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">All</button>
                    <button className="rounded-full px-4 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50">Physical</button>
                    <button className="rounded-full px-4 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50">Online</button>
                </div>

                <button className="inline-flex h-11 items-center justify-between gap-2 rounded-full border border-white/15 px-4 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50">
                    Sort
                    <ChevronDown className="h-4 w-4" />
                </button>
            </div>
        </div>
    );
}