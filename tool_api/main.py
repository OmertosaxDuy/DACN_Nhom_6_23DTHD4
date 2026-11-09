import os

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from pathlib import Path
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError  

from database import (
    get_session,
    get_commands,
    get_events,
    get_login_attempts_by_ip,
    get_sessions_by_ip,
    get_statistics,  
    detect_bruteforce,
    get_recent_activity,
    save_deception_event,
    get_deception_history,
    get_recent_decoy_events,
    get_decoy_events_by_ip,
    get_decoy_statistics,
    save_security_event,
    increase_monitoring,
    get_monitoring_state,
    was_artifact_applied_for_evidence,
)

from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Depends,
    Query,
)

API_KEY = os.environ["TOOL_API_KEY"]


def verify_api_key(
    request: Request,
    x_api_key: str = Header(default=None)
):
    if x_api_key != API_KEY:
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        save_security_event(
            timestamp,
            request.client.host if request.client else None,
            "unauthorized_api",
            str(request.url.path),
            "blocked",
            "Invalid or missing API key",
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return True

app = FastAPI(
    title="Cyber Deception Tool API",
    version="0.1.0"
)

limiter = Limiter(
    key_func=get_remote_address
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

class DeceptionEventRequest(BaseModel):
    session_id: str
    action: str
    result: str

class FakeFileRequest(BaseModel):
    session_id: str
    filename: str
    content: str

class UpdateArtifactRequest(BaseModel):
    session_id: str = Field(
        min_length=4,
        max_length=100
    )

    artifact_name: str = Field(
        min_length=1,
        max_length=50
    )

    content: str = Field(
        min_length=1,
        max_length=4096
    )

    evidence_fingerprint: str = Field(
        min_length=8,
        max_length=64
    )
class IncreaseMonitoringRequest(BaseModel):
    src_ip: str = Field(
        min_length=7,
        max_length=45
    )

    reason: str = Field(
        min_length=1,
        max_length=1000
    )

HONEYFS_ROOT = Path("/deception/honeyfs/root")

ARTIFACTS = {
    "backup_credentials": "backup_credentials.txt",
    "db_config": "db_config.txt",
    "cloud_keys": "cloud_keys.txt",
}

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get(
    "/sessions/{session_id}",
    dependencies=[Depends(verify_api_key)]
)
def session_info(session_id: str):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


@app.get(
    "/sessions/{session_id}/commands",
    dependencies=[Depends(verify_api_key)]
)
def session_commands(session_id: str):
    commands = get_commands(session_id)

    return {
        "session_id": session_id,
        "command_count": len(commands),
        "commands": commands
    }


@app.get(
    "/sessions/{session_id}/events",
    dependencies=[Depends(verify_api_key)]
)
def session_events(session_id: str):
    events = get_events(session_id)

    return {
        "session_id": session_id,
        "event_count": len(events),
        "events": events
    }

@app.get(
    "/ips/{src_ip}/logins",
    dependencies=[Depends(verify_api_key)]
)
def login_history(src_ip: str):
    attempts = get_login_attempts_by_ip(src_ip)

    return {
        "src_ip": src_ip,
        "attempt_count": len(attempts),
        "attempts": attempts
    }


@app.get(
    "/ips/{src_ip}/sessions",
    dependencies=[Depends(verify_api_key)]
)
def sessions_by_ip(src_ip: str):
    sessions = get_sessions_by_ip(src_ip)

    return {
        "src_ip": src_ip,
        "session_count": len(sessions),
        "sessions": sessions
    }

@app.get(
    "/statistics",
    dependencies=[Depends(verify_api_key)]
)
def statistics():
    return get_statistics()

@app.get(
    "/ips/{src_ip}/bruteforce",
    dependencies=[Depends(verify_api_key)]
)

def bruteforce_check(
    src_ip: str,
    threshold: int = Query(
        default=5,
        ge=1,
        le=100
    )
):
    return detect_bruteforce(src_ip, threshold)

@app.get(
    "/sessions/{session_id}/recent",
    dependencies=[Depends(verify_api_key)]
)
def recent_activity(session_id: str, limit: int = 10):
    events = get_recent_activity(session_id, limit)

    return {
        "session_id": session_id,
        "event_count": len(events),
        "events": events,
    }

@app.post(
    "/deception-events",
    dependencies=[Depends(verify_api_key)]
)
def create_deception_event(request: DeceptionEventRequest):
    timestamp = datetime.now(timezone.utc).isoformat()

    event_id = save_deception_event(
        request.session_id,
        timestamp,
        request.action,
        request.result,
    )

    return {
        "id": event_id,
        "session_id": request.session_id,
        "timestamp": timestamp,
        "action": request.action,
        "result": request.result,
    }

@app.get(
    "/sessions/{session_id}/deception-history",
    dependencies=[Depends(verify_api_key)]
)
def deception_history(session_id: str):
    history = get_deception_history(session_id)

    return {
        "session_id": session_id,
        "event_count": len(history),
        "events": history,
    }

@app.post(
    "/deception-actions/fake-file",
    dependencies=[Depends(verify_api_key)]
)
def create_fake_file(request: FakeFileRequest):
    HONEYFS_ROOT.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(request.filename).name
    file_path = HONEYFS_ROOT / safe_filename

    file_path.write_text(
        request.content,
        encoding="utf-8"
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    event_id = save_deception_event(
        request.session_id,
        timestamp,
        "create_fake_file",
        f"created:{safe_filename}",
    )

    return {
        "status": "success",
        "event_id": event_id,
        "session_id": request.session_id,
        "filename": safe_filename,
    }

@app.post(
    "/deception-actions/update-artifact",
    dependencies=[Depends(verify_api_key)]
)
def update_artifact(request: UpdateArtifactRequest):
        if request.artifact_name not in ARTIFACTS:
                timestamp = datetime.now(
                   timezone.utc
                ).isoformat()

                save_security_event(
                   timestamp,
                   None,
                   "artifact_rejected",
                   "update_artifact",
                   "blocked",
                   f"artifact={request.artifact_name}",
                )

                raise HTTPException(
                  status_code=400,
                  detail="Artifact not allowed"
                )

        if was_artifact_applied_for_evidence(
            session_id=request.session_id,
            artifact_name=request.artifact_name,
            evidence_fingerprint=request.evidence_fingerprint,
        ):
            return {
                "status": "already_applied",
                "session_id": request.session_id,
                "artifact_name": request.artifact_name,
                "evidence_fingerprint": (
                    request.evidence_fingerprint
                ),
                "detail": (
                    "Same deception action was already "
                    "applied for this evidence state"
                ),
            }

        filename = ARTIFACTS[request.artifact_name]
        file_path = HONEYFS_ROOT / filename

        file_path.write_text(
             request.content,
             encoding="utf-8"
        )

        timestamp = datetime.now(timezone.utc).isoformat()

        event_id = save_deception_event(
            request.session_id,
            timestamp,
            "update_artifact",
            (
                f"updated:{request.artifact_name}:"
                f"{request.evidence_fingerprint}"
            ),
        )

        return {
            "status": "success",
            "event_id": event_id,
            "session_id": request.session_id,
            "artifact_name": request.artifact_name,
            "filename": filename,
        }

@app.post(
    "/monitoring/increase",
    dependencies=[Depends(verify_api_key)]
)
def monitoring_increase(
    request: IncreaseMonitoringRequest
):
    result = increase_monitoring(
        src_ip=request.src_ip,
        reason=request.reason,
    )

    return {
        "status": "success",
        "action": "increase_monitoring",
        "src_ip": request.src_ip,
        "result": result,
    }

@app.get(
    "/monitoring/{src_ip}",
    dependencies=[Depends(verify_api_key)]
)
def monitoring_state(src_ip: str):
    state = get_monitoring_state(src_ip)

    if state is None:
        return {
            "src_ip": src_ip,
            "active": False,
            "level": "normal",
        }

    return state

@app.get(
    "/decoy/recent",
    dependencies=[Depends(verify_api_key)]
)
def get_decoy_recent(
    limit: int = Query(
        default=20,
        ge=1,
        le=100
    )
):
    return get_recent_decoy_events(limit)


@app.get(
    "/decoy/ips/{src_ip}",
    dependencies=[Depends(verify_api_key)]
)

def get_decoy_by_ip(
    src_ip: str,
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    )
):
    return get_decoy_events_by_ip(src_ip, limit)

@app.get(
    "/decoy/statistics",
    dependencies=[Depends(verify_api_key)]
 ) 
@limiter.limit("5/minute")
def get_decoy_stats(request: Request):
    return get_decoy_statistics()

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    timestamp = datetime.now(timezone.utc).isoformat()

    save_security_event(
        timestamp,
        request.client.host if request.client else None,
        "rate_limited",
        str(request.url.path),
        "blocked",
        str(exc.detail),
    )

    return JSONResponse(
        status_code=429,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    timestamp = datetime.now(timezone.utc).isoformat()

    save_security_event(
        timestamp,
        request.client.host if request.client else None,
        "invalid_input",
        str(request.url.path),
        "blocked",
        str(exc.errors())[:1000],
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        },
    )
