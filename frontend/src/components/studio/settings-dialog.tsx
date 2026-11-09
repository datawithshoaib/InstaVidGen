"use client";

import { ExternalLink, KeyRound } from "lucide-react";
import { useState } from "react";

import { NONE } from "@/components/studio/defaults";
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
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AiSettings } from "@/hooks/use-ai-settings";
import type { AppConfig } from "@/lib/types";

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  config: AppConfig;
  settings: AiSettings;
  onSave: (settings: AiSettings) => void;
}

export function SettingsDialog({ open, onOpenChange, ...rest }: SettingsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        {/* Remount the form on open so it starts from the saved settings. */}
        {open && <SettingsForm {...rest} onDone={() => onOpenChange(false)} />}
      </DialogContent>
    </Dialog>
  );
}

function SettingsForm({
  config,
  settings,
  onSave,
  onDone,
}: Omit<SettingsDialogProps, "open" | "onOpenChange"> & { onDone: () => void }) {
  const [apiKey, setApiKey] = useState(settings.apiKey);
  const [model, setModel] = useState(settings.model || NONE);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSave({ apiKey: apiKey.trim(), model: model === NONE ? "" : model });
        onDone();
      }}
      className="grid gap-6"
    >
      <DialogHeader>
        <DialogTitle>AI settings</DialogTitle>
        <DialogDescription>
          Quotes and captions are written by models on Groq, through LangChain and LangGraph.
        </DialogDescription>
      </DialogHeader>

      <FieldGroup>
        <Field>
          <FieldLabel htmlFor="groq-key">
            <KeyRound className="size-3.5" /> Groq API key
          </FieldLabel>
          <Input
            id="groq-key"
            type="password"
            autoComplete="off"
            placeholder={config.groqConfigured ? "Using the server key" : "gsk_…"}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <FieldDescription>
            {config.groqConfigured
              ? "The server already has a key. Add one here only to use your own."
              : "Stored in this browser only and sent with AI requests."}{" "}
            <a
              href="https://console.groq.com/keys"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-0.5 text-primary hover:underline"
            >
              Get a key <ExternalLink className="size-3" />
            </a>
          </FieldDescription>
        </Field>

        <Field>
          <FieldLabel>Model</FieldLabel>
          <Select value={model} onValueChange={setModel}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={NONE}>Server default ({config.defaultModel})</SelectItem>
              {config.models.map((m) => (
                <SelectItem key={m} value={m}>
                  {m}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
      </FieldGroup>

      <DialogFooter>
        <Button type="submit">Save</Button>
      </DialogFooter>
    </form>
  );
}
