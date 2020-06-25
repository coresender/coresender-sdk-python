__all__ = ["BodyType", "SendEmail"]

import enum
from typing import List, Dict

from .core import CoresenderApiRequest, LoginMethod
from .. import responses
from .. import errors


class BodyType(enum.Enum):
    text = 'text'
    html = 'html'


class SendEmail(CoresenderApiRequest):
    _api_version: str = '1'
    _api_method: str = 'POST'
    _api_method_uri: str = 'send_email'
    _login_required: bool = True
    _login_method: LoginMethod = LoginMethod.api_key

    def __init__(self):
        self._emails = []

    def _validate_email(self, email: dict):
        if not email['from']['email']:
            raise errors.CoresenderError('No sender address specified')
        if not email['to'][0]['email']:
            raise errors.CoresenderError('No recipient address specified')

    def add_to_batch(self,
        from_email: str, from_name: str = None,
        to: List[Dict[str, str]] = None,
        to_email: str = None, to_name: str = None,
        subject: str = None, body_html: str = None, body_text: str = None,
        reply_to: List[Dict[str, str]] = None,
        reply_to_email: str = None, reply_to_name: str = None,
        custom_id: str = None, custom_id_unique: bool = False,
        track_opens: bool = False, track_click: bool = False,
        list_id: str = None, list_unsubscribe: str = None
    ) -> None:
        if not to:
            to = [{'email': to_email, 'name': to_name}]

        if not reply_to:
            reply_to = [{'email': reply_to_email, 'name': reply_to_name}]

        email = {
            "from": {
                "email": from_email,
                "name": from_name,
            },
            "to": to,
            "reply_to": reply_to,
            "subject": subject,
            "body": {
                "html": body_html,
                "text": body_text,
            },
            "custom_id": custom_id,
            "custom_id_unique": custom_id_unique,
            "track_opens": track_opens,
            "track_clicks": track_click,
            "list_id": list_id,
            "list_unsubscribe": list_unsubscribe,
        }

        self._validate_email(email)

        self._emails.append(email)

    async def execute(self) -> responses.SendEmail:
        if not self._emails:
            raise errors.CoresenderError("No emails scheduled to send")

        api_rsp = await self.send()

        rsp = responses.SendEmail(api_rsp.status_code, api_rsp.json())

        self._emails.clear()

        return rsp

    async def simple_email(self,
        from_email: str = None, to_email: str = None,
        subject: str = None,
        body: str = None, *, body_type: BodyType = BodyType.text
    ) -> responses.SendEmailResponse:
        email = {
            "from": {
                "email": from_email,
            },
            "to": [{'email': to_email, }],
            "subject": subject,
            "body": {
                body_type.value: body,
            },
        }
        self._validate_email(email)

        api_rsp = await self.send(data=[email])

        rsp = responses.SendEmail(api_rsp.status_code, api_rsp.json())

        return rsp.entries[0]

    def _to_json(self):
        return self._emails
