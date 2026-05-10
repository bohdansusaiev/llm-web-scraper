<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import {
        startResearch, getResearchJob, listResearchJobs,
        type ResearchJob, type JobStatus,
    } from '$lib/api';

    let topic = '';
    let maxPapers = 10;
    let minYear: number | '' = '';
    let openAccessOnly = true;
    let language: 'en' | 'ua' = 'en';
    let providers = { openalex: true, semantic_scholar: true, arxiv: true, core: true, crossref: false };

    let activeJob: ResearchJob | null = null;
    let recentJobs: ResearchJob[] = [];
    let error = '';
    let pollHandle: ReturnType<typeof setInterval> | null = null;

    onMount(loadRecent);
    onDestroy(() => { if (pollHandle) clearInterval(pollHandle); });

    async function loadRecent() {
        try { recentJobs = await listResearchJobs(20); }
        catch (e: any) { error = e.message; }
    }

    async function start() {
        error = '';
        const selectedProviders = Object.entries(providers)
            .filter(([, on]) => on).map(([k]) => k);
        if (!topic.trim() || selectedProviders.length === 0) {
            error = 'Topic and at least one provider required.';
            return;
        }
        try {
            const { job_id } = await startResearch({
                topic: topic.trim(),
                max_papers: maxPapers,
                min_year: minYear === '' ? null : Number(minYear),
                open_access_only: openAccessOnly,
                language,
                providers: selectedProviders,
            });
            await loadRecent();
            activeJob = recentJobs.find(j => j.id === job_id) || null;
            startPolling(job_id);
        } catch (e: any) {
            error = e.message;
        }
    }

    function startPolling(jobId: number) {
        if (pollHandle) clearInterval(pollHandle);
        pollHandle = setInterval(async () => {
            try {
                const job = await getResearchJob(jobId);
                activeJob = job;
                // Refresh the recent list so the row updates in place
                recentJobs = recentJobs.map(j => j.id === job.id ? job : j);
                if (job.status === 'completed' || job.status === 'failed') {
                    if (pollHandle) { clearInterval(pollHandle); pollHandle = null; }
                    await loadRecent();
                }
            } catch { /* keep polling */ }
        }, 1500);
    }

    function statusLabel(s: JobStatus): string {
        return t(`research_status_${s}`);
    }

    function pickJob(j: ResearchJob) {
        activeJob = j;
        if (j.status !== 'completed' && j.status !== 'failed') {
            startPolling(j.id);
        }
    }
</script>

<svelte:head><title>{t('research_title')} · LLM-Scraper</title></svelte:head>

<h1>{t('research_title')}</h1>
<p class="subtext">{t('research_desc')}</p>

<div class="form card">
    <label>
        <span class="label">{t('research_topic_label')}</span>
        <input bind:value={topic} placeholder={t('research_topic_placeholder')}
            onkeydown={(e) => e.key === 'Enter' && !e.shiftKey && start()} />
    </label>

    <div class="row">
        <label>
            <span class="label">{t('research_max_papers')}</span>
            <input type="number" min="1" max="50" bind:value={maxPapers} />
        </label>
        <label>
            <span class="label">{t('research_min_year')}</span>
            <input type="number" min="1900" max="2100" bind:value={minYear} placeholder="2015" />
        </label>
        <label>
            <span class="label">{t('research_language')}</span>
            <select bind:value={language}>
                <option value="en">{t('research_lang_en')}</option>
                <option value="ua">{t('research_lang_ua')}</option>
            </select>
        </label>
    </div>

    <div>
        <span class="label">{t('research_providers')}</span>
        <div class="checks">
            <label class="check"><input type="checkbox" bind:checked={providers.openalex} /> OpenAlex</label>
            <label class="check"><input type="checkbox" bind:checked={providers.semantic_scholar} /> Semantic Scholar</label>
            <label class="check"><input type="checkbox" bind:checked={providers.arxiv} /> arXiv</label>
            <label class="check"><input type="checkbox" bind:checked={providers.core} /> CORE</label>
            <label class="check"><input type="checkbox" bind:checked={providers.crossref} /> Crossref</label>
        </div>
    </div>
    <label class="check inline">
        <input type="checkbox" bind:checked={openAccessOnly} />
        {t('research_open_access_only')}
    </label>

    {#if error}<p class="err">{error}</p>{/if}

    <button onclick={start} class="active" disabled={!topic.trim()}>
        {t('research_start')}
    </button>
</div>

{#if activeJob}
    <div class="card progress-card">
        <div class="progress-head">
            <span class="badge">{statusLabel(activeJob.status)}</span>
            <span class="topic">{activeJob.topic}</span>
            <span class="pct">{activeJob.progress}%</span>
        </div>
        <div class="bar"><div class="bar-fill" style="width:{activeJob.progress}%"></div></div>
        <p class="msg">{activeJob.message}</p>
        {#if activeJob.error}<p class="err">{activeJob.error}</p>{/if}
        {#if activeJob.status === 'completed' && activeJob.catalog_id}
            <button onclick={() => goto(`/catalogs/${activeJob!.catalog_id}`)} class="active">
                {t('research_view_catalog')}
            </button>
        {/if}
    </div>
{/if}

<h3>{t('research_recent')}</h3>
{#if recentJobs.length === 0}
    <p class="subtext">—</p>
{:else}
    <div class="list">
        {#each recentJobs.filter(j => !(j.status === 'completed' && !j.catalog_id)) as j}
            <button class="job-row" onclick={() => pickJob(j)}>
                <span class="badge {j.status}">{statusLabel(j.status)}</span>
                <span class="topic">{j.topic}</span>
                <span class="when">{new Date(j.created_at).toLocaleString()}</span>
                {#if j.status === 'completed' && j.catalog_id}
                    <a href="/catalogs/{j.catalog_id}" onclick={(e) => e.stopPropagation()} class="open-link">{t('open')}</a>
                {/if}
            </button>
        {/each}
    </div>
{/if}

<style>
    h1 { margin-bottom: 4px; }
    h3 { margin-top: 24px; margin-bottom: 8px; }
    .subtext { margin-bottom: var(--padding); }
    .form { display: flex; flex-direction: column; gap: 12px; padding: 16px; margin: 12px 0 20px; }
    .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
    .row label { flex: 1; min-width: 140px; }
    .label { display: block; font-size: 11px; color: var(--gray); margin-bottom: 4px; }
    .checks { display: flex; flex-wrap: wrap; gap: 6px 14px; margin-top: 4px; }
    .check { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; cursor: pointer; }
    .check input { width: auto; }
    .check.inline { margin-top: 2px; }
    input, select { width: 100%; }
    .err { color: var(--red); font-size: 12px; }
    .progress-card { padding: 16px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 8px; }
    .progress-head { display: flex; align-items: center; gap: 12px; }
    .topic { font-weight: 500; flex: 1; }
    .pct { font-variant-numeric: tabular-nums; color: var(--gray); font-size: 12px; }
    .bar { height: 4px; background: var(--card-stroke); border-radius: 2px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--blue); transition: width .3s ease; }
    .msg { font-size: 12px; color: var(--gray); margin: 0; }
    .list { display: flex; flex-direction: column; gap: 4px; }
    .job-row {
        display: flex; align-items: center; gap: 10px;
        padding: 8px 10px; background: transparent;
        border: 1px solid var(--card-stroke);
        border-radius: var(--border-radius);
        text-align: left; cursor: pointer; color: inherit;
        font-size: 12.5px;
    }
    .job-row:hover { background: var(--button-hover); }
    .job-row .topic { flex: 1; }
    .when { color: var(--gray); font-size: 11px; }
    .open-link { color: var(--blue); font-size: 12px; text-decoration: none; }
    .badge { font-size: 10px; padding: 2px 8px; border-radius: 999px; background: var(--secondary); color: var(--primary); white-space: nowrap; }
    .badge.completed { background: var(--green, #2ecc71); color: white; }
    .badge.failed { background: var(--red); color: white; }
    .badge.deleted { background: var(--gray); color: var(--primary); }
</style>
