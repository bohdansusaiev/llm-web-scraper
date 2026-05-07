<script lang="ts">
    import { goto } from '$app/navigation';
    import { auth } from '$lib/stores/auth';
    import { login } from '$lib/api';
    import { t } from '$lib/i18n';

    let username = '';
    let password = '';
    let error = '';
    let loading = false;

    async function handleLogin() {
        error = '';
        loading = true;
        try { const user = await login(username, password); auth.login(user); goto('/dashboard'); }
        catch (e: any) { error = e.message || t('login_failed'); }
        loading = false;
    }
</script>

<svelte:head><title>{t('login_title')} - NewsScraper</title></svelte:head>

<div class="center">
    <div class="form">
        <h1>{t('login_title')}</h1>
        <p class="subtext">{t('no_account')} <a href="/register">{t('register_link')}</a></p>

        {#if error}<p class="subtext" style="color:var(--red)">{error}</p>{/if}

        <input type="text" bind:value={username} placeholder={t('username')} onkeydown={(e) => e.key === 'Enter' && handleLogin()} />
        <input type="password" bind:value={password} placeholder={t('password')} onkeydown={(e) => e.key === 'Enter' && handleLogin()} />
        <button onclick={handleLogin} disabled={loading || !username || !password} class="active" style="width:100%">{loading ? '...' : t('login_btn')}</button>
    </div>
</div>

<style>
    .center {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }
    .form {
        width: 100%;
        max-width: 360px;
        display: flex;
        flex-direction: column;
        gap: var(--padding);
    }
    .form input { width: 100%; }
    a { color: var(--blue); }
</style>
