import abc
from abc import ABC, abstractmethod

class Scraper(ABC):

    @abstractmethod
    def getEventDescription(self) -> str | None:
        pass
    
    @abstractmethod
    def getImage(self):
        pass

    @abstractmethod
    def getDate(self):
        pass
