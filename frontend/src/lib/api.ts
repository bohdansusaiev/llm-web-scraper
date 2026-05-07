import { auth } from '$lib/stores/auth';

const BASE = '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE}${path}`;
    const res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...auth.getHeaders(),
            ...options.headers,
        },
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

export interface Article {
    id: number;
    url: string;
    title: string;
    summary: string;
    article_type: string;
    key_points: string;
    author: string;
    author_url: string;
    date: string;
    image: string;
    translated: boolean;
    language: string;
    scraped_at: string;
    source_id: number | null;
    source_name: string | null;
    collection_id: number | null;
}

export interface Collection {
    id: number;
    name: string;
    source_count: number;
    article_count: number;
    created_at: string;
}

export interface Source {
    id: number;
    collection_id: number;
    url: string;
    name: string;
    scrape_interval: string;
    last_scraped_at: string | null;
    last_status: string | null;
    last_error: string | null;
    article_count: number;
}

export interface BatchJob {
    job_id: number;
    total: number;
    status: string;
    completed: number;
    failed: number;
    results: Array<{ source_id: number; url: string; status: string; error?: string }>;
}

export interface DashboardStats {
    total_articles: number;
    total_collections: number;
    total_sources: number;
    type_counts: Array<{ article_type: string; cnt: number }>;
    overdue: Array<{ id: number; name: string; url: string; collection_name: string }>;
}

export interface ScrapeResult extends Article {
    error?: string;
}

export async function login(username: string, password: string) {
    return request<{ id: number; username: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
}

export async function register(username: string, password: string) {
    return request<{ status: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });
}

export async function scrapeArticle(url: string, language: string = 'en', sourceId?: number): Promise<ScrapeResult> {
    return request<ScrapeResult>('/scrape', {
        method: 'POST',
        body: JSON.stringify({ url, language, source_id: sourceId }),
    });
}

export async function batchScrape(collectionId: number, language: string = 'en'): Promise<{ job_id: number; total: number }> {
    return request('/scrape/batch', {
        method: 'POST',
        body: JSON.stringify({ collection_id: collectionId, language }),
    });
}

export async function getBatchStatus(jobId: number): Promise<BatchJob> {
    return request<BatchJob>(`/scrape/batch/${jobId}`);
}

export async function getCollections(): Promise<Collection[]> {
    return request<Collection[]>('/collections');
}

export async function createCollection(name: string) {
    return request<{ status: string }>(`/collections?name=${encodeURIComponent(name)}`, { method: 'POST' });
}

export async function deleteCollection(id: number) {
    return request<{ status: string }>(`/collections/${id}`, { method: 'DELETE' });
}

export async function getSources(collectionId: number): Promise<Source[]> {
    return request<Source[]>(`/collections/${collectionId}/sources`);
}

export async function createSource(collectionId: number, url: string, name: string = '', interval: string = 'manual') {
    const params = new URLSearchParams({ url, name, scrape_interval: interval });
    return request<{ status: string }>(`/collections/${collectionId}/sources?${params}`, { method: 'POST' });
}

export async function deleteSource(id: number) {
    return request<{ status: string }>(`/sources/${id}`, { method: 'DELETE' });
}

export async function getSource(id: number): Promise<Source> {
    return request<Source>(`/sources/${id}`);
}

export async function updateSource(id: number, data: { name?: string; scrape_interval?: string }) {
    const params = new URLSearchParams();
    if (data.name !== undefined) params.set('name', data.name);
    if (data.scrape_interval !== undefined) params.set('scrape_interval', data.scrape_interval);
    return request<{ status: string }>(`/sources/${id}?${params}`, { method: 'PUT' });
}

export async function scrapeSource(id: number): Promise<ScrapeResult> {
    return request<ScrapeResult>(`/sources/${id}/scrape`, { method: 'POST' });
}

export async function getArticles(params: {
    collection_id?: number;
    source_id?: number;
    article_type?: string;
    q?: string;
    limit?: number;
    offset?: number;
} = {}): Promise<Article[]> {
    const sp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== '') sp.set(k, String(v)); });
    return request<Article[]>(`/articles?${sp}`);
}

export async function deleteArticle(id: number) {
    return request<{ status: string }>(`/articles/${id}`, { method: 'DELETE' });
}

export async function getDashboardStats(): Promise<DashboardStats> {
    return request<DashboardStats>('/dashboard/stats');
}

export async function getHistory(limit: number = 50): Promise<Article[]> {
    return request<Article[]>(`/history?limit=${limit}`);
}

export async function exportArticles(ids: number[], format: string = 'json') {
    return request(`/export?article_ids=${ids.join(',')}&format=${format}`);
}
