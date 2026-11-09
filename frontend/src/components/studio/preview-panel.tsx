"use client";

import { Film, ImageIcon, ImageOff, Layers } from "lucide-react";
import { useEffect, useState } from "react";

import { KIND_LABEL } from "@/components/studio/defaults";
import { Button } from "@/components/ui/button";
import { Kbd } from "@/components/ui/kbd";
import { Spinner } from "@/components/ui/spinner";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { api } from "@/lib/api";
import { errorText } from "@/lib/format";
import type { AspectOption, ComposeRequest, MediaKind, VideoTiming } from "@/lib/types";

interface PreviewPanelProps {
  request: ComposeRequest | null;
  aspect: AspectOption;
  kind: MediaKind;
  timing: VideoTiming;
  rendering: boolean;
  onRender: () => void;
  onBatch: () => void;
}

export function PreviewPanel({
  request,
  aspect,
  kind,
  timing,
  rendering,
  onRender,
  onBatch,
}: PreviewPanelProps) {
  const debounced = useDebouncedValue(request ? JSON.stringify(request) : null, 350);
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!debounced) return;
    const controller = new AbortController();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reflects an in-flight request
    setLoading(true);
    api
      .preview(JSON.parse(debounced) as ComposeRequest, controller.signal)
      .then((res) => {
        setImage(res.image);
        setError(null);
      })
      .catch((err) => {
        if ((err as Error).name !== "AbortError") setError(errorText(err));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [debounced]);

  const label = KIND_LABEL[kind];
  const KindIcon = kind === "video" ? Film : ImageIcon;

  return (
    <div className="grid gap-4">
      <div className="checkerboard flex items-center justify-center overflow-hidden rounded-2xl p-4 ring-1 ring-foreground/10 sm:p-6">
        <div
          className="relative w-full overflow-hidden rounded-lg bg-black shadow-2xl ring-1 shadow-black/60 ring-white/10"
          style={{
            aspectRatio: `${aspect.width} / ${aspect.height}`,
            maxWidth: `calc(min(62vh, 620px) * ${aspect.width / aspect.height})`,
          }}
        >
          {image && (
            // eslint-disable-next-line @next/next/no-img-element -- data URI from the API
            <img src={image} alt="Live preview" className="size-full object-cover" />
          )}
          {!image && !error && (
            <div className="absolute inset-0 animate-pulse bg-gradient-to-br from-muted to-background" />
          )}
          {error && !image && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 p-6 text-center text-sm text-muted-foreground">
              <ImageOff className="size-6" />
              {error}
            </div>
          )}
          {loading && (
            <div className="absolute top-2.5 right-2.5 flex items-center gap-1.5 rounded-full bg-black/60 px-2.5 py-1 text-[11px] text-white backdrop-blur">
              <Spinner className="size-3" /> Updating
            </div>
          )}
          {request === null && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60 p-6 text-center text-sm text-white/80 backdrop-blur-sm">
              Write a quote to see the preview.
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 px-1 text-xs text-muted-foreground">
        <span className="flex items-center gap-1.5">
          <KindIcon className="size-3.5" />
          {label.one} · {aspect.width}×{aspect.height} · {label.file}
          {kind === "video" && ` · ${timing.duration}s`}
        </span>
        <span className="hidden items-center gap-1 sm:flex">
          <Kbd>Ctrl</Kbd>+<Kbd>Enter</Kbd> to render
        </span>
      </div>

      <div className="grid grid-cols-[1fr_auto] gap-2">
        <Button
          size="lg"
          className="h-11 text-sm"
          onClick={onRender}
          disabled={rendering || !request}
        >
          {rendering ? <Spinner /> : <KindIcon />}
          {rendering
            ? `Rendering ${label.one.toLowerCase()}…`
            : `Render ${label.one.toLowerCase()}`}
        </Button>
        <Button size="lg" variant="outline" className="h-11" onClick={onBatch}>
          <Layers /> Batch
        </Button>
      </div>
    </div>
  );
}
