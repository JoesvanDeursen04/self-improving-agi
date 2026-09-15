"""AtomSpace: Distributed Metagraph for Knowledge Representation.

Implements the core data structure of OpenCog Hyperon - a weighted,
labeled hypergraph where nodes and edges can contain arbitrary semantic content.
"""

import uuid
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
from loguru import logger
import json


class AtomType(Enum):
    """Types of atoms in the AtomSpace."""
    NODE = "node"  # Simple semantic unit
    LINK = "link"  # Relationship between atoms
    CONCEPT = "concept"  # Abstract conceptual entity
    PREDICATE = "predicate"  # Logical predicate
    CONTEXT = "context"  # Contextual modifier


@dataclass
class Atom:
    """Base unit of knowledge in the AtomSpace.
    
    Every atom has:
    - Type: what kind of entity is it
    - Name: unique identifier
    - Weight: importance/confidence measure (0-1)
    - Timestamp: when it was created/modified
    - Properties: arbitrary semantic content
    """
    
    atom_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    atom_type: AtomType = AtomType.NODE
    name: str = ""
    weight: float = 1.0  # Confidence/importance
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: __import__('time').time())
    modified_at: float = field(default_factory=lambda: __import__('time').time())
    
    def __hash__(self):
        return hash(self.atom_id)
    
    def __eq__(self, other):
        if isinstance(other, Atom):
            return self.atom_id == other.atom_id
        return False
    
    def update_weight(self, new_weight: float):
        """Update atom importance weight."""
        self.weight = max(0.0, min(1.0, new_weight))
        self.modified_at = __import__('time').time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize atom to dictionary."""
        return {
            "id": self.atom_id,
            "type": self.atom_type.value,
            "name": self.name,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }


@dataclass
class Node(Atom):
    """Represents a semantic entity (noun, concept, entity)."""
    
    def __init__(self, name: str, atom_type: AtomType = AtomType.CONCEPT, 
                 weight: float = 1.0, properties: Dict[str, Any] = None):
        super().__init__(
            atom_type=atom_type,
            name=name,
            weight=weight,
            properties=properties or {}
        )


@dataclass
class Link(Atom):
    """Represents a relationship between atoms (hyperedge).
    
    Can connect multiple atoms and can have arbitrary arity.
    """
    
    def __init__(self, relation_type: str, targets: List[Atom], 
                 weight: float = 1.0, properties: Dict[str, Any] = None):
        super().__init__(
            atom_type=AtomType.LINK,
            name=relation_type,
            weight=weight,
            properties=properties or {}
        )
        self.targets: List[Atom] = targets
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["targets"] = [t.atom_id for t in self.targets]
        return base


class AtomSpace:
    """Distributed metagraph for knowledge representation.
    
    The AtomSpace is the fundamental data structure that stores:
    - Declarative knowledge (facts, concepts)
    - Procedural knowledge (algorithms, patterns)
    - Episodic memories (experiences)
    - Semantic relationships
    
    Supports:
    - Pattern matching and querying
    - Weighted traversal
    - Incremental updates
    - Distributed storage
    """
    
    def __init__(self, name: str = "default", distributed: bool = False):
        self.name = name
        self.distributed = distributed
        self.atoms: Dict[str, Atom] = {}  # atom_id -> Atom
        self.graph = nx.DiGraph()  # Directed graph for relationships
        self.indices: Dict[str, Set[str]] = {}  # Type-based indexing
        
    def add_atom(self, atom: Atom, replace: bool = False) -> str:
        """Add an atom to the space.
        
        Args:
            atom: The atom to add
            replace: If True, replace existing atom with same ID
            
        Returns:
            The atom's ID
        """
        if atom.atom_id in self.atoms and not replace:
            logger.warning(f"Atom {atom.atom_id} already exists")
            return atom.atom_id
        
        self.atoms[atom.atom_id] = atom
        self.graph.add_node(atom.atom_id, weight=atom.weight)
        
        # Update type index
        type_key = atom.atom_type.value
        if type_key not in self.indices:
            self.indices[type_key] = set()
        self.indices[type_key].add(atom.atom_id)
        
        logger.debug(f"Added atom: {atom.atom_id} ({atom.name})")
        return atom.atom_id
    
    def add_link(self, relation_type: str, source: Atom, targets: List[Atom],
                 weight: float = 1.0) -> str:
        """Create a link (hyperedge) between atoms.
        
        Args:
            relation_type: Type of relationship
            source: Source atom
            targets: Target atoms
            weight: Link weight
            
        Returns:
            Link ID
        """
        link = Link(relation_type, [source] + targets, weight=weight)
        self.add_atom(link)
        
        # Add edges to graph
        for target in [source] + targets:
            if target.atom_id not in self.graph:
                self.graph.add_node(target.atom_id)
            self.graph.add_edge(source.atom_id, target.atom_id, 
                               relation=relation_type, weight=weight)
        
        return link.atom_id
    
    def query(self, atom_type: Optional[AtomType] = None,
             name_pattern: Optional[str] = None) -> List[Atom]:
        """Query atoms by type and/or name pattern.
        
        Args:
            atom_type: Filter by atom type
            name_pattern: Substring match in name
            
        Returns:
            List of matching atoms
        """
        results = []
        for atom in self.atoms.values():
            if atom_type and atom.atom_type != atom_type:
                continue
            if name_pattern and name_pattern.lower() not in atom.name.lower():
                continue
            results.append(atom)
        return results
    
    def pattern_match(self, pattern: Dict[str, Any]) -> List[Atom]:
        """Pattern matching on atom properties.
        
        Args:
            pattern: Dictionary with property constraints
            
        Returns:
            List of atoms matching the pattern
        """
        results = []
        for atom in self.atoms.values():
            if all(atom.properties.get(k) == v for k, v in pattern.items()):
                results.append(atom)
        return results
    
    def get_connections(self, atom_id: str, direction: str = "all") -> List[Tuple[Atom, str]]:
        """Get atoms connected to a given atom.
        
        Args:
            atom_id: The atom to query
            direction: "in", "out", or "all"
            
        Returns:
            List of (connected_atom, relation_type) tuples
        """
        if atom_id not in self.graph:
            return []
        
        connections = []
        if direction in ["out", "all"]:
            for target_id in self.graph.successors(atom_id):
                edge_data = self.graph.edges[atom_id, target_id]
                connections.append((self.atoms[target_id], edge_data.get("relation", "link")))
        
        if direction in ["in", "all"]:
            for source_id in self.graph.predecessors(atom_id):
                edge_data = self.graph.edges[source_id, atom_id]
                connections.append((self.atoms[source_id], edge_data.get("relation", "link")))
        
        return connections
    
    def update_atom_weight(self, atom_id: str, new_weight: float):
        """Update the weight of an atom."""
        if atom_id in self.atoms:
            self.atoms[atom_id].update_weight(new_weight)
            self.graph.nodes[atom_id]["weight"] = new_weight
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the AtomSpace."""
        return {
            "total_atoms": len(self.atoms),
            "total_edges": self.graph.number_of_edges(),
            "atom_types": {k: len(v) for k, v in self.indices.items()},
            "average_weight": sum(a.weight for a in self.atoms.values()) / max(1, len(self.atoms)),
            "graph_density": nx.density(self.graph),
        }
    
    def export_json(self) -> str:
        """Export AtomSpace to JSON format."""
        data = {
            "name": self.name,
            "atoms": {aid: atom.to_dict() for aid, atom in self.atoms.items()},
            "stats": self.get_stats(),
        }
        return json.dumps(data, indent=2, default=str)
    
    def clear(self):
        """Clear all atoms from the space."""
        self.atoms.clear()
        self.graph.clear()
        self.indices.clear()
        logger.info("AtomSpace cleared")
