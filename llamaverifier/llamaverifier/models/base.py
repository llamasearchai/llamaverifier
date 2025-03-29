"""
Base model classes for LlamaVerifier
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseModel(ABC):
    """
    Base class for all models in LlamaVerifier
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the model
        
        Args:
            model_path: Path to the model file
        """
        self.model_path = model_path
        self.parameters = {}
        self.load_model()
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Load the model from the model path
        """
        pass
    
    @abstractmethod
    def forward(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the model forward pass
        
        Args:
            inputs: Input values
            
        Returns:
            Output values
        """
        pass
    
    @abstractmethod
    def to_circuit(self) -> str:
        """
        Convert the model to a circuit representation
        
        Returns:
            Circuit representation of the model
        """
        pass


class LinearModel(BaseModel):
    """
    Simple linear model
    """
    
    def load_model(self) -> None:
        """
        Load the model from the model path
        """
        with open(self.model_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                key, value = line.split('=', 1)
                self.parameters[key.strip()] = float(value.strip())
    
    def forward(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the model forward pass
        
        Args:
            inputs: Input values
            
        Returns:
            Output values
        """
        if 'inputs' not in inputs:
            raise ValueError("Input must contain 'inputs' key")
        
        input_values = inputs['inputs']
        
        if len(input_values) != int(self.parameters.get('inputs', 0)):
            raise ValueError(f"Expected {self.parameters.get('inputs')} inputs, got {len(input_values)}")
        
        # Simple linear model: y = w1*x1 + w2*x2 + ... + b
        result = self.parameters.get('b', 0.0)
        
        for i, x in enumerate(input_values):
            w_key = f'w{i+1}'
            if w_key in self.parameters:
                result += self.parameters[w_key] * x
        
        return {'output': [result]}
    
    def to_circuit(self) -> str:
        """
        Convert the model to a circuit representation
        
        Returns:
            Circuit representation of the model
        """
        # Simple ZoKrates circuit for a linear model
        circuit = "def main("
        
        # Add input parameters
        for i in range(int(self.parameters.get('inputs', 0))):
            circuit += f"private field x{i+1}, "
        
        # Add output parameter
        circuit += "public field y) -> bool {\n"
        
        # Add computation
        circuit += "    field result = "
        
        # Add bias term if present
        if 'b' in self.parameters:
            circuit += f"{self.parameters['b']}"
        else:
            circuit += "0"
        
        # Add weighted inputs
        for i in range(int(self.parameters.get('inputs', 0))):
            w_key = f'w{i+1}'
            if w_key in self.parameters:
                circuit += f" + {self.parameters[w_key]} * x{i+1}"
        
        # Add return statement
        circuit += ";\n"
        circuit += "    return result == y;\n"
        circuit += "}"
        
        return circuit 