from dataclasses import dataclass


@dataclass
class RoutingDecision:
    risk_score: int
    risk_level: str
    route: str
    reason: str

def calculate_risk_score(
    derived_facts: dict,
) -> int:
    score = 0

    recent_failed_ssh = derived_facts.get(
        "recent_failed_ssh_attempts",
        0,
    )

    if recent_failed_ssh >= 20:
        score += 40
    elif recent_failed_ssh >= 5:
        score += 20

    if derived_facts.get(
       "nmap_http_probe_detected"
    ) is True:
       score += 20

    detected_behaviors = set(
        derived_facts.get(
            "detected_behaviors",
            []
        )
    )

    if "database_discovery" in detected_behaviors:
        score += 40

    if "credential_discovery" in detected_behaviors:
        score += 40

    if "cloud_discovery" in detected_behaviors:
        score += 40
    
    return min(
        score,
        100,
    )

def decide_route(
    derived_facts: dict,
) -> RoutingDecision:
    score = calculate_risk_score(
        derived_facts
    )

    if score >= 60:
        return RoutingDecision(
            risk_score=score,
            risk_level="high",
            route="route_to_honeypot",
            reason=(
                "High-risk malicious behavior "
                "detected"
            ),
        )

    if score >= 30:
        return RoutingDecision(
            risk_score=score,
            risk_level="medium",
            route="route_to_decoy",
            reason=(
                "Suspicious behavior detected"
            ),
        )

    return RoutingDecision(
        risk_score=score,
        risk_level="low",
        route="allow_normal",
        reason=(
            "No strong malicious evidence detected"
        ),
    )
