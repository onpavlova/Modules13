
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseModel(ABC):
    """Базовый класс для всех моделей"""

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass