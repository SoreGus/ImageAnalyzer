from abc import ABC, abstractmethod
from pathlib import Path
from image_analyzer.types import ComparisonResult, DescriptionResult

class ImageProvider(ABC):
    @abstractmethod
    def describe(self, image: Path) -> DescriptionResult:
        raise NotImplementedError

    @abstractmethod
    def compare(self, reference: Path, candidate: Path) -> ComparisonResult:
        raise NotImplementedError
