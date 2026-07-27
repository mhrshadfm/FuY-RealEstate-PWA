import json
from pathlib import Path

import httpx
import jwt
from loguru import logger


class LoginManager:

    def __init__(self, config):

        self.config = config

        # ----------------------------
        # Website Config
        # ----------------------------

        website = config["website"]

        self.base_url = website["base_url"].rstrip("/")

        self.username = website["username"]

        self.password = website["password"]

        self.client_name = website.get(
            "client_name",
            "Iceberg_Web"
        )

        self.login_url = (
            f"{self.base_url}/api/account/login"
        )

        # ----------------------------
        # HTTP Client
        # ----------------------------

        self.session = httpx.Client(

            timeout=30.0,

            follow_redirects=True

        )

        # ----------------------------
        # Project Folder
        # ----------------------------

        self.root = Path(__file__).resolve().parent.parent

        self.state_dir = self.root / "state"

        self.state_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        self.token_file = (

            self.state_dir / "token.json"

        )

        # ----------------------------
        # Tokens
        # ----------------------------

        self.access_token = None

        self.refresh_token = None

        # ----------------------------
        # Default Headers
        # ----------------------------

        self.headers = {

            "Accept": "application/json",

            "Content-Type": "application/json",

            "User-Agent":
                "Mozilla/5.0",

            "Origin":
                self.base_url,

            "Referer":
                self.base_url + "/"

        }

        logger.success(

            "Login Manager Ready"

        )

    # ----------------------------------
    # Check Token Expiry
    # ----------------------------------

    def is_token_valid(self):

        if not self.access_token:

            return False

        try:

            jwt.decode(

                self.access_token,

                options={"verify_signature": False}

            )

            return True

        except jwt.ExpiredSignatureError:

            logger.warning("Token Expired")

            return False

        except Exception as e:

            logger.warning(f"Token Invalid : {e}")

            return False

    # ----------------------------------
    # Load Saved Token
    # ----------------------------------

    def load_saved_token(self):

        if not self.token_file.exists():

            logger.info("No saved token found.")

            return False

        try:

            data = json.loads(

                self.token_file.read_text(

                    encoding="utf-8"

                )

            )

            self.access_token = data.get(

                "accessToken"

            )

            self.refresh_token = data.get(

                "refreshToken"

            )

            if not self.access_token:

                return False

            # بررسی انقضای توکن قبل از استفاده
            if not self.is_token_valid():

                logger.info("Saved Token Is Expired")

                return False

            self.headers["Authorization"] = (

                f"Bearer {self.access_token}"

            )

            logger.success(

                "Saved Token Loaded"

            )

            return True

        except Exception as e:

            logger.error(

                f"Load Token Error : {e}"

            )

            return False

    # ----------------------------------
    # Save Token
    # ----------------------------------

    def save_token(self):

        try:

            data = {

                "accessToken": self.access_token,

                "refreshToken": self.refresh_token

            }

            self.token_file.write_text(

                json.dumps(

                    data,

                    ensure_ascii=False,

                    indent=4

                ),

                encoding="utf-8"

            )

            logger.success(

                "Token Saved"

            )

        except Exception as e:

            logger.error(

                f"Save Token Error : {e}"

            )

    # ----------------------------------
    # Login
    # ----------------------------------

    def login(self):

        logger.info("Logging in...")

        payload = {

            "username": self.username,

            "password": self.password,

            "client": self.client_name

        }

        try:

            response = self.session.post(

                self.login_url,

                json=payload,

                headers=self.headers

            )

            response.raise_for_status()

            result = response.json()

        except Exception as e:

            logger.error(

                f"Login Request Failed : {e}"

            )

            raise

        if not result.get("isValid", False):

            logger.error(

                f"Login Failed : {result.get('messages')}"

            )

            raise Exception("Login Failed")

        data = result["data"]

        self.access_token = data.get(

            "accessToken"

        )

        self.refresh_token = data.get(

            "refreshToken"

        )

        if not self.access_token:

            raise Exception(

                "Access Token Not Found"

            )

        self.headers["Authorization"] = (

            f"Bearer {self.access_token}"

        )

        self.save_token()

        logger.success(

            "Login Successful"

        )

        return True

    # ----------------------------------
    # Ensure Login
    # ----------------------------------

    def ensure_login(self):

        logger.info(

            "Checking Login..."

        )

        if self.load_saved_token():

            logger.success(

                "Using Saved Token"

            )

            return True

        logger.info(

            "No Valid Token. Logging In..."

        )

        return self.login()

    # ----------------------------------
    # GET Request
    # ----------------------------------

    def get(

        self,

        endpoint,

        params=None

    ):

        url = f"{self.base_url}{endpoint}"

        try:

            response = self.session.get(

                url,

                params=params,

                headers=self.headers,

                timeout=30

            )

            # اگر توکن منقضی شده باشد
            if response.status_code == 401:

                logger.warning(

                    "Access Token Expired"

                )

                self.login()

                response = self.session.get(

                    url,

                    params=params,

                    headers=self.headers,

                    timeout=30

                )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            logger.error(

                f"GET ERROR : {e}"

            )

            raise

    # ----------------------------------
    # POST Request
    # ----------------------------------

    def post(

        self,

        endpoint,

        payload=None

    ):

        if payload is None:

            payload = {}

        url = f"{self.base_url}{endpoint}"

        try:

            response = self.session.post(

                url,

                json=payload,

                headers=self.headers,

                timeout=30

            )

            # اگر AccessToken منقضی شده باشد
            if response.status_code == 401:

                logger.warning(

                    "Access Token Expired"

                )

                self.login()

                response = self.session.post(

                    url,

                    json=payload,

                    headers=self.headers,

                    timeout=30

                )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            logger.error(

                f"POST ERROR : {e}"

            )

            raise
