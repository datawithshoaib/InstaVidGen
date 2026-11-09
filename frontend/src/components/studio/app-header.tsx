"use client";

import { Clapperboard, Settings2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

export type View = "create" | "library";

interface AppHeaderProps {
  view: View;
  onViewChange: (view: View) => void;
  libraryCount: number;
  aiReady: boolean;
  model: string;
  onOpenSettings: () => void;
}

export function AppHeader({
  view,
  onViewChange,
  libraryCount,
  aiReady,
  model,
  onOpenSettings,
}: AppHeaderProps) {
  return (
    <header className="sticky top-0 z-40 border-b bg-background/75 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1400px] items-center gap-4 px-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-[0_0_24px_-4px] shadow-primary/50">
            <Clapperboard className="size-4.5" />
          </div>
          <div className="hidden leading-none sm:block">
            <p className="font-display text-2xl tracking-tight">InstaVidGen</p>
            <p className="hidden text-[11px] text-muted-foreground sm:block">
              Quote reels & posts studio
            </p>
          </div>
        </div>

        <Tabs value={view} onValueChange={(v) => onViewChange(v as View)} className="mx-auto">
          <TabsList>
            <TabsTrigger value="create" className="px-4">
              Create
            </TabsTrigger>
            <TabsTrigger value="library" className="px-4">
              Library
              <span className="ml-1 rounded-full bg-foreground/10 px-1.5 text-[10px] tabular-nums">
                {libraryCount}
              </span>
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                type="button"
                onClick={onOpenSettings}
                className="hidden items-center gap-2 rounded-full border px-3 py-1.5 text-xs text-muted-foreground transition hover:text-foreground md:flex"
              >
                <span
                  className={cn(
                    "size-2 rounded-full",
                    aiReady ? "bg-success shadow-[0_0_8px] shadow-success" : "bg-primary",
                  )}
                />
                {aiReady ? model : "Connect Groq"}
              </button>
            </TooltipTrigger>
            <TooltipContent>
              {aiReady
                ? "AI is ready. Click to change model or key."
                : "Add a Groq API key to enable AI"}
            </TooltipContent>
          </Tooltip>
          <Button variant="outline" size="icon" onClick={onOpenSettings} aria-label="Settings">
            <Settings2 />
          </Button>
        </div>
      </div>
    </header>
  );
}
