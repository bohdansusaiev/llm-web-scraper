<script lang="ts">
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { getCollections, createCollection, deleteCollection } from '$lib/api';
    import { onMount } from 'svelte';

    let collections: any[] = [];
    let loading = true;
    let newName = '';
    let showForm = false;

    async function load() {
        try { collections = await getCollections(); } catch (e) {}
        loading = false;
    }

    async function handleCreate() {
        if (!newName.trim()) return;
        try { await createCollection(newName.trim()); newName = ''; showForm = false; await load(); } catch (e) {}
    }

    async function handleDelete(id: number) {
        try { await deleteCollection(id); await load(); } catch (e) {}
    }

    onMount(load);
</script>

<div class="header-row">
    <h1>{t('collections_title')}</h1>
    <button onclick={() => showForm = !showForm}>{showForm ? t('cancel') : '+'}</button>
</div>

{#if showForm}
    <div class="input-row" style="margin-bottom:var(--padding)">
        <input type="text" bind:value={newName} placeholder={t('collections_name')} onkeydown={(e) => e.key === 'Enter' && handleCreate()} />
        <button onclick={handleCreate} class="active">{t('collections_create')}</button>
    </div>
{/if}

{#if collections.length === 0 && !loading}
    <p class="subtext">{t('collections_empty')}</p>
{:else}
    <div class="list">
        {#each collections as c}
            <div class="card list-item">
                <button class="list-button" onclick={() => goto(`/collections/${c.id}`)}>
                    <span class="list-title">{c.name}</span>
                    <span class="list-meta">{c.source_count} {t('collections_sources')} &middot; {c.article_count} {t('collections_articles')}</span>
                </button>
                <button onclick={() => handleDelete(c.id)} class="danger">{t('delete')}</button>
            </div>
        {/each}
    </div>
{/if}

<style>
    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--padding);
    }

    .input-row {
        display: flex;
        gap: 6px;
    }
    .input-row input { flex: 1; }

    .list {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .list-item {
        display: flex;
        align-items: center;
        gap: var(--padding);
        justify-content: space-between;
    }

    .list-button {
        display: flex;
        gap: 8px;
        align-items: baseline;
        background: transparent;
        box-shadow: none;
        padding: 0;
        text-align: left;
        flex: 1;
    }
    .list-button:hover { background: transparent; }

    .list-title { font-size: 14.5px; font-weight: 500; }
    .list-meta { font-size: 12px; color: var(--gray); }

    button.danger { color: var(--red); font-size: 12.5px; padding: 4px 10px; }
    button.danger:hover { background: var(--red); color: var(--primary); }
</style>
