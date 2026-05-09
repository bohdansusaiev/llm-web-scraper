<script lang="ts">
    import '../app.css';
    import { auth } from '$lib/stores/auth';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { browser } from '$app/environment';
    import { theme, type Theme } from '$lib/stores/theme';

    import Sidebar from '$lib/components/Sidebar.svelte';
    import TopMenu from '$lib/components/TopMenu.svelte';

    let isLoggedIn = false;
    auth.subscribe(v => isLoggedIn = !!v);

    let currentTheme: string = 'light';
    theme.subscribe(v => currentTheme = v);

    $: currentPath = $page.url.pathname;
    $: isAuthPage = currentPath === '/' || currentPath === '/login' || currentPath === '/register';
    $: isLanding = currentPath === '/';

    $: if (browser && !isLoggedIn && !isAuthPage) {
        goto('/');
    }
    $: if (browser && isLoggedIn && isAuthPage) {
        goto('/research');
    }
</script>

<svelte:head>
    <meta name="darkreader-lock" />
</svelte:head>

<div style="display: contents" data-theme={browser ? currentTheme : undefined}>
    {#if isLoggedIn}
        <div id="app-root">
            <Sidebar />
            <div id="content">
                <div id="content-inner">
                    <slot />
                </div>
            </div>
        </div>
    {:else}
        <div id="app-root" style="grid-template-columns:1fr">
            <div id="content" style="margin-left:0" class:no-scroll={isLanding}>
                <div id="content-inner" class:landing-inner={isLanding}>
                    {#if !isAuthPage}
                        <div class="top-menu-fixed">
                            <TopMenu />
                        </div>
                    {/if}
                    <slot />
                </div>
            </div>
        </div>
        {#if isLanding}
            <div class="landing-settings">
                <TopMenu placement="above" />
            </div>
        {/if}
    {/if}
</div>

<style>
    #app-root {
        height: 100%;
        width: 100%;
        display: grid;
        grid-template-columns: calc(var(--sidebar-width) + var(--sidebar-inner-padding) * 2) 1fr;
        overflow: hidden;
        background-color: var(--sidebar-bg);
        color: var(--secondary);
        position: fixed;
    }

    #content {
        display: flex;
        overflow: scroll;
        background-color: var(--primary);
        border-left: var(--content-border-thickness) solid var(--content-border);
    }

    #content-inner {
        width: 100%;
        max-width: 720px;
        margin: 0 auto;
        padding: calc(var(--padding) * 2) var(--padding);
    }

    .top-menu-fixed {
        display: flex;
        justify-content: flex-end;
        margin-bottom: var(--padding);
    }

    #content.no-scroll {
        overflow: hidden;
    }

    #content-inner.landing-inner {
        padding: 0;
    }

    .landing-settings {
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 50;
    }

    @media screen and (max-width: 600px) {
        #content-inner {
            padding: var(--padding);
        }
    }
</style>
