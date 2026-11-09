"use client";

import { useLocalStorage } from "@/hooks/use-local-storage";

export interface AiSettings {
  /** Optional personal Groq key; the server's GROQ_API_KEY is used when empty. */
  apiKey: string;
  /** Empty string means "use the server default model". */
  model: string;
}

export function useAiSettings() {
  const [settings, setSettings] = useLocalStorage<AiSettings>("instavidgen.ai", {
    apiKey: "",
    model: "",
  });
  return { settings, setSettings };
}
