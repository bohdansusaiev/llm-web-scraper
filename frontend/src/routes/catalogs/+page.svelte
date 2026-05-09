<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { listCatalogs, deleteCatalog, type CatalogSummary } from '$lib/api';

    let items: CatalogSummary[] = [];
    let error = '';

    onMount(load);

    async function load() {
        try { items = await listCatalogs(); }
        catch (e: any) { error = e.message; }
    }

    async function remove(id: number) {
        if (!confirm(t('catalog_delete_confirm'))) return;
        try { await deleteCatalog(id); items = items.filter(x => x.id !== id); }
        catch (e: any) { error = e.message; }
    }
</script>

<svelte:head><title>{t('catalogs_title')} · LLM-Scraper</title></svelte:head>

<h1>{t('catalogs_title')}</h1>

{#if error}<p class="err">{error}</p>{/if}

{#if items.length === 0}
    <p class="subtext">{t('catalogs_empty')}</p>
    <a href="/research" class="link">{t('research_title')} →</a>
{:else}
    <div class="list">
        {#each items as c}
            <div class="row card">
                <button class="row-main" onclick={() => goto(`/catalogs/${c.id}`)}>
                    <div class="topic">{c.topic}</div>
                    <div class="meta">
                        <span>{c.paper_count} {t('catalog_papers')}</span>
                        <span>·</span>
                        <span>{c.language.toUpperCase()}</span>
                        <span>·</span>
                        <span>{new Date(c.created_at).toLocaleDateString()}</span>
                    </div>
                </button>
                <button class="del" onclick={() => remove(c.id)} title={t('delete')} aria-label={t('delete')}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/></svg>
                </button>
            </div>
        {/each}
    </div>
{/if}

<style>
    .list { display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }
    .row { display: flex; align-items: stretch; padding: 0; }
    .row-main {
        flex: 1; padding: 12px 14px;
        background: transparent; border: 0;
        text-align: left; cursor: pointer; color: inherit;
    }
    .row-main:hover { background: var(--button-hover); }
    .topic { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
    .meta { font-size: 11px; color: var(--gray); display: flex; gap: 6px; }
    .del {
        background: transparent; border: 0;
        padding: 0 12px; color: var(--gray); cursor: pointer;
    }
    .del:hover { color: var(--red); }
    .err { color: var(--red); font-size: 12px; }
    .link { color: var(--blue); text-decoration: none; }
</style>
