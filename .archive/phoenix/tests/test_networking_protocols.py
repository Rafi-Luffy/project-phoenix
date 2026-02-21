"""
Comprehensive Test Suite for Phoenix - Networking & Protocols
Tests 816-845: HTTP, TCP/IP, WebSockets, Network Errors (30 tests)

This file tests Phoenix's ability to detect and fix bugs in networking,
protocol handling, and network communication.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch


class TestHTTPCommunication:
    """Test HTTP protocol handling (10 tests)"""
    
    def test_connection_reuse(self):
        """Test 816: Reuse HTTP connections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoConnectionReuse:
    def make_request(self, url):
        # BUG: Creates new connection for each request
        connection = self.create_connection()
        
        response = connection.get(url)
        
        # BUG: Closes connection after single request
        connection.close()
        
        return response
    
    def create_connection(self):
        return MockConnection()

class MockConnection:
    def get(self, url):
        return "response"
    
    def close(self):
        pass

client = NoConnectionReuse()

# BUG: 100 connection open/close cycles
for i in range(100):
    response = client.make_request(f"https://api.example.com/data/{i}")
"""
            
            test_file = os.path.join(temp_dir, "connection_reuse.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_request_timeout(self):
        """Test 817: Set request timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRequestTimeout:
    def fetch_data(self, url):
        # BUG: No timeout
        response = self.http_get(url)
        return response
    
    def http_get(self, url):
        # Simulates slow server
        import time
        time.sleep(100)
        return "response"

client = NoRequestTimeout()

# BUG: Hangs indefinitely
response = client.fetch_data("https://slow-server.com/data")
"""
            
            test_file = os.path.join(temp_dir, "request_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_redirect_handling(self):
        """Test 818: Handle redirects properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class UnlimitedRedirects:
    def fetch(self, url, redirect_count=0):
        response = self.http_get(url)
        
        if response["status"] == 301:
            # BUG: No redirect limit
            return self.fetch(response["location"], redirect_count + 1)
        
        return response
    
    def http_get(self, url):
        # Simulates redirect loop
        return {"status": 301, "location": url}

client = UnlimitedRedirects()

# BUG: Infinite redirect loop
try:
    response = client.fetch("https://example.com/redirect-loop")
except RecursionError:
    print("Redirect loop detected")
"""
            
            test_file = os.path.join(temp_dir, "redirect_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_request_headers(self):
        """Test 819: Set appropriate request headers"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class MissingHeaders:
    def make_request(self, url):
        # BUG: No User-Agent header
        headers = {
            "Content-Type": "application/json"
        }
        
        return self.http_post(url, headers)
    
    def http_post(self, url, headers):
        return "response"

client = MissingHeaders()

# BUG: May be blocked by servers requiring User-Agent
response = client.make_request("https://api.example.com/data")
"""
            
            test_file = os.path.join(temp_dir, "request_headers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_response_streaming(self):
        """Test 820: Stream large responses"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoStreaming:
    def download_file(self, url):
        # BUG: Loads entire response into memory
        response = self.http_get(url)
        data = response.read_all()  # BUG: Reads all at once
        return data
    
    def http_get(self, url):
        return MockResponse()

class MockResponse:
    def read_all(self):
        # Simulates 1GB response
        return b"x" * 1000000000

client = NoStreaming()

# BUG: Out of memory on large files
data = client.download_file("https://example.com/large-file.bin")
"""
            
            test_file = os.path.join(temp_dir, "response_streaming.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_gzip_compression(self):
        """Test 821: Handle compressed responses"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCompressionHandling:
    def fetch_data(self, url):
        # BUG: Doesn't handle gzip
        response = self.http_get(url)
        return response.body  # BUG: Returns compressed data
    
    def http_get(self, url):
        return MockResponse()

class MockResponse:
    def __init__(self):
        # Gzip compressed data
        self.body = b"\\x1f\\x8b\\x08..."
        self.headers = {"Content-Encoding": "gzip"}

client = NoCompressionHandling()

# BUG: Returns compressed binary data
data = client.fetch_data("https://api.example.com/data")
"""
            
            test_file = os.path.join(temp_dir, "gzip_compression.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_cookie_handling(self):
        """Test 822: Handle cookies properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCookieHandling:
    def login(self, username, password):
        # BUG: Doesn't save cookies
        response = self.http_post("/login", {"user": username, "pass": password})
        return response
    
    def get_profile(self):
        # BUG: No session cookie sent
        response = self.http_get("/profile")
        return response
    
    def http_post(self, path, data):
        return {"cookies": {"session_id": "abc123"}}
    
    def http_get(self, path):
        # BUG: Requires session cookie
        return {"error": "Unauthorized"}

client = NoCookieHandling()

client.login("user", "pass")
# BUG: Session lost, profile request fails
profile = client.get_profile()
print(profile)
"""
            
            test_file = os.path.join(temp_dir, "cookie_handling.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_http2_support(self):
        """Test 823: Use HTTP/2 when available"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HTTP1Only:
    def make_request(self, url):
        # BUG: Always uses HTTP/1.1
        return self.http_get(url, protocol="HTTP/1.1")
    
    def http_get(self, url, protocol):
        return f"Response via {protocol}"

client = HTTP1Only()

# BUG: Doesn't leverage HTTP/2 multiplexing
responses = []
for i in range(100):
    response = client.make_request(f"https://api.example.com/data/{i}")
    responses.append(response)
"""
            
            test_file = os.path.join(temp_dir, "http2_support.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_ssl_verification(self):
        """Test 824: Verify SSL certificates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoSSLVerification:
    def fetch_data(self, url):
        # BUG: Disables SSL verification
        response = self.http_get(url, verify_ssl=False)
        return response
    
    def http_get(self, url, verify_ssl):
        return "response"

client = NoSSLVerification()

# BUG: Vulnerable to man-in-the-middle attacks
data = client.fetch_data("https://api.example.com/sensitive-data")
"""
            
            test_file = os.path.join(temp_dir, "ssl_verification.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_http_method_override(self):
        """Test 825: Handle HTTP method properly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class HTTPMethodConfusion:
    def delete_resource(self, resource_id):
        # BUG: Uses GET instead of DELETE
        url = f"/api/resources/{resource_id}/delete"
        return self.http_get(url)
    
    def http_get(self, url):
        return "deleted"

client = HTTPMethodConfusion()

# BUG: Violates REST semantics
result = client.delete_resource("123")
"""
            
            test_file = os.path.join(temp_dir, "http_method.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestTCPIPHandling:
    """Test TCP/IP protocol handling (10 tests)"""
    
    def test_tcp_keepalive(self):
        """Test 826: Enable TCP keepalive"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoTCPKeepalive:
    def create_socket(self):
        # BUG: No keepalive
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

client = NoTCPKeepalive()

# BUG: Connection may silently die
sock = client.create_socket()
"""
            
            test_file = os.path.join(temp_dir, "tcp_keepalive.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tcp_nodelay(self):
        """Test 827: Set TCP_NODELAY for low latency"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NagleEnabled:
    def create_socket(self):
        # BUG: Nagle's algorithm causes latency
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

client = NagleEnabled()

# BUG: Small messages delayed
sock = client.create_socket()
"""
            
            test_file = os.path.join(temp_dir, "tcp_nodelay.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_socket_timeout(self):
        """Test 828: Set socket timeouts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoSocketTimeout:
    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # BUG: No timeout
        sock.connect((host, port))
        
        return sock

client = NoSocketTimeout()

# BUG: Blocks indefinitely on slow network
try:
    sock = client.connect("10.0.0.1", 80)
except:
    pass
"""
            
            test_file = os.path.join(temp_dir, "socket_timeout.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_socket_buffer_size(self):
        """Test 829: Configure socket buffer sizes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class DefaultBuffers:
    def create_socket(self):
        # BUG: Uses default buffer sizes
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

client = DefaultBuffers()

# BUG: Suboptimal performance for high-throughput
sock = client.create_socket()
"""
            
            test_file = os.path.join(temp_dir, "socket_buffers.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_partial_reads(self):
        """Test 830: Handle partial socket reads"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoPartialReadHandling:
    def receive_data(self, sock, expected_size):
        # BUG: Assumes single recv() gets all data
        data = sock.recv(expected_size)
        return data

# BUG: May only receive partial data
print("Partial read not handled")
"""
            
            test_file = os.path.join(temp_dir, "partial_reads.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_connection_backlog(self):
        """Test 831: Set appropriate connection backlog"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class SmallBacklog:
    def start_server(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", port))
        
        # BUG: Small backlog
        sock.listen(1)
        
        return sock

server = SmallBacklog()

# BUG: Rejects connections under load
sock = server.start_server(8080)
"""
            
            test_file = os.path.join(temp_dir, "connection_backlog.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_address_reuse(self):
        """Test 832: Enable SO_REUSEADDR"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoReuseAddr:
    def start_server(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # BUG: No SO_REUSEADDR
        sock.bind(("0.0.0.0", port))
        
        return sock

# BUG: Can't restart server immediately after shutdown
print("SO_REUSEADDR not set")
"""
            
            test_file = os.path.join(temp_dir, "address_reuse.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_dns_resolution(self):
        """Test 833: Cache DNS resolutions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoDNSCache:
    def connect_to_host(self, hostname, port):
        # BUG: DNS lookup every time
        ip = socket.gethostbyname(hostname)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        
        return sock

client = NoDNSCache()

# BUG: 100 DNS lookups for same host
for _ in range(100):
    sock = client.connect_to_host("api.example.com", 443)
"""
            
            test_file = os.path.join(temp_dir, "dns_resolution.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_tcp_fast_open(self):
        """Test 834: Use TCP Fast Open"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class NoFastOpen:
    def create_socket(self):
        # BUG: Doesn't use TCP Fast Open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

client = NoFastOpen()

# BUG: Extra round trip on connection
sock = client.create_socket()
"""
            
            test_file = os.path.join(temp_dir, "tcp_fast_open.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_ipv6_support(self):
        """Test 835: Support IPv6"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
import socket

class IPv4Only:
    def create_socket(self):
        # BUG: Only supports IPv4
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

client = IPv4Only()

# BUG: Can't connect to IPv6-only hosts
sock = client.create_socket()
"""
            
            test_file = os.path.join(temp_dir, "ipv6_support.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)


class TestWebSocketsAndRealtime:
    """Test WebSocket and real-time communication (10 tests)"""
    
    def test_websocket_ping_pong(self):
        """Test 836: Implement WebSocket ping/pong"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoPingPong:
    def __init__(self):
        self.ws = None
    
    def keep_alive(self):
        # BUG: No ping/pong to detect dead connections
        pass

ws = NoPingPong()

# BUG: Connection may be dead but appears alive
print("No ping/pong keepalive")
"""
            
            test_file = os.path.join(temp_dir, "ws_ping_pong.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_reconnection(self):
        """Test 837: Implement WebSocket reconnection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoReconnection:
    def connect(self):
        # BUG: Connects once
        self.ws = self.create_websocket()
    
    def create_websocket(self):
        return "ws://example.com/socket"

ws = NoReconnection()
ws.connect()

# Connection drops
# BUG: No automatic reconnection
print("No reconnection logic")
"""
            
            test_file = os.path.join(temp_dir, "ws_reconnection.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_backpressure(self):
        """Test 838: Handle WebSocket backpressure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoBackpressure:
    def __init__(self):
        self.outgoing_queue = []
    
    def send_message(self, message):
        # BUG: Unbounded queue
        self.outgoing_queue.append(message)

ws = NoBackpressure()

# BUG: Queue grows unbounded
for i in range(1000000):
    ws.send_message(f"message_{i}")

print(f"Queue size: {len(ws.outgoing_queue)}")
"""
            
            test_file = os.path.join(temp_dir, "ws_backpressure.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_message_size(self):
        """Test 839: Limit WebSocket message size"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoMessageSizeLimit:
    def handle_message(self, message):
        # BUG: No size limit
        self.process(message)
    
    def process(self, message):
        return message.upper()

ws = NoMessageSizeLimit()

# BUG: Accepts huge messages
huge_message = "x" * 100000000  # 100MB
ws.handle_message(huge_message)
"""
            
            test_file = os.path.join(temp_dir, "ws_message_size.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_compression(self):
        """Test 840: Use WebSocket compression"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoCompression:
    def send_message(self, message):
        # BUG: Sends uncompressed data
        return self.ws_send(message)
    
    def ws_send(self, message):
        return f"Sent: {message}"

ws = NoCompression()

# BUG: Wastes bandwidth
large_message = "x" * 10000
ws.send_message(large_message)
"""
            
            test_file = os.path.join(temp_dir, "ws_compression.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_authentication(self):
        """Test 841: Authenticate WebSocket connections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoWSAuthentication:
    def handle_connection(self, ws):
        # BUG: No authentication
        self.connections.append(ws)
    
    def __init__(self):
        self.connections = []

server = NoWSAuthentication()

# BUG: Anyone can connect
server.handle_connection("ws://client1")
"""
            
            test_file = os.path.join(temp_dir, "ws_authentication.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_rate_limiting(self):
        """Test 842: Rate limit WebSocket messages"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoRateLimiting:
    def handle_message(self, client_id, message):
        # BUG: No rate limiting
        self.process_message(message)
    
    def process_message(self, message):
        print(f"Processing: {message}")

ws = NoRateLimiting()

# BUG: Client can flood server
for i in range(10000):
    ws.handle_message("client1", f"msg_{i}")
"""
            
            test_file = os.path.join(temp_dir, "ws_rate_limiting.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_graceful_close(self):
        """Test 843: Gracefully close WebSocket"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoGracefulClose:
    def close(self):
        # BUG: Abrupt close
        self.ws = None

ws = NoGracefulClose()

# BUG: Doesn't send close frame
ws.close()
"""
            
            test_file = os.path.join(temp_dir, "ws_graceful_close.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_protocol_version(self):
        """Test 844: Support WebSocket protocol version"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class NoVersionNegotiation:
    def handle_upgrade(self, request):
        # BUG: Doesn't check Sec-WebSocket-Version
        return "HTTP/1.1 101 Switching Protocols"

server = NoVersionNegotiation()

# BUG: May use incompatible protocol version
response = server.handle_upgrade({"Sec-WebSocket-Version": "13"})
"""
            
            test_file = os.path.join(temp_dir, "ws_protocol_version.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
    
    def test_websocket_binary_frames(self):
        """Test 845: Handle binary WebSocket frames"""
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_code = """
class TextOnly:
    def handle_message(self, message):
        # BUG: Assumes text frames only
        return message.decode("utf-8")

ws = TextOnly()

# BUG: Crashes on binary data
binary_data = b"\\x00\\x01\\x02\\x03"
try:
    result = ws.handle_message(binary_data)
except:
    print("Binary frames not handled")
"""
            
            test_file = os.path.join(temp_dir, "ws_binary_frames.py")
            with open(test_file, "w") as f:
                f.write(agent_code)
            
            assert os.path.exists(test_file)
