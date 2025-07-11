from abc import ABC, abstractmethod
import numpy as np

class BaseProtocol(ABC):
    """
    An abstract base class for LDP estimation protocols.
    
    This class is intended to serve as the interface for both frequency and mean estimation
    protocols. It defines the required methods such as obfuscate, estimate, and get_mse.
    For protocols that do not support an adversarial attack, the attack method returns None by default.
    
    Attributes
    ----------
    k : int
        The domain size (number of possible values).
    epsilon : float
        The privacy budget.
    """

    def __init__(self, k: int, epsilon: float):
        if not isinstance(k, int) or k < 2:
            raise ValueError("k must be an integer >= 2.")
        if epsilon <= 0:
            raise ValueError("epsilon must be greater than 0.")
        self.k = k
        self.epsilon = epsilon

    @abstractmethod
    def obfuscate(self, input_data: int):
        """
        Obfuscate the input data.
        
        Parameters
        ----------
        input_data : int
            The true value to be obfuscated.
        
        Returns
        -------
        The obfuscated (sanitized) result.
        """
        pass

    @abstractmethod
    def estimate(self, noisy_reports: list) -> np.ndarray:
        """
        Estimate the frequencies from noisy reports.
        
        Parameters
        ----------
        noisy_reports : list
            A collection of noisy reports from users.
        
        Returns
        -------
        np.ndarray
            An array of estimated frequencies that sums to 1.
        """
        pass

    @abstractmethod
    def attack(self, obfuscated_report):
        """
        Perform an attack to infer the true value from an obfuscated report.
        
        Parameters
        ----------
        obfuscated_report :
            The output from the obfuscation mechanism.
        
        Returns
        -------
        The inferred true value.
        """
        return None

    @abstractmethod
    def get_mse(self, n: int = 1) -> float:
        """
        Compute the Mean Squared Error (MSE) of the protocol.
        
        Parameters
        ----------
        n : int, optional
            The number of reports (default is 1).
        
        Returns
        -------
        float
            The MSE value.
        """
        pass

    @abstractmethod
    def get_asr(self) -> float:
        """
        Compute the Adversarial Success Rate (ASR) for the protocol.
        
        Returns
        -------
        float
            The ASR value.
        """
        pass
