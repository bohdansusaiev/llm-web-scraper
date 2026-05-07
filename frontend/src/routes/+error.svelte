<script>
    import { page } from '$app/stores';
</script>

<div class="flex flex-col items-center justify-center min-h-[50vh] text-center">
    <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-100 mb-2">{$page.status}</h1>
    <p class="text-surface-500 dark:text-surface-400">{$page.error?.message || 'Page not found'}</p>
    <a href="/dashboard" class="mt-4 text-primary-500 hover:text-primary-600 text-sm">Go to dashboard</a>
</div>
