// Mirrors the FastAPI Pydantic schemas (camelCase on the wire).

export type MediaKind = "video" | "post";
export type Placement = "top" | "center" | "bottom";
export type AspectRatio = "4:5" | "9:16" | "1:1" | "16:9" | "4:3";

export interface AspectOption {
  key: AspectRatio;
  label: string;
  width: number;
  height: number;
}

export interface FontOption {
  id: string;
  name: string;
  family: string;
}

export interface BackgroundOption {
  id: string;
  name: string;
  url: string;
  thumbnailUrl: string;
}

export interface AppConfig {
  version: string;
  groqConfigured: boolean;
  defaultModel: string;
  models: string[];
  themes: string[];
  authors: string[];
  aspectRatios: AspectOption[];
  placements: Placement[];
  fonts: FontOption[];
  backgrounds: BackgroundOption[];
  stats: { videos: number; posts: number };
}

export interface StyleSettings {
  aspectRatio: AspectRatio;
  fontId: string;
  fontScale: number;
  placement: Placement;
  overlay: number;
}

export interface VideoTiming {
  duration: number;
  fadeIn: number;
  fadeOut: number;
}

export interface ComposeRequest extends StyleSettings {
  quote: string;
  author?: string | null;
  background?: string | null;
}

export interface PostRequest extends ComposeRequest {
  caption?: string | null;
}

export type VideoRequest = PostRequest & VideoTiming;

export interface PreviewResponse {
  image: string;
  width: number;
  height: number;
  background: string;
}

export interface MediaItem {
  kind: MediaKind;
  filename: string;
  url: string;
  sizeBytes: number;
  createdAt: string;
  width?: number | null;
  height?: number | null;
  duration?: number | null;
  quote?: string | null;
  author?: string | null;
  caption?: string | null;
  background?: string | null;
  aspectRatio?: string | null;
}

export interface QuoteRequest {
  theme?: string | null;
  author?: string | null;
  model?: string | null;
  avoid?: string[];
}

export interface QuoteResponse {
  quote: string;
  author?: string | null;
  model: string;
}

export interface CaptionRequest {
  quote: string;
  theme?: string | null;
  author?: string | null;
  model?: string | null;
}

export interface CaptionResponse {
  caption: string;
  hashtags: string[];
  model: string;
}

export type BatchStatus = "queued" | "running" | "completed" | "failed";

export interface BatchRequest extends StyleSettings, VideoTiming {
  kind: MediaKind;
  count: number;
  quoteSource: "ai" | "manual";
  quote?: string | null;
  theme?: string | null;
  author?: string | null;
  showAuthor: boolean;
  withCaptions: boolean;
  model?: string | null;
}

export interface BatchJob {
  id: string;
  status: BatchStatus;
  kind: MediaKind;
  total: number;
  completed: number;
  stage: string;
  items: MediaItem[];
  errors: string[];
  createdAt: string;
  finishedAt?: string | null;
}
