<script lang="ts">
    import { t } from '$lib/i18n';
    import {
        runBenchmark, runBenchmarkBatch,
        type BenchmarkResult, type BenchmarkBatchSummary,
    } from '$lib/api';

    let mode: 'single' | 'batch' = 'single';
    let url = '';
    let urlsText = '';
    let instruction = '';

    let single: BenchmarkResult | null = null;
    let batch: BenchmarkBatchSummary | null = null;
    let loading = false;
    let error = '';

    async function run() {
        error = ''; single = null; batch = null; loading = true;
        try {
            if (mode === 'single') {
                if (!url.trim()) throw new Error('URL required');
                single = await runBenchmark({ url: url.trim(), instruction: instruction.trim() || null });
            } else {
                const urls = urlsText.split('\n').map(s => s.trim()).filter(Boolean);
                if (urls.length === 0) throw new Error('At least one URL required');
                batch = await runBenchmarkBatch(urls, instruction.trim() || undefined);
            }
        } catch (e: any) { error = e.message; }
        loading = false;
    }

    function fmt(v: unknown): string {
        if (v === null || v === undefined || v === '') return '—';
        if (Array.isArray(v)) return v.length === 0 ? '—' : v.join(', ');
        if (typeof v === 'object') return JSON.stringify(v);
        return String(v);
    }
</script>

<svelte:head><title>{t('benchmark_title')} · LLM-Scraper</title></svelte:head>

<h1>{t('benchmark_title')}</h1>
<p class="subtext">{t('benchmark_desc')}</p>

<div class="mode">
    <button class:active={mode === 'single'} onclick={() => mode = 'single'}>{t('benchmark_title')}</button>
    <button class:active={mode === 'batch'} onclick={() => mode = 'batch'}>{t('benchmark_batch_title')}</button>
</div>

<div class="form card">
    {#if mode === 'single'}
        <label>
            <span class="label">{t('benchmark_url_label')}</span>
            <input bind:value={url} placeholder="https://..." />
        </label>
    {:else}
        <label>
            <span class="label">{t('benchmark_batch_urls')}</span>
            <textarea bind:value={urlsText} rows="6" class="mono" placeholder="https://...&#10;https://..."></textarea>
        </label>
    {/if}
    <label>
        <span class="label">{t('scrape_instruction_label')}</span>
        <textarea bind:value={instruction} rows="2" placeholder={t('scrape_instruction_placeholder')}></textarea>
    </label>
    {#if error}<p class="err">{error}</p>{/if}
    <button onclick={run} class="active" disabled={loading}>
        {loading ? t('benchmark_running') : (mode === 'single' ? t('benchmark_run') : t('benchmark_batch_run'))}
    </button>
</div>

{#if single}
    <div class="card summary">
        <div class="cols">
            <div class="col">
                <h4>{t('benchmark_method_llm')}</h4>
                <div class="metric"><span>{t('benchmark_fields_populated')}</span><b>{single.llm.fields_populated}</b></div>
                <div class="metric"><span>{t('benchmark_duration')}</span><b>{single.llm.duration_ms}</b></div>
                <div class="metric"><span>{t('benchmark_bytes')}</span><b>{single.llm.bytes_downloaded.toLocaleString()}</b></div>
                <div class="metric"><span>{t('benchmark_tokens')}</span><b>{single.llm.tokens_used ?? '—'}</b></div>
                <div class="metric"><span>{t('benchmark_cost')}</span><b>{single.llm.estimated_cost_usd.toFixed(5)}</b></div>
                {#if single.llm.error}<p class="err">{single.llm.error}</p>{/if}
            </div>
            <div class="col">
                <h4>{t('benchmark_method_classical')}</h4>
                <div class="metric"><span>{t('benchmark_fields_populated')}</span><b>{single.classical.fields_populated}</b></div>
                <div class="metric"><span>{t('benchmark_duration')}</span><b>{single.classical.duration_ms}</b></div>
                <div class="metric"><span>{t('benchmark_bytes')}</span><b>{single.classical.bytes_downloaded.toLocaleString()}</b></div>
                <div class="metric"><span>{t('benchmark_cost')}</span><b>0</b></div>
                {#if single.classical.error}<p class="err">{single.classical.error}</p>{/if}
            </div>
        </div>
        <div class="winners">
            <span><b>{t('benchmark_winner_completeness')}:</b> {single.winner_completeness}</span>
            <span><b>{t('benchmark_winner_speed')}:</b> {single.winner_speed}</span>
        </div>
    </div>

    <table class="cmp">
        <thead>
            <tr>
                <th>{t('benchmark_field')}</th>
                <th>{t('benchmark_llm_value')}</th>
                <th>{t('benchmark_classical_value')}</th>
            </tr>
        </thead>
        <tbody>
            {#each single.fields as f}
                <tr>
                    <td class="field">{f.field}</td>
                    <td>{fmt(f.llm_value)}</td>
                    <td>{fmt(f.classical_value)}</td>
                </tr>
            {/each}
        </tbody>
    </table>
{/if}

{#if batch}
    <h3>{t('benchmark_batch_summary')}</h3>
    <div class="card summary">
        <div class="cols">
            <div class="col">
                <h4>{t('benchmark_method_llm')}</h4>
                <div class="metric"><span>{t('benchmark_success_rate')}</span><b>{(batch.llm_success_rate * 100).toFixed(0)}%</b></div>
                <div class="metric"><span>{t('benchmark_avg_fields')}</span><b>{batch.llm_avg_fields}</b></div>
                <div class="metric"><span>{t('benchmark_avg_duration')}</span><b>{batch.llm_avg_duration_ms}</b></div>
                <div class="metric"><span>{t('benchmark_total_cost')}</span><b>{batch.llm_total_cost_usd.toFixed(4)}</b></div>
            </div>
            <div class="col">
                <h4>{t('benchmark_method_classical')}</h4>
                <div class="metric"><span>{t('benchmark_success_rate')}</span><b>{(batch.classical_success_rate * 100).toFixed(0)}%</b></div>
                <div class="metric"><span>{t('benchmark_avg_fields')}</span><b>{batch.classical_avg_fields}</b></div>
                <div class="metric"><span>{t('benchmark_avg_duration')}</span><b>{batch.classical_avg_duration_ms}</b></div>
                <div class="metric"><span>{t('benchmark_total_cost')}</span><b>0</b></div>
            </div>
        </div>
    </div>

    <h3>Per-URL</h3>
    <table class="cmp">
        <thead>
            <tr>
                <th>URL</th>
                <th>LLM fields</th>
                <th>Classical fields</th>
                <th>LLM ms</th>
                <th>Classical ms</th>
                <th>Tokens</th>
            </tr>
        </thead>
        <tbody>
            {#each batch.results as r}
                <tr>
                    <td class="url">{r.url}</td>
                    <td>{r.llm.fields_populated}{r.llm.error ? ' ✗' : ''}</td>
                    <td>{r.classical.fields_populated}{r.classical.error ? ' ✗' : ''}</td>
                    <td>{r.llm.duration_ms}</td>
                    <td>{r.classical.duration_ms}</td>
                    <td>{r.llm.tokens_used ?? '—'}</td>
                </tr>
            {/each}
        </tbody>
    </table>
{/if}

<style>
    h3 { margin-top: 24px; margin-bottom: 8px; }
    .mode { display: flex; gap: 4px; margin: 12px 0; }
    .mode button {
        background: transparent; border: 1px solid var(--card-stroke);
        padding: 4px 12px; border-radius: var(--border-radius);
        font-size: 12px; cursor: pointer; color: inherit;
    }
    .mode button.active { background: var(--secondary); color: var(--primary); border-color: var(--secondary); }
    .form { display: flex; flex-direction: column; gap: 12px; padding: 16px; margin-bottom: 20px; }
    .label { display: block; font-size: 11px; color: var(--gray); margin-bottom: 4px; }
    input, textarea { width: 100%; }
    textarea { font-family: inherit; resize: vertical; }
    textarea.mono { font-family: ui-monospace, Menlo, monospace; font-size: 12px; }
    .err { color: var(--red); font-size: 12px; }
    .summary { padding: 14px 16px; margin-bottom: 16px; }
    .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .col h4 { margin: 0 0 8px; font-size: 12px; }
    .metric { display: flex; justify-content: space-between; font-size: 12px; padding: 2px 0; }
    .metric span { color: var(--gray); }
    .metric b { font-variant-numeric: tabular-nums; font-weight: 500; }
    .winners { margin-top: 10px; font-size: 12px; display: flex; gap: 14px; color: var(--gray); }
    .cmp { width: 100%; border-collapse: collapse; font-size: 12px; }
    .cmp th, .cmp td {
        padding: 6px 8px; border-bottom: 1px solid var(--card-stroke);
        text-align: left; vertical-align: top;
    }
    .cmp th { font-size: 10.5px; color: var(--gray); text-transform: uppercase; letter-spacing: 0.5px; }
    .cmp td.field { font-weight: 500; white-space: nowrap; width: 130px; }
    .cmp td.url { font-family: ui-monospace, Menlo, monospace; font-size: 11px; word-break: break-all; max-width: 260px; }
</style>
