import json
from pathlib import Path
from loguru import logger


class Storage:

    def __init__(self, config):

        self.config = config

        self.root = Path(__file__).parent

        self.daily_folder = self.root / "daily"
        self.daily_folder.mkdir(exist_ok=True)

        self.state_folder = self.root / "state"
        self.state_folder.mkdir(exist_ok=True)

        self.last_serial_file = self.state_folder / "last_serial.json"

    # -----------------------------------
    # نام فایل روز
    # -----------------------------------

    def daily_filename(self, shamsi_date):

        filename = shamsi_date.replace("/", "-")

        return self.daily_folder / f"{filename}.json"

    # -----------------------------------
    # خواندن فایل روز
    # -----------------------------------

    def load_day(self, shamsi_date):

        file = self.daily_filename(shamsi_date)

        if not file.exists():
            return []

        try:

            with open(
                file,
                "r",
                encoding="utf8"
            ) as f:

                return json.load(f)

        except Exception as e:

            logger.error(e)

            return []

    # -----------------------------------
    # ذخیره فایل روز
    # -----------------------------------

    def save_day(self, shamsi_date, data):

        file = self.daily_filename(shamsi_date)

        with open(
            file,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=False
            )

        logger.success(f"{file.name} Saved")

    # -----------------------------------
    # اضافه یا بروزرسانی ملک
    # -----------------------------------

    def add_property(self, property_data):

        shamsi = property_data["fileDate"]

        today = self.load_day(shamsi)

        updated = False

        for index, item in enumerate(today):

            if item["serial"] == property_data["serial"]:

                today[index] = property_data

                updated = True

                logger.info(
                    f"Updated Property {property_data['serial']}"
                )

                break

        if not updated:

            today.append(property_data)

            logger.info(
                f"Added Property {property_data['serial']}"
            )

        today.sort(
            key=lambda x: x["serial"],
            reverse=True
        )

        self.save_day(
            shamsi,
            today
        )

        return True

    # -----------------------------------
    # ذخیره آخرین سریال
    # -----------------------------------

    def save_last_serial(self, serial):

        with open(
            self.last_serial_file,
            "w",
            encoding="utf8"
        ) as f:

            json.dump(
                {
                    "serial": serial
                },
                f,
                ensure_ascii=False,
                indent=2
            )

    # -----------------------------------
    # خواندن آخرین سریال
    # -----------------------------------

    def load_last_serial(self):

        if not self.last_serial_file.exists():

            return 0

        try:

            with open(
                self.last_serial_file,
                "r",
                encoding="utf8"
            ) as f:

                data = json.load(f)

            return data.get("serial", 0)

        except Exception:

            return 0

    # -----------------------------------
    # تعداد فایل های روز
    # -----------------------------------

    def count(self, shamsi_date):

        return len(
            self.load_day(shamsi_date)
        )

    # -----------------------------------
    # آخرین فایل
    # -----------------------------------

    def latest(self, shamsi_date):

        data = self.load_day(shamsi_date)

        if not data:
            return None

        return max(
            data,
            key=lambda x: x["serial"]
        )

    # -----------------------------------
    # همه فایل های روز (نام تغییر یافت از all به get_all)
    # -----------------------------------

    def get_all(self, shamsi_date):

        return self.load_day(shamsi_date)

    # -----------------------------------
    # حذف فایل روز
    # -----------------------------------

    def clear_day(self, shamsi_date):

        file = self.daily_filename(shamsi_date)

        if file.exists():

            file.unlink()

            logger.warning(f"{file.name} Deleted")
