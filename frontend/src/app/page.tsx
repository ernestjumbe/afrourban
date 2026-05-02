import { getRuntimeConfig } from '@/lib/env';
import { HomeEmptyState } from '@/components/home-empty-state';
import { HomeHero } from '@/components/home-hero';

const homeHeroContent = {
    eyebrow: 'City Notes',
    title: 'AfroUrban, after dark',
    body: 'A new editorial city guide is taking shape for the people, places, and late-night rituals that deserve more than filler copy.',
    supportingNote:
        'The first public surface stays deliberately spare while the wider archive, events, and organization layers are being prepared.',
};

const homeEmptyStateContent = {
    eyebrow: 'Intentional Empty State',
    title: 'Nothing is being padded for launch.',
    body: 'No listings are being faked for launch. This opening page is here to signal the visual language, not to pretend the city guide is already full.',
    supportingNote:
        'Published stories, event calendars, and trusted directories will appear here once they are ready to earn the space.',
};

export default function HomePage() {
    const runtimeConfig = getRuntimeConfig();

    return (
        <div className="homepage">
            <HomeHero content={homeHeroContent} />
            <HomeEmptyState content={homeEmptyStateContent} />
            <p className="homepage__meta">Serving from {runtimeConfig.siteUrl} on port {runtimeConfig.port}</p>
        </div>
    );
}