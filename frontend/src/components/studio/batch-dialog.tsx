"use client";

import { CircleAlert, Film, ImageIcon, Layers } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { type Draft, KIND_LABEL } from "@/components/studio/defaults";
import { MediaThumb } from "@/components/library/media-thumb";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type { AiSettings } from "@/hooks/use-ai-settings";
import { api } from "@/lib/api";
import { errorText } from "@/lib/format";
import type { BatchJob, MediaItem, MediaKind, StyleSettings, VideoTiming } from "@/lib/types";

interface BatchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialKind: MediaKind;
  draft: Draft;
  style: StyleSettings;
  timing: VideoTiming;
  ai: AiSettings;
  aiReady: boolean;
  onFinished: () => void;
  onOpenItem: (item: MediaItem) => void;
}

const COUNTS = [3, 5, 10, 20];
const POLL_MS = 1000;

export function BatchDialog({
  open,
  onOpenChange,
  initialKind,
  draft,
  style,
  timing,
  ai,
  aiReady,
  onFinished,
  onOpenItem,
}: BatchDialogProps) {
  const [kind, setKind] = useState<MediaKind>(initialKind);
  const [count, setCount] = useState(5);
  const [source, setSource] = useState<"ai" | "manual">(aiReady ? "ai" : "manual");
  const [withCaptions, setWithCaptions] = useState(aiReady);
  const [job, setJob] = useState<BatchJob | null>(null);
  const [starting, setStarting] = useState(false);

  const running = job?.status === "queued" || job?.status === "running";

  // Sync defaults each time the dialog opens (unless a job is in flight).
  useEffect(() => {
    if (open && !running) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- reset form on open
      setKind(initialKind);
      if (!aiReady) {
        setSource("manual");
        setWithCaptions(false);
      }
    }
  }, [open, initialKind, aiReady, running]);

  // Poll while the job runs; this component stays mounted, so closing the dialog is fine.
  useEffect(() => {
    if (!job || !running) return;
    const id = window.setTimeout(async () => {
      try {
        const next = await api.getBatch(job.id);
        setJob(next);
        if (next.status === "completed" || next.status === "failed") {
          onFinished();
          const noun = KIND_LABEL[next.kind][next.items.length === 1 ? "one" : "many"];
          if (next.status === "completed") {
            toast.success(`Batch finished: ${next.items.length} ${noun.toLowerCase()}`, {
              description: next.errors.length
                ? `${next.errors.length} issue(s) reported.`
                : undefined,
            });
          } else {
            toast.error("Batch failed", { description: next.errors[0] });
          }
        }
      } catch (err) {
        toast.error("Lost track of the batch job", { description: errorText(err) });
        setJob(null);
      }
    }, POLL_MS);
    return () => window.clearTimeout(id);
  }, [job, running, onFinished]);

  async function start() {
    setStarting(true);
    try {
      const created = await api.createBatch(
        {
          ...style,
          ...timing,
          kind,
          count,
          quoteSource: source,
          quote: source === "manual" ? draft.quote : null,
          theme: draft.theme,
          author: source === "ai" ? draft.sourceAuthor : draft.author || null,
          showAuthor: draft.showAuthor,
          withCaptions,
          model: ai.model || null,
        },
        ai.apiKey || undefined,
      );
      setJob(created);
    } catch (err) {
      toast.error("Couldn't start the batch", { description: errorText(err) });
    } finally {
      setStarting(false);
    }
  }

  const progress = job ? (job.completed / Math.max(1, job.total)) * 100 : 0;
  const done = job && !running;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Layers className="size-4 text-primary" /> Batch render
          </DialogTitle>
          <DialogDescription>
            Render several {KIND_LABEL[kind].many.toLowerCase()} at once with your current design.
            Each one gets a different background.
          </DialogDescription>
        </DialogHeader>

        {job ? (
          <div className="grid gap-4">
            <div className="grid gap-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  {running && <Spinner />}
                  {job.stage}
                </span>
                <span className="text-muted-foreground tabular-nums">
                  {job.completed}/{job.total}
                </span>
              </div>
              <Progress value={progress} />
            </div>

            {job.items.length > 0 && (
              <div className="max-h-72 overflow-y-auto">
                <div className="grid grid-cols-4 gap-2 sm:grid-cols-5">
                  {job.items.map((item) => (
                    <button
                      key={item.filename}
                      type="button"
                      onClick={() => onOpenItem(item)}
                      className="overflow-hidden rounded-md ring-1 ring-foreground/10 transition hover:ring-primary"
                    >
                      <MediaThumb item={item} className="aspect-[4/5]" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {job.errors.length > 0 && (
              <ul className="grid gap-1 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-xs text-destructive">
                {job.errors.map((e) => (
                  <li key={e} className="flex gap-1.5">
                    <CircleAlert className="mt-0.5 size-3 shrink-0" /> {e}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : (
          <FieldGroup>
            <Field>
              <FieldLabel>Type</FieldLabel>
              <ToggleGroup
                type="single"
                variant="outline"
                value={kind}
                onValueChange={(v) => v && setKind(v as MediaKind)}
                className="grid w-full grid-cols-2"
              >
                <ToggleGroupItem value="video">
                  <Film /> Reels (MP4)
                </ToggleGroupItem>
                <ToggleGroupItem value="post">
                  <ImageIcon /> Posts (PNG)
                </ToggleGroupItem>
              </ToggleGroup>
            </Field>

            <Field>
              <FieldLabel>How many</FieldLabel>
              <ToggleGroup
                type="single"
                variant="outline"
                value={String(count)}
                onValueChange={(v) => v && setCount(Number(v))}
                className="grid w-full grid-cols-4"
              >
                {COUNTS.map((n) => (
                  <ToggleGroupItem key={n} value={String(n)} className="tabular-nums">
                    {n}
                  </ToggleGroupItem>
                ))}
              </ToggleGroup>
            </Field>

            <Field>
              <FieldLabel>Quotes</FieldLabel>
              <ToggleGroup
                type="single"
                variant="outline"
                value={source}
                onValueChange={(v) => v && setSource(v as "ai" | "manual")}
                className="grid w-full grid-cols-2"
              >
                <ToggleGroupItem value="ai" disabled={!aiReady}>
                  New AI quote for each
                </ToggleGroupItem>
                <ToggleGroupItem value="manual">Reuse current quote</ToggleGroupItem>
              </ToggleGroup>
              <FieldDescription>
                {source === "ai"
                  ? `Brief: ${draft.theme ?? "any theme"}${draft.sourceAuthor ? `, in the words of ${draft.sourceAuthor}` : ""}. Set it in the Quote tab.`
                  : `“${draft.quote.slice(0, 80)}${draft.quote.length > 80 ? "…" : ""}”`}
              </FieldDescription>
            </Field>

            <Field orientation="horizontal">
              <Switch
                id="batch-captions"
                checked={withCaptions}
                onCheckedChange={setWithCaptions}
                disabled={!aiReady}
              />
              <FieldLabel htmlFor="batch-captions" className="font-normal">
                Write an Instagram caption for each item
              </FieldLabel>
            </Field>
          </FieldGroup>
        )}

        <DialogFooter>
          {done ? (
            <>
              <Button variant="outline" onClick={() => setJob(null)}>
                New batch
              </Button>
              <Button onClick={() => onOpenChange(false)}>Done</Button>
            </>
          ) : running ? (
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Run in background
            </Button>
          ) : (
            <Button
              onClick={start}
              disabled={starting || (source === "manual" && !draft.quote.trim())}
            >
              {starting ? <Spinner /> : <Layers />}
              Render {count} {KIND_LABEL[kind].many.toLowerCase()}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
