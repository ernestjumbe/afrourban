import { Eye, EyeOff, Search } from "lucide-react";
import { useState } from "react";

export function FormExamples() {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div className="max-w-xl space-y-4 bg-[#0e0e0e] p-8 text-white">
            <label className="block space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Email</span>
                <input
                    type="email"
                    placeholder="you@example.com"
                    className="h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 text-[14px] text-white outline-none placeholder:text-white/30 focus:border-[var(--color-gold)]/50"
                />
            </label>

            <label className="block space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Password</span>
                <div className="flex h-11 items-center rounded-xl border border-white/[0.08] bg-white/[0.04] px-4 focus-within:border-[var(--color-gold)]/50">
                    <input
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter password"
                        className="flex-1 bg-transparent text-[14px] text-white outline-none placeholder:text-white/30"
                    />
                    <button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((value) => !value)} className="text-white/40 hover:text-[var(--color-gold)]">
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                </div>
            </label>

            <label className="block space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-[1.5px] text-white/45">Search</span>
                <div className="flex h-11 items-center gap-2.5 rounded-full border border-white/[0.08] bg-white/[0.04] px-4 focus-within:border-[var(--color-gold)]/50">
                    <Search className="h-4 w-4 text-white/30" />
                    <input
                        type="text"
                        placeholder="Search by name, description, or address"
                        className="flex-1 bg-transparent text-[14px] text-white outline-none placeholder:text-white/30"
                    />
                </div>
            </label>
        </div>
    );
}