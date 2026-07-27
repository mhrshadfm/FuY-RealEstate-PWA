import json
from pathlib import Path
from loguru import logger


class StateManager:

    def __init__(self):

        # state_manager.py در ریشه پروژه است
        self.root = Path(__file__).parent

        self.state_dir = self.root / "state"

        self.state_dir.mkdir(exist_ok=True)

        self.file = self.state_dir / "properties_state.json"

        self.data = self.load()

    def load(self):

        if not self.file.exists():

            return {}

        try:

            return json.loads(

                self.file.read_text(

                    encoding="utf8"

                )

            )

        except Exception:

            return {}

    def save(self):

        self.file.write_text(

            json.dumps(

                self.data,

                ensure_ascii=False,

                indent=4

            ),

            encoding="utf8"

        )

        logger.info("State Saved")

    def exists(

        self,

        file_id

    ):

        return file_id in self.data

    def get(

        self,

        file_id

    ):

        return self.data.get(file_id)

    def update(

        self,

        property_data

    ):

        file_id = property_data["id"]

        self.data[file_id] = {

            "serial": property_data["serial"],

            "updateDate": property_data["updateDate"],

            "status": property_data["status"],

            "fileDate": property_data["fileDate"]

        }

        self.save()

    def changed(

        self,

        property_data

    ):

        file_id = property_data["id"]

        if file_id not in self.data:

            return True

        old = self.data[file_id]

        if old["updateDate"] != property_data["updateDate"]:

            return True

        if old["status"] != property_data["status"]:

            return True

        return False

    def remove(

        self,

        file_id

    ):

        if file_id in self.data:

            del self.data[file_id]

            self.save()

    def count(self):

        return len(self.data)
