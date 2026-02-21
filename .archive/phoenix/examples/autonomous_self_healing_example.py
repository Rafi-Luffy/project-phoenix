"""
Phoenix Autonomous Self-Healing Examples

These examples show how to use Phoenix in your agentic AI projects.
I've included the most common use cases I run into.

The key thing to understand: Phoenix monitors your agent logs, detects
failures automatically, generates fixes using LLMs, and applies them
without asking for approval. The whole cycle is autonomous.

You can run it once (single healing cycle) or continuously (24/7 monitoring).
"""

import time
from phoenix.orchestrator.autonomous_self_healing_orchestrator import (
    AutonomousSelfHealingOrchestrator,
)


def simulate_agentic_ai_logs():
    """
    Simulates logs from a real agentic AI system.
    
    In production, you'd pull these from your actual logging system
    (CloudWatch, Datadog, Splunk, local log files, etc.)
    
    This simulated log shows common failures I've seen:
    - Context overflow (messages exceed LLM window)
    - Tool not found (agent calls wrong tool name)
    - Agent deadlock (circular dependencies)
    - Vector search timeout (RAG pipeline issue)
    """
    
    # This would come from your actual agent logs
    logs = """
[2024-01-15 10:23:45] INFO: Agent 'DataAnalyzer' initialized
[2024-01-15 10:23:47] INFO: Processing user query: "Analyze sales data"
[2024-01-15 10:23:48] INFO: Calling LLM with context (4200 tokens)
[2024-01-15 10:23:49] ERROR: OpenAI API Error: Context length exceeded (4200/4096)
[2024-01-15 10:23:49] ERROR: Traceback:
  File "agent.py", line 142, in process_query
    response = self.llm.complete(messages)
  File "llm_client.py", line 89, in complete
    raise ContextLengthError(f"Context too long: {token_count}")
phoenix.errors.ContextLengthError: Context too long: 4200 tokens

[2024-01-15 10:24:01] WARNING: Agent retry #1 failed
[2024-01-15 10:24:15] WARNING: Agent retry #2 failed
[2024-01-15 10:24:30] WARNING: Agent retry #3 failed
[2024-01-15 10:24:45] ERROR: Agent 'DataAnalyzer' failed after 3 retries

[2024-01-15 10:25:00] INFO: Agent 'WebSearcher' attempting tool call
[2024-01-15 10:25:01] ERROR: Tool not found: 'web_search_v2'
[2024-01-15 10:25:01] ERROR: Available tools: ['web_search', 'calculator', 'code_runner']
[2024-01-15 10:25:01] ERROR: Tool call failed

[2024-01-15 10:26:30] INFO: Multi-agent workflow started
[2024-01-15 10:26:31] INFO: Agent A waiting for Agent B
[2024-01-15 10:26:32] INFO: Agent B waiting for Agent C
[2024-01-15 10:26:33] INFO: Agent C waiting for Agent A
[2024-01-15 10:26:45] WARNING: Workflow timeout after 15s
[2024-01-15 10:26:45] ERROR: Circular dependency detected in agent workflow
[2024-01-15 10:26:45] ERROR: Agent deadlock: A -> B -> C -> A

[2024-01-15 10:27:00] INFO: RAG query: "Find documentation about API"
[2024-01-15 10:27:01] ERROR: Vector search failed: Connection timeout
[2024-01-15 10:27:01] ERROR: Could not retrieve relevant documents
"""
    
    return logs


def example_single_healing_cycle():
    """Example: Run a single autonomous healing cycle."""
    
    print("=" * 80)
    print("PHOENIX AUTONOMOUS SELF-HEALING - SINGLE CYCLE EXAMPLE")
    print("=" * 80)
    print()
    print("CORE PRINCIPLE: ZERO HUMAN INTERACTION REQUIRED")
    print()
    
    # Initialize Phoenix
    orchestrator = AutonomousSelfHealingOrchestrator(
        workspace_path="/path/to/your/agentic/ai/project",
        auto_heal=True,  # FULLY AUTONOMOUS
    )
    
    print(" Phoenix initialized in autonomous mode")
    print()
    
    # Get logs from your agentic AI system
    logs = simulate_agentic_ai_logs()
    
    print(" Analyzing logs from agentic AI system...")
    print(f"   Log size: {len(logs)} characters")
    print()
    
    # Run ONE healing cycle - Phoenix does EVERYTHING automatically
    print(" Running autonomous healing cycle...")
    print()
    
    result = orchestrator.run_healing_cycle(logs)
    
    # Print results
    print("=" * 80)
    print("HEALING CYCLE RESULTS")
    print("=" * 80)
    print()
    print(f"Cycle ID: {result.cycle_id}")
    print(f"Duration: {result.total_time_seconds:.2f}s")
    print()
    print(f" Failures Detected: {result.failures_detected}")
    print(f"  - Auto-fixable: {result.auto_fixable}")
    print(f"  - Composite failures: {result.composite_failures}")
    print()
    print(f" Fixes Generated: {result.fixes_generated}")
    print()
    print(f" Fixes Applied: {result.fixes_applied}")
    print(f"  - Successful: {result.fixes_successful}")
    print(f"  - Failed: {result.fixes_failed}")
    print(f"  - Rolled back: {result.fixes_rolled_back}")
    print()
    print(f"System Health: {result.system_health.upper()}")
    print()
    print(f"Summary: {result.human_summary}")
    print()
    
    # Show statistics
    print("=" * 80)
    print("PHOENIX STATISTICS")
    print("=" * 80)
    print()
    
    stats = orchestrator.get_statistics()
    
    print(f"Fix Success Rate: {stats['fix_stats']['success_rate']:.1f}%")
    print(f"Avg Fix Time: {stats['fix_stats']['avg_execution_time_seconds']:.2f}s")
    print()
    
    print("Top Failures:")
    for i, failure in enumerate(stats['top_failures'][:3], 1):
        print(f"  {i}. {failure['failure_type']} - {failure['count']} times")
    print()
    
    print("=" * 80)
    print("NO HUMAN INTERACTION WAS REQUIRED")
    print("=" * 80)


def example_continuous_healing():
    """Example: Run continuous autonomous healing (production mode)."""
    
    print("=" * 80)
    print("PHOENIX CONTINUOUS AUTONOMOUS HEALING")
    print("=" * 80)
    print()
    print("This is PRODUCTION MODE - Phoenix monitors and heals FOREVER")
    print()
    
    # Initialize Phoenix
    orchestrator = AutonomousSelfHealingOrchestrator(
        workspace_path="/path/to/your/agentic/ai/project",
        auto_heal=True,  # FULLY AUTONOMOUS
    )
    
    print(" Phoenix initialized in continuous healing mode")
    print()
    
    # Define log source (your actual log aggregation system)
    def get_recent_logs():
        """Get recent logs from your system."""
        # This could be:
        # - Reading from log files
        # - Querying log aggregation service (Datadog, Splunk, etc.)
        # - Streaming from Kafka
        # - Reading from CloudWatch
        
        return simulate_agentic_ai_logs()
    
    print(" Starting continuous healing loop...")
    print("   Checking every 60 seconds")
    print("   Press Ctrl+C to stop")
    print()
    
    try:
        # Run continuous healing
        orchestrator.continuous_healing_loop(
            log_source_func=get_recent_logs,
            interval_seconds=60,
            max_iterations=5,  # For demo - remove for infinite
        )
    except KeyboardInterrupt:
        print("\n\n Continuous healing stopped")
    
    # Show results
    print()
    print("=" * 80)
    print("CONTINUOUS HEALING SUMMARY")
    print("=" * 80)
    print()
    
    stats = orchestrator.get_statistics()
    
    print(f"Total Healing Cycles: {stats['autonomous_healing_stats']['total_healing_cycles']}")
    print(f"Success Rate: {stats['autonomous_healing_stats']['success_rate']:.1f}%")
    print(f"Total Failures Detected: {stats['failure_stats']['total_failures']}")
    print(f"Total Fixes Applied: {stats['fix_stats']['total_fixes']}")
    print(f"Fix Success Rate: {stats['fix_stats']['success_rate']:.1f}%")
    print()
    
    print("=" * 80)
    print("ZERO HUMAN INTERACTION - Phoenix handled everything")
    print("=" * 80)


def example_dashboard():
    """Example: View Phoenix dashboard."""
    
    print("=" * 80)
    print("PHOENIX AUTONOMOUS HEALING DASHBOARD")
    print("=" * 80)
    print()
    
    # Initialize and run some cycles
    orchestrator = AutonomousSelfHealingOrchestrator(
        workspace_path="/path/to/your/project",
        auto_heal=True,
    )
    
    # Run a few cycles
    for i in range(3):
        print(f"Running cycle {i+1}...")
        orchestrator.run_healing_cycle(simulate_agentic_ai_logs())
    
    print()
    
    # Get dashboard
    dashboard = orchestrator.get_dashboard()
    
    print(dashboard)


def example_integration_with_langchain():
    """Example: Integrate Phoenix with LangChain agents."""
    
    print("=" * 80)
    print("PHOENIX + LANGCHAIN INTEGRATION")
    print("=" * 80)
    print()
    
    # Your LangChain agent setup
    print("Setting up LangChain agent...")
    
    # Initialize Phoenix
    orchestrator = AutonomousSelfHealingOrchestrator(
        workspace_path="./my_langchain_project",
        auto_heal=True,
    )
    
    print(" Phoenix monitoring enabled")
    print()
    
    # Wrap your agent execution
    def run_agent_with_phoenix_monitoring():
        """Run LangChain agent with Phoenix monitoring."""
        
        # Your LangChain agent code
        # agent = create_agent(...)
        # result = agent.run("Your task")
        
        # Simulate agent execution and logging
        logs = simulate_agentic_ai_logs()
        
        # Phoenix automatically heals any issues
        healing_result = orchestrator.run_healing_cycle(logs)
        
        if healing_result.system_health == "healthy":
            print(" Agent executed successfully")
        else:
            print(" Agent encountered issues (Phoenix applied fixes)")
        
        return healing_result
    
    # Run agent
    result = run_agent_with_phoenix_monitoring()
    
    print()
    print(f"Result: {result.human_summary}")
    print()
    print("Phoenix ensured your agent kept running - NO manual intervention!")


def example_what_phoenix_fixes():
    """Show examples of what Phoenix can fix autonomously."""
    
    print("=" * 80)
    print("WHAT PHOENIX FIXES AUTONOMOUSLY")
    print("=" * 80)
    print()
    
    examples = [
        {
            "failure": "Context Overflow",
            "detection": "LLM context exceeds 4096 tokens",
            "fix": "Implements automatic context window management and message summarization",
            "result": "Agent continues with managed context",
        },
        {
            "failure": "Agent Deadlock",
            "detection": "Circular dependency: Agent A → B → C → A",
            "fix": "Adds timeout and dependency cycle detection",
            "result": "Workflow completes with proper coordination",
        },
        {
            "failure": "Tool Not Found",
            "detection": "Agent calls 'web_search_v2' but only 'web_search' exists",
            "fix": "Adds tool name validation and auto-correction",
            "result": "Agent uses correct tool name",
        },
        {
            "failure": "Rate Limit Hit",
            "detection": "OpenAI API rate limit exceeded",
            "fix": "Implements exponential backoff retry logic",
            "result": "API calls succeed with proper rate limiting",
        },
        {
            "failure": "Memory Corruption",
            "detection": "Agent state becomes inconsistent",
            "fix": "Implements state validation and safe recovery",
            "result": "Agent state restored to consistent state",
        },
        {
            "failure": "Vector Search Failure",
            "detection": "RAG embedding lookup times out",
            "fix": "Adds retry logic and fallback search",
            "result": "Documents retrieved successfully",
        },
        {
            "failure": "Workflow Stuck",
            "detection": "Agent workflow makes no progress for 60s",
            "fix": "Adds progress monitoring and auto-recovery",
            "result": "Workflow completes successfully",
        },
        {
            "failure": "Hallucination",
            "detection": "LLM generates factually incorrect response",
            "fix": "Adds fact-checking and validation layer",
            "result": "Response validated before use",
        },
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['failure']}")
        print(f"   Detection: {example['detection']}")
        print(f"   Fix: {example['fix']}")
        print(f"   Result: {example['result']}")
        print()
    
    print("=" * 80)
    print("ALL FIXES APPLIED AUTOMATICALLY - ZERO HUMAN INTERACTION")
    print("=" * 80)


if __name__ == "__main__":
    print()
    print(" PHOENIX - World's First Fully Autonomous Agentic AI Healing System ")
    print()
    print("Choose an example:")
    print()
    print("1. Single healing cycle (detect + fix + validate)")
    print("2. Continuous healing (production mode)")
    print("3. View dashboard")
    print("4. LangChain integration")
    print("5. What Phoenix fixes autonomously")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    print()
    
    if choice == "1":
        example_single_healing_cycle()
    elif choice == "2":
        example_continuous_healing()
    elif choice == "3":
        example_dashboard()
    elif choice == "4":
        example_integration_with_langchain()
    elif choice == "5":
        example_what_phoenix_fixes()
    else:
        print("Invalid choice")
        print()
        print("Running all examples...")
        print()
        example_what_phoenix_fixes()
        time.sleep(2)
        example_single_healing_cycle()
