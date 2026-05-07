<script lang="ts">
    import { goto } from '$app/navigation';
    import { t, lang } from '$lib/i18n';
    import { scrapeArticle } from '$lib/api';

    let url = '';
    let loading = false;
    let result: any = null;

    async function handleScrape() {
        if (!url) return;
        loading = true;
        try { result = await scrapeArticle(url, lang()); }
        catch (e: any) { result = { error: e.message || 'scrape failed' }; }
        loading = false;
    }
</script>

<svelte:head><title>NewsScraper</title></svelte:head>

<div class="center">
    <div class="hero">
        <h1>news scraper</h1>
        <p class="subtext">
            any news site &middot; structured data &middot; zero configuration
        </p>

        <div class="input-row">
            <input type="url" bind:value={url} placeholder="https://..." autocomplete="off"
                onkeydown={(e) => e.key === 'Enter' && handleScrape()} />
            <button onclick={handleScrape} disabled={loading || !url} class="active">
                {loading ? '...' : 'scrape'}
            </button>
        </div>

        {#if result}
            <div class="card result-card">
                {#if result.error}
                    <p class="subtext" style="color:var(--red)">{result.error}</p>
                {:else}
                    {#if result.image}
                        <img src={result.image} alt="" class="result-img" loading="lazy"
                            onerror={(e) => (e.target as HTMLImageElement).style.display = 'none'} />
                    {/if}

                    <div class="result-head">
                        <h3>{result.title || t('no_title')}</h3>
                        {#if result.article_type}
                            <span class="badge">{t(result.article_type)}</span>
                        {/if}
                        {#if result.translated}
                            <span class="badge badge-accent">{t('translated')}</span>
                        {/if}
                    </div>

                    <div class="result-meta">
                        {#if result.author}<span>{result.author}</span>{/if}
                        {#if result.date}<span>{result.date}</span>{/if}
                    </div>

                    {#if result.summary}
                        <div class="text-content result-summary">{result.summary}</div>
                    {/if}

                    {#if result.key_points}
                        <div class="result-points">
                            <p class="points-label">{t('key_points')}</p>
                            {#each result.key_points.split('\n').filter(Boolean) as p}
                                <p class="point">- {p.replace(/^[-*\s]+/, '')}</p>
                            {/each}
                        </div>
                    {/if}
                {/if}
            </div>
        {/if}

        <div class="bottom-links">
            <a href="/login">{t('login_btn')}</a>
            <a href="/register">{t('register_btn')}</a>
        </div>
    </div>

    <div class="about-section">
        <h3>{t('about_how_title')}</h3>
        <div class="steps">
            <div class="step"><span class="step-num">1</span><span>{t('about_how_1_desc')}</span></div>
            <div class="step"><span class="step-num">2</span><span>{t('about_how_2_desc')}</span></div>
            <div class="step"><span class="step-num">3</span><span>{t('about_how_3_desc')}</span></div>
        </div>
    </div>

    <div class="about-section">
        <h3>{t('about_adaptivity_title')}</h3>
        <div class="text-content adaptivity">{t('about_adaptivity_text')}</div>
    </div>

    <footer>
        <p class="subtext" style="text-align:center;padding:calc(var(--padding)*2)">
            {t('about_author_name')} &middot; {t('about_author_group')} &middot; {t('about_author_specialty')}
        </p>
    </footer>
</div>

<style>
    .center {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-height: 100vh;
    }

    .hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 0 40px;
        width: 100%;
        max-width: 560px;
    }

    .hero h1 {
        font-size: 32px;
        letter-spacing: -2px;
        margin-bottom: 12px;
    }

    .input-row {
        display: flex;
        width: 100%;
        gap: 6px;
        margin-top: 20px;
    }
    .input-row input { flex: 1; font-size: 14.5px; padding: 8px 14px; }
    .input-row button { padding: 8px 20px; font-size: 14.5px; }

    .result-card {
        width: 100%;
        margin-top: var(--padding);
    }

    .result-img {
        width: 100%;
        border-radius: var(--border-radius);
        margin-bottom: var(--padding);
    }

    .result-head {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 6px;
    }

    .result-meta {
        font-size: 12px;
        color: var(--gray);
        display: flex;
        gap: 12px;
        margin-bottom: var(--padding);
    }

    .result-summary {
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: var(--padding);
    }

    .result-points {
        border-top: 1px solid var(--card-stroke);
        padding-top: var(--padding);
    }

    .points-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--gray);
        margin-bottom: 6px;
    }

    .point {
        font-size: 12.5px;
        color: var(--gray);
        line-height: 1.5;
        margin: 2px 0;
        user-select: text;
        -webkit-user-select: text;
    }

    .bottom-links {
        display: flex;
        gap: 16px;
        margin-top: 20px;
        font-size: 13px;
    }

    .bottom-links a {
        color: var(--gray);
        text-decoration: none;
        font-weight: 500;
    }

    .about-section {
        width: 100%;
        max-width: 640px;
        padding: 32px var(--padding);
    }

    .about-section h3 {
        margin-bottom: 12px;
    }

    .adaptivity {
        font-size: 13px;
        line-height: 1.7;
        white-space: pre-line;
    }

    .steps {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .step {
        display: flex;
        gap: 12px;
        font-size: 13px;
        color: var(--gray);
        align-items: baseline;
    }

    .step-num {
        color: var(--secondary);
        font-weight: 500;
        font-size: 13px;
        min-width: 16px;
    }
</style>
