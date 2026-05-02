import { EditorialCardExample } from "../components/editorial-card";
import { PageShellExample } from "../components/page-shell";

export function FeatureLandingPageRecipe() {
    return (
        <PageShellExample>
            <section className="grid gap-6 pb-12 lg:grid-cols-[1.4fr_0.6fr]">
                <div className="rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-8">
                    <p className="text-[12px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Featured</p>
                    <h1 className="mt-4 max-w-2xl font-serif text-[40px] font-bold leading-[1.02] tracking-[-0.5px] md:text-[56px]">
                        Feature Landing Page
                    </h1>
                    <p className="mt-5 max-w-xl text-[16px] leading-relaxed text-white/60">
                        Combine an oversized lead story with smaller supporting modules. Vary module scale intentionally.
                    </p>
                </div>

                <div className="rounded-[32px] border border-white/[0.08] bg-white/[0.03] p-8 text-white/60">
                    <p className="text-[11px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Newsletter</p>
                    <p className="mt-4">Use the side module for sign-up, archive, or upcoming event highlights.</p>
                </div>
            </section>

            <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                <EditorialCardExample />
                <EditorialCardExample />
                <EditorialCardExample />
            </section>
        </PageShellExample>
    );
}