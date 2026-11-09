"use client";

import { Check, Search, Shuffle } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { mediaUrl } from "@/lib/api";
import type { BackgroundOption } from "@/lib/types";
import { cn } from "@/lib/utils";

interface BackgroundPanelProps {
  backgrounds: BackgroundOption[];
  selected: string | null;
  onSelect: (id: string) => void;
}

export function BackgroundPanel({ backgrounds, selected, onSelect }: BackgroundPanelProps) {
  const [query, setQuery] = useState("");
  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? backgrounds.filter((b) => b.name.toLowerCase().includes(q)) : backgrounds;
  }, [backgrounds, query]);

  function shuffle() {
    const pool = backgrounds.filter((b) => b.id !== selected);
    if (pool.length) onSelect(pool[Math.floor(Math.random() * pool.length)].id);
  }

  return (
    <div className="grid gap-4">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search ${backgrounds.length} backgrounds`}
            className="pl-8"
          />
        </div>
        <Button variant="outline" onClick={shuffle}>
          <Shuffle /> Shuffle
        </Button>
      </div>

      <div className="max-h-[560px] overflow-y-auto pr-1">
        <div className="grid grid-cols-3 gap-2.5 sm:grid-cols-4">
          {visible.map((bg) => {
            const active = bg.id === selected;
            return (
              <button
                key={bg.id}
                type="button"
                onClick={() => onSelect(bg.id)}
                title={bg.name}
                aria-pressed={active}
                className={cn(
                  "group relative aspect-[4/5] overflow-hidden rounded-lg ring-1 ring-foreground/10 transition outline-none focus-visible:ring-2 focus-visible:ring-ring",
                  active && "ring-2 ring-primary",
                )}
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- served by FastAPI */}
                <img
                  src={mediaUrl(bg.thumbnailUrl)}
                  alt={bg.name}
                  loading="lazy"
                  className="size-full object-cover transition duration-300 group-hover:scale-105"
                />
                <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 to-transparent p-1.5 pt-6 text-left text-[10px] leading-tight text-white/90 opacity-0 transition group-hover:opacity-100">
                  {bg.name}
                </span>
                {active && (
                  <span className="absolute top-1.5 right-1.5 flex size-5 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Check className="size-3" />
                  </span>
                )}
              </button>
            );
          })}
          {visible.length === 0 && (
            <p className="col-span-full py-10 text-center text-sm text-muted-foreground">
              No backgrounds match “{query}”.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
