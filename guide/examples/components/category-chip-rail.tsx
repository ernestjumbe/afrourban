type CategoryChipRailExampleProps = {
    activeCategory?: string;
};

export function CategoryChipRailExample({ activeCategory = "All" }: CategoryChipRailExampleProps) {
    const categories = ["All", "Music", "Fashion", "Art", "Community", "Food"];

    return (
        <div className="flex flex-wrap items-center gap-2">
            {categories.map((category) => {
                const active = category === activeCategory;
                return (
                    <button
                        key={category}
                        className={active ? "rounded-full bg-[var(--color-gold)] px-4 py-2 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]" : "rounded-full border border-white/15 px-4 py-2 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50 transition-all hover:border-white/30 hover:text-white"}
                    >
                        {category}
                    </button>
                );
            })}
        </div>
    );
}