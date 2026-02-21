"""
Agent Communication Protocol - Module 4.1

Implements protocol design, message serialization/deserialization,
distributed consensus algorithms, network partition handling,
and communication security for multi-agent systems.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
from datetime import datetime, timedelta
import threading
from collections import defaultdict


class CommunicationProtocol(Enum):
    """Supported communication protocols"""
    REQUEST_REPLY = "request_reply"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    BROADCAST = "broadcast"
    DIRECT_MESSAGE = "direct_message"
    CONSENSUS = "consensus"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    DEFERRED = 5


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    RECEIVED = "received"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    DELIVERED = "delivered"


@dataclass
class CommunicationMessage:
    """Message format for inter-agent communication"""
    message_id: str
    sender_id: str
    recipient_id: str
    protocol: CommunicationProtocol
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    expiry: Optional[float] = None
    requires_ack: bool = True
    requires_response: bool = False
    signature: Optional[str] = None
    encryption_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ConsensusProposal:
    """Proposal for consensus mechanism"""
    proposal_id: str
    proposer_id: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    votes: Dict[str, bool] = field(default_factory=dict)
    consensus_threshold: float = 0.67
    timeout: float = 30.0
    status: str = "proposed"


class MessageSerializer:
    """Handles message serialization and deserialization"""

    @staticmethod
    def serialize(message: CommunicationMessage) -> str:
        """Serialize message to JSON"""
        msg_dict = {
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "protocol": message.protocol.value,
            "priority": message.priority.value,
            "content": message.content,
            "timestamp": message.timestamp,
            "expiry": message.expiry,
            "requires_ack": message.requires_ack,
            "requires_response": message.requires_response,
            "signature": message.signature,
            "metadata": message.metadata,
            "status": message.status.value,
            "retry_count": message.retry_count
        }
        return json.dumps(msg_dict)

    @staticmethod
    def deserialize(data: str) -> CommunicationMessage:
        """Deserialize message from JSON"""
        msg_dict = json.loads(data)
        return CommunicationMessage(
            message_id=msg_dict["message_id"],
            sender_id=msg_dict["sender_id"],
            recipient_id=msg_dict["recipient_id"],
            protocol=CommunicationProtocol(msg_dict["protocol"]),
            priority=MessagePriority(msg_dict["priority"]),
            content=msg_dict["content"],
            timestamp=msg_dict["timestamp"],
            expiry=msg_dict.get("expiry"),
            requires_ack=msg_dict.get("requires_ack", True),
            requires_response=msg_dict.get("requires_response", False),
            signature=msg_dict.get("signature"),
            metadata=msg_dict.get("metadata", {}),
            status=MessageStatus(msg_dict.get("status", "pending")),
            retry_count=msg_dict.get("retry_count", 0)
        )


class MessageSecurity:
    """Handles message encryption and signing"""

    @staticmethod
    def sign_message(message: CommunicationMessage, secret_key: str) -> str:
        """Sign message with HMAC"""
        message_data = (
            f"{message.sender_id}{message.recipient_id}"
            f"{message.timestamp}{json.dumps(message.content, sort_keys=True)}"
        )
        signature = hashlib.sha256(
            f"{message_data}{secret_key}".encode()
        ).hexdigest()
        return signature

    @staticmethod
    def verify_signature(message: CommunicationMessage, secret_key: str) -> bool:
        """Verify message signature"""
        expected_signature = MessageSecurity.sign_message(message, secret_key)
        return message.signature == expected_signature

    @staticmethod
    def encrypt_content(content: Dict[str, Any], key: str) -> str:
        """Encrypt message content (simplified)"""
        json_content = json.dumps(content)
        return hashlib.sha256(
            f"{json_content}{key}".encode()
        ).hexdigest()


class ProtocolHandler:
    """Handles different communication protocols"""

    def __init__(self):
        self.handlers = {}
        self.subscriptions = defaultdict(list)
        self.broadcast_buffer = []

    def register_handler(self, protocol: CommunicationProtocol,
                        handler: Callable):
        """Register handler for protocol"""
        self.handlers[protocol] = handler

    def handle_request_reply(self, message: CommunicationMessage,
                            responder: Callable) -> Optional[CommunicationMessage]:
        """Handle request-reply protocol"""
        response_content = responder(message.content)
        response = CommunicationMessage(
            message_id=f"{message.message_id}_response",
            sender_id=message.recipient_id,
            recipient_id=message.sender_id,
            protocol=CommunicationProtocol.REQUEST_REPLY,
            priority=message.priority,
            content=response_content,
            requires_ack=False
        )
        return response

    def subscribe_to_topic(self, topic: str, agent_id: str,
                          callback: Callable):
        """Subscribe agent to topic for publish-subscribe"""
        self.subscriptions[topic].append({
            "agent_id": agent_id,
            "callback": callback
        })

    def publish_to_topic(self, topic: str, message: CommunicationMessage):
        """Publish message to all subscribers"""
        for subscription in self.subscriptions[topic]:
            subscription["callback"](message)

    def broadcast_message(self, message: CommunicationMessage,
                         agent_ids: List[str]):
        """Broadcast message to multiple agents"""
        for agent_id in agent_ids:
            broadcast_msg = CommunicationMessage(
                message_id=f"{message.message_id}_{agent_id}",
                sender_id=message.sender_id,
                recipient_id=agent_id,
                protocol=CommunicationProtocol.BROADCAST,
                priority=message.priority,
                content=message.content
            )
            self.broadcast_buffer.append(broadcast_msg)


class ConsensusAlgorithm:
    """Implements distributed consensus mechanism"""

    def __init__(self, consensus_type: str = "byzantine"):
        self.consensus_type = consensus_type
        self.proposals: Dict[str, ConsensusProposal] = {}
        self.completed_proposals: List[str] = []

    def submit_proposal(self, proposal: ConsensusProposal):
        """Submit proposal for consensus"""
        self.proposals[proposal.proposal_id] = proposal

    def cast_vote(self, proposal_id: str, voter_id: str,
                  vote: bool) -> bool:
        """Cast vote on proposal"""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        proposal.votes[voter_id] = vote

        # Check if consensus reached
        total_votes = len(proposal.votes)
        affirmative_votes = sum(1 for v in proposal.votes.values() if v)

        if total_votes > 0:
            agreement_ratio = affirmative_votes / total_votes
            if agreement_ratio >= proposal.consensus_threshold:
                proposal.status = "consensus_reached"
                self.completed_proposals.append(proposal_id)
                return True

        return False

    def has_consensus(self, proposal_id: str) -> bool:
        """Check if proposal has reached consensus"""
        return (proposal_id in self.proposals and
                self.proposals[proposal_id].status == "consensus_reached")

    def handle_network_partition(self, partition_members: Set[str],
                                isolated_members: Set[str]):
        """Handle network partition by suspending consensus until healed"""
        for proposal_id, proposal in self.proposals.items():
            if proposal.status == "proposed":
                # Only allow consensus if partition has majority
                total_agents = len(partition_members) + len(isolated_members)
                if len(partition_members) < total_agents / 2:
                    proposal.status = "suspended"


class NetworkPartitionDetector:
    """Detects and handles network partitions"""

    def __init__(self, heartbeat_timeout: float = 5.0):
        self.heartbeat_timeout = heartbeat_timeout
        self.last_heartbeat: Dict[str, float] = {}
        self.suspected_dead: Set[str] = set()
        self.partitions: List[Set[str]] = []

    def record_heartbeat(self, agent_id: str):
        """Record heartbeat from agent"""
        self.last_heartbeat[agent_id] = time.time()
        if agent_id in self.suspected_dead:
            self.suspected_dead.remove(agent_id)

    def detect_partitions(self, all_agents: Set[str]) -> Optional[Set[str]]:
        """Detect if partition has occurred"""
        current_time = time.time()
        dead_agents = set()

        for agent_id in all_agents:
            last_beat = self.last_heartbeat.get(agent_id, current_time)
            if current_time - last_beat > self.heartbeat_timeout:
                dead_agents.add(agent_id)
                self.suspected_dead.add(agent_id)

        if dead_agents and len(all_agents - dead_agents) > 0:
            return dead_agents

        return None

    def is_partition_healed(self) -> bool:
        """Check if partition has healed"""
        return len(self.suspected_dead) == 0


class AgentCommunicationManager:
    """Central manager for agent communication"""

    def __init__(self):
        self.protocol_handler = ProtocolHandler()
        self.serializer = MessageSerializer()
        self.security = MessageSecurity()
        self.consensus = ConsensusAlgorithm()
        self.partition_detector = NetworkPartitionDetector()
        self.message_queue: List[CommunicationMessage] = []
        self.delivery_confirmations: Dict[str, float] = {}
        self.message_history: List[CommunicationMessage] = []
        self.lock = threading.RLock()

    def send_message(self, message: CommunicationMessage,
                    secret_key: Optional[str] = None) -> bool:
        """Send message through appropriate protocol"""
        with self.lock:
            # Sign message if key provided
            if secret_key:
                message.signature = self.security.sign_message(
                    message, secret_key
                )

            # Route based on protocol
            if message.protocol == CommunicationProtocol.REQUEST_REPLY:
                self.message_queue.append(message)
            elif message.protocol == CommunicationProtocol.PUBLISH_SUBSCRIBE:
                self.protocol_handler.publish_to_topic(
                    message.content.get("topic", "default"),
                    message
                )
            elif message.protocol == CommunicationProtocol.BROADCAST:
                self.protocol_handler.broadcast_message(
                    message,
                    message.content.get("recipients", [])
                )

            self.message_history.append(message)
            message.status = MessageStatus.SENT
            return True

    def receive_message(self, message: CommunicationMessage) -> bool:
        """Receive and acknowledge message"""
        with self.lock:
            message.status = MessageStatus.RECEIVED

            # Verify signature if present
            if message.signature:
                if not self.security.verify_signature(message, "default_key"):
                    return False

            if message.requires_ack:
                self.delivery_confirmations[message.message_id] = time.time()
                message.status = MessageStatus.ACKNOWLEDGED

            self.message_history.append(message)
            return True

    def get_message_queue(self) -> List[CommunicationMessage]:
        """Get pending messages"""
        with self.lock:
            pending = [m for m in self.message_queue
                      if m.status == MessageStatus.SENT]
            return pending

    def clear_expired_messages(self):
        """Remove expired messages"""
        with self.lock:
            current_time = time.time()
            self.message_queue = [
                m for m in self.message_queue
                if m.expiry is None or m.expiry > current_time
            ]

    def get_communication_metrics(self) -> Dict[str, Any]:
        """Get communication performance metrics"""
        with self.lock:
            total_messages = len(self.message_history)
            delivered = sum(
                1 for m in self.message_history
                if m.status == MessageStatus.DELIVERED
            )
            failed = sum(
                1 for m in self.message_history
                if m.status == MessageStatus.FAILED
            )

            return {
                "total_messages": total_messages,
                "delivered_messages": delivered,
                "failed_messages": failed,
                "delivery_rate": (delivered / total_messages
                                 if total_messages > 0 else 0.0),
                "queue_size": len(self.message_queue),
                "confirmations": len(self.delivery_confirmations)
            }
