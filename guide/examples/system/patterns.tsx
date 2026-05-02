export function AfricanBackgroundPattern() {
    return (
        <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true" style={{ zIndex: -1 }}>
            <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <pattern id="africanBgExample" width="240" height="240" patternUnits="userSpaceOnUse">
                        {[
                            [0, 0],
                            [240, 0],
                            [0, 240],
                            [240, 240],
                        ].map(([cx, cy]) => (
                            <g key={`${cx}-${cy}`} fill="none" stroke="white" strokeWidth="0.5" opacity="0.045">
                                <path d={`M${cx},${cy - 14}L${cx + 14},${cy} ${cx},${cy + 14} ${cx - 14},${cy}Z`} />
                                <path d={`M${cx},${cy - 7}L${cx + 7},${cy} ${cx},${cy + 7} ${cx - 7},${cy}Z`} />
                            </g>
                        ))}
                        <g fill="none" stroke="white" strokeWidth="0.5" opacity="0.03">
                            <path d="M120,106L134,120 120,134 106,120Z" />
                            <path d="M120,113L127,120 120,127 113,120Z" />
                        </g>
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#africanBgExample)" />
            </svg>
        </div>
    );
}