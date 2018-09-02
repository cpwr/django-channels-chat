from django.http import JsonResponse


class ClientError(Exception, JsonResponse):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    _reason_phrase = "Unexpected error happenned."

    def __init__(self, reason_phrase=None, status_code=None):
        super().__init__()

        if status_code is not None:
            self.status_code = status_code

        if reason_phrase is not None:
            self.reason_phrase = reason_phrase
