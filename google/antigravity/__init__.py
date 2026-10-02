class Agent:
    def __init__(self, config):
        self.conversation_id = "test_id"
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
