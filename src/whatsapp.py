"""WhatsApp Cloud API client.

`WhatsAppClient` is the seam: production uses `MetaWhatsAppClient`
(real HTTPS calls to graph.facebook.com); tests inject `FakeWhatsAppClient`
which records outbound messages for assertions.
"""

from __future__ import annotations

import abc


class WhatsAppClient(abc.ABC):
    @abc.abstractmethod
    def send_text(self, to: str, body: str) -> None:
        """Send a plain-text WhatsApp message to an E.164 number."""
        ...

    @abc.abstractmethod
    def send_image(self, to: str, media_ref: str, caption: str = "") -> None:
        """Send a photo message.

        media_ref is "photo:<media-id>" for a real WhatsApp upload, or
        "sample:<label>" for clearly-labeled sample/fixture data used in
        tests and local development (never presented as a real upload).
        """
        ...


class MetaWhatsAppClient(WhatsAppClient):
    def __init__(
        self,
        token: str,
        phone_number_id: str,
        api_base: str = "https://graph.facebook.com/v21.0",
        http_client=None,
    ) -> None:
        if not token or not phone_number_id:
            raise RuntimeError(
                "WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID must be set"
            )
        self._token = token
        self._url = f"{api_base}/{phone_number_id}/messages"
        self._http = http_client  # injectable for tests

    def _client(self):
        if self._http is not None:
            return self._http
        import httpx

        return httpx.Client(timeout=15.0)

    def send_text(self, to: str, body: str) -> None:
        self._post(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {"preview_url": False, "body": body},
            }
        )

    def send_image(self, to: str, media_ref: str, caption: str = "") -> None:
        if media_ref.startswith("photo:"):
            image = {"id": media_ref[len("photo:"):]}
        else:
            # "sample:..." refs have no hosted media to attach: deliver the
            # caption as text, explicitly labeled as sample data.
            label = media_ref.removeprefix("sample:")
            self.send_text(to, f"📸 [sample photo: {label}]\n{caption}")
            return
        self._post(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "image",
                "image": {**image, "caption": caption},
            }
        )

    def _post(self, payload: dict) -> None:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        client = self._client()
        close = False
        if not hasattr(client, "post"):
            raise RuntimeError("HTTP client has no post()")
        # Reuse an injected client; otherwise open/close our own.
        if self._http is None:
            close = True
        try:
            resp = client.post(self._url, json=payload, headers=headers)
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"WhatsApp API error {resp.status_code}: {resp.text[:300]}"
                )
        finally:
            if close and hasattr(client, "close"):
                client.close()


class FakeWhatsAppClient(WhatsAppClient):
    """Test double: records (to, body) instead of hitting Meta."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []
        self.images: list[tuple[str, str, str]] = []  # (to, media_ref, caption)

    def send_text(self, to: str, body: str) -> None:
        self.sent.append((to, body))

    def send_image(self, to: str, media_ref: str, caption: str = "") -> None:
        self.images.append((to, media_ref, caption))

    def last_to(self, phone: str) -> str | None:
        for to, body in reversed(self.sent):
            if to == phone:
                return body
        return None

    def clear(self) -> None:
        self.sent.clear()
        self.images.clear()
