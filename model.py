from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class JobPosting:
    company: str
    title: str
    requirements: str
    deadline: str
    link: str

    def to_dict(self) -> Dict:
        """Convert to plain dict for JSON/JS usage."""
        return asdict(self)
