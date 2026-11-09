"use client";

import {
  AlignVerticalJustifyCenter,
  AlignVerticalJustifyEnd,
  AlignVerticalJustifyStart,
  RotateCcw,
} from "lucide-react";
import { useMemo } from "react";

import { DEFAULT_STYLE, DEFAULT_TIMING } from "@/components/studio/defaults";
import { Button } from "@/components/ui/button";
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldSeparator,
} from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import type {
  AppConfig,
  AspectRatio,
  MediaKind,
  Placement,
  StyleSettings,
  VideoTiming,
} from "@/lib/types";
import { cn } from "@/lib/utils";

interface DesignPanelProps {
  config: AppConfig;
  kind: MediaKind;
  style: StyleSettings;
  onStyleChange: (patch: Partial<StyleSettings>) => void;
  timing: VideoTiming;
  onTimingChange: (patch: Partial<VideoTiming>) => void;
}

const PLACEMENT_ICONS: Record<Placement, typeof AlignVerticalJustifyCenter> = {
  top: AlignVerticalJustifyStart,
  center: AlignVerticalJustifyCenter,
  bottom: AlignVerticalJustifyEnd,
};

export function DesignPanel({
  config,
  kind,
  style,
  onStyleChange,
  timing,
  onTimingChange,
}: DesignPanelProps) {
  const fontsByFamily = useMemo(() => {
    const groups = new Map<string, AppConfig["fonts"]>();
    for (const font of config.fonts) {
      groups.set(font.family, [...(groups.get(font.family) ?? []), font]);
    }
    return [...groups.entries()];
  }, [config.fonts]);

  return (
    <FieldGroup>
      <Field>
        <FieldLabel>Format</FieldLabel>
        <ToggleGroup
          type="single"
          value={style.aspectRatio}
          onValueChange={(v) => v && onStyleChange({ aspectRatio: v as AspectRatio })}
          variant="outline"
          spacing={2}
          className="grid w-full grid-cols-5"
        >
          {config.aspectRatios.map((a) => {
            const scale = 22 / Math.max(a.width, a.height);
            return (
              <ToggleGroupItem
                key={a.key}
                value={a.key}
                aria-label={`${a.key} ${a.label}`}
                className="flex h-auto flex-col gap-1.5 py-2.5"
              >
                <span
                  className="rounded-[3px] border-[1.5px] border-current opacity-80"
                  style={{ width: a.width * scale, height: a.height * scale }}
                />
                <span className="text-xs font-semibold">{a.key}</span>
                <span className="hidden text-[10px] font-normal text-muted-foreground sm:block">
                  {a.label}
                </span>
              </ToggleGroupItem>
            );
          })}
        </ToggleGroup>
      </Field>

      <div className="grid gap-4 sm:grid-cols-[1fr_auto]">
        <Field>
          <FieldLabel>Font</FieldLabel>
          <Select value={style.fontId} onValueChange={(v) => onStyleChange({ fontId: v })}>
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {fontsByFamily.map(([family, fonts]) => (
                <SelectGroup key={family}>
                  <SelectLabel>{family}</SelectLabel>
                  {fonts.map((f) => (
                    <SelectItem key={f.id} value={f.id}>
                      {f.name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              ))}
            </SelectContent>
          </Select>
        </Field>
        <Field>
          <FieldLabel>Position</FieldLabel>
          <ToggleGroup
            type="single"
            value={style.placement}
            onValueChange={(v) => v && onStyleChange({ placement: v as Placement })}
            variant="outline"
          >
            {config.placements.map((p) => {
              const Icon = PLACEMENT_ICONS[p];
              return (
                <ToggleGroupItem key={p} value={p} aria-label={p} className="px-3 capitalize">
                  <Icon />
                </ToggleGroupItem>
              );
            })}
          </ToggleGroup>
        </Field>
      </div>

      <RangeField
        label="Text size"
        value={style.fontScale}
        display={`${style.fontScale.toFixed(1)}%`}
        min={2}
        max={10}
        step={0.5}
        onChange={(v) => onStyleChange({ fontScale: v })}
        hint="Long quotes shrink automatically to fit."
      />
      <RangeField
        label="Background dim"
        value={style.overlay}
        display={`${style.overlay}%`}
        min={0}
        max={85}
        step={5}
        onChange={(v) => onStyleChange({ overlay: v })}
        hint="Darken the image so the text stands out."
      />

      <div className={cn("grid gap-6", kind !== "video" && "hidden")}>
        <FieldSeparator>Reel timing</FieldSeparator>
        <RangeField
          label="Length"
          value={timing.duration}
          display={`${timing.duration}s`}
          min={3}
          max={30}
          step={1}
          onChange={(v) =>
            onTimingChange({
              duration: v,
              fadeIn: Math.min(timing.fadeIn, v - timing.fadeOut),
            })
          }
        />
        <div className="grid gap-6 sm:grid-cols-2">
          <RangeField
            label="Fade in"
            value={timing.fadeIn}
            display={`${timing.fadeIn.toFixed(1)}s`}
            min={0}
            max={Math.min(5, timing.duration - timing.fadeOut)}
            step={0.1}
            onChange={(v) => onTimingChange({ fadeIn: v })}
          />
          <RangeField
            label="Fade out"
            value={timing.fadeOut}
            display={`${timing.fadeOut.toFixed(1)}s`}
            min={0}
            max={Math.min(5, timing.duration - timing.fadeIn)}
            step={0.1}
            onChange={(v) => onTimingChange({ fadeOut: v })}
          />
        </div>
      </div>

      <Button
        variant="ghost"
        size="sm"
        className="justify-self-start text-muted-foreground"
        onClick={() => {
          onStyleChange(DEFAULT_STYLE);
          onTimingChange(DEFAULT_TIMING);
        }}
      >
        <RotateCcw /> Reset design
      </Button>
    </FieldGroup>
  );
}

interface RangeFieldProps {
  label: string;
  value: number;
  display: string;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  hint?: string;
}

function RangeField({ label, value, display, min, max, step, onChange, hint }: RangeFieldProps) {
  return (
    <Field>
      <div className="flex items-center justify-between">
        <FieldLabel>{label}</FieldLabel>
        <span className="text-xs font-medium text-primary tabular-nums">{display}</span>
      </div>
      <Slider
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={([v]) => onChange(Number(v.toFixed(2)))}
      />
      {hint && <FieldDescription>{hint}</FieldDescription>}
    </Field>
  );
}
