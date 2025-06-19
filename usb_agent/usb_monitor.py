import os
import time
import socket
from datetime import datetime
from pathlib import Path
import getpass
import psutil
import win32file
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import RPI_ALERT_FOLDER, RPI_SAFE_FOLDER, CHECK_INTERVAL
from .log_utils import setup_logger
from .ai_utils import is_sensitive
from .remote import request_approval
from .ocr_utils import extract_text


class USBEventHandler(FileSystemEventHandler):
    def __init__(self, drive: str, logger):
        super().__init__()
        self.drive = drive
        self.logger = logger

    def process_file(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        info = {
            "user": getpass.getuser(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "hostname": socket.gethostname(),
            "path": file_path,
            "time": datetime.utcnow().isoformat(),
        }
        if ext in [".txt", ".doc", ".docx", ".ppt", ".pptx"]:
            text = extract_document_text(file_path)
            if text and is_sensitive(text):
                approved = request_approval(info)
                if approved:
                    copy_to_rpi(file_path, RPI_ALERT_FOLDER)
                else:
                    os.remove(file_path)
                    self.logger.info("Removed sensitive file %s", file_path)
                    return
        elif ext in [".zip", ".rar"]:
            approved = request_approval(info)
            if not approved:
                os.remove(file_path)
                self.logger.info("Removed archive %s without approval", file_path)
                return
        elif ext in [".jpg", ".jpeg", ".png"]:
            text = extract_text(file_path)
            if text and is_sensitive(text):
                approved = request_approval(info)
                if approved:
                    copy_to_rpi(file_path, RPI_ALERT_FOLDER)
                else:
                    os.remove(file_path)
                    self.logger.info("Removed sensitive image %s", file_path)
                    return
        self.logger.info("File %s processed", file_path)
        copy_to_rpi(file_path, RPI_SAFE_FOLDER)

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)


class USBMonitor:
    def __init__(self):
        self.observers = {}
        self.logger = setup_logger("usb", "logs/usb.log")

    def poll_drives(self):
        while True:
            current_drives = self.get_usb_drives()
            for drive in list(self.observers.keys()):
                if drive not in current_drives:
                    self.observers[drive].stop()
                    self.observers[drive].join()
                    del self.observers[drive]
                    self.logger.info("USB removed: %s", drive)

            for drive in current_drives:
                if drive not in self.observers:
                    handler = USBEventHandler(drive, self.logger)
                    observer = Observer()
                    observer.schedule(handler, drive, recursive=True)
                    observer.start()
                    self.observers[drive] = observer
                    self.logger.info("USB inserted: %s", drive)
            time.sleep(CHECK_INTERVAL)

    @staticmethod
    def get_usb_drives():
        drives = []
        for part in psutil.disk_partitions(all=False):
            if win32file.GetDriveType(part.device) == win32file.DRIVE_REMOVABLE:
                drives.append(part.device)
        return drives


def extract_document_text(path: str):
    ext = Path(path).suffix.lower()
    try:
        if ext == ".txt":
            return Path(path).read_text(errors="ignore")
        elif ext in [".docx", ".pptx"]:
            import zipfile
            with zipfile.ZipFile(path) as z:
                texts = []
                for name in z.namelist():
                    if name.endswith(".xml"):
                        with z.open(name) as f:
                            texts.append(f.read().decode(errors="ignore"))
                return "\n".join(texts)
    except Exception:
        return None
    return None


def copy_to_rpi(src: str, dst_folder: str):
    try:
        Path(dst_folder).mkdir(parents=True, exist_ok=True)
        dst = Path(dst_folder) / Path(src).name
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())
    except Exception:
        pass
