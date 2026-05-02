import { DetailHeroExample } from "../components/detail-hero";
import { EditorialCardExample } from "../components/editorial-card";
import { PageShellExample } from "../components/page-shell";

export function IdentityDetailPageRecipe() {
    return (
        <PageShellExample>
            <DetailHeroExample />

            <section className="grid gap-8 pt-10 lg:grid-cols-[1.3fr_0.7fr]">
                <div className="space-y-6">
                    <div className="rounded-[24px] border border-white/[0.08] bg-white/[0.03] p-6 text-white/70">
                        <p className="text-[11px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">About</p>
                        <p className="mt-4 text-[15px] leading-7">Use this area for description, stats, contact actions, or structured identity details.</p>
                    </div>
                    <EditorialCardExample />
                </div>

                <aside className="rounded-[24px] border border-white/[0.08] bg-white/[0.03] p-6 text-white/60">
                    <p className="text-[11px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Actions</p>
                    <div className="mt-4 flex flex-col gap-3">
                        <button className="rounded-full bg-[var(--color-gold)] px-5 py-3 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">Visit website</button>
                        <button className="rounded-full border border-white/15 px-5 py-3 text-[12px] font-bold uppercase tracking-[1.5px] text-white">Contact</button>
                    </div>
                </aside>
            </section>
        </PageShellExample>
    );
}