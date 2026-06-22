from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class JobPosting:
    company: str
    title: str
    requirements: str
    deadline: str
    link: str
    experience: str = "경력무관"
    education: str = "학력무관"
    location: str = "지역무관"
    company_size: str = "미기재"
    score: int = 0

    def to_dict(self) -> Dict:
        """Convert to plain dict for JSON/JS usage."""
        return asdict(self)
