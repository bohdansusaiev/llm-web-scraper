<script lang="ts">
    import { goto } from '$app/navigation';
    import { register } from '$lib/api';
    import { t } from '$lib/i18n';

    let username = '';
    let password = '';
    let error = '';
    let success = '';
    let loading = false;

    async function handleRegister() {
        error = ''; success = '';
        loading = true;
        try { await register(username, password); success = t('register_success'); setTimeout(() => goto('/login'), 1500); }
        catch (e: any) { error = e.message || t('register_failed'); }
        loading = false;
    }
</script>

<svelte:head><title>{t('register_title')} - NewsScraper</title></svelte:head>

<div class="center">
    <div class="form">
        <h1>{t('register_title')}</h1>
        <p class="subtext">{t('has_account')} <a href="/login">{t('login_link')}</a></p>

        {#if success}<p class="subtext" style="color:var(--green)">{success}</p>{/if}
        {#if error}<p class="subtext" style="color:var(--red)">{error}</p>{/if}

        <input type="text" bind:value={username} placeholder={t('username')} />
        <input type="password" bind:value={password} placeholder={t('password')} />
        <button onclick={handleRegister} disabled={loading || !username || !password} class="active" style="width:100%">{loading ? '...' : t('register_btn')}</button>
    </div>
</div>

<style>
    .center { display: flex; align-items: center; justify-content: center; min-height: 80vh; }
    .form { width: 100%; max-width: 360px; display: flex; flex-direction: column; gap: var(--padding); }
    .form input { width: 100%; }
    a { color: var(--blue); }
</style>
