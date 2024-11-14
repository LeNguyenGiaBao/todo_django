import json
import logging
import re
from datetime import datetime

from django.utils.deprecation import MiddlewareMixin

EXCLUDED_PATHS = [
    re.compile(r"^/static/.*$"),  # Static files
    re.compile(r"^/admin/jsi18n/"),  # Admin JS translations
    re.compile(r"^/admin/.*/css/.*$"),  # Admin CSS files
    re.compile(r"^/admin/login/.*$"),  # Admin login page
    re.compile(r"^/api/token/.*$"),  # login
    re.compile(r"^/admin/logout/.*$"),  # Admin logout page
    re.compile(r"^/admin/password_change/.*$"),  # Admin password change page
    re.compile(r"^/admin/.*/blockedPage\.css$"),  # Specific blockedPage.css
]

logger = logging.getLogger(__name__)


class CustomLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if any(pattern.match(request.path) for pattern in EXCLUDED_PATHS):
            return

        request.start_time = datetime.now()
        logger.info("=" * 30)
        logger.info(f"{request.start_time} - Request: {request.method} {request.path}")
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type")
            if content_type:
                if "application/json" in content_type:
                    try:
                        body = json.loads(request.body)
                        logger.info(f"Body: {body}")
                    except json.JSONDecodeError:
                        logger.error("Could not decode JSON")
                        logger.info(f"Raw body: {request.body}")
                elif "multipart/form-data" in content_type:
                    logger.info(f"Multipart body: {request.POST}")
                else:
                    logger.info(f"Raw body: {request.body}")

    def process_response(self, request, response):
        if any(pattern.match(request.path) for pattern in EXCLUDED_PATHS):
            return response

        duration = datetime.now() - request.start_time
        logger.info(
            f"Response: {response.status_code} {response.reason_phrase} - Duration: {duration} - \
            User: {self.get_user(request)}"
        )
        if request.method == "GET":
            return response

        if hasattr(response, "content"):
            content = response.content.decode(encoding="utf-8", errors="ignore")
            if response.get("Content-Type", "").startswith("application/json"):
                try:
                    response_data = json.loads(content)
                    logger.info(f"Response content: {response_data}")
                except json.JSONDecodeError:
                    logger.error("Could not decode JSON response content")
                    logger.info(f"Raw response content: {content}")
            elif str(content).startswith("<!DOCTYPE html>"):
                pass
            else:
                logger.info(f"Response content: {content[:1000]}")

        return response

    def process_exception(self, request, exception):
        logger.error(f"Exception: {exception}")
        return None

    def get_user(self, request):
        if request.user.is_authenticated:
            return str(request.user)
        return "Anonymous"
