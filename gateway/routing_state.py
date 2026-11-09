import json
from pathlib import Path


STATE_FILE = Path(
    "gateway/routing_state.json"
)


DEFAULT_STATE = {
    "last_session_id": None,
    "risk_score": 0,
    "risk_level": "low",
    "route": "allow_normal",
}


def load_all_states() -> dict:
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {}


def get_routing_state(
    src_ip: str,
) -> dict:
    states = load_all_states()

    state = states.get(
        src_ip
    )

    if not isinstance(state, dict):
        return DEFAULT_STATE.copy()

    result = DEFAULT_STATE.copy()
    result.update(state)

    return result


def update_routing_state(
    src_ip: str,
    session_id: str | None,
    risk_score: int,
    risk_level: str,
    route: str,
) -> None:
    states = load_all_states()

    states[src_ip] = {
        "last_session_id": session_id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "route": route,
    }

    STATE_FILE.write_text(
        json.dumps(
            states,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
