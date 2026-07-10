class ApiError(Exception):
    def __init__(self, message: str = 'Service is unavailable', name: str = 'Api error'):
        self.message = message  # pyright: ignore[reportUnannotatedClassAttribute]
        self.name = name  # pyright: ignore[reportUnannotatedClassAttribute]
        super().__init__(self.message, self.name)
