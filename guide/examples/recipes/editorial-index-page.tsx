import { CategoryChipRailExample } from "../components/category-chip-rail";
import { EditorialCardExample } from "../components/editorial-card";
import { PageShellExample } from "../components/page-shell";

export function EditorialIndexPageRecipe() {
    return (
        <PageShellExample>
            <header className="max-w-3xl pb-10">
                <p className="text-[12px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Stories</p>
                <h1 className="mt-4 font-serif text-[40px] font-bold leading-[1.02] tracking-[-0.5px] md:text-[56px]">
                    Editorial Index Page
                </h1>
                <p className="mt-5 max-w-2xl text-[16px] leading-relaxed text-white/60">
                    Use a short hero, a filter rail, one featured item, and a disciplined card grid.
                </p>
            </header>

            <section className="pb-8">
                <CategoryChipRailExample activeCategory="All" />
            </section>

            <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                <EditorialCardExample />
                <EditorialCardExample />
                <EditorialCardExample />
            </section>
        </PageShellExample>
    );
}