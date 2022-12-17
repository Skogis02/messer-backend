from dataclasses import dataclass, field
import json

@dataclass
class Error:
    error: str
    code: str
    content: str = ''

    def as_dict(self):
        return {
            'error': self.error,
            'content': self.content,
            'code': self.code
        }

@dataclass
class Response:
    endpoint: str
    id: str
    content: dict = field(default_factory=dict)
    errors: list[Error] = field(default_factory=list)

    def as_dict(self):
        return {
            'endpoint': self.endpoint,
            'id': self.id,
            'content': self.content,
            'errors': [error.as_dict() for error in self.errors]
        }