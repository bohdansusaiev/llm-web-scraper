<script lang="ts">
    import { theme, type Theme } from '$lib/stores/theme';
    import { language, type Lang } from '$lib/stores/language';
    import { auth } from '$lib/stores/auth';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { t } from '$lib/i18n';
    import { browser } from '$app/environment';
    import { onMount } from 'svelte';

    export let placement: 'right' | 'below' | 'above' = 'right';

    let open = false;
    let lang: Lang;
    let themeVal: Theme;
    let isLoggedIn = false;

    language.subscribe(v => lang = v);
    theme.subscribe(v => themeVal = v);
    auth.subscribe(v => isLoggedIn = !!v);

    let currentPath = '';
    page.subscribe(p => currentPath = p.url.pathname);

    function setTheme(tm: Theme) { theme.set(tm); }

    function setLanguage(l: Lang) {
        language.set(l);
        if (browser) window.location.reload();
    }

    function getThemeLabel(tm: Theme): string {
        if (tm === 'light') return lang === 'ua' ? 'Світла' : 'Light';
        if (tm === 'dark') return lang === 'ua' ? 'Темна' : 'Dark';
        return 'Auto';
    }

    onMount(() => {
        document.addEventListener('click', (e) => {
            if (!(e.target as HTMLElement).closest('.top-menu-container')) {
                open = false;
            }
        });
    });
</script>

<div class="top-menu-container">
    <button
        onclick={() => open = !open}
        class="sidebar-tab settings-btn"
        aria-label="Settings"
    >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
        </svg>
        <span class="tab-label">{lang === 'ua' ? 'Вигляд' : 'settings'}</span>
    </button>

    {#if open}
        <div class="popover" class:popover-below={placement === 'below'} class:popover-above={placement === 'above'}>
            <p class="popover-label">{lang === 'ua' ? 'Тема' : 'theme'}</p>
            <div class="popover-row">
                {#each ['light', 'dark', 'auto'] as tm}
                    <button
                        onclick={() => setTheme(tm as Theme)}
                        class="popover-option"
                        class:active={themeVal === tm}
                    >
                        {getThemeLabel(tm as Theme)}
                    </button>
                {/each}
            </div>

            <p class="popover-label">{lang === 'ua' ? 'Мова' : 'language'}</p>
            <div class="popover-row">
                <button
                    onclick={() => setLanguage('en')}
                    class="popover-option"
                    class:active={lang === 'en'}
                >EN</button>
                <button
                    onclick={() => setLanguage('ua')}
                    class="popover-option"
                    class:active={lang === 'ua'}
                >UA</button>
            </div>
        </div>
    {/if}
</div>

<style>
    .top-menu-container {
        position: relative;
    }

    .settings-btn {
        color: var(--gray);
        background: transparent;
        box-shadow: none;
        border: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: var(--sidebar-width);
        height: calc(var(--sidebar-width) - 8px);
        border-radius: var(--border-radius);
        gap: 2px;
        cursor: pointer;
        font-family: inherit;
    }

    .settings-btn:hover {
        color: var(--sidebar-highlight);
        background: var(--button-hover);
    }

    .tab-label {
        font-size: 9px;
        font-weight: 500;
        line-height: 1;
        color: inherit;
    }

    .popover {
        position: absolute;
        left: calc(100% + 8px);
        bottom: 0;
        width: 200px;
        background: var(--button-elevated);
        border: 1px solid var(--button-stroke);
        border-radius: var(--border-radius);
        padding: 10px;
        z-index: 100;
    }

    .popover-below {
        left: auto;
        right: 0;
        bottom: auto;
        top: calc(100% + 8px);
    }

    .popover-above {
        left: 0;
        right: auto;
        bottom: calc(100% + 8px);
        top: auto;
    }

    .popover-label {
        font-size: 10px;
        font-weight: 500;
        color: var(--gray);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 0 6px 4px;
    }

    .popover-row {
        display: flex;
        gap: 4px;
        margin-bottom: 10px;
    }
    .popover-row:last-child { margin-bottom: 0; }

    .popover-option {
        flex: 1;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        background: var(--button);
        color: var(--button-text);
        border: none;
        box-shadow: 0 0 0 1px var(--button-stroke) inset;
        font-family: inherit;
        text-align: center;
    }
    .popover-option:hover { background: var(--button-hover); }
    .popover-option.active { background: var(--secondary); color: var(--primary); }
</style>
