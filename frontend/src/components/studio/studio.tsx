"use client";

import { Film, ImageIcon, Images, Palette, Quote } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { LibraryView } from "@/components/library/library-view";
import { MediaViewerDialog } from "@/components/library/media-viewer-dialog";
import { AppHeader, type View } from "@/components/studio/app-header";
import { BackendOffline } from "@/components/studio/backend-offline";
import { BackgroundPanel } from "@/components/studio/background-panel";
import { BatchDialog } from "@/components/studio/batch-dialog";
import { DesignPanel } from "@/components/studio/design-panel";
import {
  DEFAULT_STYLE,
  DEFAULT_TIMING,
  type Draft,
  INITIAL_DRAFT,
  KIND_LABEL,
} from "@/components/studio/defaults";
import { PreviewPanel } from "@/components/studio/preview-panel";
import { QuotePanel } from "@/components/studio/quote-panel";
import { SettingsDialog } from "@/components/studio/settings-dialog";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useAiSettings } from "@/hooks/use-ai-settings";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { api } from "@/lib/api";
import { errorText, joinCaption } from "@/lib/format";
import type {
  AppConfig,
  ComposeRequest,
  MediaItem,
  MediaKind,
  StyleSettings,
  VideoTiming,
} from "@/lib/types";

export function Studio() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setConfig(await api.config());
    } catch (err) {
      setError(errorText(err));
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data load
    void load();
  }, [load]);

  if (error) return <BackendOffline message={error} onRetry={load} />;
  if (!config) return <StudioSkeleton />;
  return <Workspace config={config} />;
}

function Workspace({ config }: { config: AppConfig }) {
  const [view, setView] = useState<View>("create");
  const [kind, setKind] = useLocalStorage<MediaKind>("instavidgen.kind", "video");
  const [style, setStyle] = useLocalStorage<StyleSettings>("instavidgen.style", DEFAULT_STYLE);
  const [timing, setTiming] = useLocalStorage<VideoTiming>("instavidgen.timing", DEFAULT_TIMING);
  const [history, setHistory] = useLocalStorage<string[]>("instavidgen.history", []);
  const [draft, setDraft] = useState<Draft>(INITIAL_DRAFT);
  const [background, setBackground] = useState<string | null>(
    () => config.backgrounds[Math.floor(Math.random() * config.backgrounds.length)]?.id ?? null,
  );
  const { settings: ai, setSettings: setAi } = useAiSettings();
  const aiReady = config.groqConfigured || Boolean(ai.apiKey);

  const [library, setLibrary] = useState<MediaItem[]>([]);
  const [libraryLoading, setLibraryLoading] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [viewing, setViewing] = useState<MediaItem | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [batchOpen, setBatchOpen] = useState(false);

  const fontIds = useMemo(() => new Set(config.fonts.map((f) => f.id)), [config.fonts]);
  // Fall back if a stored font no longer exists on the server.
  const safeStyle: StyleSettings = useMemo(
    () =>
      fontIds.has(style.fontId) ? style : { ...style, fontId: config.fonts[0]?.id ?? "default" },
    [fontIds, style, config.fonts],
  );
  const aspect =
    config.aspectRatios.find((a) => a.key === safeStyle.aspectRatio) ?? config.aspectRatios[0];

  const refreshLibrary = useCallback(async () => {
    setLibraryLoading(true);
    try {
      setLibrary(await api.listMedia());
    } catch (err) {
      toast.error("Couldn't load the library", { description: errorText(err) });
    } finally {
      setLibraryLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial data load
    void refreshLibrary();
  }, [refreshLibrary]);

  const composeRequest: ComposeRequest | null = useMemo(
    () =>
      draft.quote.trim()
        ? {
            ...safeStyle,
            quote: draft.quote.trim(),
            author: draft.showAuthor ? draft.author.trim() || null : null,
            background,
          }
        : null,
    [safeStyle, draft.quote, draft.author, draft.showAuthor, background],
  );

  const render = useCallback(async () => {
    if (!composeRequest || rendering) return;
    setRendering(true);
    const caption = draft.caption ? joinCaption(draft.caption.text, draft.caption.hashtags) : null;
    try {
      const item =
        kind === "video"
          ? await api.renderVideo({ ...composeRequest, ...timing, caption })
          : await api.renderPost({ ...composeRequest, caption });
      setLibrary((prev) => [item, ...prev]);
      setViewing(item);
      toast.success(`${KIND_LABEL[kind].one} ready`);
    } catch (err) {
      toast.error(`Couldn't render the ${KIND_LABEL[kind].one.toLowerCase()}`, {
        description: errorText(err),
      });
    } finally {
      setRendering(false);
    }
  }, [composeRequest, rendering, draft.caption, kind, timing]);

  // Ctrl/Cmd + Enter renders from anywhere in the studio.
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (view === "create" && e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        void render();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [render, view]);

  async function deleteItem(item: MediaItem) {
    try {
      await api.deleteMedia(item.kind, item.filename);
      setLibrary((prev) =>
        prev.filter((i) => !(i.kind === item.kind && i.filename === item.filename)),
      );
      setViewing(null);
      toast.success("Deleted");
    } catch (err) {
      toast.error("Couldn't delete", { description: errorText(err) });
    }
  }

  const addHistory = (quote: string) =>
    setHistory((prev) => [quote, ...prev.filter((q) => q !== quote)].slice(0, 20));

  return (
    <div className="flex min-h-dvh flex-col">
      <AppHeader
        view={view}
        onViewChange={setView}
        libraryCount={library.length}
        aiReady={aiReady}
        model={ai.model || config.defaultModel}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 py-6 sm:px-6 lg:py-8">
        {view === "create" ? (
          <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(380px,520px)] lg:gap-8">
            <Card className="py-0">
              <CardContent className="p-0">
                <Tabs defaultValue="quote" className="gap-0">
                  <div className="flex flex-wrap items-center justify-between gap-3 border-b p-3 sm:px-5">
                    <TabsList>
                      <TabsTrigger value="quote" className="px-3">
                        <Quote /> Quote
                      </TabsTrigger>
                      <TabsTrigger value="design" className="px-3">
                        <Palette /> Design
                      </TabsTrigger>
                      <TabsTrigger value="background" className="px-3">
                        <Images /> Background
                      </TabsTrigger>
                    </TabsList>
                    <ToggleGroup
                      type="single"
                      variant="outline"
                      size="sm"
                      value={kind}
                      onValueChange={(v) => v && setKind(v as MediaKind)}
                      aria-label="Output type"
                    >
                      <ToggleGroupItem value="video" className="px-3">
                        <Film /> Reel
                      </ToggleGroupItem>
                      <ToggleGroupItem value="post" className="px-3">
                        <ImageIcon /> Post
                      </ToggleGroupItem>
                    </ToggleGroup>
                  </div>
                  <div className="p-4 sm:p-6">
                    <TabsContent value="quote">
                      <QuotePanel
                        config={config}
                        draft={draft}
                        onDraftChange={(patch) => setDraft((d) => ({ ...d, ...patch }))}
                        ai={ai}
                        aiReady={aiReady}
                        onRequireAi={() => {
                          toast.info("Add a Groq API key to use AI features.");
                          setSettingsOpen(true);
                        }}
                        history={history}
                        onHistoryAdd={addHistory}
                      />
                    </TabsContent>
                    <TabsContent value="design">
                      <DesignPanel
                        config={config}
                        kind={kind}
                        style={safeStyle}
                        onStyleChange={(patch) => setStyle((s) => ({ ...s, ...patch }))}
                        timing={timing}
                        onTimingChange={(patch) => setTiming((t) => ({ ...t, ...patch }))}
                      />
                    </TabsContent>
                    <TabsContent value="background">
                      <BackgroundPanel
                        backgrounds={config.backgrounds}
                        selected={background}
                        onSelect={setBackground}
                      />
                    </TabsContent>
                  </div>
                </Tabs>
              </CardContent>
            </Card>

            <aside className="lg:sticky lg:top-24">
              <PreviewPanel
                request={composeRequest}
                aspect={aspect}
                kind={kind}
                timing={timing}
                rendering={rendering}
                onRender={render}
                onBatch={() => setBatchOpen(true)}
              />
            </aside>
          </div>
        ) : (
          <LibraryView
            items={library}
            loading={libraryLoading}
            onRefresh={refreshLibrary}
            onOpen={setViewing}
            onCreate={() => setView("create")}
          />
        )}
      </main>

      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        config={config}
        settings={ai}
        onSave={setAi}
      />
      <BatchDialog
        open={batchOpen}
        onOpenChange={setBatchOpen}
        initialKind={kind}
        draft={draft}
        style={safeStyle}
        timing={timing}
        ai={ai}
        aiReady={aiReady}
        onFinished={refreshLibrary}
        onOpenItem={setViewing}
      />
      <MediaViewerDialog
        item={viewing}
        onOpenChange={(open) => !open && setViewing(null)}
        onDelete={deleteItem}
      />
    </div>
  );
}

function StudioSkeleton() {
  return (
    <div className="mx-auto grid w-full max-w-[1400px] gap-6 px-4 py-24 sm:px-6 lg:grid-cols-[1fr_520px]">
      <Skeleton className="h-[640px] rounded-xl" />
      <Skeleton className="h-[640px] rounded-xl" />
    </div>
  );
}
