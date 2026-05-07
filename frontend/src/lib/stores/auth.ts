import { writable } from 'svelte/store';
import { browser } from '$app/environment';

interface User {
    id: number;
    username: string;
}

function createAuthStore() {
    const stored = browser ? localStorage.getItem('newsscraper_user') : null;
    const initial: User | null = stored ? JSON.parse(stored) : null;

    const { subscribe, set } = writable<User | null>(initial);
    let current: User | null = initial;
    subscribe(v => current = v);

    return {
        subscribe,
        login(user: User) {
            if (browser) localStorage.setItem('newsscraper_user', JSON.stringify(user));
            current = user;
            set(user);
        },
        logout() {
            if (browser) localStorage.removeItem('newsscraper_user');
            current = null;
            set(null);
        },
        getHeaders(): Record<string, string> {
            if (current) return { 'X-User-Id': String(current.id) };
            return {};
        }
    };
}

export const auth = createAuthStore();
