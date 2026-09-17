"""CoALA Memory Architecture: Structured Episodic, Semantic, and Procedural Memory.

Implements a four-tier memory system:
1. Working Memory - Active, volatile, limited capacity
2. Episodic Memory - Timestamped experiences and events
3. Semantic Memory - Abstract facts, concepts, knowledge
4. Procedural Memory - Algorithms, skills, code
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from loguru import logger
import numpy as np


class MemoryType(Enum):
    """Types of memory in the CoALA architecture."""
    WORKING = "working"  # Active processing
    EPISODIC = "episodic"  # Timestamped experiences
    SEMANTIC = "semantic"  # Abstract knowledge
    PROCEDURAL = "procedural"  # Executable code/skills


@dataclass
class MemoryTrace:
    """A single memory trace/engram."""
    trace_id: str
    memory_type: MemoryType
    content: Any
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    strength: float = 1.0  # 0-1, how well consolidated
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def decay(self, time_passed: float, decay_rate: float = 0.01):
        """Apply memory decay based on time.
        
        Args:
            time_passed: Time since trace creation (seconds)
            decay_rate: How quickly memory fades
        """
        self.strength = max(0.0, self.strength - (decay_rate * time_passed / 3600))  # Hourly decay
    
    def reinforce(self, boost: float = 0.1):
        """Strengthen memory trace through rehearsal/use."""
        self.strength = min(1.0, self.strength + boost)
        self.access_count += 1


class WorkingMemory:
    """Limited-capacity active memory (Miller's 7±2).
    
    Holds current focus of attention and immediate computations.
    Volatile - cleared when attention shifts.
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.traces: List[MemoryTrace] = []
        
    def add_trace(self, trace: MemoryTrace) -> bool:
        """Add trace to working memory.
        
        Args:
            trace: Memory trace to add
            
        Returns:
            True if added, False if capacity exceeded
        """
        if len(self.traces) >= self.capacity:
            # Remove weakest (least recently used)
            self.traces.sort(key=lambda t: t.strength * t.access_count)
            self.traces.pop(0)
        
        self.traces.append(trace)
        return True
    
    def retrieve(self, trace_id: str) -> Optional[MemoryTrace]:
        """Retrieve from working memory."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                trace.access_count += 1
                return trace
        return None
    
    def clear(self):
        """Clear working memory."""
        self.traces.clear()
    
    def get_contents(self) -> List[MemoryTrace]:
        """Get all current contents."""
        return self.traces.copy()


class EpisodicMemory:
    """Event-based memory with temporal structure.
    
    Stores specific experiences with timestamps, creating a
    chronological narrative of the AGI's history.
    """
    
    def __init__(self):
        self.traces: Dict[str, MemoryTrace] = {}
        self.timeline: List[str] = []  # Chronological ordering
        
    def store_episode(self, episode_id: str, content: Any, tags: List[str] = None) -> MemoryTrace:
        """Store an episodic memory.
        
        Args:
            episode_id: Unique identifier
            content: What happened
            tags: Labels for retrieval
            
        Returns:
            Created memory trace
        """
        trace = MemoryTrace(
            trace_id=episode_id,
            memory_type=MemoryType.EPISODIC,
            content=content,
            tags=tags or []
        )
        self.traces[episode_id] = trace
        self.timeline.append(episode_id)
        logger.debug(f"Episodic memory stored: {episode_id}")
        return trace
    
    def retrieve_episode(self, episode_id: str) -> Optional[MemoryTrace]:
        """Retrieve specific episode."""
        if episode_id in self.traces:
            trace = self.traces[episode_id]
            trace.reinforce()
            return trace
        return None
    
    def retrieve_by_tag(self, tag: str) -> List[MemoryTrace]:
        """Retrieve all episodes with given tag."""
        return [t for t in self.traces.values() if tag in t.tags]
    
    def get_timeline(self, limit: int = 100) -> List[MemoryTrace]:
        """Get episodic timeline in order.
        
        Args:
            limit: Maximum number of episodes
            
        Returns:
            Chronologically ordered episodes
        """
        recent_ids = self.timeline[-limit:]
        return [self.traces[eid] for eid in recent_ids if eid in self.traces]
    
    def get_stats(self) -> Dict:
        """Get episodic memory statistics."""
        return {
            "total_episodes": len(self.traces),
            "average_strength": np.mean([t.strength for t in self.traces.values()]) if self.traces else 0,
            "total_accesses": sum(t.access_count for t in self.traces.values()),
        }


class SemanticMemory:
    """Conceptual knowledge and facts.
    
    Stores abstract knowledge about concepts, relationships,
    and general facts about the world.
    """
    
    def __init__(self):
        self.traces: Dict[str, MemoryTrace] = {}  # concept_id -> trace
        self.concepts: Dict[str, Dict] = {}  # concept_id -> properties
        self.relations: Dict[str, List[Tuple[str, str]]] = {}  # relation_type -> [(source, target)]
        
    def add_concept(self, concept_id: str, properties: Dict[str, Any], tags: List[str] = None) -> MemoryTrace:
        """Add a conceptual entity.
        
        Args:
            concept_id: Unique concept identifier
            properties: Properties of the concept
            tags: Labels for retrieval
            
        Returns:
            Memory trace
        """
        trace = MemoryTrace(
            trace_id=concept_id,
            memory_type=MemoryType.SEMANTIC,
            content=properties,
            tags=tags or []
        )
        self.traces[concept_id] = trace
        self.concepts[concept_id] = properties
        return trace
    
    def add_relation(self, relation_type: str, source: str, target: str):
        """Add a relationship between concepts.
        
        Args:
            relation_type: Type of relationship (e.g., 'is_a', 'part_of')
            source: Source concept
            target: Target concept
        """
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        self.relations[relation_type].append((source, target))
    
    def retrieve_concept(self, concept_id: str) -> Optional[Dict]:
        """Retrieve concept properties."""
        if concept_id in self.traces:
            self.traces[concept_id].reinforce()
            return self.concepts[concept_id]
        return None
    
    def find_relations(self, concept_id: str, relation_type: str = None) -> List[str]:
        """Find concepts related to a given concept.
        
        Args:
            concept_id: Source concept
            relation_type: Specific relation type (None for all)
            
        Returns:
            List of related concept IDs
        """
        results = []
        for rtype, relations in self.relations.items():
            if relation_type and rtype != relation_type:
                continue
            for source, target in relations:
                if source == concept_id:
                    results.append(target)
        return results
    
    def get_stats(self) -> Dict:
        return {
            "total_concepts": len(self.concepts),
            "total_relations": sum(len(r) for r in self.relations.values()),
            "relation_types": len(self.relations),
        }


class ProceduralMemory:
    """Executable code and algorithms.
    
    Stores the AGI's procedures: algorithms, heuristics, policies,
    and executable code for self-modification.
    """
    
    def __init__(self):
        self.procedures: Dict[str, Dict] = {}  # proc_id -> {code, signature, metadata}
        self.execution_stats: Dict[str, Dict] = {}  # proc_id -> {calls, successes, avg_time}
        
    def register_procedure(self, proc_id: str, code: str, signature: str = "", 
                          tags: List[str] = None) -> MemoryTrace:
        """Register a procedure/algorithm.
        
        Args:
            proc_id: Unique procedure identifier
            code: Executable code
            signature: Function signature
            tags: Labels
            
        Returns:
            Memory trace
        """
        self.procedures[proc_id] = {
            "code": code,
            "signature": signature,
            "tags": tags or [],
        }
        self.execution_stats[proc_id] = {
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "total_time": 0,
        }
        return MemoryTrace(
            trace_id=proc_id,
            memory_type=MemoryType.PROCEDURAL,
            content={"code": code, "signature": signature},
            tags=tags or []
        )
    
    def get_procedure(self, proc_id: str) -> Optional[Dict]:
        """Retrieve procedure code."""
        return self.procedures.get(proc_id)
    
    def update_procedure(self, proc_id: str, new_code: str) -> bool:
        """Update procedure code (used in self-improvement).
        
        Args:
            proc_id: Procedure to modify
            new_code: New code
            
        Returns:
            True if successful
        """
        if proc_id in self.procedures:
            self.procedures[proc_id]["code"] = new_code
            logger.info(f"Procedure updated: {proc_id}")
            return True
        return False
    
    def record_execution(self, proc_id: str, success: bool, execution_time: float):
        """Record execution statistics."""
        if proc_id in self.execution_stats:
            stats = self.execution_stats[proc_id]
            stats["calls"] += 1
            if success:
                stats["successes"] += 1
            else:
                stats["failures"] += 1
            stats["total_time"] += execution_time
    
    def get_stats(self) -> Dict:
        return {
            "total_procedures": len(self.procedures),
            "execution_stats": self.execution_stats,
        }


class MemoryArchitecture:
    """Complete CoALA memory system integrating all four memory types."""
    
    def __init__(self):
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        
    def get_all_stats(self) -> Dict:
        """Get statistics across all memory systems."""
        return {
            "working": {"items": len(self.working.traces)},
            "episodic": self.episodic.get_stats(),
            "semantic": self.semantic.get_stats(),
            "procedural": self.procedural.get_stats(),
        }
    
    def export_json(self) -> str:
        """Export memory architecture to JSON."""
        return json.dumps(self.get_all_stats(), indent=2, default=str)
