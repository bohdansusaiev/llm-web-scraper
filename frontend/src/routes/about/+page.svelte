<script lang="ts">
    import { t } from '$lib/i18n';

    const techs: { id: string, label: string }[] = [
        { id: 'python',      label: 'Python + FastAPI' },
        { id: 'crawl4ai',    label: 'Crawl4AI + Jina Reader' },
        { id: 'deepseek',    label: 'DeepSeek-chat' },
        { id: 'openalex',    label: 'OpenAlex · Semantic Scholar · arXiv · CORE' },
        { id: 'trafilatura', label: 'trafilatura + BeautifulSoup' },
        { id: 'svelte',      label: 'SvelteKit' },
        { id: 'sqlite',      label: 'SQLite' },
    ];
</script>

<svelte:head><title>{t('about_title')} · LLM-Scraper</title></svelte:head>

<h1>{t('about_title')}</h1>
<p class="subtitle">{t('about_subtitle')}</p>

<section class="block">
    <h3>{t('about_overview_title')}</h3>
    {#each t('about_overview_text').split('\n\n') as para}
        <p class="text">{para}</p>
    {/each}
</section>

<section class="block">
    <h3>{t('about_pipeline_title')}</h3>
    <p class="text">{t('about_pipeline_text')}</p>
</section>

<section class="block">
    <h3>{t('about_features_title')}</h3>
    <p class="text">{t('about_features_text')}</p>
</section>

<section class="block">
    <h3>{t('about_tech_title')}</h3>
    <div class="tech-grid">
        {#each techs as tech}
            <div class="tech-row">
                <span class="tech-name">{tech.label}</span>
                <span class="tech-desc">{t(`about_tech_${tech.id}`)}</span>
            </div>
        {/each}
    </div>
</section>

<section class="block author-block" style="margin-top: 48px; padding-bottom: 32px;">
    <h3>{t('about_author_title')}</h3>
    <p class="text">{t('about_author_name')} · <a href="mailto:{t('about_author_contact')}">{t('about_author_contact')}</a></p>
</section>

<style>
    h1 { margin-bottom: 6px; }
    .subtitle {
        font-size: 13px; color: var(--gray);
        margin-bottom: 32px; font-weight: 400;
    }
    .block { margin-bottom: 32px; }
    .block h3 { margin: 0 0 12px; font-size: 14px; }
    .text {
        font-size: 13.5px; line-height: 1.75; color: var(--secondary);
        margin: 0 0 10px; max-width: 680px;
    }
    .text:last-child { margin-bottom: 0; }

    .tech-grid { display: flex; flex-direction: column; gap: 8px; }
    .tech-row {
        display: flex; gap: 12px; align-items: baseline;
        font-size: 13px;
    }
    .tech-name {
        min-width: 220px; font-weight: 500; color: var(--secondary);
        flex-shrink: 0;
    }
    .tech-desc { color: var(--gray); line-height: 1.5; }

    .author-block p { color: var(--secondary); }
    .author-block a { color: var(--gray); }

    @media (max-width: 600px) {
        .tech-row { flex-direction: column; gap: 2px; }
        .tech-name { min-width: unset; }
    }
</style>
