"use client";

import { Play } from "lucide-react";

import { mediaUrl } from "@/lib/api";
import type { MediaItem } from "@/lib/types";
import { cn } from "@/lib/utils";

/** Static thumbnail for a post or (first frame of) a video. Videos play on hover. */
export function MediaThumb({ item, className }: { item: MediaItem; className?: string }) {
  const src = mediaUrl(item.url);
  return (
    <div className={cn("relative overflow-hidden bg-black", className)}>
      {item.kind === "video" ? (
        <>
          <video
            src={`${src}#t=2`}
            muted
            loop
            playsInline
            preload="metadata"
            className="size-full object-cover"
            onMouseEnter={(e) => void e.currentTarget.play().catch(() => {})}
            onMouseLeave={(e) => e.currentTarget.pause()}
          />
          <span className="pointer-events-none absolute top-1.5 left-1.5 flex size-5 items-center justify-center rounded-full bg-black/60 text-white backdrop-blur">
            <Play className="size-2.5 fill-current" />
          </span>
        </>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element -- served by FastAPI
        <img
          src={src}
          alt={item.quote ?? item.filename}
          loading="lazy"
          className="size-full object-cover"
        />
      )}
    </div>
  );
}
