"""
Streaming Response System

Enable real-time streaming of LLM responses:
- Server-Sent Events (SSE)
- WebSocket streaming
- Chunked transfer encoding
- Response buffering and flushing
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class StreamFormat(Enum):
    """Response streaming formats"""
    SSE = "sse"              # Server-Sent Events
    WEBSOCKET = "websocket"
    CHUNKED = "chunked"
    JSON_LINES = "jsonlines"
    TEXT = "text"


@dataclass
class StreamChunk:
    """Represents a chunk of streamed data"""
    id: str
    sequence: int
    content: str
    timestamp: datetime
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class StreamBuffer:
    """Buffer for managing stream chunks"""
    
    def __init__(self, flush_size: int = 1024, flush_timeout_ms: int = 50):
        self.flush_size = flush_size
        self.flush_timeout_ms = flush_timeout_ms
        self.buffer: List[str] = []
        self.buffer_size = 0
        self.last_flush = datetime.now()
    
    def add(self, data: str) -> bool:
        """Add data to buffer"""
        self.buffer.append(data)
        self.buffer_size += len(data)
        
        return self.should_flush()
    
    def should_flush(self) -> bool:
        """Check if buffer should be flushed"""
        if self.buffer_size >= self.flush_size:
            return True
        
        elapsed_ms = (datetime.now() - self.last_flush).total_seconds() * 1000
        if elapsed_ms >= self.flush_timeout_ms and self.buffer:
            return True
        
        return False
    
    def flush(self) -> str:
        """Get buffered data and clear buffer"""
        data = "".join(self.buffer)
        self.buffer.clear()
        self.buffer_size = 0
        self.last_flush = datetime.now()
        
        return data
    
    def force_flush(self) -> str:
        """Force flush regardless of size"""
        return self.flush()


class StreamResponseFormatter:
    """Format stream responses in different formats"""
    
    @staticmethod
    def format_sse(chunk: StreamChunk) -> str:
        """Format as Server-Sent Event"""
        data = {
            "id": chunk.id,
            "sequence": chunk.sequence,
            "content": chunk.content,
            "timestamp": chunk.timestamp.isoformat(),
            "is_final": chunk.is_final
        }
        
        if chunk.metadata:
            data["metadata"] = chunk.metadata
        
        return f"data: {json.dumps(data)}\n\n"
    
    @staticmethod
    def format_websocket(chunk: StreamChunk) -> str:
        """Format for WebSocket"""
        data = {
            "type": "stream",
            "id": chunk.id,
            "sequence": chunk.sequence,
            "content": chunk.content,
            "is_final": chunk.is_final
        }
        
        if chunk.metadata:
            data["metadata"] = chunk.metadata
        
        return json.dumps(data)
    
    @staticmethod
    def format_chunked(chunk: StreamChunk) -> str:
        """Format as chunked transfer encoding"""
        size_hex = hex(len(chunk.content))[2:]
        return f"{size_hex}\r\n{chunk.content}\r\n"
    
    @staticmethod
    def format_jsonlines(chunk: StreamChunk) -> str:
        """Format as JSON Lines"""
        data = {
            "id": chunk.id,
            "sequence": chunk.sequence,
            "content": chunk.content,
            "is_final": chunk.is_final
        }
        
        if chunk.metadata:
            data["metadata"] = chunk.metadata
        
        return json.dumps(data) + "\n"
    
    @staticmethod
    def format_text(chunk: StreamChunk) -> str:
        """Format as plain text"""
        return chunk.content


class StreamingResponse:
    """Manages streaming responses"""
    
    def __init__(
        self,
        stream_id: str,
        format: StreamFormat = StreamFormat.SSE,
        chunk_size: int = 1024
    ):
        self.stream_id = stream_id
        self.format = format
        self.chunk_size = chunk_size
        self.buffer = StreamBuffer(flush_size=chunk_size)
        self.sequence = 0
        self.callbacks: List[Callable[[str], Any]] = []
    
    def register_callback(self, callback: Callable[[str], Any]):
        """Register callback for chunk output"""
        self.callbacks.append(callback)
    
    async def write_chunk(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Write a chunk to the stream"""
        self.sequence += 1
        
        chunk = StreamChunk(
            id=self.stream_id,
            sequence=self.sequence,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        # Format chunk
        formatted = self._format_chunk(chunk)
        
        # Add to buffer
        if self.buffer.add(formatted):
            await self._flush_buffer()
        
        # Trigger callbacks
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(formatted)
                else:
                    callback(formatted)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def _flush_buffer(self):
        """Flush buffered content"""
        data = self.buffer.flush()
        
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    async def finish(self, metadata: Optional[Dict[str, Any]] = None):
        """Mark stream as finished"""
        self.sequence += 1
        
        chunk = StreamChunk(
            id=self.stream_id,
            sequence=self.sequence,
            content="",
            timestamp=datetime.now(),
            is_final=True,
            metadata=metadata
        )
        
        formatted = self._format_chunk(chunk)
        await self._flush_buffer()
        
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(formatted)
                else:
                    callback(formatted)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def _format_chunk(self, chunk: StreamChunk) -> str:
        """Format chunk based on stream format"""
        if self.format == StreamFormat.SSE:
            return StreamResponseFormatter.format_sse(chunk)
        elif self.format == StreamFormat.WEBSOCKET:
            return StreamResponseFormatter.format_websocket(chunk)
        elif self.format == StreamFormat.CHUNKED:
            return StreamResponseFormatter.format_chunked(chunk)
        elif self.format == StreamFormat.JSON_LINES:
            return StreamResponseFormatter.format_jsonlines(chunk)
        else:
            return StreamResponseFormatter.format_text(chunk)


class StreamingLLMResponse:
    """Streaming wrapper for LLM responses"""
    
    def __init__(self, llm_generator: AsyncGenerator[str, None], stream_id: str):
        self.llm_generator = llm_generator
        self.stream_id = stream_id
        self.full_response = ""
        self.token_count = 0
    
    async def stream_with_format(
        self,
        format: StreamFormat = StreamFormat.SSE,
        chunk_size: int = 100
    ) -> AsyncGenerator[str, None]:
        """Stream with specific format"""
        response = StreamingResponse(self.stream_id, format, chunk_size)
        
        try:
            async for token in self.llm_generator:
                self.full_response += token
                self.token_count += 1
                
                await response.write_chunk(token)
            
            # Send completion
            metadata = {
                "total_tokens": self.token_count,
                "response_length": len(self.full_response)
            }
            await response.finish(metadata)
        
        except Exception as e:
            await response.finish(metadata={"error": str(e)})
            raise
    
    async def collect_stream(self) -> str:
        """Collect entire stream into single response"""
        async for _ in self.stream_with_format():
            pass
        
        return self.full_response


class StreamingMetrics:
    """Track streaming response metrics"""
    
    def __init__(self):
        self.streams: Dict[str, Dict[str, Any]] = {}
    
    def start_stream(self, stream_id: str):
        """Mark stream as started"""
        self.streams[stream_id] = {
            "start_time": datetime.now(),
            "chunks": 0,
            "total_bytes": 0,
            "first_chunk_time": None
        }
    
    def record_chunk(self, stream_id: str, chunk_size: int):
        """Record chunk data"""
        if stream_id in self.streams:
            stream = self.streams[stream_id]
            stream["chunks"] += 1
            stream["total_bytes"] += chunk_size
            
            if stream["first_chunk_time"] is None:
                elapsed = (datetime.now() - stream["start_time"]).total_seconds()
                stream["first_chunk_time"] = elapsed
    
    def end_stream(self, stream_id: str):
        """Mark stream as ended"""
        if stream_id in self.streams:
            stream = self.streams[stream_id]
            stream["end_time"] = datetime.now()
            stream["duration"] = (stream["end_time"] - stream["start_time"]).total_seconds()
            stream["throughput"] = stream["total_bytes"] / stream["duration"] if stream["duration"] > 0 else 0
    
    def get_metrics(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for specific stream"""
        return self.streams.get(stream_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary metrics"""
        if not self.streams:
            return {}
        
        completed = [s for s in self.streams.values() if "end_time" in s]
        
        if not completed:
            return {}
        
        total_duration = sum(s["duration"] for s in completed)
        total_bytes = sum(s["total_bytes"] for s in completed)
        total_chunks = sum(s["chunks"] for s in completed)
        
        return {
            "total_streams": len(self.streams),
            "completed_streams": len(completed),
            "total_duration": total_duration,
            "total_bytes": total_bytes,
            "total_chunks": total_chunks,
            "avg_throughput": total_bytes / total_duration if total_duration > 0 else 0,
            "avg_chunk_size": total_bytes / total_chunks if total_chunks > 0 else 0,
            "avg_first_chunk_time": sum(s["first_chunk_time"] for s in completed if s["first_chunk_time"]) / len(completed) if completed else 0
        }


if __name__ == "__main__":
    async def test_streaming():
        # Simulate LLM stream
        async def mock_llm_stream():
            tokens = ["Hello", " ", "world", "!", " ", "This", " ", "is", " ", "streaming"]
            for token in tokens:
                await asyncio.sleep(0.01)
                yield token
        
        # Create streaming response
        stream_response = StreamingLLMResponse(mock_llm_stream(), "test-stream-1")
        
        # Stream with SSE format
        print("=== SSE Format ===")
        async for chunk in stream_response.stream_with_format(StreamFormat.SSE):
            print(chunk, end="")
        
        print(f"\n\nFull response: {stream_response.full_response}")
        print(f"Total tokens: {stream_response.token_count}")
    
    asyncio.run(test_streaming())
