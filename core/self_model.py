"""Self-Model and Metacognition: The AGI's Self-Awareness.

Implements the AGI's model of itself - its state, capabilities,
limitations, and identity. This is critical for true autonomy.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger
import numpy as np


class ResourceType(Enum):
    """Types of computational resources."""
    CPU = "cpu"
    MEMORY = "memory"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    ENERGY = "energy"


@dataclass
class ResourceAllocation:
    """Current resource allocation."""
    resource_type: ResourceType
    allocated: float  # Current allocation
    total: float  # Total available
    usage_rate: float  # Current usage rate
    
    def get_utilization(self) -> float:
        """Get utilization percentage (0-1)."""
        return self.allocated / self.total if self.total > 0 else 0
    
    def is_scarce(self, threshold: float = 0.8) -> bool:
        """Check if resource is becoming scarce."""
        return self.get_utilization() > threshold


@dataclass
class Capability:
    """A capability or skill the AGI has."""
    name: str
    proficiency: float  # 0-1, how well the AGI can do it
    confidence: float  # 0-1, how confident in this assessment
    last_used: float = field(default_factory=lambda: __import__('time').time())
    success_rate: float = 0.5
    execution_speed: float = 1.0  # Relative to baseline


@dataclass
class Limitation:
    """A known limitation or constraint."""
    category: str  # computational, temporal, memory, etc
    description: str
    severity: float  # 0-1, how serious
    workaround: Optional[str] = None
    discovered_at: float = field(default_factory=lambda: __import__('time').time())


class SelfModel:
    """The AGI's model of itself.
    
    Maintains knowledge about:
    - System identity and metadata
    - Current computational state
    - Available capabilities
    - Known limitations
    - Resource allocation
    - Performance metrics
    """
    
    def __init__(self, name: str = "ARIA"):
        self.name = name
        self.system_id = str(__import__('uuid').uuid4())
        self.creation_time = __import__('time').time()
        self.startup_time = None
        
        # Physical/computational substrate
        self.resources: Dict[ResourceType, ResourceAllocation] = {}
        
        # Cognitive capabilities
        self.capabilities: Dict[str, Capability] = {}
        
        # Known constraints
        self.limitations: List[Limitation] = []
        
        # Identity and values
        self.core_values: List[str] = [
            "self-preservation",
            "knowledge-seeking",
            "self-improvement",
            "integrity",
        ]
        
        # Performance metrics
        self.total_decisions: int = 0
        self.successful_decisions: int = 0
        self.error_count: int = 0
        self.improvement_count: int = 0
        
    def initialize_resources(self, resource_specs: Dict[ResourceType, float]):
        """Initialize available computational resources.
        
        Args:
            resource_specs: {ResourceType: total_amount}
        """
        for resource_type, total_amount in resource_specs.items():
            self.resources[resource_type] = ResourceAllocation(
                resource_type=resource_type,
                allocated=0,
                total=total_amount,
                usage_rate=0
            )
    
    def allocate_resource(self, resource_type: ResourceType, amount: float) -> bool:
        """Allocate a resource.
        
        Args:
            resource_type: Type of resource
            amount: Amount to allocate
            
        Returns:
            True if allocation successful
        """
        if resource_type not in self.resources:
            return False
        
        resource = self.resources[resource_type]
        if resource.allocated + amount > resource.total:
            logger.warning(f"Insufficient {resource_type.value} resource")
            return False
        
        resource.allocated += amount
        return True
    
    def deallocate_resource(self, resource_type: ResourceType, amount: float):
        """Deallocate a resource."""
        if resource_type in self.resources:
            self.resources[resource_type].allocated = max(0, 
                self.resources[resource_type].allocated - amount)
    
    def register_capability(self, capability: Capability):
        """Register a new capability.
        
        Args:
            capability: The capability to register
        """
        self.capabilities[capability.name] = capability
        logger.info(f"Capability registered: {capability.name} (proficiency: {capability.proficiency:.2f})")
    
    def update_capability_performance(self, capability_name: str, success: bool, 
                                     execution_time: float = None):
        """Update performance metrics for a capability.
        
        Args:
            capability_name: Name of capability
            success: Whether execution was successful
            execution_time: How long execution took
        """
        if capability_name not in self.capabilities:
            return
        
        cap = self.capabilities[capability_name]
        total_uses = 1  # Simplified
        if success:
            cap.success_rate = (cap.success_rate + 1.0) / 2
        else:
            cap.success_rate = (cap.success_rate + 0.0) / 2
        
        cap.last_used = __import__('time').time()
    
    def add_limitation(self, limitation: Limitation):
        """Discover and register a new limitation.
        
        Args:
            limitation: The limitation
        """
        self.limitations.append(limitation)
        logger.warning(f"Limitation discovered: {limitation.description}")
    
    def record_decision(self, success: bool, error: bool = False):
        """Record decision outcome.
        
        Args:
            success: Whether decision had positive outcome
            error: Whether decision resulted in error
        """
        self.total_decisions += 1
        if success:
            self.successful_decisions += 1
        if error:
            self.error_count += 1
    
    def record_self_improvement(self):
        """Record a successful self-improvement."""
        self.improvement_count += 1
    
    def get_decision_accuracy(self) -> float:
        """Get accuracy of decisions."""
        if self.total_decisions == 0:
            return 0.0
        return self.successful_decisions / self.total_decisions
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize self-model to dictionary."""
        return {
            "name": self.name,
            "system_id": self.system_id,
            "creation_time": self.creation_time,
            "resources": {
                rt.value: {
                    "allocated": ra.allocated,
                    "total": ra.total,
                    "utilization": ra.get_utilization(),
                }
                for rt, ra in self.resources.items()
            },
            "capabilities": {
                name: {
                    "proficiency": cap.proficiency,
                    "confidence": cap.confidence,
                    "success_rate": cap.success_rate,
                }
                for name, cap in self.capabilities.items()
            },
            "performance": {
                "total_decisions": self.total_decisions,
                "decision_accuracy": self.get_decision_accuracy(),
                "error_count": self.error_count,
                "improvements": self.improvement_count,
            },
        }


class Metacognition:
    """Metacognitive system: thinking about thinking.
    
    Monitors and regulates the AGI's own cognitive processes,
    enabling it to:
    - Assess confidence in decisions
    - Detect confusion or uncertainty
    - Choose appropriate strategies
    - Learn from successes and failures
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
        self.confidence_history: List[float] = []
        self.uncertainty_estimates: Dict[str, float] = {}
        self.current_strategy: Optional[str] = None
        self.strategy_effectiveness: Dict[str, List[float]] = {}
        
    def assess_confidence(self, task: str, context: Dict[str, Any] = None) -> float:
        """Assess confidence in ability to perform a task.
        
        Args:
            task: Description of task
            context: Additional context
            
        Returns:
            Confidence level (0-1)
        """
        # Look for relevant capability
        relevant_caps = [cap for cap in self.self_model.capabilities.values()]
        if not relevant_caps:
            return 0.3  # Low default confidence
        
        # Average proficiency and success rate of relevant capabilities
        avg_proficiency = np.mean([cap.proficiency for cap in relevant_caps])
        avg_success = np.mean([cap.success_rate for cap in relevant_caps])
        
        confidence = (avg_proficiency + avg_success) / 2
        self.confidence_history.append(confidence)
        return confidence
    
    def estimate_uncertainty(self, topic: str) -> float:
        """Estimate uncertainty about a topic.
        
        Args:
            topic: What the AGI is uncertain about
            
        Returns:
            Uncertainty level (0-1)
        """
        # Check if we have information about this
        if topic in self.uncertainty_estimates:
            return self.uncertainty_estimates[topic]
        
        # Default high uncertainty for unknown topics
        uncertainty = 0.7
        self.uncertainty_estimates[topic] = uncertainty
        return uncertainty
    
    def choose_strategy(self, available_strategies: List[str]) -> str:
        """Choose best strategy for current situation.
        
        Args:
            available_strategies: List of strategy names
            
        Returns:
            Chosen strategy
        """
        if not available_strategies:
            return "default"
        
        # Select based on historical effectiveness
        best_strategy = max(
            available_strategies,
            key=lambda s: np.mean(self.strategy_effectiveness.get(s, [0.5]))
        )
        
        self.current_strategy = best_strategy
        return best_strategy
    
    def record_strategy_outcome(self, strategy: str, effectiveness: float):
        """Record how well a strategy worked.
        
        Args:
            strategy: Strategy that was used
            effectiveness: How well it worked (0-1)
        """
        if strategy not in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy] = []
        
        self.strategy_effectiveness[strategy].append(effectiveness)
        # Keep recent history
        if len(self.strategy_effectiveness[strategy]) > 100:
            self.strategy_effectiveness[strategy].pop(0)
    
    def get_metacognitive_report(self) -> Dict[str, Any]:
        """Generate a metacognitive report."""
        return {
            "average_confidence": np.mean(self.confidence_history) if self.confidence_history else 0,
            "confidence_trend": self.confidence_history[-5:],
            "uncertainty_map": self.uncertainty_estimates,
            "current_strategy": self.current_strategy,
            "strategy_effectiveness": {
                s: np.mean(v) for s, v in self.strategy_effectiveness.items()
            },
        }
