<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth';
    import { t } from '$lib/i18n';
    import TopMenu from '$lib/components/TopMenu.svelte';

    const navItems = [
        { id: 'research', label: t('nav_research'), path: '/research' },
        { id: 'catalogs', label: t('nav_catalogs'), path: '/catalogs' },
        { id: 'scrape', label: t('nav_scrape'), path: '/scrape' },
        { id: 'benchmark', label: t('nav_benchmark'), path: '/benchmark' },
        { id: 'about', label: t('nav_about'), path: '/about' },
    ];

    function logout() {
        auth.logout();
        goto('/');
    }
</script>

<nav id="sidebar">
    <div class="sidebar-tabs">
        {#each navItems as item}
            <a
                href={item.path}
                class="sidebar-tab"
                class:active={item.path === $page.url.pathname}
                onclick={(e) => { e.preventDefault(); goto(item.path); }}
                title={item.label}
            >
                {#if item.id === 'research'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                {:else if item.id === 'catalogs'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                {:else if item.id === 'scrape'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20"/><path d="M2 12h20"/></svg>
                {:else if item.id === 'benchmark'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                {:else if item.id === 'about'}
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
                {/if}
                <span class="tab-label">{item.label.split(' ')[0]}</span>
            </a>
        {/each}
    </div>

    <div class="sidebar-bottom">
        <TopMenu />
        <button onclick={logout} class="sidebar-tab" title={t('logout_btn')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            <span class="tab-label">{t('logout_btn')}</span>
        </button>
    </div>
</nav>

<style>
    #sidebar {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: var(--sidebar-inner-padding);
        height: 100%;
        gap: 4px;
    }

    .sidebar-tabs {
        display: flex;
        flex-direction: column;
        gap: 2px;
        flex: 1;
        padding-top: 8px;
    }

    .sidebar-tab {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: var(--sidebar-width);
        height: calc(var(--sidebar-width) - 8px);
        border-radius: var(--border-radius);
        color: var(--gray);
        text-decoration: none;
        gap: 2px;
        transition: none;
    }

    .sidebar-tab:hover {
        color: var(--sidebar-highlight);
        background: var(--button-hover);
    }

    .sidebar-tab.active {
        color: var(--primary);
        background: var(--secondary);
    }

    .tab-label {
        font-size: 9px;
        font-weight: 500;
        line-height: 1;
        text-align: center;
        max-width: calc(var(--sidebar-width) - 4px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .sidebar-bottom {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding-bottom: 4px;
        align-items: center;
    }
</style>
