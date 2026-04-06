from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse, urlunparse

import httpx
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()


def normalize_ha_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return "http://homeassistant.local:8123"
    if "://" not in raw:
        raw = f"http://{raw}"
    return raw.rstrip("/")


def normalize_ma_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        raw = "ws://192.168.100.50:8095/ws"
    if "://" not in raw:
        raw = f"ws://{raw}"
    parsed = urlparse(raw)
    scheme = parsed.scheme
    if scheme == "http":
        scheme = "ws"
    elif scheme == "https":
        scheme = "wss"
    elif scheme not in ("ws", "wss"):
        scheme = "ws"

    path = parsed.path or "/ws"
    if path == "/":
        path = "/ws"
    return urlunparse((scheme, parsed.netloc, path, "", "", "")).rstrip("/")


def to_ma_base_url(ma_ws_url: str) -> str:
    parsed = urlparse(ma_ws_url)
    scheme = "https" if parsed.scheme == "wss" else "http"
    return urlunparse((scheme, parsed.netloc, "", "", "", "")).rstrip("/")


# ── Config (loaded from settings.json, env vars are first-run fallbacks) ────
_HOST = os.getenv("HOST", "0.0.0.0")
_PORT = int(os.getenv("PORT", "8000"))
_MA_COMMAND_TIMEOUT = int(os.getenv("MA_COMMAND_TIMEOUT", "10"))

# These will be overridden once settings are loaded
_HA_URL = normalize_ha_url(os.getenv("HA_URL", ""))
_HA_TOKEN = os.getenv("HA_TOKEN", "").strip()
_MA_URL = normalize_ma_url(os.getenv("MA_URL", ""))
_MA_TOKEN = os.getenv("MA_TOKEN", "").strip()


def _get_ha_config():
    return {"url": _HA_URL, "token": _HA_TOKEN}


def _get_ma_config():
    return {"url": _MA_URL, "token": _MA_TOKEN, "base_url": to_ma_base_url(_MA_URL)}


def _reload_ha_ma_from_settings(settings: dict):
    global _HA_URL, _HA_TOKEN, _MA_URL, _MA_TOKEN
    _HA_URL = normalize_ha_url(settings.get("ha_url", _HA_URL))
    _HA_TOKEN = settings.get("ha_token", _HA_TOKEN) or ""
    _MA_URL = normalize_ma_url(settings.get("ma_url", _MA_URL))
    _MA_TOKEN = settings.get("ma_token", _MA_TOKEN) or ""

app = FastAPI(title="Obsidian Hub API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HAServiceCall(BaseModel):
    domain: str
    service: str
    entity_id: Optional[str] = None
    service_data: Optional[dict[str, Any]] = None


class MACmd(BaseModel):
    command: str
    args: dict[str, Any] = Field(default_factory=dict)


ha_entities: dict[str, dict[str, Any]] = {}
ha_summary: dict[str, Any] = {}
ha_signature: dict[str, tuple[str, str, str]] = {}
ha_lock = asyncio.Lock()

ma_state: dict[str, Any] = {
    "connected": False,
    "queues": [],
    "players": [],
    "queue_player_map": {},
    "active_queue_id": None,
    "active_player_id": None,
    "ma_base_url": _get_ma_config()["base_url"],
    "refreshed_at": None,
}
ma_signature: tuple[Any, ...] = ()
ma_lock = asyncio.Lock()

active_connections: set[WebSocket] = set()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_ha_token() -> None:
    if not _HA_TOKEN:
        raise HTTPException(status_code=500, detail="HA_TOKEN is not configured")


def state_is_offline(state: Any) -> bool:
    return str(state).lower() in {"unknown", "unavailable", "none"}


def parse_number(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def choose_by_device_class(
    entities: Iterable[dict[str, Any]],
    device_class: str,
    preferred_min: Optional[float] = None,
    preferred_max: Optional[float] = None,
) -> Optional[dict[str, Any]]:
    candidates: list[tuple[float, dict[str, Any]]] = []
    for entity in entities:
        attrs = entity.get("attributes", {})
        if attrs.get("device_class") != device_class:
            continue
        value = parse_number(entity.get("state"))
        if value is None:
            continue
        candidates.append((value, entity))
    if not candidates:
        return None

    if preferred_min is not None and preferred_max is not None:
        preferred = [
            entity
            for value, entity in candidates
            if preferred_min <= value <= preferred_max
        ]
        if preferred:
            return preferred[0]

    return candidates[0][1]


def build_ha_summary(entities: list[dict[str, Any]]) -> dict[str, Any]:
    lights = [entity for entity in entities if entity["entity_id"].startswith("light.")]
    climates = [entity for entity in entities if entity["entity_id"].startswith("climate.")]
    weather_entities = [
        entity for entity in entities if entity["entity_id"].startswith("weather.")
    ]

    low_battery_count = 0
    offline_count = 0
    for entity in entities:
        state = entity.get("state")
        if state_is_offline(state):
            offline_count += 1
        attrs = entity.get("attributes", {})
        if attrs.get("device_class") == "battery":
            battery_level = parse_number(state)
            if battery_level is not None and battery_level <= 20:
                low_battery_count += 1

    temperature_entity = choose_by_device_class(
        entities, "temperature", preferred_min=5, preferred_max=45
    )
    humidity_entity = choose_by_device_class(
        entities, "humidity", preferred_min=10, preferred_max=95
    )
    weather_entity = weather_entities[0] if weather_entities else None

    summary = {
        "lights_total": len(lights),
        "lights_on": sum(1 for light in lights if light.get("state") == "on"),
        "climate_total": len(climates),
        "low_battery_count": low_battery_count,
        "offline_count": offline_count,
        "temperature": (
            parse_number(temperature_entity["state"]) if temperature_entity else None
        ),
        "humidity": parse_number(humidity_entity["state"]) if humidity_entity else None,
        "temperature_entity_id": (
            temperature_entity["entity_id"] if temperature_entity else None
        ),
        "humidity_entity_id": humidity_entity["entity_id"] if humidity_entity else None,
        "weather": None,
    }

    if weather_entity:
        weather_attrs = weather_entity.get("attributes", {})
        summary["weather"] = {
            "entity_id": weather_entity.get("entity_id"),
            "state": weather_entity.get("state"),
            "temperature": weather_attrs.get("temperature"),
            "humidity": weather_attrs.get("humidity"),
            "precipitation": weather_attrs.get("precipitation"),
            "friendly_name": weather_attrs.get("friendly_name"),
        }

    return summary


def build_ha_signature(entities: list[dict[str, Any]]) -> dict[str, tuple[str, str, str]]:
    signature: dict[str, tuple[str, str, str]] = {}
    for entity in entities:
        entity_id = entity.get("entity_id")
        if not entity_id:
            continue
        signature[entity_id] = (
            str(entity.get("state")),
            str(entity.get("last_changed")),
            str(entity.get("last_updated")),
        )
    return signature


def choose_active_queue_id(queues: list[dict[str, Any]]) -> Optional[str]:
    for queue in queues:
        if queue.get("state") in {"playing", "paused"}:
            return queue.get("queue_id")
    for queue in queues:
        if queue.get("current_item"):
            return queue.get("queue_id")
    for queue in queues:
        if queue.get("available"):
            return queue.get("queue_id")
    return queues[0].get("queue_id") if queues else None


def build_queue_player_map(
    queues: list[dict[str, Any]], players: list[dict[str, Any]]
) -> dict[str, str]:
    player_ids = {player.get("player_id") for player in players if player.get("player_id")}
    queue_ids = {queue.get("queue_id") for queue in queues if queue.get("queue_id")}
    mapping: dict[str, str] = {}

    for queue_id in queue_ids:
        if queue_id in player_ids:
            mapping[queue_id] = queue_id

    for player in players:
        player_id = player.get("player_id")
        if not player_id:
            continue
        active_source = player.get("active_source")
        if isinstance(active_source, str) and active_source in queue_ids:
            mapping[active_source] = player_id
        for source in player.get("source_list") or []:
            source_id = source.get("id")
            if isinstance(source_id, str) and source_id in queue_ids:
                mapping[source_id] = player_id

    return mapping


def choose_active_player_id(
    active_queue_id: Optional[str],
    queue_player_map: dict[str, str],
    players: list[dict[str, Any]],
) -> Optional[str]:
    if active_queue_id and active_queue_id in queue_player_map:
        return queue_player_map[active_queue_id]

    for player in players:
        if player.get("playback_state") in {"playing", "paused"}:
            return player.get("player_id")

    return players[0].get("player_id") if players else None


def build_ma_signature(state: dict[str, Any]) -> tuple[Any, ...]:
    queue_sig = tuple(
        sorted(
            (
                queue.get("queue_id"),
                queue.get("state"),
                queue.get("current_index"),
                queue.get("elapsed_time_last_updated"),
                (queue.get("current_item") or {}).get("queue_item_id"),
                queue.get("repeat_mode"),
                queue.get("shuffle_enabled"),
            )
            for queue in state.get("queues", [])
        )
    )
    player_sig = tuple(
        sorted(
            (
                player.get("player_id"),
                player.get("playback_state"),
                player.get("volume_level"),
                player.get("active_source"),
                player.get("elapsed_time_last_updated"),
            )
            for player in state.get("players", [])
        )
    )
    return (
        state.get("connected"),
        state.get("active_queue_id"),
        state.get("active_player_id"),
        queue_sig,
        player_sig,
    )


async def fetch_ha_entities_from_server() -> list[dict[str, Any]]:
    ensure_ha_token()
    headers = {
        "Authorization": f"Bearer {_HA_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{_HA_URL}/api/states", headers=headers)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise HTTPException(status_code=502, detail="Invalid HA states response")
        return data


async def call_ha_service_server(call: HAServiceCall) -> Any:
    ensure_ha_token()
    headers = {
        "Authorization": f"Bearer {_HA_TOKEN}",
        "Content-Type": "application/json",
    }
    payload: dict[str, Any] = {}
    if call.entity_id:
        payload["entity_id"] = call.entity_id
    if call.service_data:
        payload.update(call.service_data)
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"{_HA_URL}/api/services/{call.domain}/{call.service}",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()


class MusicAssistantClient:
    def __init__(self, url: str, token: str, timeout_seconds: int = 10):
        self.url = url
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.ws = None
        self.connected_event = asyncio.Event()
        self._pending: dict[str, asyncio.Future] = {}
        self._send_lock = asyncio.Lock()
        self._msg_counter = 1
        self._stopping = False

    def next_message_id(self, prefix: str = "cmd") -> str:
        message_id = f"{prefix}_{self._msg_counter}"
        self._msg_counter += 1
        return message_id

    async def run(self) -> None:
        if not self.token:
            print("[MA] MA_TOKEN is empty, MA integration disabled.")
            return

        while not self._stopping:
            try:
                async with websockets.connect(
                    self.url,
                    open_timeout=10,
                    ping_interval=20,
                    ping_timeout=20,
                ) as ws:
                    self.ws = ws
                    await self._authenticate(ws)
                    self.connected_event.set()
                    print(f"[MA] Connected: {self.url}")
                    await self._read_loop(ws)
            except Exception as exc:
                if not self._stopping:
                    print(f"[MA] Connection error: {exc}")
            finally:
                self.connected_event.clear()
                self.ws = None
                self._fail_pending(RuntimeError("MA websocket disconnected"))
                if not self._stopping:
                    await asyncio.sleep(4)

    async def close(self) -> None:
        self._stopping = True
        if self.ws:
            await self.ws.close()

    async def _authenticate(self, ws) -> None:
        hello_raw = await asyncio.wait_for(ws.recv(), timeout=10)
        hello = json.loads(hello_raw)
        if not hello.get("server_version"):
            raise RuntimeError("MA hello message missing server_version")

        auth_message_id = self.next_message_id(prefix="auth")
        await ws.send(
            json.dumps(
                {
                    "message_id": auth_message_id,
                    "command": "auth",
                    "args": {"token": self.token},
                }
            )
        )

        while True:
            auth_raw = await asyncio.wait_for(ws.recv(), timeout=10)
            auth_data = json.loads(auth_raw)
            if auth_data.get("message_id") != auth_message_id:
                continue
            authenticated = auth_data.get("result", {}).get("authenticated")
            if authenticated:
                return
            raise RuntimeError("MA auth failed")

    async def _read_loop(self, ws) -> None:
        while True:
            raw_message = await ws.recv()
            data = json.loads(raw_message)
            message_id = data.get("message_id")
            if message_id and message_id in self._pending:
                future = self._pending.get(message_id)
                if future and not future.done():
                    future.set_result(data)
                continue

            event_name = data.get("event")
            if event_name:
                await broadcast(
                    {
                        "type": "ma_event",
                        "event": event_name,
                        "data": data.get("data"),
                    }
                )

    async def send_command(self, command: str, args: Optional[dict[str, Any]] = None) -> Any:
        if not self.connected_event.is_set() or not self.ws:
            raise RuntimeError("Music Assistant is not connected")

        message_id = self.next_message_id()
        payload: dict[str, Any] = {"message_id": message_id, "command": command}
        if args is not None:
            payload["args"] = args

        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._pending[message_id] = future

        try:
            async with self._send_lock:
                if not self.ws:
                    raise RuntimeError("Music Assistant websocket is not available")
                await self.ws.send(json.dumps(payload))

            response = await asyncio.wait_for(future, timeout=self.timeout_seconds)
            if "error" in response:
                raise RuntimeError(str(response["error"]))
            return response.get("result")
        finally:
            self._pending.pop(message_id, None)

    def _fail_pending(self, error: Exception) -> None:
        for future in self._pending.values():
            if not future.done():
                future.set_exception(error)
        self._pending.clear()

    async def refresh_state(self) -> dict[str, Any]:
        queues_raw = await self.send_command("player_queues/all")
        players_raw = await self.send_command("players/all")
        queues = queues_raw if isinstance(queues_raw, list) else []
        players = players_raw if isinstance(players_raw, list) else []

        queue_player_map = build_queue_player_map(queues, players)
        active_queue_id = choose_active_queue_id(queues)
        active_player_id = choose_active_player_id(active_queue_id, queue_player_map, players)

        return {
            "connected": True,
            "queues": queues,
            "players": players,
            "queue_player_map": queue_player_map,
            "active_queue_id": active_queue_id,
            "active_player_id": active_player_id,
            "ma_base_url": _get_ma_config()["base_url"],
            "refreshed_at": utc_now_iso(),
        }


ma_client = MusicAssistantClient(_MA_URL, _MA_TOKEN, timeout_seconds=_MA_COMMAND_TIMEOUT)


async def broadcast(payload: dict[str, Any]) -> None:
    if not active_connections:
        return
    stale: list[WebSocket] = []
    for connection in list(active_connections):
        try:
            await connection.send_json(payload)
        except Exception:
            stale.append(connection)
    for connection in stale:
        active_connections.discard(connection)


async def refresh_ha_state_once() -> bool:
    global ha_entities, ha_summary, ha_signature

    entities = await fetch_ha_entities_from_server()
    signature = build_ha_signature(entities)
    summary = build_ha_summary(entities)
    changed = signature != ha_signature

    async with ha_lock:
        ha_entities = {entity["entity_id"]: entity for entity in entities}
        ha_summary = summary
        ha_signature = signature

    return changed


async def refresh_ma_state_once() -> bool:
    global ma_state, ma_signature

    if not ma_client.connected_event.is_set():
        next_state = {
            "connected": False,
            "queues": [],
            "players": [],
            "queue_player_map": {},
            "active_queue_id": None,
            "active_player_id": None,
            "ma_base_url": MA_BASE_URL,
            "refreshed_at": utc_now_iso(),
        }
    else:
        next_state = await ma_client.refresh_state()

    next_signature = build_ma_signature(next_state)
    changed = next_signature != ma_signature

    async with ma_lock:
        ma_state = next_state
        ma_signature = next_signature

    return changed


async def ha_poll_loop() -> None:
    while True:
        try:
            changed = await refresh_ha_state_once()
            if changed:
                await broadcast(
                    {
                        "type": "ha_state",
                        "entities": list(ha_entities.values()),
                        "summary": ha_summary,
                    }
                )
        except Exception as exc:
            print(f"[HA] Poll error: {exc}")
        await asyncio.sleep(max(5, current_settings.get("ha_refresh_interval", 15)))


async def ma_poll_loop() -> None:
    while True:
        try:
            changed = await refresh_ma_state_once()
            if changed:
                await broadcast({"type": "ma_state", "state": ma_state})
        except Exception as exc:
            print(f"[MA] Poll error: {exc}")
        await asyncio.sleep(max(2, current_settings.get("ma_refresh_interval", 5)))


@app.get("/api/status")
async def get_status():
    async with ha_lock:
        entity_count = len(ha_entities)
    async with ma_lock:
        current_ma_state = dict(ma_state)
    return {
        "success": True,
        "status": {
            "ha_url": _HA_URL,
            "ha_connected": entity_count > 0,
            "ha_entity_count": entity_count,
            "ma_url": _MA_URL,
            "ma_connected": bool(current_ma_state.get("connected")),
            "ws_clients": len(active_connections),
            "last_ma_refresh": current_ma_state.get("refreshed_at"),
        },
    }


@app.get("/api/ha/entities")
async def get_ha_entities(domain: Optional[str] = Query(default=None)):
    if not ha_entities:
        try:
            await refresh_ha_state_once()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    async with ha_lock:
        entities = list(ha_entities.values())
        summary = dict(ha_summary)

    if domain:
        normalized_domain = domain.strip().lower()
        entities = [
            entity
            for entity in entities
            if entity.get("entity_id", "").startswith(f"{normalized_domain}.")
        ]

    return {"success": True, "entities": entities, "summary": summary}


@app.get("/api/ha/summary")
async def get_ha_summary():
    if not ha_entities:
        try:
            await refresh_ha_state_once()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    async with ha_lock:
        summary = dict(ha_summary)
    return {"success": True, "summary": summary}


@app.post("/api/ha/service")
async def call_ha_service(call: HAServiceCall):
    try:
        result = await call_ha_service_server(call)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"HA service call failed: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    try:
        changed = await refresh_ha_state_once()
        if changed:
            await broadcast(
                {
                    "type": "ha_state",
                    "entities": list(ha_entities.values()),
                    "summary": ha_summary,
                }
            )
    except Exception as exc:
        print(f"[HA] Refresh after service call failed: {exc}")

    return {"success": True, "result": result}


@app.get("/api/ma/state")
async def get_ma_state():
    if not ma_state.get("refreshed_at"):
        try:
            await refresh_ma_state_once()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    async with ma_lock:
        snapshot = dict(ma_state)
    return {"success": True, "state": snapshot}


@app.post("/api/ma/cmd")
async def send_ma_cmd(cmd: MACmd):
    try:
        result = await ma_client.send_command(cmd.command, cmd.args)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MA command failed: {exc}") from exc

    try:
        changed = await refresh_ma_state_once()
        if changed:
            await broadcast({"type": "ma_state", "state": ma_state})
    except Exception as exc:
        print(f"[MA] Refresh after command failed: {exc}")

    return {"success": True, "result": result}


@app.get("/api/config")
async def get_config():
    """Return current HA/MA configuration (read-only, from current runtime config)."""
    return {
        "success": True,
        "config": {
            "ha_url": _HA_URL,
            "ha_token_masked": ("***" + _HA_TOKEN[-8:]) if _HA_TOKEN else "",
            "ma_url": _MA_URL,
            "ma_token_masked": ("***" + _MA_TOKEN[-8:]) if _MA_TOKEN else "",
        }
    }


@app.get("/api/settings")
async def get_settings():
    """Return current frontend-accessible settings (read-only view)."""
    return {
        "success": True,
        "settings": {
            **current_settings,
            "ha_token": _HA_TOKEN,
            "ma_token": _MA_TOKEN,
        }
    }


@app.put("/api/settings")
async def update_settings(new_settings: dict[str, Any]):
    """Update settings and persist to disk. Reloads HA/MA connections if config changed."""
    allowed = {
        "ha_url", "ha_token",
        "ma_url", "ma_token",
        "ha_refresh_interval", "ma_refresh_interval",
        "temperature_entity", "humidity_entity",
        "light_mapping", "light_positions",
        "show_sidebar", "clock_24h",
    }
    filtered = {k: v for k, v in new_settings.items() if k in allowed}
    current_settings.update(filtered)
    save_settings(current_settings)
    _reload_ha_ma_from_settings(current_settings)
    asyncio.create_task(_reload_connections())
    return {"success": True, "settings": {**current_settings, "ha_token": _HA_TOKEN, "ma_token": _MA_TOKEN}}


@app.post("/api/restart")
async def restart_service():
    """Signal service restart (reload HA/MA connections)."""
    asyncio.create_task(_reload_connections())
    return {"success": True, "message": "Restart signalled"}


async def _reload_connections():
    """Reload HA/MA state with updated settings."""
    # Update MA client config
    ma_client.url = _MA_URL
    ma_client.token = _MA_TOKEN
    # Restart MA connect loop to pick up new URL/token
    for name in ("ma_connect_task", "ma_poll_task"):
        t = getattr(app.state, name, None)
        if t:
            t.cancel()
    ma_client._stopping = False
    ma_client._pending.clear()
    ma_client.connected_event.clear()
    ma_client.ws = None
    app.state.ma_connect_task = asyncio.create_task(ma_client.run())
    app.state.ma_poll_task = asyncio.create_task(ma_poll_loop())
    try:
        await refresh_ha_state_once()
    except Exception as exc:
        print(f"[Reload] HA refresh failed: {exc}")


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)

    await websocket.send_json(
        {
            "type": "init",
            "ha_entities": list(ha_entities.values()),
            "ha_summary": ha_summary,
            "ma_state": ma_state,
        }
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.discard(websocket)


# ── Settings persistence ────────────────────────────────────────────────────────
SETTINGS_FILE = Path(__file__).parent / "settings.json"

DEFAULT_SETTINGS = {
    "ha_refresh_interval": 15,
    "ma_refresh_interval": 5,
    "temperature_entity": "",
    "humidity_entity": "",
    "ha_url": "",
    "ha_token": "",
    "ma_url": "",
    "ma_token": "",
    "light_mapping": ["", "", "", "", "", "", "", ""],
    "light_positions": [[140, 130], [240, 170], [560, 130], [660, 170],
                        [120, 350], [280, 430], [430, 390], [620, 350]],
    "show_sidebar": True,
    "clock_24h": True,
    "sidebar_widgets": {
        "weather": True,
        "stats": True,
        "lights": True,
        "climate": True,
        "battery": True,
        "offline": True,
        "music": True,
    },
    "weather_entity_id": "",
    "selected_light_entities": [],
    "selected_climate_entities": [],
    "selected_battery_entities": [],
    "selected_offline_entities": [],
}

def load_settings() -> dict[str, Any]:
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE) as f:
                saved = json.load(f)
                return {**DEFAULT_SETTINGS, **saved}
    except Exception:
        pass
    return dict(DEFAULT_SETTINGS)

def save_settings(settings: dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as exc:
        print(f"[Settings] Save failed: {exc}")

current_settings = load_settings()

# Override with env vars only on very first load (first-run bootstrap)
if _HA_URL and not current_settings.get("ha_url"):
    current_settings["ha_url"] = _HA_URL
if _HA_TOKEN and not current_settings.get("ha_token"):
    current_settings["ha_token"] = _HA_TOKEN
if _MA_URL and not current_settings.get("ma_url"):
    current_settings["ma_url"] = _MA_URL
if _MA_TOKEN and not current_settings.get("ma_token"):
    current_settings["ma_token"] = _MA_TOKEN

# Sync module-level vars
_HA_URL = normalize_ha_url(current_settings.get("ha_url", ""))
_HA_TOKEN = current_settings.get("ha_token", "") or ""
_MA_URL = normalize_ma_url(current_settings.get("ma_url", ""))
_MA_TOKEN = current_settings.get("ma_token", "") or ""

# ── Frontend static ────────────────────────────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
else:

    @app.get("/")
    async def root():
        return {
            "message": (
                "Frontend not built yet. "
                "Run `cd frontend && npm install && npm run build` first."
            )
        }


@app.on_event("startup")
async def startup_event():
    app.state.ma_connect_task = asyncio.create_task(ma_client.run())
    app.state.ha_poll_task = asyncio.create_task(ha_poll_loop())
    app.state.ma_poll_task = asyncio.create_task(ma_poll_loop())

    try:
        await refresh_ha_state_once()
    except Exception as exc:
        print(f"[HA] Initial refresh failed: {exc}")

    try:
        await refresh_ma_state_once()
    except Exception as exc:
        print(f"[MA] Initial refresh failed: {exc}")


@app.on_event("shutdown")
async def shutdown_event():
    for task_name in ("ma_poll_task", "ha_poll_task", "ma_connect_task"):
        task = getattr(app.state, task_name, None)
        if task:
            task.cancel()
    await ma_client.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
