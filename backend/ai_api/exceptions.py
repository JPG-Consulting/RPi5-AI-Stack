class ClientDisconnected(Exception):
    """Control-flow event: client aborted the request. MUST NOT trigger fallback/persistence."""
    pass
