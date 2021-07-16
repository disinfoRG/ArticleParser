from dataclasses import dataclass

@dataclass(frozen=True)
class NewPublicationMessage:
    publication_id: str
    version: int
