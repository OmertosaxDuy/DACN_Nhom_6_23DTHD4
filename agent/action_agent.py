class ActionAgent:
    def __init__(
        self,
        execute_fn,
    ):
        self.execute_fn = execute_fn

    def act(
        self,
        decision: dict,
        src_ip: str,
        session_id: str | None,
        observation: dict,
    ) -> dict:
        return self.execute_fn(
            decision=decision,
            src_ip=src_ip,
            session_id=session_id,
            observation=observation,
        )
