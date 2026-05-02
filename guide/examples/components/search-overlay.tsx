import { Search, X } from "lucide-react";

type SearchOverlayExampleProps = {
    open?: boolean;
};

export function SearchOverlayExample({ open = true }: SearchOverlayExampleProps) {
    if (!open) return null;

    return (
        <div className="fixed inset-0 z-[60] flex flex-col" role="dialog" aria-label="Search">
            <div className="absolute inset-0 bg-[#0e0e0e]/97 backdrop-blur-xl" />
            <div className="relative z-10 flex h-full flex-col">
                <div className="mx-auto flex h-16 w-full max-w-[1400px] items-center justify-between px-6 md:px-16">
                    <span className="text-[12px] font-medium tracking-[2px] text-white/30">SEARCH</span>
                    <button aria-label="Close search" className="text-white/50 transition-colors hover:text-white">
                        <X size={24} />
                    </button>
                </div>

                <div className="flex flex-1 items-start justify-center px-6 pt-[15vh] md:px-16 md:pt-[20vh]">
                    <div className="w-full max-w-2xl">
                        <div className="relative">
                            <Search className="absolute left-0 top-1/2 h-6 w-6 -translate-y-1/2 text-white/30" />
                            <input
                                autoFocus
                                placeholder="Search events, categories, cities…"
                                className="w-full border-b border-white/[0.08] bg-transparent pb-4 pl-10 text-2xl font-light text-white outline-none placeholder:text-white/20 caret-[var(--color-gold)] md:text-3xl"
                            />
                        </div>

                        <div className="mt-8 flex flex-wrap gap-2">
                            {["Music", "Fashion", "Art", "Stockholm", "Copenhagen", "Oslo"].map((tag) => (
                                <button key={tag} className="rounded-full border border-white/[0.08] px-3 py-1.5 text-[12px] font-medium tracking-[1px] text-white/30 transition-colors hover:border-white/20 hover:text-white/50">
                                    {tag.toUpperCase()}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}