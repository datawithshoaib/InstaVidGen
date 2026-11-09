import { RefreshCw, ServerOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";

export function BackendOffline({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <main className="flex min-h-dvh items-center justify-center p-6">
      <Empty className="max-w-lg border border-dashed">
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <ServerOff />
          </EmptyMedia>
          <EmptyTitle>Can&apos;t reach the backend</EmptyTitle>
          <EmptyDescription>{message}</EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <pre className="w-full rounded-lg bg-muted px-4 py-3 text-left text-xs">
            cd backend{"\n"}uv run fastapi dev --port 8002
          </pre>
          <Button onClick={onRetry}>
            <RefreshCw /> Try again
          </Button>
        </EmptyContent>
      </Empty>
    </main>
  );
}
