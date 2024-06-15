from abc import ABC, abstractmethod

class BaseCalculator(ABC):

    @abstractmethod
    def calculate(self, customer_id: int) -> float:
        pass
