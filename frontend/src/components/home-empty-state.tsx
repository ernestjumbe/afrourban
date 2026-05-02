export type HomeEmptyStateContent = {
    eyebrow: string;
    title: string;
    body: string;
    supportingNote: string;
};

type HomeEmptyStateProps = {
    content: HomeEmptyStateContent;
};

export function HomeEmptyState({ content }: HomeEmptyStateProps) {
    return (
        <section className="home-empty-state" aria-labelledby="home-empty-state-title">
            <p className="home-empty-state__eyebrow">{content.eyebrow}</p>
            <div className="home-empty-state__card">
                <div>
                    <h2 className="home-empty-state__title" id="home-empty-state-title">
                        {content.title}
                    </h2>
                    <p className="home-empty-state__body">{content.body}</p>
                </div>

                <p className="home-empty-state__supporting-note">{content.supportingNote}</p>
            </div>
        </section>
    );
}