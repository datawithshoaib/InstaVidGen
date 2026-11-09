"use client";

import { Check, Copy, History, Sparkles, WandSparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { type Draft, NONE } from "@/components/studio/defaults";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { AiSettings } from "@/hooks/use-ai-settings";
import { useCopy } from "@/hooks/use-copy";
import { api } from "@/lib/api";
import { errorText, joinCaption } from "@/lib/format";
import type { AppConfig } from "@/lib/types";

interface QuotePanelProps {
  config: AppConfig;
  draft: Draft;
  onDraftChange: (patch: Partial<Draft>) => void;
  ai: AiSettings;
  aiReady: boolean;
  onRequireAi: () => void;
  history: string[];
  onHistoryAdd: (quote: string) => void;
}

const MAX_QUOTE = 600;

export function QuotePanel({
  config,
  draft,
  onDraftChange,
  ai,
  aiReady,
  onRequireAi,
  history,
  onHistoryAdd,
}: QuotePanelProps) {
  const [loadingQuote, setLoadingQuote] = useState(false);
  const [loadingCaption, setLoadingCaption] = useState(false);
  const quoteCopy = useCopy();
  const captionCopy = useCopy();

  async function generateQuote() {
    if (!aiReady) return onRequireAi();
    setLoadingQuote(true);
    try {
      const res = await api.generateQuote(
        {
          theme: draft.theme,
          author: draft.sourceAuthor,
          model: ai.model || null,
          avoid: history.slice(0, 15),
        },
        ai.apiKey || undefined,
      );
      onDraftChange({
        quote: res.quote,
        author: draft.sourceAuthor ?? "",
        showAuthor: Boolean(draft.sourceAuthor),
        caption: null,
      });
      onHistoryAdd(res.quote);
    } catch (err) {
      toast.error("Couldn't write a quote", { description: errorText(err) });
    } finally {
      setLoadingQuote(false);
    }
  }

  async function generateCaption() {
    if (!aiReady) return onRequireAi();
    setLoadingCaption(true);
    try {
      const res = await api.generateCaption(
        {
          quote: draft.quote,
          theme: draft.theme,
          author: draft.showAuthor ? draft.author || null : null,
          model: ai.model || null,
        },
        ai.apiKey || undefined,
      );
      onDraftChange({ caption: { text: res.caption, hashtags: res.hashtags } });
    } catch (err) {
      toast.error("Couldn't write a caption", { description: errorText(err) });
    } finally {
      setLoadingCaption(false);
    }
  }

  return (
    <div className="grid gap-6">
      {/* AI brief */}
      <section className="grid gap-4 rounded-xl border bg-muted/30 p-4">
        <div className="flex items-center gap-2 text-sm font-medium">
          <WandSparkles className="size-4 text-primary" />
          Write with AI
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field>
            <FieldLabel>Theme</FieldLabel>
            <Select
              value={draft.theme ?? NONE}
              onValueChange={(v) => onDraftChange({ theme: v === NONE ? null : v })}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={NONE}>Any theme</SelectItem>
                <SelectSeparator />
                {config.themes.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field>
            <FieldLabel>Voice</FieldLabel>
            <Select
              value={draft.sourceAuthor ?? NONE}
              onValueChange={(v) => onDraftChange({ sourceAuthor: v === NONE ? null : v })}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={NONE}>Original aphorism</SelectItem>
                <SelectSeparator />
                {config.authors.map((a) => (
                  <SelectItem key={a} value={a}>
                    {a}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
        </div>
        <Button onClick={generateQuote} disabled={loadingQuote} className="w-full">
          {loadingQuote ? <Spinner /> : <Sparkles />}
          {loadingQuote ? "Writing…" : "Generate quote"}
        </Button>
      </section>

      {/* Quote */}
      <FieldGroup>
        <Field>
          <div className="flex items-center justify-between">
            <FieldLabel htmlFor="quote">Quote</FieldLabel>
            <Button
              variant="ghost"
              size="xs"
              onClick={() => quoteCopy.copy(draft.quote)}
              disabled={!draft.quote}
            >
              {quoteCopy.copied ? <Check /> : <Copy />}
              {quoteCopy.copied ? "Copied" : "Copy"}
            </Button>
          </div>
          <Textarea
            id="quote"
            value={draft.quote}
            maxLength={MAX_QUOTE}
            onChange={(e) => onDraftChange({ quote: e.target.value, caption: null })}
            placeholder="Type a quote, or generate one above…"
            className="min-h-28 font-display text-xl leading-snug md:text-xl"
          />
          <FieldDescription className="flex justify-between">
            <span>Short lines read best. Press Enter for a manual line break.</span>
            <span className="tabular-nums">
              {draft.quote.length}/{MAX_QUOTE}
            </span>
          </FieldDescription>
        </Field>

        <div className="flex items-end gap-3">
          <Field className="flex-1">
            <FieldLabel htmlFor="author">Attribution</FieldLabel>
            <Input
              id="author"
              value={draft.author}
              maxLength={80}
              placeholder="e.g. Seneca"
              onChange={(e) => onDraftChange({ author: e.target.value })}
              disabled={!draft.showAuthor}
            />
          </Field>
          <label className="flex h-9 items-center gap-2 text-sm text-muted-foreground">
            <Switch
              checked={draft.showAuthor}
              onCheckedChange={(checked) => onDraftChange({ showAuthor: checked })}
            />
            Show
          </label>
        </div>
      </FieldGroup>

      {history.length > 0 && (
        <section className="grid gap-2">
          <p className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <History className="size-3.5" /> Recent quotes
          </p>
          <div className="grid max-h-40 gap-1 overflow-y-auto pr-1">
            {history.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => onDraftChange({ quote: q, caption: null })}
                className="truncate rounded-md px-2.5 py-1.5 text-left text-sm text-muted-foreground transition hover:bg-muted hover:text-foreground aria-[current=true]:bg-accent aria-[current=true]:text-foreground"
                aria-current={q === draft.quote}
              >
                “{q}”
              </button>
            ))}
          </div>
        </section>
      )}

      <Separator />

      {/* Caption */}
      <section className="grid gap-3">
        <div className="flex items-center justify-between gap-2">
          <div>
            <p className="text-sm font-medium">Instagram caption</p>
            <p className="text-xs text-muted-foreground">Saved with every render.</p>
          </div>
          <div className="flex gap-1.5">
            {draft.caption && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Copy caption"
                    onClick={() =>
                      captionCopy.copy(joinCaption(draft.caption!.text, draft.caption!.hashtags))
                    }
                  >
                    {captionCopy.copied ? <Check /> : <Copy />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Copy caption + hashtags</TooltipContent>
              </Tooltip>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={generateCaption}
              disabled={loadingCaption || !draft.quote.trim()}
            >
              {loadingCaption ? <Spinner /> : <Sparkles />}
              {draft.caption ? "Rewrite" : "Generate"}
            </Button>
          </div>
        </div>

        {draft.caption ? (
          <div className="grid gap-3 rounded-xl border bg-muted/30 p-3">
            <Textarea
              value={draft.caption.text}
              onChange={(e) =>
                onDraftChange({ caption: { ...draft.caption!, text: e.target.value } })
              }
              className="min-h-24 border-0 bg-transparent p-0 shadow-none focus-visible:ring-0 dark:bg-transparent"
            />
            <div className="flex flex-wrap gap-1.5">
              {draft.caption.hashtags.map((tag) => (
                <Badge key={tag} variant="secondary" className="font-normal">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        ) : (
          <p className="rounded-xl border border-dashed p-4 text-center text-xs text-muted-foreground">
            Generate a caption and hashtags that match this quote.
          </p>
        )}
      </section>
    </div>
  );
}
