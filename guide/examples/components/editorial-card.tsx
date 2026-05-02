import { ArrowUpRight, Clock, MapPin } from "lucide-react";

const sampleItem = {
    category: "Music",
    date: "21 Jun 2026",
    title: "Afrobeats Summer Festival",
    time: "18:00",
    city: "Stockholm",
    image: "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=900&q=80",
};

export function EditorialCardExample() {
    return (
        <article className="group w-full max-w-[420px] cursor-pointer">
            <div className="relative overflow-hidden rounded-xl">
                <div className="relative aspect-[4/5]">
                    <img src={sampleItem.image} alt={sampleItem.title} className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105" />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                </div>

                <div className="absolute inset-0 flex flex-col justify-end p-6">
                    <div className="mb-3 flex items-center gap-3">
                        <span className="rounded bg-[var(--color-gold)] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">
                            {sampleItem.category}
                        </span>
                        <span className="text-[12px] font-medium text-white/60">{sampleItem.date}</span>
                    </div>

                    <h3 className="font-serif text-[26px] font-bold leading-[1.15] text-white">{sampleItem.title}</h3>

                    <div className="mt-3 flex items-center gap-4 text-[12px] text-white/50">
                        <span className="inline-flex items-center gap-1">
                            <Clock className="h-3.5 w-3.5" />
                            {sampleItem.time}
                        </span>
                        <span className="inline-flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5" />
                            {sampleItem.city}
                        </span>
                        <ArrowUpRight className="ml-auto h-4 w-4 text-white/35" />
                    </div>
                </div>
            </div>
        </article>
    );
}