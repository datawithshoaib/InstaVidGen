"use client";

import { Check, Copy, Download, Trash2 } from "lucide-react";

import { KIND_LABEL } from "@/components/studio/defaults";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { useCopy } from "@/hooks/use-copy";
import { mediaUrl } from "@/lib/api";
import { formatBytes, formatRelativeTime } from "@/lib/format";
import type { MediaItem } from "@/lib/types";

interface MediaViewerDialogProps {
  item: MediaItem | null;
  onOpenChange: (open: boolean) => void;
  onDelete: (item: MediaItem) => void;
}

export function MediaViewerDialog({ item, onOpenChange, onDelete }: MediaViewerDialogProps) {
  const captionCopy = useCopy();
  const quoteCopy = useCopy();

  return (
    <Dialog open={item !== null} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92dvh] overflow-y-auto p-0 sm:max-w-4xl">
        {item && (
          <div className="grid md:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
            <div className="flex items-center justify-center bg-black md:rounded-l-xl">
              {item.kind === "video" ? (
                <video
                  key={item.url}
                  src={mediaUrl(item.url)}
                  controls
                  autoPlay
                  loop
                  playsInline
                  className="max-h-[80dvh] w-full object-contain"
                />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element -- served by FastAPI
                <img
                  src={mediaUrl(item.url)}
                  alt={item.quote ?? item.filename}
                  className="max-h-[80dvh] w-full object-contain"
                />
              )}
            </div>

            <div className="grid content-start gap-5 p-6">
              <div className="grid gap-1.5">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{KIND_LABEL[item.kind].one}</Badge>
                  {item.aspectRatio && <Badge variant="outline">{item.aspectRatio}</Badge>}
                </div>
                <DialogTitle className="sr-only">{item.filename}</DialogTitle>
                <DialogDescription className="text-xs">
                  {item.width && item.height ? `${item.width}×${item.height} · ` : ""}
                  {item.duration ? `${item.duration}s · ` : ""}
                  {formatBytes(item.sizeBytes)} · {formatRelativeTime(item.createdAt)}
                </DialogDescription>
              </div>

              {item.quote && (
                <blockquote className="group relative grid gap-1">
                  <p className="font-display text-2xl leading-snug">“{item.quote}”</p>
                  {item.author && <p className="text-sm text-muted-foreground">— {item.author}</p>}
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    aria-label="Copy quote"
                    className="absolute -top-1 -right-1 opacity-0 group-hover:opacity-100"
                    onClick={() => quoteCopy.copy(item.quote!)}
                  >
                    {quoteCopy.copied ? <Check /> : <Copy />}
                  </Button>
                </blockquote>
              )}

              {item.caption && (
                <div className="grid gap-2">
                  <Separator />
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-medium text-muted-foreground">Caption</p>
                    <Button
                      variant="ghost"
                      size="xs"
                      onClick={() => captionCopy.copy(item.caption!)}
                    >
                      {captionCopy.copied ? <Check /> : <Copy />}
                      {captionCopy.copied ? "Copied" : "Copy"}
                    </Button>
                  </div>
                  <p className="max-h-48 overflow-y-auto text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground">
                    {item.caption}
                  </p>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <Button asChild className="flex-1">
                  <a href={mediaUrl(item.url)} download={item.filename}>
                    <Download /> Download {KIND_LABEL[item.kind].file}
                  </a>
                </Button>
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="icon" aria-label="Delete">
                      <Trash2 />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>
                        Delete this {KIND_LABEL[item.kind].one.toLowerCase()}?
                      </AlertDialogTitle>
                      <AlertDialogDescription>
                        The file is removed from the server. This can&apos;t be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction variant="destructive" onClick={() => onDelete(item)}>
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
