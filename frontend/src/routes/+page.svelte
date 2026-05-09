<script lang="ts">
    import { t } from '$lib/i18n';
</script>

<svelte:head><title>LLM-Scraper</title></svelte:head>

<div class="hero">
    <div class="inner">
        <img src="/logo.svg" alt="LLM-Scraper" class="logo" />
        <h1>{t('app_subtitle')}</h1>
        <p class="desc">{t('app_desc')}</p>

        <div class="actions">
            <a href="/login" class="btn-primary">{t('login_btn')}</a>
            <a href="/register" class="btn-ghost">{t('register_btn')}</a>
        </div>
    </div>
</div>

<style>
    .hero {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: calc(100vh - 48px);
        padding: 0 var(--padding);
    }

    .inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        max-width: 560px;
        gap: 0;
    }

    .logo {
        width: 90px;
        height: auto;
        margin-bottom: 24px;
    }

    h1 {
        font-size: 26px;
        font-weight: 600;
        line-height: 1.35;
        letter-spacing: -0.5px;
        margin: 0 0 16px;
        color: var(--secondary);
    }

    .desc {
        font-size: 13px;
        line-height: 1.7;
        color: var(--gray);
        margin: 0 0 36px;
        max-width: 420px;
    }

    .actions {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .btn-primary {
        padding: 8px 24px;
        background: var(--secondary);
        color: var(--primary);
        border-radius: var(--border-radius);
        font-size: 13px;
        font-weight: 500;
        text-decoration: none;
        transition: opacity .15s;
    }
    .btn-primary:hover { opacity: 0.85; }

    .btn-ghost {
        padding: 8px 24px;
        background: transparent;
        color: var(--gray);
        border: 1px solid var(--card-stroke);
        border-radius: var(--border-radius);
        font-size: 13px;
        font-weight: 500;
        text-decoration: none;
        transition: background .15s;
    }
    .btn-ghost:hover { background: var(--button-hover); }
</style>
