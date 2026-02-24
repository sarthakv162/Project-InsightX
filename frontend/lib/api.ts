/* ── InsightX API Client ─────────────────────────────────────
   Centralised, typed API layer for all backend communication.
   Uses NEXT_PUBLIC_API_URL from .env.local (defaults to localhost:8000).
   ──────────────────────────────────────────────────────────── */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

/* ── Types ─────────────────────────────────────────────────── */

export interface SessionResponse {
    session_id: string
    status: string
    source_type: string
    filename?: string
    youtube_url?: string
    filename2?: string
    youtube_url2?: string
    is_comparison?: boolean
}

export interface AnalysisResponse {
    response: string
    session_id: string
    key_events: KeyEvent[]
}

export interface KeyEvent {
    event_type: string
    timestamp: string
    start_seconds: number
    end_seconds: number
    confidence: number
    description: string
    visual_cues?: string[]
}

export interface HealthResponse {
    status: string
    model: string
}

export interface SessionInfo {
    session_id: string
    sport: string
    source_type: string
    youtube_url?: string
    youtube_url2?: string
    filename?: string
    filename2?: string
    is_comparison?: boolean
}

/* ── Error class ───────────────────────────────────────────── */

export class ApiError extends Error {
    status: number
    constructor(message: string, status: number) {
        super(message)
        this.name = "ApiError"
        this.status = status
    }
}

/* ── Helpers ───────────────────────────────────────────────── */

async function handleResponse<T>(res: Response): Promise<T> {
    if (!res.ok) {
        let msg: string
        try {
            const body = await res.json()
            msg = body.detail || body.message || JSON.stringify(body)
        } catch {
            msg = await res.text()
        }
        throw new ApiError(msg, res.status)
    }
    return res.json() as Promise<T>
}

/* ── API Functions ─────────────────────────────────────────── */

/** Check backend health */
export async function checkHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" })
    return handleResponse<HealthResponse>(res)
}

/** Upload a video file */
export async function uploadVideo(
    file: File,
    sport: string = "unknown",
): Promise<SessionResponse> {
    const form = new FormData()
    form.append("file", file)
    form.append("sport", sport)
    const res = await fetch(`${API_BASE}/api/video/upload`, {
        method: "POST",
        body: form,
    })
    return handleResponse<SessionResponse>(res)
}

/** Submit a YouTube URL */
export async function submitYouTubeUrl(
    url: string,
    sport: string = "unknown",
): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/api/video/youtube`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), sport }),
    })
    return handleResponse<SessionResponse>(res)
}

/** Run analysis query against a session */
export async function runAnalysis(
    sessionId: string,
    query: string,
    sport?: string,
): Promise<AnalysisResponse> {
    const res = await fetch(`${API_BASE}/api/analysis/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, query, sport }),
    })
    return handleResponse<AnalysisResponse>(res)
}

/** Get session metadata */
export async function getSession(sessionId: string): Promise<SessionInfo> {
    const res = await fetch(`${API_BASE}/api/session/${sessionId}`, {
        cache: "no-store",
    })
    return handleResponse<SessionInfo>(res)
}

/** Build the URL to stream an uploaded video file */
export function getVideoFileUrl(filename: string): string {
    return `${API_BASE}/api/video/file/${filename}`
}

/** Submit two YouTube URLs for comparison */
export async function submitCompareYouTubeUrls(
    url1: string,
    url2: string,
    sport: string = "unknown",
): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE}/api/video/youtube-compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url1: url1.trim(), url2: url2.trim(), sport }),
    })
    return handleResponse<SessionResponse>(res)
}

/** Upload two video files for comparison */
export async function uploadCompareVideos(
    file1: File,
    file2: File,
    sport: string = "unknown",
): Promise<SessionResponse> {
    const form = new FormData()
    form.append("file1", file1)
    form.append("file2", file2)
    form.append("sport", sport)
    const res = await fetch(`${API_BASE}/api/video/upload-compare`, {
        method: "POST",
        body: form,
    })
    return handleResponse<SessionResponse>(res)
}

/** Get the API base URL (for components that need it directly) */
export function getApiBaseUrl(): string {
    return API_BASE
}
