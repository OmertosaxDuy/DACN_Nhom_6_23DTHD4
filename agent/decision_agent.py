from agent.routing_policy import (
    decide_route,
)


class DecisionAgent:
    def decide(
        self,
        analysis: dict,
        observation: dict,
        base_decision: dict | None = None,
    ) -> dict:
        facts = analysis.get(
            "facts",
            {},
        )

        # =========================
        # Routing decision
        # =========================

        routing = decide_route(
            facts
        )

        detected_behaviors = set(
             facts.get(
                "detected_behaviors",
                [],
             )    
        )  
         
        # Nếu chỉ cần routing
        if base_decision is None:
             if "cloud_discovery" in detected_behaviors:
                decision = {
                    "risk_level": routing.risk_level,
                    "behavior": "cloud_discovery",
                    "evidence": analysis.get(
                    "evidence",
                    [],
                  ),
                  "recommended_action": "update_artifact",
                  "action_params": {
                        "artifact_name": "cloud_keys",
                  },
                  "reason": (
                     "Cloud discovery behavior detected"
                  ),
                }
     
             elif "credential_discovery" in detected_behaviors:
               decision = {
                 "risk_level": routing.risk_level,
                 "behavior": "credential_discovery",
                 "evidence": analysis.get(
                    "evidence",
                    [],
                 ),
                 "recommended_action": "update_artifact",
                 "action_params": {
                    "artifact_name": "backup_credentials",
                 },
                 "reason": (
                     "Credential discovery behavior detected"
                 ),
               }

             elif "database_discovery" in detected_behaviors:
               decision = {
                 "risk_level": routing.risk_level,
                 "behavior": "database_discovery",
                 "evidence": analysis.get(
                     "evidence",
                     [],
                 ),
                 "recommended_action": "update_artifact",
                 "action_params": {
                    "artifact_name": "db_config",
                 },
                 "reason": (
                   "Database discovery behavior detected"
                 ),
             }

             else:
               decision = {
                 "risk_level": routing.risk_level,
                 "behavior": "observed_activity",
                 "evidence": (
                     analysis.get("evidence")
                     or ["network_probe_observed"]
                 ),
                 "recommended_action": "observe_only",
                 "action_params": {},
                 "reason": routing.reason,
               }

             decision["risk_score"] = routing.risk_score
             decision["route"] = routing.route
             decision["routing_risk_level"] = routing.risk_level

             return decision

        # Copy để không sửa object gốc
        decision = dict(
            base_decision
        )

        monitoring = observation.get(
            "monitoring",
            {},
        )

        adaptation_state = observation.get(
            "adaptation_state",
            {},
        )

        monitoring_normal = (
            monitoring.get("active") is True
            and monitoring.get("level")
            == "normal"
        )

        monitoring_enhanced = (
            monitoring.get("active") is True
            and monitoring.get("level")
            == "enhanced"
        )

        strong_malicious_evidence = (
            facts.get(
                "bruteforce_detected"
            ) is True
            or facts.get(
                "successful_root_login"
            ) is True
            or facts.get(
                "nmap_http_probe_detected"
            ) is True
        )

        same_evidence_adapted = (
            adaptation_state.get(
                "same_evidence_already_adapted"
            ) is True
        )

        # =========================
        # Monitoring adaptation
        # =========================

        if (
            monitoring_normal
            and strong_malicious_evidence
        ):
            decision = {
                "risk_level": "high",
                "behavior": (
                    "malicious activity under "
                    "normal monitoring"
                ),
                "evidence": [
                    "strong malicious evidence detected"
                ],
                "recommended_action":
                    "increase_monitoring",
                "action_params": {},
                "reason": (
                    "Malicious activity requires "
                    "enhanced monitoring"
                ),
            }

        elif (
            monitoring_enhanced
            and same_evidence_adapted
        ):
            decision = {
                "risk_level": decision.get(
                    "risk_level",
                    routing.risk_level,
                ),
                "behavior": (
                    "previously handled evidence state"
                ),
                "evidence": [
                    "same evidence fingerprint "
                    "already adapted"
                ],
                "recommended_action":
                    "observe_only",
                "action_params": {},
                "reason": (
                    "Current evidence state was "
                    "already handled; no new "
                    "deception action is required"
                ),
            }
            


            artifact_name = (
                  decision
                  .get("action_params", {})
                  .get("artifact_name")
            )
        # =========================
        # Artifact safety policy
        # =========================

        detected_behaviors = set(
               facts.get(
                   "detected_behaviors",
                   []
               )
            )

        database_evidence = (
               "database_discovery"
               in detected_behaviors
        )

        credential_evidence = (
              "credential_discovery"
              in detected_behaviors
        )

        cloud_evidence = (
              "cloud_discovery"
              in detected_behaviors
        )

        if (
                artifact_name == "db_config"
                and not database_evidence
           ):
                decision = {
                    "risk_level": decision.get(
                        "risk_level",
                        routing.risk_level,
                    ),
                    "behavior": (
                        "malicious activity without "
                        "database-specific evidence"
                    ),
                    "evidence": [
                        "no database-related evidence "
                        "supports db_config adaptation"
                    ],
                    "recommended_action":
                        "observe_only",
                    "action_params": {},
                    "reason": (
                        "Database artifact update "
                        "blocked because "
                        "database-specific evidence "
                        "was not observed"
                    ),
                }

        elif (
                artifact_name == "cloud_keys"
                and not cloud_evidence
             ):
                decision = {
                    "risk_level": decision.get(
                        "risk_level",
                        routing.risk_level,
                    ),
                    "behavior": (
                        "malicious activity without "
                        "cloud-specific evidence"
                    ),
                    "evidence": [
                        "no cloud-related evidence "
                        "supports cloud_keys adaptation"
                    ],
                    "recommended_action":
                        "observe_only",
                    "action_params": {},
                    "reason": (
                        "Cloud artifact update blocked "
                        "because cloud-specific "
                        "evidence was not observed"
                    ),
                }

        elif (
                artifact_name
                == "backup_credentials"
                and not credential_evidence
            ):
                decision = {
                    "risk_level": decision.get(
                        "risk_level",
                        routing.risk_level,
                    ),
                    "behavior": (
                        "malicious activity without "
                        "credential-specific evidence"
                    ),
                    "evidence": [
                        "no credential-related evidence "
                        "supports backup_credentials "
                        "adaptation"
                    ],
                    "recommended_action":
                        "observe_only",
                    "action_params": {},
                    "reason": (
                        "Credential artifact update "
                        "blocked because "
                        "credential-specific evidence "
                        "was not observed"
                    ),
                }

        # Routing luôn do deterministic policy quyết định
        decision["risk_score"] = (
            routing.risk_score
        )

        decision["route"] = (
            routing.route
        )

        decision["routing_risk_level"] = (
            routing.risk_level
        )

        return decision
