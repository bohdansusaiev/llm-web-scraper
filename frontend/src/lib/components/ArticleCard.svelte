<script lang="ts">
    import { language } from '$lib/stores/language';
    import { t } from '$lib/i18n';
    import type { Article } from '$lib/api';

    export let article: Article;
    export let onDelete: (() => void) | null = null;
    export let showFull: boolean = false;

    let expanded = showFull;
    let lang: 'en' | 'ua';
    language.subscribe(v => lang = v);
</script>

<div class="card">
    {#if article.image}
        <img
            src={article.image}
            alt=""
            class="thumb"
            onerror={(e) => (e.target as HTMLImageElement).style.display = 'none'}
            loading="lazy"
        />
    {/if}

    <div class="card-body">
        <div class="card-header">
            <h4>{article.title || t('no_title')}</h4>
            <div class="card-meta">
                {#if article.article_type}
                    <span class="badge">{t(article.article_type)}</span>
                {/if}
                {#if article.translated}
                    <span class="badge badge-accent">{t('translated')}</span>
                {/if}
            </div>
        </div>

        <div class="meta-line">
            {#if article.author}<span>{article.author}</span>{/if}
            {#if article.date}<span>{article.date}</span>{/if}
            {#if article.source_name}<span>{article.source_name}</span>{/if}
        </div>

        {#if expanded}
            <div class="expanded-content">
                {#if article.summary}
                    <p class="text-content">{article.summary}</p>
                {/if}
                {#if article.key_points}
                    <p class="subtext">{article.key_points.split('\n').filter(Boolean).map(p => p.replace(/^[-*\s]+/, '')).join('\n')}</p>
                {/if}
            </div>
        {/if}

        <div class="card-actions">
            <button onclick={() => expanded = !expanded}>
                {expanded ? (lang === 'ua' ? 'згорнути' : 'collapse') : t('show_details')}
            </button>
            {#if onDelete}
                <button onclick={onDelete} class="danger">
                    {t('delete')}
                </button>
            {/if}
        </div>
    </div>
</div>

<style>
    .thumb {
        width: 100%;
        border-radius: var(--border-radius);
        margin-bottom: var(--padding);
    }

    .card-body {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--padding);
    }

    .card-meta {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
    }

    .meta-line {
        font-size: 12px;
        color: var(--gray);
        display: flex;
        gap: 12px;
    }

    .expanded-content {
        margin-top: var(--padding);
        padding-top: var(--padding);
        border-top: 1px solid var(--card-stroke);
    }

    .card-actions {
        display: flex;
        gap: 6px;
        margin-top: 4px;
    }

    button {
        font-size: 12.5px;
        padding: 4px 10px;
    }

    button.danger {
        color: var(--red);
    }

    button.danger:hover {
        background: var(--red);
        color: var(--primary);
    }
</style>
