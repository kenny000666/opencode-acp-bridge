"""ACP server wrapping remote opencode serve."""
from __future__ import annotations
import logging
from collections.abc import AsyncGenerator
from typing import Any
import uvicorn
import uvicorn.config

if not hasattr(uvicorn.config, "LoopSetupType"): uvicorn.config.LoopSetupType = str
if not hasattr(uvicorn.config, "HTTPProtocolType"): uvicorn.config.HTTPProtocolType = str
if not hasattr(uvicorn.config, "WSProtocolType"): uvicorn.config.WSProtocolType = str
if not hasattr(uvicorn.config, "LifespanType"): uvicorn.config.LifespanType = str
if not hasattr(uvicorn.config, "InterfaceType"): uvicorn.config.InterfaceType = str

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from acp_sdk.server.app import create_app
from config import get_settings
from opencode_client import OpenCodeClient, OpenCodeError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("opencode_bridge.server")

server = Server()
client: OpenCodeClient | None = None
session_map: dict[str, str] = {}

async def get_or_create_opencode_session(acp_session_id: str | None, title: str | None = None) -> str:
    global session_map, client
    settings = get_settings()
    if not settings.reuse_sessions or not acp_session_id:
        return await client.create_session(title=title)
    if acp_session_id not in session_map:
        oc_session = await client.create_session(title=title)
        session_map[acp_session_id] = oc_session
    return session_map[acp_session_id]

def extract_prompt(messages: list[Message]) -> str:
    parts: list[str] = []
    for msg in messages:
        for part in msg.parts:
            content = getattr(part, "content", None) or getattr(part, "text", None)
            if content: parts.append(str(content))
    return "\n\n".join(parts).strip()

def format_response(response: dict[str, Any]) -> str:
    texts: list[str] = []
    for part in response.get("parts", []):
        if part.get("type") == "text":
            t = part.get("text", "")
            if t: texts.append(t)
    return "\n\n".join(texts).strip() if texts else "(no response)"

_s = get_settings()

@server.agent(name=_s.agent_name, description=_s.agent_description)
async def opencode_agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    global client
    if client is None: client = OpenCodeClient(get_settings())
    prompt = extract_prompt(input)
    if not prompt:
        yield MessagePart(content="No prompt provided.", content_type="text/plain"); return
    try:
        acp_sid = context.session.id if context.session and context.session.id else None
        oc_session = await get_or_create_opencode_session(acp_sid, title=prompt[:80])
        response = await client.send_message(oc_session, prompt)
        yield MessagePart(content=format_response(response), content_type="text/plain")
    except OpenCodeError as e:
        yield MessagePart(content=f"OpenCode error: {e}", content_type="text/plain")
    except Exception as e:
        logger.exception("unexpected"); yield MessagePart(content=f"Unexpected error: {e}", content_type="text/plain")

async def main():
    global client
    settings = get_settings()
    client = OpenCodeClient(settings)
    try:
        h = await client.health()
        logger.info("Connected to OpenCode %s (v%s)", settings.opencode_url, h.get("version", "?"))
    except Exception as e:
        logger.warning("OpenCode not yet reachable: %s", e)
    app = create_app(*server.agents, lifespan=server.lifespan)
    config = uvicorn.Config(app=app, host=settings.acp_host, port=settings.acp_port, log_level="info", access_log=True, headers=[("server", "acp-opencode-bridge")])
    await uvicorn.Server(config).serve()

if __name__ == "__main__":
    import asyncio; asyncio.run(main())
