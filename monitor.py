import time

from loguru import logger

from auth.login import LoginManager
from api import AlborzAPI
from file_parser import FileParser
from storage import Storage
from state_manager import StateManager
from git_sync import GitSync


class Monitor:

    def __init__(self, config):

        self.config = config

        self.login = LoginManager(config)

        self.api = AlborzAPI(self.login)

        self.parser = FileParser()

        self.storage = Storage(config)

        self.state = StateManager()

        self.git = GitSync(config)

        self.interval = (
            config["monitor"]["interval_minutes"] * 60
        )

        self.max_pages = config["monitor"].get(
            "max_pages",
            100
        )

        self.stop_when_last_serial_found = config["monitor"].get(
            "stop_when_last_serial_found",
            True
        )

    # ----------------------------------
    # شروع مانیتور
    # ----------------------------------

    def start(self):

        logger.success(
            "Alborz Monitor Started"
        )

        while True:

            try:

                self.login.ensure_login()

                self.scan()

            except Exception as e:

                logger.exception(e)

            logger.info(

                f"Sleep {self.interval} Seconds"

            )

            time.sleep(self.interval)

    # ----------------------------------
    # اجرای یکبار
    # ----------------------------------

    def run_once(self):

        self.login.ensure_login()

        self.scan()

    # ----------------------------------
    # تست اتصال
    # ----------------------------------

    def test(self):

        self.login.ensure_login()

        if self.api.ping():

            logger.success(
                "API Connected"
            )

        else:

            logger.error(
                "API Failed"
            )

    # ----------------------------------
    # اسکن سایت
    # ----------------------------------

    def scan(self):

        logger.info("Scanning Website...")

        last_serial = self.storage.load_last_serial()

        newest_serial = last_serial

        need_git_push = False

        stop = False

        page = 1

        while page <= self.max_pages:

            logger.info(f"Loading Page {page}")

            response = self.api.get_files(

                page=page,

                page_size=100

            )

            if not response:

                logger.error(

                    "Empty Response"

                )

                break

            items = response["data"]["items"]

            if len(items) == 0:

                logger.info(

                    "No More Pages"

                )

                break

            for item in items:

                serial = item["serial"]

                file_id = item["id"]

                # ------------------------
                # فایل قدیمی — بررسی تغییر قبل از stop
                # ------------------------

                if serial <= last_serial:

                    # اگر فایل قبلاً دیده شده و تغییر نکرده
                    if self.stop_when_last_serial_found and self.state.exists(file_id):

                        # بررسی آخرین وضعیت قبل از توقف
                        full = self.api.get_full_file(file_id)

                        if full:

                            parsed = self.parser.parse(full)

                            if self.state.changed(parsed):

                                logger.success(

                                    f"Old File Changed : {serial}"

                                )

                                self.storage.add_property(parsed)

                                self.state.update(parsed)

                                need_git_push = True

                        stop = True

                        break

                logger.info(

                    f"Checking {serial}"

                )

                # ------------------------
                # دریافت جزئیات
                # ------------------------

                full = self.api.get_full_file(

                    file_id

                )

                if not full:

                    logger.warning(

                        f"Skip {serial}"

                    )

                    continue

                parsed = self.parser.parse(

                    full

                )

                # ------------------------
                # تغییر کرده؟
                # ------------------------

                if self.state.changed(parsed):

                    logger.success(

                        f"Changed : {serial}"

                    )

                    self.storage.add_property(

                        parsed

                    )

                    self.state.update(

                        parsed

                    )

                    need_git_push = True

                else:

                    logger.info(

                        f"No Change : {serial}"

                    )

                # ------------------------
                # آخرین سریال
                # ------------------------

                if serial > newest_serial:

                    newest_serial = serial

            if stop:

                logger.info(

                    "Reached Old Files"

                )

                break

            page += 1

        # ------------------------
        # ذخیره آخرین سریال
        # ------------------------

        if newest_serial > last_serial:

            self.storage.save_last_serial(

                newest_serial

            )

            logger.success(

                f"Last Serial Saved : {newest_serial}"

            )

        else:

            logger.info(

                "No New Serial"

            )

        # ------------------------
        # Git Sync
        # ------------------------

        if need_git_push:

            logger.success(

                "Start Git Sync"

            )

            self.git.push()

        else:

            logger.info(

                "Nothing Changed"

            )

        logger.success(

            "Scan Finished"

        )

    # ----------------------------------
    # دریافت همه فایل های جدید
    # ----------------------------------

    def scan_all(self):

        try:

            self.login.ensure_login()

            self.scan()

        except Exception as e:

            logger.exception(e)

    # ----------------------------------
    # دریافت یک فایل
    # ----------------------------------

    def fetch_one(self, file_id):

        try:

            full = self.api.get_full_file(file_id)

            if not full:

                return False

            parsed = self.parser.parse(full)

            self.storage.add_property(parsed)

            self.state.update(parsed)

            return True

        except Exception as e:

            logger.exception(e)

            return False

    # ----------------------------------
    # همگام سازی Git
    # ----------------------------------

    def sync_git(self):

        try:

            self.git.push()

        except Exception as e:

            logger.exception(e)

    # ----------------------------------
    # بررسی Login
    # ----------------------------------

    def ensure_login(self):

        try:

            self.login.ensure_login()

        except Exception as e:

            logger.exception(e)

            raise

    # ----------------------------------
    # وضعیت برنامه
    # ----------------------------------

    def status(self):

        logger.info(

            f"Saved Files : {self.state.count()}"

        )

        logger.info(

            f"Interval : {self.interval}"

        )

        logger.info(

            f"Max Pages : {self.max_pages}"

        )
