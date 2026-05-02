import { MapPin } from "lucide-react";

const profile = {
    tagline: "Community Builder",
    name: "Kwame Mensah",
    handle: "kwame-mensah",
    city: "Stockholm",
    cover: "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=1600&q=80",
    avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=500&q=80",
};

export function DetailHeroExample() {
    return (
        <section className="relative w-full overflow-hidden pt-8 md:pt-10 text-white">
            <div className="mx-auto max-w-[1200px] px-0 md:px-6">
                <div className="relative aspect-[1.91/1] w-full overflow-hidden md:rounded-2xl">
                    <img src={profile.cover} alt="" className="h-full w-full object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
                </div>
            </div>

            <div className="relative mx-auto -mt-14 max-w-[1200px] px-6 md:-mt-20 md:px-12">
                <div className="flex flex-col gap-6 md:flex-row md:items-end md:gap-8">
                    <div className="relative h-28 w-28 shrink-0 overflow-hidden rounded-full ring-4 ring-[#0e0e0e] md:h-40 md:w-40">
                        <img src={profile.avatar} alt={profile.name} className="h-full w-full object-cover" />
                        <div className="pointer-events-none absolute inset-0 rounded-full ring-2 ring-[var(--color-gold)]/40" />
                    </div>

                    <div className="min-w-0 flex-1 md:pb-3">
                        <p className="text-[11px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">{profile.tagline}</p>
                        <h1 className="mt-2 font-serif text-[36px] font-bold leading-[1.05] tracking-[-0.5px] md:text-[52px]">{profile.name}</h1>
                        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-[13px] text-white/55">
                            <span>@{profile.handle}</span>
                            <span aria-hidden="true">·</span>
                            <span className="inline-flex items-center gap-1.5">
                                <MapPin className="h-3.5 w-3.5" />
                                {profile.city}
                            </span>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 md:pb-3">
                        <button className="rounded-full bg-[var(--color-gold)] px-5 py-2.5 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">Follow</button>
                        <button className="rounded-full border border-white/15 bg-white/[0.03] px-5 py-2.5 text-[12px] font-bold uppercase tracking-[1.5px] text-white">Message</button>
                    </div>
                </div>
            </div>
        </section>
    );
}