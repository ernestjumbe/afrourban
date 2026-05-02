export function TopTrimStrip() {
    return (
        <div className="relative h-[6px] w-full overflow-hidden bg-[var(--color-gold)]">
            <svg className="absolute inset-0 h-full w-full" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
                <defs>
                    <pattern id="trimTopExample" x="0" y="0" width="12" height="6" patternUnits="userSpaceOnUse">
                        <polygon points="0,6 6,0 12,6" fill="rgba(0,0,0,0.25)" />
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#trimTopExample)" />
            </svg>
        </div>
    );
}

export function BottomTrimStrip() {
    return <TopTrimStrip />;
}