export type HomeHeroContent = {
    eyebrow: string;
    title: string;
    body: string;
    supportingNote: string;
};

type HomeHeroProps = {
    content: HomeHeroContent;
};

export function HomeHero({ content }: HomeHeroProps) {
    return (
        <section className="home-hero" aria-labelledby="home-hero-title">
            <p className="home-hero__eyebrow">{content.eyebrow}</p>
            <div className="home-hero__layout">
                <div className="home-hero__copy">
                    <h1 className="home-hero__title" id="home-hero-title">
                        {content.title}
                    </h1>
                    <p className="home-hero__body">{content.body}</p>
                </div>

                <p className="home-hero__supporting-note">{content.supportingNote}</p>
            </div>
        </section>
    );
}