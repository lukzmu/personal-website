class ImproperlyConfiguredRepository(Exception):
    def __init__(self, message: str = "Repository is improperly configured.") -> None:
        super().__init__(message)
