<script lang="ts">
    import { t } from '$lib/i18n';
</script>

<h1>{t('about_title')}</h1>

<section style="margin-bottom:32px">
    <p class="subtext">{t('about_value_prop')}</p>
</section>

<h3>{t('about_adaptivity_title')}</h3>
<div class="text-content adaptivity">{t('about_adaptivity_text')}</div>

<h3 style="margin-top:32px">{t('about_how_title')}</h3>
<div class="steps">
    <div class="step"><span class="step-num">1</span><span>{t('about_how_1_desc')}</span></div>
    <div class="step"><span class="step-num">2</span><span>{t('about_how_2_desc')}</span></div>
    <div class="step"><span class="step-num">3</span><span>{t('about_how_3_desc')}</span></div>
</div>

<h3 style="margin-top:32px">{t('about_compare_title')}</h3>
<div class="card" style="margin-bottom:var(--padding);padding:var(--padding);border-left:3px solid var(--red)">
    <p class="subtext">{t('about_compare_old')}</p>
</div>
<div class="card" style="padding:var(--padding);border-left:3px solid var(--green)">
    <p class="subtext">{t('about_compare_new')}</p>
</div>

<h3 style="margin-top:32px">{t('about_features_title')}</h3>
<div class="features">
    {#each [1,2,3,4,5,6,7,8] as i}
        <span>{i}. {t(`about_feature_${i}`)}</span>
    {/each}
</div>

<h3 style="margin-top:32px">{t('about_tech_title')}</h3>
<div class="tech-grid">
    {#each ['python', 'crawl4ai', 'deepseek', 'svelte', 'sqlite'] as tech}
        <div class="card">
            <h4>{tech === 'python' ? 'Python + FastAPI' : tech === 'crawl4ai' ? 'Crawl4AI' : tech === 'deepseek' ? 'DeepSeek V4' : tech === 'svelte' ? 'SvelteKit' : 'SQLite'}</h4>
            <p class="subtext">{t(`about_tech_detail_${tech}`)}</p>
        </div>
    {/each}
</div>

<h3 style="margin-top:32px">{t('about_author_title')}</h3>
<div class="card">
    <p class="subtext">{t('about_author_name')}</p>
    <p class="subtext">{t('about_author_group')} &middot; {t('about_author_institute')}</p>
    <p class="subtext">{t('about_author_specialty')}</p>
    <p class="subtext" style="margin-top:var(--padding);color:var(--gray)">{t('about_purpose')}</p>
    <p class="subtext" style="margin-top:4px;color:var(--gray)">{t('about_relevance')}</p>
</div>

<style>
    .adaptivity {
        font-size: 13px;
        line-height: 1.7;
        white-space: pre-line;
        margin-top: var(--padding);
    }

    .steps {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-top: var(--padding);
    }

    .step {
        display: flex;
        gap: 12px;
        font-size: 13px;
        color: var(--gray);
        align-items: baseline;
    }

    .step-num {
        color: var(--secondary);
        font-weight: 500;
        min-width: 16px;
    }

    .features {
        display: flex;
        flex-direction: column;
        gap: 6px;
        font-size: 13px;
        color: var(--gray);
        margin-top: var(--padding);
    }

    .tech-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: var(--padding);
    }

    .tech-grid .card h4 {
        margin-bottom: 4px;
    }
</style>
