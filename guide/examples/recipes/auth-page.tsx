import { AuthFormExample } from "../components/auth-form";
import { PageShellExample } from "../components/page-shell";

export function AuthPageRecipe() {
    return (
        <PageShellExample>
            <div className="grid items-start gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:pt-8">
                <section className="max-w-xl">
                    <p className="text-[12px] font-bold uppercase tracking-[2px] text-[var(--color-gold)]">Register</p>
                    <h1 className="mt-4 font-serif text-[40px] font-bold leading-[1.02] tracking-[-0.5px] md:text-[56px]">
                        Auth Page
                    </h1>
                    <p className="mt-5 text-[16px] leading-relaxed text-white/60">
                        Pair one concise editorial intro with a controlled auth form. Keep the UI calm and the CTA obvious.
                    </p>
                </section>

                <AuthFormExample />
            </div>
        </PageShellExample>
    );
}