import type { MediaKind, StyleSettings, VideoTiming } from "@/lib/types";

export const DEFAULT_STYLE: StyleSettings = {
  aspectRatio: "4:5",
  fontId: "Montserrat/Montserrat-ExtraBold.ttf",
  fontScale: 4.5,
  placement: "center",
  overlay: 35,
};

export const DEFAULT_TIMING: VideoTiming = {
  duration: 6,
  fadeIn: 1.5,
  fadeOut: 0.5,
};

export const DEFAULT_QUOTE = "Waste no more time arguing about what a good man should be. Be one.";
export const DEFAULT_AUTHOR = "Marcus Aurelius";

export interface Caption {
  text: string;
  hashtags: string[];
}

export interface Draft {
  quote: string;
  /** Attribution line drawn under the quote. */
  author: string;
  showAuthor: boolean;
  /** AI brief. */
  theme: string | null;
  sourceAuthor: string | null;
  caption: Caption | null;
}

export const INITIAL_DRAFT: Draft = {
  quote: DEFAULT_QUOTE,
  author: DEFAULT_AUTHOR,
  showAuthor: true,
  theme: "Stoicism",
  sourceAuthor: DEFAULT_AUTHOR,
  caption: null,
};

export const KIND_LABEL: Record<MediaKind, { one: string; many: string; file: string }> = {
  video: { one: "Reel", many: "Reels", file: "MP4" },
  post: { one: "Post", many: "Posts", file: "PNG" },
};

export const NONE = "__none__";
