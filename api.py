from loguru import logger


class AlborzAPI:

    def __init__(self, login):

        self.login = login

    # -----------------------------
    # وضعیت سیستم
    # -----------------------------

    def get_status(self):

        logger.info("Loading Status...")

        return self.login.get(
            "/api/Application/Status"
        )

    # -----------------------------
    # دریافت لیست فایل ها
    # -----------------------------

    def get_files(

        self,

        page=1,

        page_size=100

    ):

        params = {

            "pageNo": page,

            "pageSize": page_size,

            "fastSearch": "",

            "sort": "fileDateShamsi",

            "descending": "true",

            "justMine": "false",

            "justMyPublic": "false",

            "justAlborzFile": "false",

            "justSubscriber": "false",

            "justWaitingOwnership": "false"

        }

        logger.info(
            f"Loading Page {page}"
        )

        return self.login.get(

            "/api/File/List",

            params=params

        )

    # -----------------------------
    # جزئیات فایل
    # -----------------------------

    def get_file(

        self,

        file_id

    ):

        logger.info(

            f"Loading File {file_id}"

        )

        return self.login.get(

            f"/api/File/View?FileId={file_id}"

        )

    # -----------------------------
    # همه صفحات
    # -----------------------------

    def get_all_files(

        self,

        max_pages=50

    ):

        result = []

        for page in range(

            1,

            max_pages + 1

        ):

            response = self.get_files(page)

            items = response["data"]["items"]

            if not items:

                break

            result.extend(items)

            logger.info(

                f"{len(items)} Files"

            )

        return result

    # -----------------------------
    # آخرین فایل ها
    # -----------------------------

    def get_latest(

        self,

        count=30

    ):

        response = self.get_files(

            page=1,

            page_size=count

        )

        return response["data"]["items"]

    # -----------------------------
    # دریافت اطلاعات کامل
    # -----------------------------

    def get_full_file(

        self,

        file_id

    ):

        response = self.get_file(

            file_id

        )

        return response["data"]

    # -----------------------------
    # تست اتصال
    # -----------------------------

    def ping(self):

        try:

            self.get_status()

            return True

        except Exception as e:

            logger.error(e)

            return False