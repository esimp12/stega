class Aggregate:
    def __init__(self, aggregate_id: str version_number: int = 0) -> None:
        self.aggregate_id = aggregate_id
        self.version_number = version_number
        self.events = []
