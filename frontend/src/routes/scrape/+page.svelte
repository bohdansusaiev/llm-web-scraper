<script lang="ts">
    import { t } from '$lib/i18n';
    import { genericScrape, type GenericExtractResponse } from '$lib/api';

    let url = '';
    let instruction = '';
    let schemaText = '';
    let result: GenericExtractResponse | null = null;
    let loading = false;
    let error = '';
    let view: 'formatted' | 'json' = 'formatted';

    async function run() {
        error = ''; result = null;
        if (!url.trim()) { error = 'URL required'; return; }
        let parsedSchema: Record<string, unknown> | null = null;
        if (schemaText.trim()) {
            try { parsedSchema = JSON.parse(schemaText); }
            catch (e: any) { error = `Schema JSON invalid: ${e.message}`; return; }
        }
        loading = true;
        try {
            result = await genericScrape({
                url: url.trim(),
                instruction: instruction.trim() || null,
                output_schema: parsedSchema,
            });
        } catch (e: any) {
            error = e.message;
        }
        loading = false;
    }

    // Fields rendered in the top meta line (short values only)
    const META_KEYS = new Set([
        'author', 'authors', 'date', 'date_published', 'published', 'published_at',
        'publication_date', 'year', 'read_time', 'reading_time', 'venue', 'source',
        'publication', 'publisher',
    ]);
    // Fields skipped entirely (already shown as title/tags)
    const SKIP_KEYS = new Set(['title', 'tags', 'keywords']);

    function str(v: unknown): string {
        if (!v) return '';
        if (typeof v === 'string') return v;
        if (Array.isArray(v)) return v.map(String).join(', ');
        return String(v);
    }

    function cleanMarkdown(s: string): string {
        return s
            .replace(/^#{1,6}\s+/gm, '')        // ## headers
            .replace(/\*\*(.*?)\*\*/g, '$1')     // **bold**
            .replace(/\*(.*?)\*/g, '$1')          // *italic*
            .replace(/`([^`]+)`/g, '$1')          // `code`
            .replace(/^\s*[-*]\s+/gm, '• ')      // bullet points
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // [links](url)
            .trim();
    }

    function isMeta(key: string, val: unknown): boolean {
        if (META_KEYS.has(key)) return true;
        // Also treat any short string that looks like a date or time as meta
        const s = str(val);
        return s.length < 60 && (
            /\d{4}/.test(s) || /min read/.test(s) || /^\d+\s/.test(s)
        );
    }

    function copyJson() {
        if (!result) return;
        navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
    }
</script>

<svelte:head><title>{t('scrape_title')} · LLM-Scraper</title></svelte:head>

<h1>{t('scrape_title')}</h1>
<p class="subtext">{t('scrape_desc')}</p>

<div class="form card">
    <label>
        <span class="label">{t('scrape_url_label')}</span>
        <input bind:value={url} placeholder={t('scrape_url_placeholder')} />
    </label>
    <label>
        <span class="label">{t('scrape_instruction_label')}</span>
        <textarea bind:value={instruction} rows="3"
            placeholder={t('scrape_instruction_placeholder')}></textarea>
    </label>
    <label>
        <span class="label">{t('scrape_schema_label')}</span>
        <textarea bind:value={schemaText} rows="4" class="mono"
            placeholder={t('scrape_schema_placeholder')}></textarea>
    </label>
    {#if error}<p class="err">{error}</p>{/if}
    <button onclick={run} class="active" disabled={loading || !url.trim()}>
        {loading ? t('scrape_running') : t('scrape_run')}
    </button>
</div>

{#if result}
    <div class="result-header">
        <h3>{t('scrape_result')}</h3>
        <div class="view-tabs">
            <button class:active={view === 'formatted'} onclick={() => view = 'formatted'}>Formatted</button>
            <button class:active={view === 'json'} onclick={() => view = 'json'}>JSON</button>
        </div>
    </div>

    <div class="card result">
        <div class="meta">
            {#if !result.success}<span class="badge fail">error</span>{/if}
            {#if result.cached}<span class="badge">{t('scrape_cached')}</span>{/if}
            <span>{t('scrape_duration')}: {result.duration_ms}ms</span>
        </div>
        {#if result.error}<p class="err">{result.error}</p>{/if}

        {#if result.success}
            {#if view === 'formatted'}
                {@const d = result.data}
                {@const metaEntries = Object.entries(d).filter(([k, v]) => !SKIP_KEYS.has(k) && v && isMeta(k, v))}
                {@const tagVal = d.tags || d.keywords}
                <div class="formatted">
                    {#if str(d.title)}
                        <h2 class="f-title">{str(d.title)}</h2>
                    {/if}

                    {#if metaEntries.length > 0}
                        <div class="f-meta">
                            {#each metaEntries as [key, val], i}
                                {#if i > 0}<span class="sep">·</span>{/if}
                                <span>{str(val)}</span>
                            {/each}
                        </div>
                    {/if}

                    {#if tagVal}
                        <div class="f-tags">
                            {#each (Array.isArray(tagVal) ? tagVal as string[] : [str(tagVal)]) as tag}
                                <span class="badge">{tag}</span>
                            {/each}
                        </div>
                    {/if}

                    {#each Object.entries(d) as [key, val]}
                        {#if !SKIP_KEYS.has(key) && !isMeta(key, val) && val}
                            <section class="f-section">
                                <span class="f-label">{key.replace(/_/g, ' ')}</span>
                                <p class="f-text">{cleanMarkdown(str(val))}</p>
                            </section>
                        {/if}
                    {/each}
                </div>
            {:else if view === 'json'}
                <div class="json-header">
                    <button class="copy-btn" onclick={copyJson}>Copy</button>
                </div>
                <pre class="json">{JSON.stringify(result.data, null, 2)}</pre>
            {/if}
        {/if}
    </div>
{/if}

<style>
    h3 { margin-top: 24px; margin-bottom: 8px; }
    .form { display: flex; flex-direction: column; gap: 12px; padding: 16px; margin: 12px 0 20px; }
    .label { display: block; font-size: 11px; color: var(--gray); margin-bottom: 4px; }
    input, textarea { width: 100%; }
    textarea { font-family: inherit; resize: vertical; }
    textarea.mono { font-family: ui-monospace, Menlo, monospace; font-size: 12px; }
    .err { color: var(--red); font-size: 12px; }

    .result-header { display: flex; align-items: center; justify-content: space-between; margin-top: 24px; margin-bottom: 8px; }
    .result-header h3 { margin: 0; }
    .view-tabs { display: flex; gap: 2px; }
    .view-tabs button {
        padding: 4px 12px; font-size: 12px; border: 1px solid var(--card-stroke);
        background: transparent; cursor: pointer; color: var(--gray);
        border-radius: var(--border-radius);
    }
    .view-tabs button.active { background: var(--secondary); color: var(--primary); border-color: var(--secondary); }

    .result { padding: 14px 16px; }
    .meta { display: flex; gap: 8px; align-items: center; font-size: 11px; color: var(--gray); margin-bottom: 12px; }
    .badge { font-size: 10px; padding: 1px 8px; border-radius: 999px; background: var(--secondary); color: var(--primary); }
    .badge.fail { background: var(--red); color: white; }

    /* Formatted view */
    .formatted { display: flex; flex-direction: column; gap: 10px; }
    .f-title { font-size: 18px; font-weight: 600; margin: 0; line-height: 1.3; }
    .f-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 12px; color: var(--gray); }
    .sep { color: var(--card-stroke); }
    .f-tags { display: flex; flex-wrap: wrap; gap: 4px; }
    .f-section { margin-top: 4px; }
    .f-label {
        display: block; font-size: 10.5px; color: var(--gray);
        text-transform: uppercase; letter-spacing: 0.6px; font-weight: 500; margin-bottom: 3px;
    }
    .f-text { font-size: 13.5px; line-height: 1.6; margin: 0; white-space: pre-wrap; }

    /* JSON / Markdown views */
    .json-header { display: flex; justify-content: flex-end; margin-bottom: 6px; }
    .copy-btn {
        font-size: 11px; padding: 3px 10px;
        border: 1px solid var(--card-stroke); border-radius: var(--border-radius);
        background: transparent; cursor: pointer; color: var(--gray);
    }
    .copy-btn:hover { background: var(--button-hover); }
    .json {
        font-family: ui-monospace, Menlo, monospace;
        font-size: 11.5px; line-height: 1.5;
        background: var(--button-hover);
        padding: 10px; border-radius: var(--border-radius);
        overflow: auto; max-height: 500px;
        white-space: pre-wrap; word-break: break-word;
        margin: 0;
    }
</style>
