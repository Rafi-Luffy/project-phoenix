"""
Advanced State Coordination
Distributed state management and consensus for multi-agent systems
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging


class CoordinationMode(Enum):
    """State coordination modes"""
    CENTRALIZED = "centralized"      # Single source of truth
    DISTRIBUTED = "distributed"      # Each agent maintains state
    CONSENSUS = "consensus"          # Quorum-based agreement
    EVENTUAL = "eventual"            # Eventual consistency


class ConsensusStrategy(Enum):
    """Consensus algorithms"""
    RAFT = "raft"                    # Leader-based
    PAXOS = "paxos"                  # Multi-phase
    BYZANTINE = "byzantine"         # Byzantine fault tolerant
    VOTING = "voting"                # Simple majority vote


@dataclass
class StateChange:
    """Record of state change"""
    
    agent_id: str
    old_state: str
    new_state: str
    timestamp: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'old_state': self.old_state,
            'new_state': self.new_state,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason,
            'metadata': self.metadata
        }


@dataclass
class StateVersion:
    """Versioned state snapshot"""
    
    version_number: int
    state: Dict[str, Any]
    agent_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute hash of state"""
        import hashlib
        state_str = str(sorted(self.state.items()))
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'version_number': self.version_number,
            'state': self.state,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp.isoformat(),
            'hash': self.hash or self.compute_hash()
        }


class StateCoordinator:
    """Coordinates state across multiple agents"""
    
    def __init__(self, coordination_mode: CoordinationMode = CoordinationMode.DISTRIBUTED):
        self.logger = logging.getLogger(__name__)
        self.mode = coordination_mode
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.state_versions: Dict[str, List[StateVersion]] = {}
        self.state_changes: List[StateChange] = []
        self.state_subscribers: Dict[str, List[Callable]] = {}
        self.max_changes_log = 50000
        self.max_versions_per_agent = 1000
    
    def register_state(self, agent_id: str, initial_state: Dict[str, Any]):
        """Register agent state"""
        self.agent_states[agent_id] = initial_state
        self.state_versions[agent_id] = [
            StateVersion(
                version_number=1,
                state=initial_state.copy(),
                agent_id=agent_id
            )
        ]
        self.logger.info(f"State registered for agent: {agent_id}")
    
    def get_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of agent"""
        return self.agent_states.get(agent_id)
    
    def update_state(self, agent_id: str, new_state: Dict[str, Any],
                    reason: Optional[str] = None) -> bool:
        """Update agent state"""
        if agent_id not in self.agent_states:
            return False
        
        old_state = self.agent_states[agent_id]
        self.agent_states[agent_id] = new_state.copy()
        
        # Record change
        change = StateChange(
            agent_id=agent_id,
            old_state=str(old_state),
            new_state=str(new_state),
            reason=reason
        )
        self.state_changes.append(change)
        
        # Trim log
        if len(self.state_changes) > self.max_changes_log:
            self.state_changes = self.state_changes[-self.max_changes_log:]
        
        # Record version
        next_version = len(self.state_versions.get(agent_id, [])) + 1
        version = StateVersion(
            version_number=next_version,
            state=new_state.copy(),
            agent_id=agent_id
        )
        
        if agent_id not in self.state_versions:
            self.state_versions[agent_id] = []
        
        self.state_versions[agent_id].append(version)
        
        # Trim versions
        if len(self.state_versions[agent_id]) > self.max_versions_per_agent:
            self.state_versions[agent_id] = \
                self.state_versions[agent_id][-self.max_versions_per_agent:]
        
        # Notify subscribers
        self._notify_subscribers(agent_id, change)
        
        self.logger.info(f"State updated for agent {agent_id}: {reason}")
        return True
    
    def subscribe_to_state_changes(self, agent_id: str, callback: Callable):
        """Subscribe to state changes"""
        if agent_id not in self.state_subscribers:
            self.state_subscribers[agent_id] = []
        self.state_subscribers[agent_id].append(callback)
    
    def _notify_subscribers(self, agent_id: str, change: StateChange):
        """Notify subscribers of state change"""
        if agent_id in self.state_subscribers:
            for callback in self.state_subscribers[agent_id]:
                try:
                    callback(change)
                except Exception as e:
                    self.logger.error(f"Subscriber callback error: {e}")
    
    def get_state_history(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Get state change history for agent"""
        changes = [c for c in self.state_changes if c.agent_id == agent_id]
        return [c.to_dict() for c in changes[-limit:]]
    
    def get_state_versions(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Get state versions for agent"""
        if agent_id not in self.state_versions:
            return []
        versions = self.state_versions[agent_id][-limit:]
        return [v.to_dict() for v in versions]
    
    def get_all_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Get current state of all agents"""
        return {aid: state.copy() for aid, state in self.agent_states.items()}


class ConsensusManager:
    """Manages consensus-based state coordination"""
    
    def __init__(self, strategy: ConsensusStrategy = ConsensusStrategy.VOTING,
                 min_majority: float = 0.5):
        self.logger = logging.getLogger(__name__)
        self.strategy = strategy
        self.min_majority = min_majority
        self.voting_rounds: Dict[str, 'VotingRound'] = {}
        self.consensus_history: List[Dict[str, Any]] = []
        self.max_history = 10000
    
    def start_voting_round(self, proposal_id: str, proposer_id: str,
                          proposal: Dict[str, Any], voters: Set[str]) -> 'VotingRound':
        """Start a voting round"""
        round_obj = VotingRound(proposal_id, proposer_id, proposal, voters)
        self.voting_rounds[proposal_id] = round_obj
        self.logger.info(f"Voting round started: {proposal_id} by {proposer_id}")
        return round_obj
    
    def cast_vote(self, proposal_id: str, voter_id: str, vote: bool,
                  reason: Optional[str] = None) -> bool:
        """Cast vote in voting round"""
        if proposal_id not in self.voting_rounds:
            return False
        
        round_obj = self.voting_rounds[proposal_id]
        if voter_id not in round_obj.voters:
            return False
        
        round_obj.cast_vote(voter_id, vote, reason)
        
        # Check if consensus reached
        if round_obj.has_consensus(self.min_majority):
            result = round_obj.finalize()
            self._record_consensus(result)
            del self.voting_rounds[proposal_id]
        
        return True
    
    def _record_consensus(self, result: Dict[str, Any]):
        """Record consensus decision"""
        record = {
            'timestamp': datetime.now(),
            'proposal_id': result['proposal_id'],
            'consensus_reached': result['consensus_reached'],
            'votes_for': result['votes_for'],
            'votes_against': result['votes_against']
        }
        self.consensus_history.append(record)
        
        # Trim history
        if len(self.consensus_history) > self.max_history:
            self.consensus_history = self.consensus_history[-self.max_history:]
    
    def get_voting_round_status(self, proposal_id: str) -> Optional[Dict]:
        """Get status of voting round"""
        if proposal_id not in self.voting_rounds:
            return None
        
        round_obj = self.voting_rounds[proposal_id]
        return {
            'proposal_id': proposal_id,
            'voters_count': len(round_obj.voters),
            'votes_received': len(round_obj.votes),
            'votes_for': sum(1 for v in round_obj.votes.values() if v),
            'votes_against': sum(1 for v in round_obj.votes.values() if not v),
            'votes_abstain': len(round_obj.voters) - len(round_obj.votes)
        }


@dataclass
class VotingRound:
    """Single voting round for consensus"""
    
    proposal_id: str
    proposer_id: str
    proposal: Dict[str, Any]
    voters: Set[str]
    created_at: datetime = field(default_factory=datetime.now)
    votes: Dict[str, bool] = field(default_factory=dict)  # voter_id -> vote
    vote_reasons: Dict[str, Optional[str]] = field(default_factory=dict)
    
    def cast_vote(self, voter_id: str, vote: bool, reason: Optional[str] = None):
        """Cast a vote"""
        if voter_id in self.voters:
            self.votes[voter_id] = vote
            self.vote_reasons[voter_id] = reason
    
    def has_consensus(self, min_majority: float) -> bool:
        """Check if consensus reached"""
        if not self.votes:
            return False
        
        votes_for = sum(1 for v in self.votes.values() if v)
        total_votes = len(self.votes)
        
        return (votes_for / total_votes) >= min_majority
    
    def finalize(self) -> Dict[str, Any]:
        """Finalize voting round"""
        votes_for = sum(1 for v in self.votes.values() if v)
        votes_against = len(self.votes) - votes_for
        
        return {
            'proposal_id': self.proposal_id,
            'proposer_id': self.proposer_id,
            'consensus_reached': len(self.votes) > 0,
            'votes_for': votes_for,
            'votes_against': votes_against,
            'total_votes': len(self.votes),
            'approved': votes_for > votes_against,
            'finalized_at': datetime.now().isoformat()
        }


class DistributedLock:
    """Distributed lock for coordinating access"""
    
    def __init__(self, lock_id: str, max_hold_time_seconds: int = 30):
        self.lock_id = lock_id
        self.owner_id: Optional[str] = None
        self.acquired_at: Optional[datetime] = None
        self.max_hold_time = max_hold_time_seconds
        self.lock_count = 0
    
    def acquire(self, agent_id: str) -> bool:
        """Attempt to acquire lock"""
        if self.owner_id is None:
            self.owner_id = agent_id
            self.acquired_at = datetime.now()
            self.lock_count += 1
            return True
        
        # Check if lock has expired
        if self.owner_id is not None and self.acquired_at is not None:
            elapsed = (datetime.now() - self.acquired_at).total_seconds()
            if elapsed > self.max_hold_time:
                # Lock expired, transfer ownership
                self.owner_id = agent_id
                self.acquired_at = datetime.now()
                self.lock_count += 1
                return True
        
        return False
    
    def release(self, agent_id: str) -> bool:
        """Release lock"""
        if self.owner_id == agent_id:
            self.owner_id = None
            self.acquired_at = None
            return True
        return False
    
    def is_held(self) -> bool:
        """Check if lock is held"""
        if self.owner_id is None:
            return False
        
        if self.acquired_at is not None:
            elapsed = (datetime.now() - self.acquired_at).total_seconds()
            if elapsed > self.max_hold_time:
                self.owner_id = None
                self.acquired_at = None
                return False
        
        return True
    
    def get_holder(self) -> Optional[str]:
        """Get current lock holder"""
        if self.is_held():
            return self.owner_id
        return None


class DistributedLockManager:
    """Manages distributed locks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.locks: Dict[str, DistributedLock] = {}
    
    def create_lock(self, lock_id: str, max_hold_time: int = 30) -> DistributedLock:
        """Create a new lock"""
        lock = DistributedLock(lock_id, max_hold_time)
        self.locks[lock_id] = lock
        self.logger.info(f"Lock created: {lock_id}")
        return lock
    
    def acquire_lock(self, lock_id: str, agent_id: str) -> bool:
        """Acquire a lock"""
        if lock_id not in self.locks:
            self.create_lock(lock_id)
        
        success = self.locks[lock_id].acquire(agent_id)
        if success:
            self.logger.info(f"Lock acquired: {lock_id} by {agent_id}")
        return success
    
    def release_lock(self, lock_id: str, agent_id: str) -> bool:
        """Release a lock"""
        if lock_id not in self.locks:
            return False
        
        success = self.locks[lock_id].release(agent_id)
        if success:
            self.logger.info(f"Lock released: {lock_id} by {agent_id}")
        return success
    
    def get_lock_status(self, lock_id: str) -> Optional[Dict]:
        """Get lock status"""
        if lock_id not in self.locks:
            return None
        
        lock = self.locks[lock_id]
        return {
            'lock_id': lock_id,
            'is_held': lock.is_held(),
            'holder': lock.get_holder(),
            'acquired_at': lock.acquired_at.isoformat() if lock.acquired_at else None,
            'lock_count': lock.lock_count
        }
