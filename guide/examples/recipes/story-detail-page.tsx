import { DetailHeroExample } from "../components/detail-hero";
import { PageShellExample } from "../components/page-shell";

export function StoryDetailPageRecipe() {
    return (
        <PageShellExample>
            <DetailHeroExample />
            <div className="grid gap-10 pt-10 lg:grid-cols-[minmax(0,1fr)_280px]">
                <article className="max-w-3xl space-y-6 text-[16px] leading-8 text-white/78">
                    <p>
                        This recipe uses a strong title area, large media, a readable prose column, and a separate side rail for secondary actions.
                    </p>
                    <p>
                        Keep ornament away from the body column. The page should feel editorial, not decorative.
                    </p>
                    <blockquote className="border-l border-[var(--color-gold)] pl-5 font-serif text-[24px] leading-snug text-white">
                        Let typography and spacing carry the emotion.
                    </blockquote>
                </article>

                <aside className="space-y-4 rounded-[24px] border border-white/[0.08] bg-white/[0.03] p-6 text-white/60">
                    <p className="text-[11px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Side Rail</p>
                    <p>Author, share, save, or related links live here.</p>
                </aside>
            </div>
        </PageShellExample>
    );
}