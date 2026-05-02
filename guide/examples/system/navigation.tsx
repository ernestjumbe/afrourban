import { Menu, Search, X } from "lucide-react";

type NavigationExampleProps = {
    mobileMenuOpen?: boolean;
    activeItem?: string;
};

export function NavigationExample({
    mobileMenuOpen = false,
    activeItem = "EVENTS",
}: NavigationExampleProps) {
    const items = ["BUSINESSES", "MUSIC", "FASHION", "ART", "STORIES", "EVENTS", "PODCASTS"];

    return (
        <nav className="fixed left-0 right-0 top-0 z-50 border-b border-white/[0.06] bg-[#0e0e0e]/95 backdrop-blur-md">
            <div className="mx-auto max-w-[1400px] px-6 md:px-16">
                <div className="flex h-16 items-center justify-between">
                    <a href="#" className="text-[18px] font-black uppercase tracking-[1px] text-white">
                        AFROURBAN
                    </a>

                    <div className="hidden items-center gap-8 md:flex">
                        {items.map((item) => (
                            <button
                                key={item}
                                className={item === activeItem ? "text-[12px] font-medium tracking-[2px] text-[var(--color-gold)]" : "text-[12px] font-medium tracking-[2px] text-white/50 transition-colors hover:text-white"}
                            >
                                {item}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center gap-5">
                        <button aria-label="Search" className="text-white/60 transition-colors hover:text-white">
                            <Search size={20} />
                        </button>
                        <button className="hidden text-[12px] font-medium tracking-[2px] text-white/50 md:inline-flex">LOGIN</button>
                        <button aria-label={mobileMenuOpen ? "Close menu" : "Open menu"} className="text-white/60 md:hidden">
                            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}