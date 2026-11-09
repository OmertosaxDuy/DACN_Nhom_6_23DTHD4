class ObservationAgent:
    def __init__(
        self,
        observe_fn,
    ):
        self.observe_fn = observe_fn

    def observe(
        self,
        src_ip: str,
        session_id: str | None = None,
    ) -> dict:
        return self.observe_fn(
            src_ip,
            preferred_session_id=session_id,
        )
