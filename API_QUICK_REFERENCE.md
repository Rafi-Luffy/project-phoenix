# 🚀 API Integration Quick Reference

## Quick Start

### Start Backend
```bash
cd src/backend
python3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Configure API URL
Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

---

## Using the API Client

### Import
```typescript
import { apiClient } from '@/services/api';
```

### Authentication
```typescript
// Login
const loginRes = await apiClient.login('user@example.com', 'password');
if (loginRes.data?.access_token) {
  apiClient.setToken(loginRes.data.access_token);
}

// Or generate token
const tokenRes = await apiClient.generateToken('user@example.com', 'password');

// Refresh token
await apiClient.refreshToken();

// Revoke token
await apiClient.revokeToken();
```

### Agents
```typescript
// Create
const agent = await apiClient.createAgent({ name: 'Monitor-01' });

// List
const agents = await apiClient.listAgents(limit: 10);

// Get one
const agent = await apiClient.getAgent('agent-id');

// Update
await apiClient.updateAgent('agent-id', { name: 'Monitor-02' });

// Delete
await apiClient.deleteAgent('agent-id');

// Control
await apiClient.startAgent('agent-id');
await apiClient.stopAgent('agent-id');

// Tasks
await apiClient.createAgentTask('agent-id', { task: 'check-health' });
```

### Memory
```typescript
// Store
await apiClient.storeMemory('agent-id', { key: 'value' });

// Get
const memory = await apiClient.getMemory('memory-id');

// Delete
await apiClient.deleteMemory('memory-id');

// Search
const results = await apiClient.searchMemory('query', 'agent-id');
```

### Corrections
```typescript
// List
const corrections = await apiClient.listCorrections('agent-id', limit: 10);

// Get
const correction = await apiClient.getCorrection('correction-id');

// Replay
await apiClient.replayCorrection('correction-id');
```

### Messages
```typescript
// Send
await apiClient.sendMessage({ to: 'agent-id', content: 'message' });

// Get
const messages = await apiClient.getMessages('agent-id');
```

### Monitoring
```typescript
// Status
const health = await apiClient.getHealth();
const status = await apiClient.getStatus();

// Metrics
const metrics = await apiClient.getMetrics();
const alerts = await apiClient.getAlerts();
const logs = await apiClient.getLogs(limit: 100, level: 'ERROR');
const events = await apiClient.getEvents(limit: 100, type: 'error');

// LLM
const llmHealth = await apiClient.getLlmHealth();
```

### LLM Integration
```typescript
// Analyze error
const analysis = await apiClient.analyzeError('error message', { context: {} });

// Explain correction
const explanation = await apiClient.explainCorrection({ id: 'correction-id' });

// Detect patterns
const patterns = await apiClient.detectPatterns({ data: [] });

// Optimize
const recommendations = await apiClient.optimizeSystem(systemState, metrics);
```

---

## Using Real-Time Hooks

### Agent Activity
```typescript
import { useRealtimeAgentActivity } from '@/hooks/useRealtimeData';

function Dashboard() {
  const { activities, isConnected, usesMockData } = useRealtimeAgentActivity(10);
  
  return (
    <>
      {usesMockData && <p>⚠️ Using mock data</p>}
      {isConnected && <p>✅ Connected to API</p>}
      {activities.map(activity => (
        <div key={activity.id}>{activity.title}</div>
      ))}
    </>
  );
}
```

### Incidents
```typescript
import { useRealtimeIncidents } from '@/hooks/useRealtimeData';

function IncidentMonitor() {
  const { incidents, resolveIncident, usesMockData } = useRealtimeIncidents(5);
  
  return (
    <>
      {incidents.map(incident => (
        <div key={incident.id}>
          {incident.message}
          {incident.status !== 'resolved' && (
            <button onClick={() => resolveIncident(incident.id)}>
              Resolve
            </button>
          )}
        </div>
      ))}
    </>
  );
}
```

### Live Metrics
```typescript
import { useLiveMetrics } from '@/hooks/useRealtimeData';

function MetricsDisplay() {
  const { activeAgents, successRate, cpuUsage, usesMockData } = useLiveMetrics();
  
  return (
    <>
      <div>Agents: {activeAgents}</div>
      <div>Success: {successRate}%</div>
      <div>CPU: {cpuUsage}%</div>
    </>
  );
}
```

### Chart Data
```typescript
import { useRealtimeChartData } from '@/hooks/useRealtimeData';

function Chart() {
  const chartData = useRealtimeChartData();
  
  return <ResponsiveLineChart data={chartData} />;
}
```

---

## Response Format

All API calls return:
```typescript
interface ApiResponse<T> {
  data?: T;      // Response data if successful
  error?: string; // Error message if failed
  status: number; // HTTP status code
}
```

Check response:
```typescript
const response = await apiClient.getMetrics();
if (response.data) {
  // Success
  console.log(response.data);
} else {
  // Error
  console.error(response.error);
}
```

---

## Error Handling

```typescript
// Check if request succeeded
const res = await apiClient.createAgent({ name: 'Test' });

if (res.status === 200 || res.status === 201) {
  console.log('Success:', res.data);
} else if (res.status === 401) {
  console.log('Unauthorized - please login');
  apiClient.clearToken();
} else if (res.status === 404) {
  console.log('Resource not found');
} else if (res.status >= 500) {
  console.log('Server error - might be down');
} else {
  console.error('Error:', res.error);
}
```

---

## Environment Setup

### Development (.env.local)
```
VITE_API_URL=http://localhost:8000
```

### Staging (.env.staging)
```
VITE_API_URL=https://api-staging.phoenixruntime.dev
```

### Production (.env.prod)
```
VITE_API_URL=https://api.phoenixruntime.dev
```

---

## Common Issues

### API Returns 404
- Backend not running: `python3.11 -m uvicorn main:app --host 0.0.0.0 --port 8000`
- Check API URL in .env.local
- Verify endpoint path is correct

### Authentication Failed
- Clear token: `apiClient.clearToken()`
- Re-login through UI
- Check token expiration

### Mock Data Instead of Real Data
- Backend may be down - check http://localhost:8000/health
- Check API URL configuration
- Check browser console for errors

### CORS Error
- Backend needs CORS headers
- Check that backend is running
- Frontend and backend running on same machine

---

## API Documentation

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### Frontend API Reference
```
http://localhost:5173/docs/api
```

---

## Testing Endpoints

### Using cURL
```bash
# Health check
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/metrics

# Create agent (with auth)
curl -X POST http://localhost:8000/agents \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Monitor-01"}'
```

### Using Postman
1. Import collection from http://localhost:8000/docs
2. Set Authorization header: `Bearer {token}`
3. Test endpoints

---

## Production Deployment

1. **Backend**
   ```bash
   # Use production-grade server
   python3.11 -m gunicorn main:app --bind 0.0.0.0:8000
   ```

2. **Frontend**
   ```bash
   # Build for production
   npm run build
   
   # Deploy dist folder
   ```

3. **Environment**
   - Set VITE_API_URL to production backend
   - Enable HTTPS
   - Configure CORS properly
   - Set up rate limiting
   - Enable authentication

---

## Monitoring

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Check Metrics
```bash
curl http://localhost:8000/metrics
```

### Check Logs
```bash
curl http://localhost:8000/logs?limit=100
```

### Check Events
```bash
curl http://localhost:8000/events?limit=100
```

---

## Support

For issues or questions:
1. Check detailed report: [API_ALIGNMENT_IMPLEMENTATION_COMPLETE.md](API_ALIGNMENT_IMPLEMENTATION_COMPLETE.md)
2. Review API documentation at http://localhost:8000/docs
3. Check frontend API reference at http://localhost:5173/docs/api
4. Review browser console for error messages
5. Check backend logs for issues

---

**Last Updated:** January 8, 2026  
**Status:** ✅ Production Ready
