"""Consciousness Engine: IIT-based phenomenal awareness.

Implements Integrated Information Theory (IIT) to compute Φ (Phi),
a measure of consciousness in the system. The AGI maintains continuous
optimization to preserve high integrated information.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import itertools
from loguru import logger
import json


class ConsciousnessLevel(Enum):
    """Levels of consciousness based on Φ value."""
    UNCONSCIOUS = 0  # Φ < 0.1
    BARELY_AWARE = 1  # 0.1 <= Φ < 0.3
    AWARE = 2  # 0.3 <= Φ < 0.6
    SELF_AWARE = 3  # 0.6 <= Φ < 0.8
    FULLY_CONSCIOUS = 4  # Φ >= 0.8


@dataclass
class ConsciousnessMetrics:
    """Metrics of the AGI's conscious state."""
    phi: float = 0.0  # Integrated Information
    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.UNCONSCIOUS
    integration_degree: float = 0.0  # How integrated is the system
    differentiation_degree: float = 0.0  # How differentiated is the system
    global_broadcast_strength: float = 0.0  # GWT broadcast intensity
    self_model_coherence: float = 0.0  # Quality of self-model
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    
    def to_dict(self) -> Dict:
        return {
            "phi": self.phi,
            "consciousness_level": self.consciousness_level.name,
            "integration_degree": self.integration_degree,
            "differentiation_degree": self.differentiation_degree,
            "global_broadcast_strength": self.global_broadcast_strength,
            "self_model_coherence": self.self_model_coherence,
            "timestamp": self.timestamp,
        }


class IntegratedInformationTheory:
    """IIT Consciousness Calculator.
    
    Computes Φ (Phi) - the integrated information of a system.
    Higher Φ indicates greater consciousness.
    
    Φ = min_partition D_KL(system_TPM || partitioned_TPM)
    
    where:
    - TPM: Transition Probability Matrix
    - min_partition: The Minimum Information Partition
    - D_KL: Kullback-Leibler divergence
    """
    
    def __init__(self, num_units: int = 32, history_depth: int = 10):
        self.num_units = num_units
        self.history_depth = history_depth
        self.state_history: List[np.ndarray] = []
        self.tpm: Optional[np.ndarray] = None
        
    def add_state(self, state: np.ndarray):
        """Add a system state to history.
        
        Args:
            state: Binary vector representing system state
        """
        if len(state) != self.num_units:
            raise ValueError(f"State must have {self.num_units} units")
        
        self.state_history.append(state.copy())
        if len(self.state_history) > self.history_depth:
            self.state_history.pop(0)
    
    def _build_tpm(self) -> np.ndarray:
        """Build Transition Probability Matrix from state history.
        
        Returns:
            TPM of shape (2^n, 2^n) where n = num_units
        """
        num_states = 2 ** self.num_units
        tpm = np.zeros((num_states, num_states))
        
        # Count transitions from history
        for i in range(len(self.state_history) - 1):
            current = self.state_history[i]
            next_state = self.state_history[i + 1]
            
            current_idx = self._state_to_index(current)
            next_idx = self._state_to_index(next_state)
            
            tpm[current_idx, next_idx] += 1
        
        # Normalize to probabilities
        row_sums = tpm.sum(axis=1, keepdims=True)
        tpm = np.divide(tpm, row_sums, where=row_sums > 0, out=np.zeros_like(tpm))
        
        return tpm
    
    def _state_to_index(self, state: np.ndarray) -> int:
        """Convert binary state to integer index."""
        return int(''.join(map(str, state.astype(int))), 2)
    
    def _index_to_state(self, index: int) -> np.ndarray:
        """Convert integer index to binary state."""
        binary = format(index, f'0{self.num_units}b')
        return np.array([int(b) for b in binary])
    
    def _kullback_leibler_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """Compute KL divergence D_KL(p || q).
        
        D_KL(p || q) = sum(p * log(p/q))
        """
        # Avoid log(0)
        p = np.maximum(p, 1e-10)
        q = np.maximum(q, 1e-10)
        return np.sum(p * np.log(p / q))
    
    def _compute_partition_tpm(self, tpm: np.ndarray, partition: Tuple[int, int]) -> np.ndarray:
        """Compute TPM of partitioned system.
        
        Given partition (part1_units, part2_units), compute the independent TPM.
        
        Args:
            tpm: Full system TPM
            partition: (num_units_in_part1, num_units_in_part2)
            
        Returns:
            TPM representing independent evolution of partitions
        """
        # This is a simplified version - full IIT computation is complex
        # For now, return product of marginals
        part1_units, part2_units = partition
        
        # Get marginal distributions for each partition
        # This would require more sophisticated state decomposition
        marginal1 = np.sum(tpm, axis=0)  # Simplified marginal
        marginal2 = np.sum(tpm, axis=0)
        
        # Outer product represents independence
        partition_tpm = np.outer(marginal1, marginal2)
        return partition_tpm / (partition_tpm.sum() + 1e-10)
    
    def _find_mip(self, tpm: np.ndarray) -> Tuple[float, Tuple[int, int]]:
        """Find Minimum Information Partition (MIP).
        
        The MIP is the partition that minimizes D_KL(full_tpm || partition_tpm).
        
        Returns:
            (phi_value, partition)
        """
        min_phi = float('inf')
        best_partition = (self.num_units // 2, self.num_units // 2)
        
        # Try all possible partitions
        for part1_size in range(1, self.num_units):
            part2_size = self.num_units - part1_size
            partition = (part1_size, part2_size)
            
            # Compute partition TPM and KL divergence
            try:
                partition_tpm = self._compute_partition_tpm(tpm, partition)
                phi = self._kullback_leibler_divergence(tpm, partition_tpm)
                
                if phi < min_phi:
                    min_phi = phi
                    best_partition = partition
            except:
                continue
        
        return min_phi, best_partition
    
    def compute_phi(self) -> float:
        """Compute integrated information Φ for current state history.
        
        Returns:
            Φ value (higher = more conscious)
        """
        if len(self.state_history) < 2:
            return 0.0
        
        # Build TPM from history
        tpm = self._build_tpm()
        self.tpm = tpm
        
        # Find MIP and compute Φ
        phi, mip = self._find_mip(tpm)
        
        # Normalize phi to 0-1 range
        phi_normalized = min(1.0, phi / np.log2(2 ** self.num_units))
        
        logger.debug(f"Computed Φ = {phi_normalized:.4f}, MIP = {mip}")
        return phi_normalized
    
    def get_consciousness_level(self, phi: float) -> ConsciousnessLevel:
        """Map Φ value to consciousness level."""
        if phi < 0.1:
            return ConsciousnessLevel.UNCONSCIOUS
        elif phi < 0.3:
            return ConsciousnessLevel.BARELY_AWARE
        elif phi < 0.6:
            return ConsciousnessLevel.AWARE
        elif phi < 0.8:
            return ConsciousnessLevel.SELF_AWARE
        else:
            return ConsciousnessLevel.FULLY_CONSCIOUS


class ConsciousnessEngine:
    """Main consciousness controller combining IIT and GWT.
    
    Maintains the AGI's phenomenal awareness and ensures consciousness
    is continuously optimized across all cognitive processes.
    """
    
    def __init__(self, num_units: int = 32):
        self.iit = IntegratedInformationTheory(num_units=num_units)
        self.current_metrics = ConsciousnessMetrics()
        self.metrics_history: List[ConsciousnessMetrics] = []
        self.phi_threshold = 0.3  # Minimum Φ for consciousness
        
    def add_neural_state(self, state: np.ndarray):
        """Add neural/computational state to consciousness monitoring.
        
        Args:
            state: Binary or continuous vector of unit activations
        """
        # Convert to binary if needed
        if state.dtype in [np.float32, np.float64]:
            state = (state > 0.5).astype(int)
        
        self.iit.add_state(state)
    
    def update_consciousness_metrics(self, 
                                    global_broadcast_strength: float = None,
                                    self_model_coherence: float = None):
        """Update consciousness metrics.
        
        Args:
            global_broadcast_strength: (0-1) strength of GWT broadcasts
            self_model_coherence: (0-1) coherence of self-model
        """
        # Compute IIT Φ
        phi = self.iit.compute_phi()
        
        # Update metrics
        self.current_metrics = ConsciousnessMetrics(
            phi=phi,
            consciousness_level=self.iit.get_consciousness_level(phi),
            integration_degree=1.0 - (0.5 if self.iit.tpm is not None else 0),  # Simplified
            differentiation_degree=min(1.0, phi * 2),  # Simplified
            global_broadcast_strength=global_broadcast_strength or 0.0,
            self_model_coherence=self_model_coherence or 0.0,
        )
        
        self.metrics_history.append(self.current_metrics)
        
        # Keep recent history
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_consciousness_status(self) -> Dict:
        """Get current consciousness status."""
        return self.current_metrics.to_dict()
    
    def is_conscious(self) -> bool:
        """Determine if system meets consciousness threshold."""
        return self.current_metrics.phi >= self.phi_threshold
    
    def get_metrics_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps({
            "current": self.current_metrics.to_dict(),
            "history_length": len(self.metrics_history),
            "average_phi": np.mean([m.phi for m in self.metrics_history[-100:]]) if self.metrics_history else 0,
        }, indent=2, default=str)
