<script lang="ts">
    import { t } from '$lib/i18n';
    import { getArticles, deleteArticle, getCollections, exportArticles } from '$lib/api';
    import { onMount } from 'svelte';
    import ArticleCard from '$lib/components/ArticleCard.svelte';

    let articles: any[] = [];
    let loading = true;
    let search = '';
    let selectedType = '';
    let selectedCollection: number | null = null;
    let collections: any[] = [];
    const types = ['', 'news', 'analysis', 'opinion', 'interview', 'report', 'other'];

    async function load() {
        try {
            const params: any = { limit: 100 };
            if (search) params.q = search;
            if (selectedType) params.article_type = selectedType;
            if (selectedCollection) params.collection_id = selectedCollection;
            articles = await getArticles(params);
            if (collections.length === 0) collections = await getCollections();
        } catch (e) {}
        loading = false;
    }

    async function handleExport(format: string) {
        const ids = articles.map(a => a.id);
        if (ids.length === 0) return;
        try {
            const data = await exportArticles(ids, format);
            if (format === 'json') {
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'articles.json'; a.click();
                URL.revokeObjectURL(url);
            } else if (format === 'csv' && data.csv) {
                const blob = new Blob([data.csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'articles.csv'; a.click();
                URL.revokeObjectURL(url);
            }
        } catch (e) {}
    }

    onMount(load);
</script>

<h1>{t('history_title')}</h1>

<div class="filters">
    <input type="text" bind:value={search} placeholder={t('history_search')} oninput={load} />
    <select bind:value={selectedType} onchange={load}>
        <option value="">{t('type_all')}</option>
        {#each types.filter(t => t) as tp}<option value={tp}>{t(tp)}</option>{/each}
    </select>
    <select bind:value={selectedCollection} onchange={load}>
        <option value="">{t('collections_title')}</option>
        {#each collections as c}<option value={c.id}>{c.name}</option>{/each}
    </select>
</div>

<div class="header-row">
    <p class="subtext">{t('history_results').replace('{}', String(articles.length))}</p>
    <div class="actions">
        <button onclick={() => handleExport('json')}>{t('export_json')}</button>
        <button onclick={() => handleExport('csv')}>{t('export_csv')}</button>
    </div>
</div>

{#if articles.length === 0 && !loading}
    <p class="subtext">{t('history_no_results')}</p>
{:else}
    <div class="list">
        {#each articles as a}
            <ArticleCard article={a} showFull={false} onDelete={async () => { await deleteArticle(a.id); await load(); }} />
        {/each}
    </div>
{/if}

<style>
    .filters {
        display: flex;
        gap: 6px;
        margin-bottom: var(--padding);
    }
    .filters input { flex: 1; }

    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--padding);
    }

    .actions { display: flex; gap: 4px; }

    .list { display: flex; flex-direction: column; gap: 8px; }

    button { font-size: 12.5px; padding: 4px 10px; }
</style>
