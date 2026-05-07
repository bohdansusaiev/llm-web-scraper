<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { language } from '$lib/stores/language';
    import { t } from '$lib/i18n';
    import { getCollections, getSources, createSource, deleteSource, scrapeSource, batchScrape, getBatchStatus } from '$lib/api';
    import { onMount } from 'svelte';

    let lang: 'en' | 'ua';
    language.subscribe(v => lang = v);

    let id = Number($page.params.id);
    let collection: any = null;
    let sources: any[] = [];
    let loading = true;
    let newUrl = '';
    let showForm = false;
    let batchJob: any = null;

    async function load() {
        const cols = await getCollections();
        collection = cols.find(c => c.id === id) || null;
        if (!collection) { goto('/collections'); return; }
        sources = await getSources(id);
        loading = false;
    }

    async function handleAdd() {
        if (!newUrl.trim()) return;
        await createSource(id, newUrl.trim());
        newUrl = ''; showForm = false;
        await load();
    }

    async function handleBatch() {
        const job = await batchScrape(id, lang);
        batchJob = { ...job, completed: 0, failed: 0 };
        const poll = setInterval(async () => {
            const j = await getBatchStatus(job.job_id);
            batchJob = j;
            if (j.status === 'completed') { clearInterval(poll); await load(); setTimeout(() => batchJob = null, 3000); }
        }, 1500);
    }

    onMount(load);
</script>

<a href="/collections" class="back-link">&larr; {t('back')}</a>
<h1>{collection?.name || ''}</h1>
<p class="subtext">{sources.length} {t('collections_sources')} &middot; {collection?.article_count} {t('collections_articles')}</p>

{#if sources.length > 0}
    <button onclick={handleBatch} disabled={!!batchJob} class="active" style="margin-bottom:var(--padding)">{t('sources_scrape_all')}</button>
{/if}

{#if batchJob}
    <div class="card" style="margin-bottom:var(--padding)">
        <div class="progress">
            <div class="progress-bar" style="width:{(batchJob.completed + batchJob.failed) / batchJob.total * 100}%"></div>
        </div>
        <p class="subtext">{batchJob.completed + batchJob.failed} / {batchJob.total}</p>
        {#if batchJob.status === 'completed'}
            <p class="subtext" style="color:var(--green)">{t('sources_batch_done').replace('{}', String(batchJob.completed)).replace('{}', String(batchJob.failed))}</p>
        {/if}
    </div>
{/if}

<div class="input-row" style="margin-bottom:var(--padding)">
    <button onclick={() => showForm = !showForm}>+</button>
</div>

{#if showForm}
    <div class="input-row" style="margin-bottom:var(--padding)">
        <input type="url" bind:value={newUrl} placeholder={t('sources_url')} onkeydown={(e) => e.key === 'Enter' && handleAdd()} />
        <button onclick={handleAdd} class="active">{t('sources_add_btn')}</button>
    </div>
{/if}

<div class="list">
    {#each sources as s}
        <div class="card list-item">
            <button class="list-button" onclick={() => goto(`/sources/${s.id}`)}>
                <div>
                    <span class="list-title">{s.name || s.url}</span>
                    <div class="list-sub">{s.url}</div>
                </div>
            </button>
            <div class="item-actions">
                <button onclick={() => { scrapeSource(s.id); load(); }}>{t('sources_scrape_now')}</button>
                <button onclick={() => deleteSource(s.id).then(load)} class="danger">{t('delete')}</button>
            </div>
        </div>
    {/each}
    {#if sources.length === 0 && !loading}
        <p class="subtext">{t('sources_empty')}</p>
    {/if}
</div>

<style>
    .back-link { color: var(--gray); font-size: 13px; text-decoration: none; }
    .back-link:hover { color: var(--secondary); }

    .input-row { display: flex; gap: 6px; }
    .input-row input { flex: 1; }

    .progress {
        height: 4px;
        background: var(--button);
        border-radius: 2px;
        overflow: hidden;
    }
    .progress-bar {
        height: 100%;
        background: var(--secondary);
        border-radius: 2px;
        transition: width 0.3s ease;
    }

    .list { display: flex; flex-direction: column; gap: 6px; }
    .list-item { display: flex; align-items: center; gap: var(--padding); justify-content: space-between; }
    .list-button { background: transparent; box-shadow: none; padding: 0; text-align: left; flex: 1; display: block; }
    .list-button:hover { background: transparent; }
    .list-title { font-size: 14.5px; font-weight: 500; }
    .list-sub { font-size: 11px; color: var(--gray); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px; }
    .item-actions { display: flex; gap: 4px; }
    button.danger { color: var(--red); font-size: 12.5px; padding: 4px 10px; }
    button.danger:hover { background: var(--red); color: var(--primary); }
</style>
