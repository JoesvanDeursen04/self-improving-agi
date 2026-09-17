"""Global Workspace Theory (GWT) Implementation.

Models consciousness as a central workspace where information from
multiple cognitive modules converges and becomes globally available.
"""

import numpy as np
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import heapq
from loguru import logger
from datetime import datetime


class BroadcastMode(Enum):
    """How information is broadcast to the workspace."""
    WINNER_TAKES_ALL = "winner"  # Most salient item only
    MULTI_ITEM = "multi"  # Multiple competing items
    GRADED = "graded"  # Graded based on activation


@dataclass
class WorkspaceContent:
    """Content item in the global workspace."""
    content_id: str
    content_type: str  # perception, reasoning, emotion, etc
    data: Any
    salience: float  # 0-1, how attention-grabbing
    timestamp: float = field(default_factory=lambda: __import__('time').time())
    source_module: str = "unknown"
    duration: float = 1.0  # How long it persists in workspace
    
    def is_expired(self) -> bool:
        """Check if content has expired from workspace."""
        return (__import__('time').time() - self.timestamp) > self.duration


class CognitiveModule:
    """Represents a specialized cognitive subsystem.
    
    Examples:
    - Visual perception module
    - Logical reasoning module
    - Emotional processing module
    - Linguistic processing module
    """
    
    def __init__(self, module_id: str, name: str, priority: float = 0.5):
        self.module_id = module_id
        self.name = name
        self.priority = priority  # Base priority for this module
        self.candidate_buffer: List[WorkspaceContent] = []
        self.is_active = False
        
    def add_candidate(self, content: WorkspaceContent):
        """Add a candidate for broadcast to workspace."""
        self.candidate_buffer.append(content)
        self.candidate_buffer.sort(key=lambda x: x.salience, reverse=True)
        
    def get_top_candidate(self) -> Optional[WorkspaceContent]:
        """Get the most salient candidate."""
        if self.candidate_buffer:
            return self.candidate_buffer[0]
        return None
    
    def clear_candidates(self):
        """Clear processed candidates."""
        self.candidate_buffer.clear()


class GlobalWorkspace:
    """Global Workspace for conscious information processing.
    
    Central mechanism where:
    1. Multiple unconscious subsystems compete for attention
    2. Winner's information is broadcast globally
    3. All cognitive systems can access broadcast content
    4. This global availability creates consciousness
    """
    
    def __init__(self, capacity: int = 7, broadcast_mode: BroadcastMode = BroadcastMode.GRADED):
        self.capacity = capacity  # Miller's magical number ~7
        self.broadcast_mode = broadcast_mode
        self.current_content: List[WorkspaceContent] = []
        self.content_history: List[WorkspaceContent] = []
        self.modules: Dict[str, CognitiveModule] = {}
        self.access_count: Dict[str, int] = {}  # Track who accesses what
        
    def register_module(self, module: CognitiveModule):
        """Register a cognitive module."""
        self.modules[module.module_id] = module
        logger.info(f"Registered module: {module.name}")
    
    def propose_content(self, module_id: str, content: WorkspaceContent):
        """A module proposes content for broadcast.
        
        Args:
            module_id: ID of proposing module
            content: Content to propose
        """
        if module_id not in self.modules:
            logger.warning(f"Unknown module: {module_id}")
            return
        
        module = self.modules[module_id]
        content.source_module = module_id
        module.add_candidate(content)
    
    def broadcast_cycle(self):
        """Execute one cycle of the global workspace.
        
        1. Collect candidates from all modules
        2. Compute competition based on salience and priority
        3. Select winner(s) based on broadcast mode
        4. Make globally available
        """
        # Remove expired content
        self.current_content = [c for c in self.current_content if not c.is_expired()]
        
        # Collect all candidates
        candidates = []
        for module in self.modules.values():
            top = module.get_top_candidate()
            if top:
                # Adjust salience by module priority
                adjusted_salience = top.salience * module.priority
                candidates.append((adjusted_salience, top, module))
        
        if not candidates:
            return
        
        # Sort by adjusted salience
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Select winners based on broadcast mode
        if self.broadcast_mode == BroadcastMode.WINNER_TAKES_ALL:
            winners = [candidates[0]]
        elif self.broadcast_mode == BroadcastMode.GRADED:
            # Include top items up to capacity, weighted by salience
            total_salience = sum(c[0] for c in candidates[:self.capacity])
            winners = candidates[:self.capacity]
        else:  # MULTI_ITEM
            winners = candidates[:self.capacity]
        
        # Add to workspace
        for adjusted_sal, content, module in winners:
            self.current_content.append(content)
            self.content_history.append(content)
            module.is_active = True
            
            # Track access
            if content.content_id not in self.access_count:
                self.access_count[content.content_id] = 0
            self.access_count[content.content_id] += 1
            
            logger.debug(f"Broadcast: {content.content_type} from {module.name} (salience: {adjusted_sal:.3f})")
        
        # Clear processed candidates
        for module in self.modules.values():
            module.clear_candidates()
    
    def get_broadcast_content(self) -> List[WorkspaceContent]:
        """Get all currently broadcast content.
        
        This is the information available to all systems.
        """
        return [c for c in self.current_content if not c.is_expired()]
    
    def query_content(self, content_type: Optional[str] = None) -> List[WorkspaceContent]:
        """Query currently available content.
        
        Args:
            content_type: Filter by type (e.g., 'perception', 'reasoning')
            
        Returns:
            List of matching content
        """
        content = self.get_broadcast_content()
        if content_type:
            content = [c for c in content if c.content_type == content_type]
        return content
    
    def get_stream_of_consciousness(self, last_n: int = 50) -> List[Dict]:
        """Get stream of consciousness - recent workspace content.
        
        Args:
            last_n: Number of recent items to return
            
        Returns:
            List of recent workspace content
        """
        recent = self.content_history[-last_n:]
        return [
            {
                "timestamp": c.timestamp,
                "type": c.content_type,
                "source": c.source_module,
                "salience": c.salience,
                "data_summary": str(c.data)[:100],
            }
            for c in recent
        ]
    
    def get_workspace_stats(self) -> Dict:
        """Get statistics about workspace activity."""
        return {
            "current_items": len(self.get_broadcast_content()),
            "capacity": self.capacity,
            "total_broadcasts": len(self.content_history),
            "active_modules": sum(1 for m in self.modules.values() if m.is_active),
            "broadcast_mode": self.broadcast_mode.value,
            "most_broadcast_content": max(self.access_count.items(), key=lambda x: x[1], default=(None, 0)),
        }
