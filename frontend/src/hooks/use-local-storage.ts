"use client";

import { useCallback, useEffect, useState } from "react";

/** useState persisted to localStorage. Reads after mount to stay hydration-safe. */
export function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(initial);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(key);
      // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time hydration from storage
      if (raw !== null) setValue(JSON.parse(raw) as T);
    } catch {
      // Storage unavailable or corrupt: keep the initial value.
    }
    setLoaded(true);
  }, [key]);

  const update = useCallback(
    (next: T | ((prev: T) => T)) => {
      setValue((prev) => {
        const resolved = next instanceof Function ? next(prev) : next;
        try {
          window.localStorage.setItem(key, JSON.stringify(resolved));
        } catch {
          // Ignore quota / privacy-mode errors.
        }
        return resolved;
      });
    },
    [key],
  );

  return [value, update, loaded] as const;
}
