"""Generated media on disk (videos and posts), each with a JSON metadata sidecar."""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from app.core.catalog import MediaKind
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.schemas.media import MediaItem, MediaStats
from app.services.media.assets import safe_child

SUFFIX = {MediaKind.VIDEO: ".mp4", MediaKind.POST: ".png"}
URL_PREFIX = {MediaKind.VIDEO: "/media/videos", MediaKind.POST: "/media/posts"}

_SLUG = re.compile(r"[^A-Za-z0-9]+")


class MediaLibrary:
    def __init__(self, settings: Settings) -> None:
        self._dirs = {MediaKind.VIDEO: settings.videos_dir, MediaKind.POST: settings.posts_dir}

    def directory(self, kind: MediaKind) -> Path:
        return self._dirs[kind]

    def new_path(self, kind: MediaKind, background_name: str, aspect_ratio: str) -> Path:
        slug = _SLUG.sub("-", background_name).strip("-").lower()[:32] or "quote"
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        aspect = aspect_ratio.replace(":", "x")
        name = f"{slug}_{aspect}_{stamp}_{uuid.uuid4().hex[:6]}{SUFFIX[kind]}"
        return self.directory(kind) / name

    def save_metadata(self, path: Path, metadata: dict) -> None:
        sidecar = path.with_name(path.name + ".json")
        sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def item(self, kind: MediaKind, path: Path) -> MediaItem:
        stat = path.stat()
        metadata: dict = {}
        sidecar = path.with_name(path.name + ".json")
        if sidecar.exists():
            try:
                metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                metadata = {}
        known = MediaItem.model_fields.keys()
        return MediaItem(
            kind=kind,
            filename=path.name,
            url=f"{URL_PREFIX[kind]}/{path.name}",
            size_bytes=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_mtime),
            **{k: v for k, v in metadata.items() if k in known},
        )

    def list(self, kind: MediaKind | None = None) -> list[MediaItem]:
        kinds = [kind] if kind else list(MediaKind)
        items = [
            self.item(k, p)
            for k in kinds
            if self.directory(k).is_dir()
            for p in self.directory(k).glob(f"*{SUFFIX[k]}")
        ]
        return sorted(items, key=lambda i: i.created_at, reverse=True)

    def stats(self) -> MediaStats:
        def count(kind: MediaKind) -> int:
            directory = self.directory(kind)
            return sum(1 for _ in directory.glob(f"*{SUFFIX[kind]}")) if directory.is_dir() else 0

        return MediaStats(videos=count(MediaKind.VIDEO), posts=count(MediaKind.POST))

    def delete(self, kind: MediaKind, filename: str) -> None:
        path = safe_child(self.directory(kind), filename)
        if path.suffix != SUFFIX[kind] or not path.is_file():
            raise NotFoundError(f"{kind.value.title()} '{filename}' not found.")
        path.unlink()
        path.with_name(path.name + ".json").unlink(missing_ok=True)
