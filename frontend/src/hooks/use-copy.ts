"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";

export function useCopy(timeoutMs = 1800) {
  const [copied, setCopied] = useState(false);
  const copy = useCallback(
    async (text: string) => {
      try {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        window.setTimeout(() => setCopied(false), timeoutMs);
      } catch {
        toast.error("Could not access the clipboard.");
      }
    },
    [timeoutMs],
  );
  return { copied, copy };
}
