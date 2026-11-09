"use client";

import { FolderOpen, RefreshCw } from "lucide-react";
import { useMemo, useState } from "react";

import { MediaThumb } from "@/components/library/media-thumb";
import { KIND_LABEL } from "@/components/studio/defaults";
import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { formatRelativeTime } from "@/lib/format";
import type { MediaItem, MediaKind } from "@/lib/types";

interface LibraryViewProps {
  items: MediaItem[];
  loading: boolean;
  onRefresh: () => void;
  onOpen: (item: MediaItem) => void;
  onCreate: () => void;
}

type Filter = "all" | MediaKind;

export function LibraryView({ items, loading, onRefresh, onOpen, onCreate }: LibraryViewProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const counts = useMemo(
    () => ({
      all: items.length,
      video: items.filter((i) => i.kind === "video").length,
      post: items.filter((i) => i.kind === "post").length,
    }),
    [items],
  );
  const visible = filter === "all" ? items : items.filter((i) => i.kind === filter);

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-4xl tracking-tight">Library</h1>
          <p className="text-sm text-muted-foreground">
            Everything you have rendered, ready to post.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ToggleGroup
            type="single"
            variant="outline"
            value={filter}
            onValueChange={(v) => v && setFilter(v as Filter)}
          >
            {(["all", "video", "post"] as const).map((f) => (
              <ToggleGroupItem key={f} value={f} className="px-3">
                {f === "all" ? "All" : KIND_LABEL[f].many}
                <span className="text-muted-foreground tabular-nums">{counts[f]}</span>
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <Button variant="outline" size="icon" onClick={onRefresh} aria-label="Refresh">
            <RefreshCw className={loading ? "animate-spin" : undefined} />
          </Button>
        </div>
      </div>

      {visible.length === 0 ? (
        <Empty className="border border-dashed py-20">
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <FolderOpen />
            </EmptyMedia>
            <EmptyTitle>Nothing here yet</EmptyTitle>
            <EmptyDescription>Render a reel or post and it will show up here.</EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <Button onClick={onCreate}>Open the studio</Button>
          </EmptyContent>
        </Empty>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {visible.map((item) => (
            <button
              key={`${item.kind}/${item.filename}`}
              type="button"
              onClick={() => onOpen(item)}
              className="group grid overflow-hidden rounded-xl bg-card text-left ring-1 ring-foreground/10 transition hover:-translate-y-0.5 hover:ring-primary/60 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
            >
              <MediaThumb item={item} className="aspect-[4/5]" />
              <div className="grid gap-0.5 p-3">
                <p className="line-clamp-2 text-sm leading-snug">
                  {item.quote ? `“${item.quote}”` : item.filename}
                </p>
                <p className="text-xs text-muted-foreground">
                  {KIND_LABEL[item.kind].one}
                  {item.aspectRatio ? ` · ${item.aspectRatio}` : ""} ·{" "}
                  {formatRelativeTime(item.createdAt)}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
