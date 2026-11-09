import type {
  AppConfig,
  BatchJob,
  BatchRequest,
  CaptionRequest,
  CaptionResponse,
  ComposeRequest,
  MediaItem,
  MediaKind,
  PostRequest,
  PreviewResponse,
  QuoteRequest,
  QuoteResponse,
  VideoRequest,
} from "@/lib/types";

// Empty by default: requests go to the Next.js origin and are proxied to FastAPI
// (see next.config.ts). Set NEXT_PUBLIC_API_URL to call the backend directly.
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE";
  body?: unknown;
  apiKey?: string;
  signal?: AbortSignal;
}

function errorMessage(detail: unknown, fallback: string): string {
  if (typeof detail === "string") return detail;
  // FastAPI validation errors: [{ loc, msg, ... }]
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d: { msg?: string }) => d.msg?.replace(/^Value error, /, ""))
      .filter(Boolean)
      .join(" ");
  }
  return fallback;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (options.apiKey) headers["X-Groq-Api-Key"] = options.apiKey;

  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: options.method ?? "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: options.signal,
      cache: "no-store",
    });
  } catch (err) {
    if ((err as Error).name === "AbortError") throw err;
    throw new ApiError("Cannot reach the backend. Is the FastAPI server running?", 0);
  }

  if (!res.ok) {
    const payload = await res.json().catch(() => null);
    const fallback =
      res.status >= 500 && !payload
        ? "Cannot reach the backend. Is the FastAPI server running?"
        : `Request failed (${res.status})`;
    throw new ApiError(errorMessage(payload?.detail, fallback), res.status);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export function mediaUrl(path: string): string {
  return /^(https?:|data:)/.test(path) ? path : `${API_BASE}${path}`;
}

export const api = {
  config: () => request<AppConfig>("/api/config"),

  generateQuote: (body: QuoteRequest, apiKey?: string) =>
    request<QuoteResponse>("/api/ai/quote", { method: "POST", body, apiKey }),

  generateCaption: (body: CaptionRequest, apiKey?: string) =>
    request<CaptionResponse>("/api/ai/caption", { method: "POST", body, apiKey }),

  preview: (body: ComposeRequest, signal?: AbortSignal) =>
    request<PreviewResponse>("/api/render/preview", { method: "POST", body, signal }),

  renderPost: (body: PostRequest) =>
    request<MediaItem>("/api/render/post", { method: "POST", body }),

  renderVideo: (body: VideoRequest) =>
    request<MediaItem>("/api/render/video", { method: "POST", body }),

  listMedia: (kind?: MediaKind) => request<MediaItem[]>(`/api/media${kind ? `?kind=${kind}` : ""}`),

  deleteMedia: (kind: MediaKind, filename: string) =>
    request<void>(`/api/media/${kind}/${encodeURIComponent(filename)}`, { method: "DELETE" }),

  createBatch: (body: BatchRequest, apiKey?: string) =>
    request<BatchJob>("/api/batches", { method: "POST", body, apiKey }),

  getBatch: (id: string) => request<BatchJob>(`/api/batches/${id}`),
};
