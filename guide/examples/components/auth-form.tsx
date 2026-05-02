import { Eye, EyeOff, Mail, User } from "lucide-react";
import { useState } from "react";

export function AuthFormExample() {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div className="max-w-xl rounded-[24px] border border-white/[0.08] bg-white/[0.03] p-6 md:p-8 text-white">
            <div className="mb-6 inline-flex rounded-full border border-white/15 p-1">
                <button className="rounded-full bg-[var(--color-gold)] px-4 py-2 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">Passphrase</button>
                <button className="rounded-full px-4 py-2 text-[12px] font-bold uppercase tracking-[1.5px] text-white/50">Password</button>
            </div>

            <form className="space-y-4">
                <label className="block space-y-2">
                    <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Username</span>
                    <div className="flex h-11 items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 focus-within:border-[var(--color-gold)]/50">
                        <User className="h-4 w-4 text-white/30" />
                        <input className="flex-1 bg-transparent text-[14px] text-white outline-none placeholder:text-white/30" placeholder="kwame-mensah" />
                    </div>
                </label>

                <label className="block space-y-2">
                    <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Email</span>
                    <div className="flex h-11 items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 focus-within:border-[var(--color-gold)]/50">
                        <Mail className="h-4 w-4 text-white/30" />
                        <input className="flex-1 bg-transparent text-[14px] text-white outline-none placeholder:text-white/30" placeholder="you@example.com" />
                    </div>
                </label>

                <label className="block space-y-2">
                    <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Password</span>
                    <div className="flex h-11 items-center gap-2.5 rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 focus-within:border-[var(--color-gold)]/50">
                        <input type={showPassword ? "text" : "password"} className="flex-1 bg-transparent text-[14px] text-white outline-none placeholder:text-white/30" placeholder="Create a password" />
                        <button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)} className="text-white/40 hover:text-[var(--color-gold)]">
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </button>
                    </div>
                </label>

                <label className="flex items-start gap-3 pt-1 text-[13px] text-white/60">
                    <input type="checkbox" className="mt-0.5 h-4 w-4 rounded border-white/15 bg-transparent" />
                    <span>I agree to the terms and privacy policy.</span>
                </label>

                <button className="inline-flex h-12 w-full items-center justify-center rounded-full bg-[var(--color-gold)] px-6 text-[12px] font-bold uppercase tracking-[1.5px] text-[#1a1a1a]">
                    Create account
                </button>
            </form>
        </div>
    );
}