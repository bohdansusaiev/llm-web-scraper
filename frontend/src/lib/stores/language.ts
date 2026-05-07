import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Lang = 'en' | 'ua';

function getInitial(): Lang {
    if (!browser) return 'en';
    const params = new URLSearchParams(window.location.search);
    const urlLang = params.get('lang');
    if (urlLang === 'en' || urlLang === 'ua') return urlLang;
    const stored = localStorage.getItem('newsscraper_lang') as Lang | null;
    if (stored === 'en' || stored === 'ua') return stored;
    return 'en';
}

export const language = writable<Lang>(getInitial());

language.subscribe(v => {
    if (browser) {
        localStorage.setItem('newsscraper_lang', v);
        const url = new URL(window.location.href);
        if (url.searchParams.get('lang') !== v) {
            url.searchParams.set('lang', v);
            window.history.replaceState({}, '', url.toString());
        }
    }
});
