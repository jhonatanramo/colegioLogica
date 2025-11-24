from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def puede_procesar(self, prompt):
        pass
    
    @abstractmethod
    def procesar(self, prompt, parametros):
        pass
    
    @property
    @abstractmethod
    def tipo_reporte(self):
        pass