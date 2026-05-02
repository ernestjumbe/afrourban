import { NavigationExample } from "../system/navigation";
import { AfricanBackgroundPattern } from "../system/patterns";
import { TopTrimStrip } from "../system/trim-strips";

export function PageShellExample({ children }: { children: React.ReactNode }) {
    return (
        <div className="relative min-h-screen bg-[#0e0e0e] text-white">
            <AfricanBackgroundPattern />
            <TopTrimStrip />
            <NavigationExample />
            <div className="h-16" />
            <main className="mx-auto max-w-[1400px] px-6 py-12 md:px-16 md:py-16">{children}</main>
        </div>
    );
}