"""
Collaboration Patterns - Module 4.3

Peer-to-peer collaboration, hierarchical coordination,
democratic decision making, conflict resolution protocols,
and performance optimization.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime
import threading


class CollaborationStyle(Enum):
    """Types of collaboration patterns"""
    PEER_TO_PEER = "peer_to_peer"
    HIERARCHICAL = "hierarchical"
    DEMOCRATIC = "democratic"
    HYBRID = "hybrid"


class VotingStrategy(Enum):
    """Voting mechanisms for democratic decisions"""
    UNANIMOUS = "unanimous"  # All must agree
    MAJORITY = "majority"  # More than 50%
    QUALIFIED_MAJORITY = "qualified_majority"  # 2/3 or more
    PLURALITY = "plurality"  # Most votes win
    WEIGHTED = "weighted"  # Votes have weights


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts"""
    MAJORITY_RULE = "majority_rule"
    CONSENSUS = "consensus"
    ESCALATE = "escalate"  # To higher authority
    ARBITRATION = "arbitration"  # Third party
    COMPROMISE = "compromise"  # Find middle ground


@dataclass
class Agent:
    """Represents an agent in collaboration"""
    agent_id: str
    role: str
    hierarchy_level: int = 0
    expertise_areas: List[str] = field(default_factory=list)
    reputation: float = 1.0
    voting_weight: float = 1.0
    active: bool = True


@dataclass
class CollaborativeDecision:
    """Decision made through collaboration"""
    decision_id: str
    topic: str
    proposer_id: str
    timestamp: float = field(default_factory=time.time)
    votes: Dict[str, Any] = field(default_factory=dict)
    voting_strategy: VotingStrategy = VotingStrategy.MAJORITY
    decision_made: Optional[Any] = None
    confidence: float = 0.0
    deadline: Optional[float] = None


@dataclass
class ConflictRecord:
    """Record of a conflict and its resolution"""
    conflict_id: str
    parties: List[str]
    issue: str
    proposed_resolutions: Dict[str, Any] = field(default_factory=dict)
    resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MAJORITY_RULE
    resolved_solution: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)


class PeerToPeerCollaborator:
    """Implements peer-to-peer collaboration pattern"""

    def __init__(self):
        self.peers: Dict[str, Agent] = {}
        self.shared_resources: Dict[str, Any] = {}
        self.peer_connections: Dict[str, Set[str]] = {}
        self.data_sync_log: List[Dict[str, Any]] = []

    def add_peer(self, agent: Agent):
        """Add peer to network"""
        self.peers[agent.agent_id] = agent
        self.peer_connections[agent.agent_id] = set()

    def connect_peers(self, agent1_id: str, agent2_id: str):
        """Establish direct connection between peers"""
        if agent1_id in self.peers and agent2_id in self.peers:
            self.peer_connections[agent1_id].add(agent2_id)
            self.peer_connections[agent2_id].add(agent1_id)

    def share_resource(self, resource_id: str, owner_id: str,
                      resource_data: Any, access_control: str = "read"):
        """Share resource with peers"""
        self.shared_resources[resource_id] = {
            "owner": owner_id,
            "data": resource_data,
            "access_control": access_control,
            "timestamp": time.time(),
            "accessed_by": []
        }

    def access_resource(self, resource_id: str, requester_id: str) -> Optional[Any]:
        """Access shared resource"""
        if resource_id not in self.shared_resources:
            return None

        resource = self.shared_resources[resource_id]
        resource["accessed_by"].append({
            "agent": requester_id,
            "timestamp": time.time()
        })

        return resource["data"]

    def replicate_data(self, data_id: str, source_agent: str,
                       target_agents: List[str]) -> bool:
        """Replicate data across peers for resilience"""
        if source_agent not in self.peers:
            return False

        for target in target_agents:
            if target in self.peers:
                self.data_sync_log.append({
                    "data_id": data_id,
                    "from": source_agent,
                    "to": target,
                    "timestamp": time.time()
                })

        return True

    def get_peer_status(self) -> Dict[str, Any]:
        """Get peer network status"""
        return {
            "total_peers": len(self.peers),
            "shared_resources": len(self.shared_resources),
            "data_sync_operations": len(self.data_sync_log),
            "connectivity": {
                agent_id: len(connections)
                for agent_id, connections in self.peer_connections.items()
            }
        }


class HierarchicalCoordinator:
    """Implements hierarchical coordination pattern"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.hierarchy_tree: Dict[int, List[str]] = {}
        self.supervisor_assignments: Dict[str, str] = {}
        self.directives: List[Dict[str, Any]] = []

    def add_agent_to_hierarchy(self, agent: Agent):
        """Add agent at specific hierarchy level"""
        self.agents[agent.agent_id] = agent
        level = agent.hierarchy_level

        if level not in self.hierarchy_tree:
            self.hierarchy_tree[level] = []

        self.hierarchy_tree[level].append(agent.agent_id)

    def assign_supervisor(self, subordinate_id: str, supervisor_id: str) -> bool:
        """Assign supervisor to subordinate"""
        if (subordinate_id in self.agents and
            supervisor_id in self.agents):
            sub_level = self.agents[subordinate_id].hierarchy_level
            sup_level = self.agents[supervisor_id].hierarchy_level

            if sup_level < sub_level:  # Supervisor at higher level
                self.supervisor_assignments[subordinate_id] = supervisor_id
                return True

        return False

    def issue_directive(self, issuer_id: str, target_agents: List[str],
                       directive: Dict[str, Any]) -> bool:
        """Issue directive from supervisor to subordinates"""
        if issuer_id not in self.agents:
            return False

        issuer = self.agents[issuer_id]

        # Check authority
        has_authority = all(
            issuer.hierarchy_level <
            self.agents.get(target_id, Agent("", "")).hierarchy_level
            for target_id in target_agents
            if target_id in self.agents
        )

        if has_authority:
            self.directives.append({
                "issuer": issuer_id,
                "targets": target_agents,
                "directive": directive,
                "timestamp": time.time(),
                "status": "issued"
            })
            return True

        return False

    def report_status(self, reporting_agent: str,
                     status_data: Dict[str, Any]):
        """Agent reports status to supervisor"""
        supervisor = self.supervisor_assignments.get(reporting_agent)

        if supervisor:
            return {
                "reporter": reporting_agent,
                "supervisor": supervisor,
                "status": status_data,
                "timestamp": time.time()
            }

        return None

    def get_hierarchy_structure(self) -> Dict[str, Any]:
        """Get complete hierarchy structure"""
        structure = {}

        for level in sorted(self.hierarchy_tree.keys()):
            agents_at_level = self.hierarchy_tree[level]
            structure[f"level_{level}"] = {
                "agents": agents_at_level,
                "count": len(agents_at_level)
            }

        return structure


class DemocraticDecisionMaker:
    """Implements democratic decision making pattern"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.pending_decisions: Dict[str, CollaborativeDecision] = {}
        self.completed_decisions: List[CollaborativeDecision] = []
        self.voting_history: List[Dict[str, Any]] = []

    def register_agent(self, agent: Agent):
        """Register agent for voting"""
        self.agents[agent.agent_id] = agent

    def propose_decision(self, decision: CollaborativeDecision) -> bool:
        """Propose decision for voting"""
        if decision.proposer_id in self.agents:
            self.pending_decisions[decision.decision_id] = decision
            return True
        return False

    def cast_vote(self, decision_id: str, agent_id: str,
                 vote: Any) -> bool:
        """Cast vote on pending decision"""
        if (decision_id not in self.pending_decisions or
            agent_id not in self.agents):
            return False

        decision = self.pending_decisions[decision_id]
        agent = self.agents[agent_id]

        # Record vote with agent's weight
        decision.votes[agent_id] = {
            "vote": vote,
            "weight": agent.voting_weight,
            "timestamp": time.time()
        }

        # Check if decision can be made
        self._try_finalize_decision(decision_id)

        return True

    def _try_finalize_decision(self, decision_id: str) -> bool:
        """Try to finalize decision if voting threshold met"""
        decision = self.pending_decisions[decision_id]

        if not decision.votes:
            return False

        total_weight = sum(
            self.agents[agent_id].voting_weight
            for agent_id in self.agents
        )

        votes_cast = sum(
            vote_data["weight"]
            for vote_data in decision.votes.values()
        )

        # Check if enough votes cast
        if votes_cast < total_weight * 0.5:
            return False

        # Apply voting strategy
        decision_made, confidence = self._apply_voting_strategy(
            decision.votes,
            decision.voting_strategy
        )

        if decision_made is not None:
            decision.decision_made = decision_made
            decision.confidence = confidence
            self.pending_decisions.pop(decision_id)
            self.completed_decisions.append(decision)
            return True

        return False

    def _apply_voting_strategy(self, votes: Dict[str, Any],
                               strategy: VotingStrategy) -> tuple:
        """Apply voting strategy to determine outcome"""
        if not votes:
            return None, 0.0

        if strategy == VotingStrategy.UNANIMOUS:
            # All must agree
            vote_values = [v["vote"] for v in votes.values()]
            if len(set(vote_values)) == 1:
                return vote_values[0], 1.0
            return None, 0.0

        elif strategy == VotingStrategy.MAJORITY:
            # More than 50%
            vote_counts = {}
            total_weight = sum(v["weight"] for v in votes.values())

            for vote_data in votes.values():
                vote = vote_data["vote"]
                weight = vote_data["weight"]
                vote_counts[vote] = vote_counts.get(vote, 0) + weight

            if vote_counts:
                max_vote = max(vote_counts, key=vote_counts.get)
                confidence = vote_counts[max_vote] / total_weight
                if confidence > 0.5:
                    return max_vote, confidence

        return None, 0.0

    def get_decision_status(self) -> Dict[str, Any]:
        """Get decision making status"""
        return {
            "pending_decisions": len(self.pending_decisions),
            "completed_decisions": len(self.completed_decisions),
            "total_agents": len(self.agents),
            "voting_history_count": len(self.voting_history)
        }


class ConflictResolver:
    """Handles conflict resolution between agents"""

    def __init__(self):
        self.conflicts: Dict[str, ConflictRecord] = {}
        self.resolution_log: List[Dict[str, Any]] = []
        self.mediators: List[str] = []

    def register_mediator(self, mediator_id: str):
        """Register mediator for conflict resolution"""
        self.mediators.append(mediator_id)

    def report_conflict(self, conflict: ConflictRecord) -> bool:
        """Report conflict between agents"""
        self.conflicts[conflict.conflict_id] = conflict
        return True

    def propose_resolution(self, conflict_id: str, proposer_id: str,
                         proposal: Any) -> bool:
        """Propose resolution for conflict"""
        if conflict_id not in self.conflicts:
            return False

        conflict = self.conflicts[conflict_id]
        conflict.proposed_resolutions[proposer_id] = proposal
        return True

    def resolve_conflict(self, conflict_id: str,
                        strategy: ConflictResolutionStrategy) -> Optional[Any]:
        """Resolve conflict using specified strategy"""
        if conflict_id not in self.conflicts:
            return None

        conflict = self.conflicts[conflict_id]
        conflict.resolution_strategy = strategy

        if strategy == ConflictResolutionStrategy.MAJORITY_RULE:
            # Use majority vote among proposals
            if conflict.proposed_resolutions:
                most_supported = max(
                    conflict.proposed_resolutions.items(),
                    key=lambda x: str(x[1])
                )
                conflict.resolved_solution = most_supported[1]

        elif strategy == ConflictResolutionStrategy.ESCALATE:
            # Escalate to higher authority
            if self.mediators:
                conflict.resolved_solution = {
                    "escalated_to": self.mediators[0],
                    "pending_review": True
                }

        self.resolution_log.append({
            "conflict_id": conflict_id,
            "strategy": strategy.value,
            "resolution": conflict.resolved_solution,
            "timestamp": time.time()
        })

        return conflict.resolved_solution

    def get_conflict_metrics(self) -> Dict[str, Any]:
        """Get conflict resolution metrics"""
        resolved = sum(
            1 for c in self.conflicts.values()
            if c.resolved_solution is not None
        )
        unresolved = len(self.conflicts) - resolved

        return {
            "total_conflicts": len(self.conflicts),
            "resolved_conflicts": resolved,
            "unresolved_conflicts": unresolved,
            "resolution_rate": resolved / len(self.conflicts) if self.conflicts else 0.0,
            "mediators_available": len(self.mediators)
        }


class CollaborationManager:
    """Central manager for all collaboration patterns"""

    def __init__(self):
        self.style: CollaborationStyle = CollaborationStyle.HYBRID
        self.peer_collaborator = PeerToPeerCollaborator()
        self.hierarchical_coordinator = HierarchicalCoordinator()
        self.democratic_decision_maker = DemocraticDecisionMaker()
        self.conflict_resolver = ConflictResolver()

    def set_collaboration_style(self, style: CollaborationStyle):
        """Set overall collaboration style"""
        self.style = style

    def get_collaboration_metrics(self) -> Dict[str, Any]:
        """Get metrics for all collaboration patterns"""
        return {
            "collaboration_style": self.style.value,
            "peer_to_peer": self.peer_collaborator.get_peer_status(),
            "hierarchical": self.hierarchical_coordinator.get_hierarchy_structure(),
            "democratic": self.democratic_decision_maker.get_decision_status(),
            "conflict_resolution": self.conflict_resolver.get_conflict_metrics()
        }
