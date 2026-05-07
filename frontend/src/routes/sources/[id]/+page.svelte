<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { getSource, getArticles, scrapeSource, updateSource } from '$lib/api';
    import { onMount } from 'svelte';
    import ArticleCard from '$lib/components/ArticleCard.svelte';

    let id = Number($page.params.id);
    let source: any = null;
    let articles: any[] = [];
    let loading = true;

    async function load() {
        try {
            [source, articles] = await Promise.all([getSource(id), getArticles({ source_id: id })]);
            if (!source) { goto('/collections'); return; }
        } catch (e) {}
        loading = false;
    }

    async function handleScrape() {
        try { await scrapeSource(id); await load(); } catch (e) {}
    }

    async function handleIntervalChange() {
        if (source) await updateSource(id, { scrape_interval: source.scrape_interval });
    }

    onMount(load);
</script>

<a href="/collections" class="back-link">&larr; {t('back')}</a>
<h1>{source?.name || source?.url || ''}</h1>
<p class="subtext"><a href={source?.url} target="_blank">{source?.url}</a></p>

<div class="card" style="display:flex;gap:var(--padding);align-items:center;margin:var(--padding) 0">
    <select value={source?.scrape_interval} onchange={handleIntervalChange}>
        <option value="manual">{t('sources_manual')}</option>
        <option value="hourly">{t('sources_hourly')}</option>
        <option value="daily">{t('sources_daily')}</option>
        <option value="weekly">{t('sources_weekly')}</option>
    </select>
    <button onclick={handleScrape} class="active">{t('sources_scrape_now')}</button>
</div>

<h3>{t('sources_articles')} ({articles.length})</h3>
<div class="list">
    {#each articles as a}
        <ArticleCard article={a} showFull={false} />
    {/each}
</div>

<style>
    .back-link { color: var(--gray); font-size: 13px; text-decoration: none; }
    .back-link:hover { color: var(--secondary); }
    .list { display: flex; flex-direction: column; gap: 8px; margin-top: var(--padding); }
</style>
