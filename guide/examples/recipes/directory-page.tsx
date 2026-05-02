import { DirectoryFiltersExample } from "../components/directory-filters";
import { EditorialCardExample } from "../components/editorial-card";
import { PageShellExample } from "../components/page-shell";

export function DirectoryPageRecipe() {
    return (
        <PageShellExample>
            <header className="max-w-3xl pb-10">
                <p className="text-[12px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Directory</p>
                <h1 className="mt-4 font-serif text-[40px] font-bold leading-[1.02] tracking-[-0.5px] md:text-[56px]">
                    Directory Page
                </h1>
                <p className="mt-5 text-[16px] leading-relaxed text-white/60">Lead with a concise intro, then keep search, filters, and cards in a clean editorial shell.</p>
            </header>

            <section className="pb-8">
                <DirectoryFiltersExample />
            </section>

            <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                <EditorialCardExample />
                <EditorialCardExample />
                <EditorialCardExample />
            </section>
        </PageShellExample>
    );
}