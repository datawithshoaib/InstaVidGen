"""Background batch rendering with pollable progress (in-memory job store)."""

import asyncio
import logging
import random
import threading
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from app.core.catalog import MediaKind
from app.core.config import Settings
from app.core.errors import AppError, NotFoundError
from app.schemas.batch import BatchJob, BatchRequest
from app.schemas.render import PostRequest, StyleSettings, VideoRequest, VideoTiming
from app.services.ai.service import ContentAI, GeneratedContent
from app.services.media.assets import AssetLibrary
from app.services.media.renderer import RenderService

logger = logging.getLogger(__name__)

MAX_STORED_JOBS = 50


class BatchManager:
    def __init__(
        self,
        settings: Settings,
        ai: ContentAI,
        renderer: RenderService,
        assets: AssetLibrary,
    ) -> None:
        self._ai = ai
        self._renderer = renderer
        self._assets = assets
        self._jobs: OrderedDict[str, BatchJob] = OrderedDict()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=settings.batch_workers, thread_name_prefix="batch"
        )

    # ------------------------------------------------------------ public API

    def submit(self, req: BatchRequest, api_key: str | None) -> BatchJob:
        job = BatchJob(
            id=uuid.uuid4().hex[:12],
            status="queued",
            kind=req.kind,
            total=req.count,
            created_at=datetime.now(),
        )
        with self._lock:
            self._jobs[job.id] = job
            while len(self._jobs) > MAX_STORED_JOBS:
                self._jobs.popitem(last=False)
        self._executor.submit(self._run, job.id, req, api_key)
        return job.model_copy(deep=True)

    def get(self, job_id: str) -> BatchJob:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise NotFoundError("Batch job not found.")
            return job.model_copy(deep=True)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    # ------------------------------------------------------------- internals

    def _update(self, job_id: str, **changes) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None:
                for key, value in changes.items():
                    setattr(job, key, value)

    def _append(self, job_id: str, *, item=None, error: str | None = None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            if item is not None:
                job.items.append(item)
                job.completed += 1
            if error:
                job.errors.append(error)

    def _contents(self, req: BatchRequest, api_key: str | None) -> list[GeneratedContent]:
        if req.quote_source == "ai":
            return self._ai.generate_sync(
                count=req.count,
                theme=req.theme,
                author=req.author,
                with_captions=req.with_captions,
                model=req.model,
                api_key=api_key,
            )
        content = GeneratedContent(quote=req.quote or "")
        if req.with_captions:
            result = asyncio.run(
                self._ai.caption(
                    quote=content.quote,
                    theme=req.theme,
                    author=req.author,
                    model=req.model,
                    api_key=api_key,
                )
            )
            content = GeneratedContent(
                quote=content.quote, caption=result.caption, hashtags=tuple(result.hashtags)
            )
        return [content] * req.count

    def _run(self, job_id: str, req: BatchRequest, api_key: str | None) -> None:
        self._update(job_id, status="running", stage="Writing quotes")
        try:
            contents = self._contents(req, api_key)
        except AppError as exc:
            self._update(job_id, status="failed", stage=exc.message, finished_at=datetime.now())
            self._append(job_id, error=exc.message)
            return
        except Exception as exc:  # noqa: BLE001 - report any failure to the client
            logger.exception("Batch %s failed while generating content", job_id)
            self._update(job_id, status="failed", stage="Failed", finished_at=datetime.now())
            self._append(job_id, error=str(exc))
            return

        if len(contents) < req.count:
            self._append(
                job_id,
                error=f"The model produced {len(contents)} unique quotes of {req.count} requested.",
            )
            self._update(job_id, total=len(contents))

        # Spread items across distinct backgrounds before repeating any.
        backgrounds = [b.id for b in self._assets.backgrounds()]
        random.shuffle(backgrounds)
        style_fields = set(StyleSettings.model_fields) | set(VideoTiming.model_fields)
        style = req.model_dump(include=style_fields)

        for index, content in enumerate(contents):
            self._update(job_id, stage=f"Rendering {index + 1} of {len(contents)}")
            payload = {
                **style,
                "quote": content.quote,
                "author": req.author if req.show_author else None,
                "caption": content.full_caption,
                "background": backgrounds[index % len(backgrounds)] if backgrounds else None,
            }
            try:
                if req.kind is MediaKind.VIDEO:
                    item = self._renderer.video(VideoRequest(**payload))
                else:
                    item = self._renderer.post(PostRequest(**payload))
                self._append(job_id, item=item)
            except Exception as exc:  # noqa: BLE001 - keep rendering the rest
                logger.exception("Batch %s item %d failed", job_id, index + 1)
                message = exc.message if isinstance(exc, AppError) else str(exc)
                self._append(job_id, error=f"Item {index + 1}: {message}")

        job = self.get(job_id)
        self._update(
            job_id,
            status="completed" if job.items else "failed",
            stage="Done" if job.items else "No items were rendered",
            finished_at=datetime.now(),
        )
