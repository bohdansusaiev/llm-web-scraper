<script lang="ts">
    import { language } from '$lib/stores/language';
    import { t } from '$lib/i18n';
    import { scrapeArticle, getCollections, createSource, getSources, type ScrapeResult } from '$lib/api';
    import { onMount } from 'svelte';

    let lang: 'en' | 'ua';
    language.subscribe(v => lang = v);

    let tab: 'quick' | 'collection' = 'quick';
    let url = '';
    let loading = false;
    let result: ScrapeResult | null = null;
    let error = '';

    let collections: any[] = [];
    let selectedCollection: number | null = null;
    let collUrl = '';
    let collLoading = false;
    let collResult = '';

    let saveTargetId: number | null = null;
    let saveResult = '';

    async function loadCollections() {
        try { collections = await getCollections(); if (collections.length) selectedCollection = collections[0].id; } catch (e) {}
    }

    async function handleScrape() {
        if (!url) return;
        error = '';
        loading = true;
        saveResult = '';
        try { result = await scrapeArticle(url, lang); }
        catch (e: any) { error = e.message; }
        loading = false;
    }

    async function handleCollectionScrape() {
        if (!collUrl || !selectedCollection) return;
        collLoading = true;
        collResult = '';
        try {
            const srcs = await getSources(selectedCollection);
            let sid = srcs.filter(s => s.url === collUrl)[0]?.id || null;
            if (!sid) {
                await createSource(selectedCollection, collUrl);
                const updated = await getSources(selectedCollection);
                sid = updated.filter(s => s.url === collUrl)[0]?.id || null;
            }
            await scrapeArticle(collUrl, lang, sid || undefined);
            collResult = t('saved');
        } catch (e) {}
        collLoading = false;
    }

    async function handleSaveToCollection() {
        if (!result || !saveTargetId) return;
        saveResult = '';
        try {
            const srcs = await getSources(saveTargetId);
            let sid = srcs.filter(s => s.url === result.url)[0]?.id || null;
            if (!sid) {
                await createSource(saveTargetId, result.url, '');
                const updated = await getSources(saveTargetId);
                sid = updated.filter(s => s.url === result.url)[0]?.id || null;
            }
            await scrapeArticle(result.url, lang, sid || undefined);
            saveResult = t('saved');
        } catch (e: any) { saveResult = e.message || 'error'; }
    }

    onMount(loadCollections);
</script>

<h1>{t('nav_scraper')}</h1>

<div class="tabs">
    <button class:active={tab === 'quick'} onclick={() => tab = 'quick'}>{t('scraper_quick')}</button>
    <button class:active={tab === 'collection'} onclick={() => { tab = 'collection'; loadCollections(); }}>{t('scraper_to_collection')}</button>
</div>

{#if tab === 'quick'}
    <div class="input-row">
        <input type="url" bind:value={url} placeholder={t('url_placeholder')}
            onkeydown={(e) => e.key === 'Enter' && handleScrape()} />
        <button onclick={handleScrape} disabled={loading || !url} class="active">
            {loading ? '...' : t('scrape_btn')}
        </button>
    </div>

    {#if error}
        <p class="subtext" style="color:var(--red);margin-top:var(--padding)">{error}</p>
    {/if}

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
                    <div class="result-badges">
                        {#if result.article_type}
                            <span class="badge">{t(result.article_type)}</span>
                        {/if}
                        {#if result.translated}
                            <span class="badge badge-accent">{t('translated')}</span>
                        {/if}
                    </div>
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

                <div class="result-actions">
                    <div class="save-row">
                        <select bind:value={saveTargetId} class="save-select">
                            <option value="">+ {t('collection_select')}</option>
                            {#each collections as c}
                                <option value={c.id}>{c.name}</option>
                            {/each}
                        </select>
                        <button onclick={handleSaveToCollection} disabled={!saveTargetId}>
                            {t('sources_add_btn')}
                        </button>
                    </div>
                    {#if saveResult}
                        <span class="save-msg">{saveResult}</span>
                    {/if}
                </div>
            {/if}
        </div>

        <button onclick={() => { result = null; saveResult = ''; }} class="again-btn">
            {t('scraper_again')}
        </button>
    {/if}

{:else}
    <div class="card">
        {#if collections.length === 0}
            <p class="subtext">{t('collections_empty')}</p>
        {:else}
            <select bind:value={selectedCollection}>
                {#each collections as c}
                    <option value={c.id}>{c.name} ({c.source_count})</option>
                {/each}
            </select>
            <div class="input-row" style="margin-top:var(--padding)">
                <input type="url" bind:value={collUrl} placeholder={t('url_placeholder')}
                    onkeydown={(e) => e.key === 'Enter' && handleCollectionScrape()} />
                <button onclick={handleCollectionScrape} disabled={collLoading || !collUrl} class="active">
                    {collLoading ? '...' : t('scrape_btn')}
                </button>
            </div>
            {#if collResult}
                <p class="subtext" style="color:var(--green);margin-top:var(--padding)">{collResult}</p>
            {/if}
        {/if}
    </div>
{/if}

<style>
    .tabs {
        display: flex;
        gap: 2px;
        margin: var(--padding) 0;
    }
    .tabs button.active {
        background: var(--secondary);
        color: var(--primary);
    }

    .input-row {
        display: flex;
        gap: 6px;
    }
    .input-row input { flex: 1; }

    .result-card {
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

    .result-badges {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
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
        margin-bottom: var(--padding);
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

    .result-actions {
        border-top: 1px solid var(--card-stroke);
        padding-top: var(--padding);
    }

    .save-row {
        display: flex;
        gap: 6px;
    }

    .save-select {
        flex: 1;
        font-size: 13px;
    }

    .save-msg {
        font-size: 12px;
        color: var(--green);
        margin-top: 4px;
        display: block;
    }

    .again-btn {
        margin-top: var(--padding);
    }

    select {
        width: 100%;
    }
</style>
