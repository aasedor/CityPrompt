"""Consume small fixture responses through their real ASGI response lifecycle."""


async def response_bytes(response):
    chunks = []

    async def send(message):
        if message["type"] == "http.response.body":
            chunks.append(message.get("body", b""))

    async def receive():
        return {"type": "http.disconnect"}

    await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
    return b"".join(chunks)
