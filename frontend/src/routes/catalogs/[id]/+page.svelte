<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { t } from '$lib/i18n';
    import { getCatalog, type ScientificCatalog } from '$lib/api';
    import { auth } from '$lib/stores/auth';

    let cat: ScientificCatalog | null = null;
    let error = '';
    let expanded = new Set<number>();

    onMount(async () => {
        const id = Number($page.params.id);
        try { cat = await getCatalog(id); }
        catch (e: any) { error = e.message; }
    });

    async function download(format: 'json' | 'csv' | 'bibtex') {
        if (!cat) return;
        const res = await fetch(`/api/export/${cat.id}?format=${format}`, {
            headers: auth.getHeaders(),
        });
        if (!res.ok) return;
        const blob = await res.blob();
        const objectUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = `catalog_${cat.id}.${format === 'bibtex' ? 'bib' : format}`;
        a.click();
        URL.revokeObjectURL(objectUrl);
    }

    function failureBadge(reason: string): string | null {
        if (reason === 'none' || !reason) return null;
        return reason.replaceAll('_', ' ');
    }

    function toggle(i: number) {
        if (expanded.has(i)) expanded.delete(i); else expanded.add(i);
        expanded = new Set(expanded);  // trigger reactivity
    }

    function previewText(s: string, n = 240): string {
        if (!s) return '';
        if (s.length <= n) return s;
        return s.slice(0, n).replace(/\s+\S*$/, '') + '…';
    }
</script>

<svelte:head><title>{cat?.topic || t('catalogs_title')} · LLM-Scraper</title></svelte:head>

<a href="/catalogs" class="back">← {t('back')}</a>

{#if error}
    <p class="err">{error}</p>
{:else if !cat}
    <p class="subtext">…</p>
{:else}
    <h1>{cat.topic}</h1>
    <div class="header-meta">
        <span>{new Date(cat.created_at).toLocaleString()}</span>
        <span>·</span>
        <span>{cat.papers.length} {t('catalog_papers')}</span>
        <span>·</span>
        <span>{cat.language.toUpperCase()}</span>
    </div>

    <div class="exports">
        <button class="btn" onclick={() => download('json')}>{t('catalog_export_json')}</button>
        <button class="btn" onclick={() => download('csv')}>{t('catalog_export_csv')}</button>
        <button class="btn" onclick={() => download('bibtex')}>{t('catalog_export_bibtex')}</button>
    </div>

    <div class="card stats">
        <h3>{t('catalog_stats_title')}</h3>
        <div class="stats-grid">
            <div><span>{t('catalog_stats_discovered')}</span><b>{cat.stats.discovered}</b></div>
            <div><span>{t('catalog_stats_filtered')}</span><b>{cat.stats.relevance_filtered}</b></div>
            <div><span>{t('catalog_stats_extracted')}</span><b>{cat.stats.deeply_extracted}</b></div>
            <div><span>{t('catalog_stats_failed')}</span><b>{cat.stats.failed}</b></div>
            <div><span>{t('catalog_stats_duration')}</span><b>{cat.stats.duration_seconds}</b></div>
        </div>
        {#if Object.keys(cat.stats.failure_breakdown).length > 0}
            <div class="failure-breakdown">
                {#each Object.entries(cat.stats.failure_breakdown) as [reason, count]}
                    <span class="badge fail">{reason.replaceAll('_', ' ')}: {count}</span>
                {/each}
            </div>
        {/if}
    </div>

    <div class="papers">
        {#each cat.papers as p, i}
            {@const isOpen = expanded.has(i)}
            <article class="paper-card" class:open={isOpen}>
                <button class="paper-summary" onclick={() => toggle(i)} aria-expanded={isOpen}>
                    <div class="paper-head">
                        {#if p.image_url}
                            <img class="paper-thumb" src={p.image_url} alt=""
                                onerror={(e) => ((e.target as HTMLImageElement).style.display = 'none')} />
                        {/if}
                        <div class="paper-head-text">
                            <h3 class="paper-title">{p.title || '(no title)'}</h3>
                        </div>
                        <span class="rel">★ {(p.relevance_score * 10).toFixed(1)}/10</span>
                    </div>
                    <div class="paper-meta">
                        {#if p.authors.length > 0}
                            <span>{p.authors.slice(0, 4).map(a => a.name).join(', ')}{p.authors.length > 4 ? `, +${p.authors.length - 4}` : ''}</span>
                        {/if}
                        {#if p.publication_year}<span>· {p.publication_year}</span>{/if}
                        {#if p.venue}<span class="venue">· {p.venue}</span>{/if}
                        {#if p.citation_count !== null && p.citation_count !== undefined}
                            <span>· {p.citation_count} {t('catalog_paper_citations').toLowerCase()}</span>
                        {/if}
                        {#if p.is_open_access}<span class="badge green">OA</span>{/if}
                        {#if failureBadge(p.failure_reason)}
                            <span class="badge fail">{failureBadge(p.failure_reason)}</span>
                        {/if}
                    </div>
                    {#if !isOpen && p.abstract}
                        <p class="preview prose">{previewText(p.abstract)}</p>
                    {/if}
                    <div class="caret" aria-hidden="true">{isOpen ? '▾' : '▸'}</div>
                </button>

                {#if isOpen}
                    <div class="paper-body">
                        {#if p.abstract}
                            <section class="section">
                                <span class="section-label">{t('catalog_paper_abstract')}</span>
                                <p class="prose">{p.abstract}</p>
                            </section>
                        {/if}
                        {#if p.methodology}
                            <section class="section">
                                <span class="section-label">{t('catalog_paper_methodology')}</span>
                                <p class="prose">{p.methodology}</p>
                            </section>
                        {/if}
                        {#if p.conclusions}
                            <section class="section">
                                <span class="section-label">{t('catalog_paper_conclusions')}</span>
                                <p class="prose">{p.conclusions}</p>
                            </section>
                        {/if}
                        {#if p.keywords.length > 0}
                            <div class="kw">
                                {#each p.keywords as k}<span class="badge kw-badge">{k}</span>{/each}
                            </div>
                        {/if}
                        <div class="paper-actions">
                            {#if p.url}
                                <a class="btn primary" href={p.url} target="_blank" rel="noopener">
                                    Open source ↗
                                </a>
                            {/if}
                            {#if p.doi}
                                <a class="btn" href={`https://doi.org/${p.doi}`} target="_blank" rel="noopener">
                                    DOI: {p.doi}
                                </a>
                            {/if}
                        </div>
                    </div>
                {/if}
            </article>
        {/each}
    </div>
{/if}

<style>
    .back { font-size: 12px; color: var(--gray); text-decoration: none; }
    .header-meta { display: flex; gap: 6px; font-size: 12px; color: var(--gray); margin-bottom: 14px; user-select: text; }
    .exports { display: flex; gap: 6px; margin-bottom: 16px; }
    .btn {
        display: inline-flex; align-items: center; gap: 4px;
        padding: 5px 12px; font-size: 12.5px;
        border: 1px solid var(--card-stroke); border-radius: var(--border-radius);
        text-decoration: none; color: var(--secondary);
        background: transparent;
    }
    .btn:hover { background: var(--button-hover); }
    .btn.primary { background: var(--secondary); color: var(--primary); border-color: var(--secondary); }
    .btn.primary:hover { opacity: 0.85; }

    .stats { padding: 14px 16px; margin-bottom: 16px; }
    .stats h3 { margin: 0 0 8px; }
    .stats-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 10px; font-size: 12.5px;
    }
    .stats-grid div { display: flex; flex-direction: column; gap: 2px; user-select: text; }
    .stats-grid span { color: var(--gray); font-size: 11px; }
    .stats-grid b { font-size: 16px; font-weight: 500; }
    .failure-breakdown { margin-top: 10px; display: flex; gap: 4px; flex-wrap: wrap; }

    .papers { display: flex; flex-direction: column; gap: 8px; }
    .paper-card {
        background: var(--card-bg);
        border: 1px solid var(--card-stroke);
        border-radius: var(--border-radius);
        overflow: hidden;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    .paper-card:hover { border-color: rgba(0, 0, 0, 0.12); }
    .paper-card.open { border-color: rgba(0, 0, 0, 0.12); }

    .paper-summary {
        display: block;
        width: 100%;
        text-align: left;
        background: transparent;
        border: 0;
        padding: 14px 16px;
        cursor: pointer;
        position: relative;
        color: inherit;
        font-family: inherit;
    }
    .paper-summary:hover { background: var(--button-hover); }
    .paper-card.open .paper-summary { background: transparent; }

    .paper-head { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 4px; padding-right: 24px; }
    .paper-head-text { flex: 1; }
    .paper-thumb {
        width: 64px; height: 64px; flex-shrink: 0;
        object-fit: cover; border-radius: 6px;
        background: var(--card-stroke);
    }
    .paper-title {
        font-size: 15px; font-weight: 500; margin: 0;
        line-height: 1.35; user-select: text;
    }
    .rel {
        font-size: 11px; color: var(--gray); white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }
    .paper-meta {
        font-size: 12px; color: var(--gray);
        display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px;
        align-items: center;
        user-select: text;
    }
    .paper-meta .venue { font-style: italic; }

    .preview {
        font-size: 13px; line-height: 1.55;
        margin: 4px 0 0; color: var(--gray);
        user-select: text;
    }

    .caret {
        position: absolute; right: 14px; top: 14px;
        color: var(--gray); font-size: 11px;
    }

    .paper-body {
        padding: 4px 16px 14px;
        border-top: 1px solid var(--card-stroke);
        margin-top: 0;
    }

    .section { margin-top: 12px; }
    .section-label {
        display: block; font-size: 10.5px; color: var(--gray);
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px;
        font-weight: 500;
    }

    .kw { display: flex; gap: 4px; flex-wrap: wrap; margin-top: 12px; }

    .badge {
        font-size: 10.5px; padding: 1px 8px;
        border-radius: 999px; background: var(--secondary); color: var(--primary);
    }
    .badge.green { background: var(--green); color: white; }
    .badge.fail { background: var(--red); color: white; }
    .kw-badge { background: var(--card-stroke); color: var(--gray); }

    .paper-actions {
        display: flex; gap: 6px; flex-wrap: wrap; margin-top: 16px;
    }

    .err { color: var(--red); font-size: 13px; }
</style>
