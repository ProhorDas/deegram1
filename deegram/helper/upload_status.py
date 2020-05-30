import logging
import time

from telethon.errors import MessageNotModifiedError

from deegram.utils.bot_utils import get_readable_file_size

logger = logging.getLogger(__name__)


class UploadStatus:
    def __init__(self, event, track_count: int = None, total_tracks: int = None):
        self.current = 0
        self.total = 0
        self.event = event
        self._start_time = 0.0
        self._update_time = 0.0
        self.track_count = track_count
        self.total_tracks = total_tracks

    @property
    def download_speed(self):
        return self.current / (time.time() - self._start_time)

    async def _on_upload_started(self):
        self._start_time = time.time()
        self.message = await self.event.reply("Uploading...")

    async def _on_upload_progress(self, current, total):
        self.current = current
        self.total = total
        if (time.time() - self._update_time) > 1:
            msg = ""
            if self.track_count:
                msg += f" 💿 Track {self.track_count} of {self.total_tracks}\n"
            msg += (
                f"🔼 Uploading... {(self.current / self.total):.1%}\n"
                f"⚡ Speed: {get_readable_file_size(self.download_speed)}/s"
            )
            try:
                await self.message.edit(msg)
            except MessageNotModifiedError:
                logger.debug("Message not modified")
            except ZeroDivisionError:
                logger.debug("Divided zero")
            else:
                self._update_time = time.time()

    async def _on_upload_finished(self):
        await self.message.delete()

    async def start(self):
        return await self._on_upload_started()

    async def progress(self, current, total):
        return await self._on_upload_progress(current, total)

    async def finished(self):
        return await self._on_upload_finished()