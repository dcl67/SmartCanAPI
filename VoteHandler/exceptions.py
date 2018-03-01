class ClientError(Exception):
    """
    Exception class that is caught by the websocket receive()
    handler and used to send an error back to the client.
    """
    def __init__(self, code):
        super().__init__(code)
        self.code = code