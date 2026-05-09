import { auth } from '$lib/stores/auth';

const BASE = '/api';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...auth.getHeaders(),
            ...options.headers,
        },
    });
    if (!res.ok) {
        const payload = await res.json().catch(() => null);
        // Stale session (server recreated DB while we still had a cookie of the
        // old user). Clear local auth so the layout redirects to login.
        if (res.status === 401 && auth.getHeaders()['X-User-Id']) {
            auth.logout();
            if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
                window.location.href = '/login';
            }
        }
        throw new Error(formatError(payload, res.status));
    }
    return res.json();
}

/** FastAPI returns 422 detail as an array of {loc, msg, type} objects;
 *  4xx/5xx with HTTPException returns detail as a string. Render either. */
function formatError(payload: unknown, status: number): string {
    if (!payload || typeof payload !== 'object') return `HTTP ${status}`;
    const detail = (payload as { detail?: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        return detail.map((d) => {
            if (!d || typeof d !== 'object') return String(d);
            const o = d as { loc?: unknown[]; msg?: string };
            const field = Array.isArray(o.loc) ? o.loc.filter((x) => x !== 'body').join('.') : '';
            return field ? `${field}: ${o.msg ?? 'invalid'}` : (o.msg ?? 'invalid');
        }).join('; ');
    }
    return `HTTP ${status}`;
}

// ---------- Auth ----------

export interface User { id: number; username: string; }

export async function login(username: string, password: string) {
    return request<User>('/auth/login', {
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

// ---------- Generic /scrape ----------

export interface GenericExtractRequest {
    url: string;
    output_schema?: Record<string, unknown> | null;
    instruction?: string | null;
    language?: string;
    use_cache?: boolean;
}
export interface GenericExtractResponse {
    url: string;
    success: boolean;
    data: Record<string, unknown>;
    markdown_preview: string;
    duration_ms: number;
    cached: boolean;
    error: string;
}
export async function genericScrape(req: GenericExtractRequest) {
    return request<GenericExtractResponse>('/scrape', {
        method: 'POST',
        body: JSON.stringify(req),
    });
}

// ---------- Research jobs ----------

export interface ResearchRequest {
    topic: string;
    max_papers?: number;
    discovery_limit?: number;
    providers?: string[];
    min_year?: number | null;
    open_access_only?: boolean;
    language?: string;
}
export type JobStatus =
    | 'pending' | 'discovering' | 'filtering'
    | 'extracting' | 'translating' | 'saving'
    | 'completed' | 'failed';

export interface ResearchJob {
    id: number;
    user_id: number;
    topic: string;
    language: string;
    status: JobStatus;
    progress: number;
    message: string;
    catalog_id: number | null;
    error: string;
    created_at: string;
    updated_at: string;
}

export async function startResearch(req: ResearchRequest) {
    return request<{ job_id: number }>('/research', {
        method: 'POST',
        body: JSON.stringify(req),
    });
}
export async function getResearchJob(jobId: number) {
    return request<ResearchJob>(`/research/${jobId}`);
}
export async function listResearchJobs(limit = 20) {
    return request<ResearchJob[]>(`/research?limit=${limit}`);
}

// ---------- Catalogs ----------

export interface Author { name: string; affiliation?: string | null; orcid?: string | null; }
export interface ScientificPaper {
    doi?: string | null;
    title: string;
    authors: Author[];
    publication_year?: number | null;
    venue?: string | null;
    url: string;
    abstract: string;
    methodology: string;
    conclusions: string;
    keywords: string[];
    image_url?: string;
    citation_count?: number | null;
    is_open_access: boolean;
    relevance_score: number;
    extraction_source: string;
    failure_reason: string;
    language: string;
}
export interface CatalogStats {
    discovered: number;
    after_dedupe: number;
    relevance_filtered: number;
    deeply_extracted: number;
    failed: number;
    duration_seconds: number;
    failure_breakdown: Record<string, number>;
}
export interface ScientificCatalog {
    id: number;
    user_id: number;
    topic: string;
    language: string;
    created_at: string;
    papers: ScientificPaper[];
    stats: CatalogStats;
}
export interface CatalogSummary {
    id: number;
    topic: string;
    language: string;
    created_at: string;
    paper_count: number;
}

export async function listCatalogs() {
    return request<CatalogSummary[]>('/catalogs');
}
export async function getCatalog(id: number) {
    return request<ScientificCatalog>(`/catalogs/${id}`);
}
export async function deleteCatalog(id: number) {
    return request<{ status: string }>(`/catalogs/${id}`, { method: 'DELETE' });
}
export function exportUrl(catalogId: number, format: 'json' | 'csv' | 'bibtex') {
    return `${BASE}/export/${catalogId}?format=${format}`;
}

// ---------- Benchmark ----------

export interface BenchmarkRequest {
    url: string;
    instruction?: string | null;
    ground_truth?: Record<string, unknown> | null;
}
export interface ScraperResult {
    method: 'llm' | 'classical';
    success: boolean;
    fields: Record<string, unknown>;
    fields_populated: number;
    duration_ms: number;
    bytes_downloaded: number;
    tokens_used?: number | null;
    estimated_cost_usd: number;
    error: string;
}
export interface FieldComparison {
    field: string;
    llm_value: unknown;
    classical_value: unknown;
    ground_truth: unknown;
    llm_match: boolean | null;
    classical_match: boolean | null;
}
export interface BenchmarkResult {
    url: string;
    llm: ScraperResult;
    classical: ScraperResult;
    fields: FieldComparison[];
    winner_completeness: 'llm' | 'classical' | 'tie';
    winner_speed: 'llm' | 'classical' | 'tie';
}
export interface BenchmarkBatchSummary {
    total_urls: number;
    llm_success_rate: number;
    classical_success_rate: number;
    llm_avg_fields: number;
    classical_avg_fields: number;
    llm_avg_duration_ms: number;
    classical_avg_duration_ms: number;
    llm_total_cost_usd: number;
    results: BenchmarkResult[];
}

export async function runBenchmark(req: BenchmarkRequest) {
    return request<BenchmarkResult>('/benchmark', {
        method: 'POST',
        body: JSON.stringify(req),
    });
}
export async function runBenchmarkBatch(urls: string[], instruction?: string) {
    return request<BenchmarkBatchSummary>('/benchmark/batch', {
        method: 'POST',
        body: JSON.stringify({ urls, instruction }),
    });
}
