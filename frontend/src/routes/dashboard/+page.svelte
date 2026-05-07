<script lang="ts">
    import { t } from '$lib/i18n';
    import { getDashboardStats, getArticles, type DashboardStats, type Article } from '$lib/api';
    import { onMount } from 'svelte';
    import ArticleCard from '$lib/components/ArticleCard.svelte';

    let stats: DashboardStats | null = null;
    let articles: Article[] = [];
    let loading = true;

    onMount(async () => {
        try { [stats, articles] = await Promise.all([getDashboardStats(), getArticles({ limit: 5 })]); } catch (e) {}
        loading = false;
    });
</script>

<h1>{t('dashboard_title')}</h1>

<div class="stats-row">
    <div class="card stat">
        <span class="stat-num">{stats?.total_articles ?? 0}</span>
        <span class="stat-label">{t('dashboard_total_articles')}</span>
    </div>
    <div class="card stat">
        <span class="stat-num">{stats?.total_collections ?? 0}</span>
        <span class="stat-label">{t('dashboard_total_collections')}</span>
    </div>
    <div class="card stat">
        <span class="stat-num">{stats?.total_sources ?? 0}</span>
        <span class="stat-label">{t('dashboard_total_sources')}</span>
    </div>
</div>

<h3 style="margin-top:24px;margin-bottom:12px">{t('dashboard_recent')}</h3>
{#if articles.length > 0}
    <div class="articles-list">
        {#each articles as a}
            <ArticleCard article={a} showFull={false} />
        {/each}
    </div>
{:else if !loading}
    <p class="subtext">{t('dashboard_empty')}</p>
{/if}

{#if stats?.type_counts?.length}
    <h3 style="margin-top:24px;margin-bottom:12px">{t('dashboard_by_type')}</h3>
    <div class="card type-list">
        {#each stats.type_counts as tc}
            <div class="type-item">
                <span class="badge">{t(tc.article_type)}</span>
                <span class="type-count">{tc.cnt}</span>
            </div>
        {/each}
    </div>
{/if}

<style>
    .stats-row {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 8px;
        margin-top: var(--padding);
    }

    .stat-num {
        font-size: 28px;
        font-weight: 500;
        letter-spacing: -1px;
        color: var(--secondary);
    }

    .stat-label {
        font-size: 12px;
        color: var(--gray);
        display: block;
        margin-top: 2px;
    }

    .articles-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .type-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .type-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .type-count {
        font-size: 14px;
        font-weight: 500;
        color: var(--secondary);
    }
</style>
