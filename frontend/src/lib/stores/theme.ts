import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark' | 'auto';

const stored = browser ? (localStorage.getItem('newsscraper_theme') as Theme | null) : null;
const initial: Theme = stored || 'light';

function applyTheme(theme: Theme) {
    if (!browser) return;
    const isDark = theme === 'dark' || (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.className = isDark ? 'dark' : 'light';
}

export const theme = writable<Theme>(initial);

theme.subscribe(v => {
    if (browser) {
        localStorage.setItem('newsscraper_theme', v);
        applyTheme(v);
    }
});

if (browser && initial === 'auto') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => applyTheme('auto'));
}
