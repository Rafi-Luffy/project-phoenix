"""
Enhanced Message Protocol System
Advanced messaging patterns for inter-agent communication
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging


class MessageProtocol(Enum):
    """Advanced messaging protocols"""
    REQUEST_REPLY = "request_reply"           # Standard synchronous
    PUBLISH_SUBSCRIBE = "publish_subscribe"   # Event-based
    FIRE_AND_FORGET = "fire_and_forget"       # Asynchronous
    REQUEST_WAIT_REPLY = "request_wait_reply" # With acknowledgment
    BATCH_PROCESS = "batch_process"           # Batch messages
    STREAMING = "streaming"                   # Continuous stream


class AcknowledgmentStatus(Enum):
    """Message acknowledgment status"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    PROCESSED = "processed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class MessageMetadata:
    """Metadata for enhanced message tracking"""
    
    message_id: str
    correlation_id: Optional[str] = None      # Links related messages
    conversation_id: Optional[str] = None     # Groups conversation messages
    protocol: MessageProtocol = MessageProtocol.REQUEST_REPLY
    
    # Delivery tracking
    delivery_attempts: int = 0
    max_retries: int = 3
    retry_delay_ms: int = 1000
    
    # Acknowledgment tracking
    ack_status: AcknowledgmentStatus = AcknowledgmentStatus.PENDING
    ack_timeout_seconds: int = 30
    ack_received_at: Optional[datetime] = None
    
    # Expiration
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if message expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def needs_retry(self) -> bool:
        """Check if message needs retry"""
        return self.delivery_attempts < self.max_retries and \
               self.ack_status == AcknowledgmentStatus.PENDING
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'correlation_id': self.correlation_id,
            'conversation_id': self.conversation_id,
            'protocol': self.protocol.value,
            'delivery_attempts': self.delivery_attempts,
            'ack_status': self.ack_status.value,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class AcknowledgmentMessage:
    """Acknowledgment of message receipt"""
    
    original_message_id: str
    acknowledging_agent_id: str
    status: AcknowledgmentStatus
    timestamp: datetime = field(default_factory=datetime.now)
    error_details: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'original_message_id': self.original_message_id,
            'acknowledging_agent_id': self.acknowledging_agent_id,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'error_details': self.error_details
        }


class MessageProtocolHandler:
    """Handles different messaging protocols"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.protocol_handlers: Dict[MessageProtocol, Callable] = {}
        self.pending_acks: Dict[str, MessageMetadata] = {}
        self.message_conversations: Dict[str, List[Dict]] = {}  # conversation_id -> messages
        self.max_conversation_size = 1000
    
    def register_protocol_handler(self, protocol: MessageProtocol, handler: Callable):
        """Register handler for protocol"""
        self.protocol_handlers[protocol] = handler
        self.logger.info(f"Protocol handler registered: {protocol.value}")
    
    async def send_with_protocol(self, message: Dict[str, Any], 
                                protocol: MessageProtocol,
                                metadata: Optional[MessageMetadata] = None) -> Dict[str, Any]:
        """Send message using specified protocol"""
        
        if protocol not in self.protocol_handlers:
            return {
                'status': 'error',
                'error': f'No handler for protocol: {protocol.value}'
            }
        
        handler = self.protocol_handlers[protocol]
        return await handler(message, metadata)
    
    def track_acknowledgment(self, metadata: MessageMetadata):
        """Track message for acknowledgment"""
        self.pending_acks[metadata.message_id] = metadata
    
    def acknowledge_message(self, message_id: str, status: AcknowledgmentStatus,
                           agent_id: str) -> AcknowledgmentMessage:
        """Acknowledge receipt of message"""
        ack = AcknowledgmentMessage(
            original_message_id=message_id,
            acknowledging_agent_id=agent_id,
            status=status
        )
        
        if message_id in self.pending_acks:
            metadata = self.pending_acks[message_id]
            metadata.ack_status = status
            metadata.ack_received_at = datetime.now()
        
        return ack
    
    def add_to_conversation(self, conversation_id: str, message: Dict[str, Any]):
        """Add message to conversation thread"""
        if conversation_id not in self.message_conversations:
            self.message_conversations[conversation_id] = []
        
        self.message_conversations[conversation_id].append(message)
        
        # Trim if exceeding max
        if len(self.message_conversations[conversation_id]) > self.max_conversation_size:
            self.message_conversations[conversation_id] = \
                self.message_conversations[conversation_id][-self.max_conversation_size:]
    
    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a conversation"""
        return self.message_conversations.get(conversation_id, [])
    
    def get_pending_acknowledgments(self) -> List[MessageMetadata]:
        """Get all pending acknowledgments"""
        pending = []
        expired_ids = []
        
        for msg_id, metadata in self.pending_acks.items():
            if metadata.is_expired() or metadata.ack_status != AcknowledgmentStatus.PENDING:
                expired_ids.append(msg_id)
            else:
                pending.append(metadata)
        
        # Clean up expired
        for msg_id in expired_ids:
            del self.pending_acks[msg_id]
        
        return pending
    
    def retry_failed_messages(self) -> List[str]:
        """Retry messages that need it"""
        retry_ids = []
        
        for msg_id, metadata in self.pending_acks.items():
            if metadata.needs_retry() and not metadata.is_expired():
                metadata.delivery_attempts += 1
                retry_ids.append(msg_id)
                self.logger.info(f"Retrying message: {msg_id} " +
                               f"(attempt {metadata.delivery_attempts}/{metadata.max_retries})")
        
        return retry_ids


class ConversationManager:
    """Manages multi-message conversations between agents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_conversations: Dict[str, 'Conversation'] = {}
        self.completed_conversations: List['Conversation'] = []
        self.max_completed = 5000
    
    def start_conversation(self, conversation_id: str, initiator_id: str,
                          participants: List[str], subject: str) -> 'Conversation':
        """Start a new conversation"""
        conv = Conversation(conversation_id, initiator_id, participants, subject)
        self.active_conversations[conversation_id] = conv
        self.logger.info(f"Conversation started: {conversation_id}")
        return conv
    
    def add_message_to_conversation(self, conversation_id: str, sender_id: str,
                                   content: Dict[str, Any]):
        """Add message to active conversation"""
        if conversation_id in self.active_conversations:
            conv = self.active_conversations[conversation_id]
            conv.add_message(sender_id, content)
    
    def end_conversation(self, conversation_id: str) -> Optional['Conversation']:
        """End active conversation"""
        if conversation_id in self.active_conversations:
            conv = self.active_conversations[conversation_id]
            conv.end()
            self.completed_conversations.append(conv)
            del self.active_conversations[conversation_id]
            
            # Trim completed
            if len(self.completed_conversations) > self.max_completed:
                self.completed_conversations = self.completed_conversations[-self.max_completed:]
            
            self.logger.info(f"Conversation ended: {conversation_id}")
            return conv
        
        return None
    
    def get_conversation(self, conversation_id: str) -> Optional['Conversation']:
        """Get conversation by ID"""
        return self.active_conversations.get(conversation_id)
    
    def get_agent_conversations(self, agent_id: str) -> List['Conversation']:
        """Get all conversations involving agent"""
        conversations = []
        
        for conv in self.active_conversations.values():
            if agent_id in conv.participants or conv.initiator_id == agent_id:
                conversations.append(conv)
        
        return conversations


@dataclass
class ConversationMessage:
    """Single message in conversation"""
    
    sender_id: str
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(__import__('uuid').uuid4()))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


class Conversation:
    """Multi-message conversation between agents"""
    
    def __init__(self, conversation_id: str, initiator_id: str,
                 participants: List[str], subject: str):
        self.conversation_id = conversation_id
        self.initiator_id = initiator_id
        self.participants = set(participants)
        self.subject = subject
        self.messages: List[ConversationMessage] = []
        self.created_at = datetime.now()
        self.ended_at: Optional[datetime] = None
        self.status = 'active'
    
    def add_message(self, sender_id: str, content: Dict[str, Any]):
        """Add message to conversation"""
        if sender_id not in self.participants and sender_id != self.initiator_id:
            raise ValueError(f"Agent {sender_id} not in conversation participants")
        
        msg = ConversationMessage(sender_id, content)
        self.messages.append(msg)
    
    def end(self):
        """End conversation"""
        self.ended_at = datetime.now()
        self.status = 'completed'
    
    def get_messages_from(self, agent_id: str) -> List[ConversationMessage]:
        """Get all messages from specific agent"""
        return [m for m in self.messages if m.sender_id == agent_id]
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'conversation_id': self.conversation_id,
            'initiator_id': self.initiator_id,
            'participants': list(self.participants),
            'subject': self.subject,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'message_count': len(self.messages),
            'messages': [m.to_dict() for m in self.messages]
        }


class ProtocolEndpoint:
    """Endpoint for handling protocol-specific communication"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"ProtocolEndpoint-{agent_id}")
        self.supported_protocols = [
            MessageProtocol.REQUEST_REPLY,
            MessageProtocol.REQUEST_WAIT_REPLY,
            MessageProtocol.FIRE_AND_FORGET
        ]
    
    async def handle_request_reply(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request-reply pattern"""
        # Send and wait for response
        return {'status': 'acknowledged', 'message_id': message.get('message_id')}
    
    async def handle_fire_and_forget(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle fire-and-forget pattern"""
        # Send without waiting for response
        return {'status': 'sent', 'message_id': message.get('message_id')}
    
    async def handle_request_wait_reply(self, message: Dict[str, Any],
                                       timeout_seconds: int = 30) -> Dict[str, Any]:
        """Handle request with acknowledgment"""
        # Send and wait for acknowledgment
        return {'status': 'sent', 'message_id': message.get('message_id')}
    
    def supports_protocol(self, protocol: MessageProtocol) -> bool:
        """Check if protocol is supported"""
        return protocol in self.supported_protocols
