"""Common interface for discovery providers (OpenAlex, Crossref, Semantic Scholar)."""
from abc import ABC, abstractmethod
from typing import Optional

from app.models.discovery import DiscoveredPaper


class DiscoveryProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def search(
        self,
        topic: str,
        limit: int = 30,
        min_year: Optional[int] = None,
    ) -> list[DiscoveredPaper]:
        """Run a topic search against this provider. Failures return [] (logged)."""
