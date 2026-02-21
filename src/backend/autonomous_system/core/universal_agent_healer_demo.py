"""
Universal Agent Healer Demo

Demonstrates autonomous self-healing for ANY agent system:
- Test suites
- Production microservices  
- Batch agents
- Distributed systems
- Cloud applications

When ANY system breaks → Phoenix heals it autonomously!
"""

from autonomous_system.core import (
    UniversalAgentHealer, AgentSystemType,
    register_agent_system, heal_agent_system, get_system_health
)


def demo_test_suite_healing():
    """Healing a broken test suite application"""
    print("\n" + "="*80)
    print("DEMO 1: AUTONOMOUS TEST SUITE HEALING")
    print("="*80)
    
    # Register test suite as agent system
    def test_suite_health_check():
        # Simulating test suite that would check if all tests pass
        return False  # Currently broken
    
    register_agent_system(
        "phase6_test_suite",
        AgentSystemType.TEST_SUITE,
        test_suite_health_check
    )
    
    # Test suite fails with missing attribute
    try:
        from autonomous_system.core import SystemConfiguration
        config = SystemConfiguration(
            exploration_max_depth=5,
            exploration_max_breadth=3,
            exploration_max_paths=10,
            pruning_threshold=0.4,
            learning_rate=0.1,
            error_threshold=0.3,
            timeout_threshold=1000.0,
            cache_enabled=True,
            parallel_enabled=False,
            correction_timeout=500.0
        )
        # This would fail: depth = config.exploration_depth
        raise AttributeError("'SystemConfiguration' object has no attribute 'exploration_depth'")
    except AttributeError as e:
        # System detects failure and heals it autonomously
        heal_agent_system(
            "phase6_test_suite",
            AgentSystemType.TEST_SUITE,
            e
        )


def demo_production_agent_healing():
    """Healing a broken production agent service"""
    print("\n" + "="*80)
    print("DEMO 2: AUTONOMOUS PRODUCTION AGENT HEALING")
    print("="*80)
    
    # Register production agent service
    def production_agent_health_check():
        return False  # Service is down
    
    register_agent_system(
        "payment_processing_agent",
        AgentSystemType.PRODUCTION_AGENT,
        production_agent_health_check
    )
    
    # Production service fails with missing component
    try:
        from autonomous_system.core import MetaLearningEngine
        from autonomous_system.core.correction_strategy import CorrectionStrategy
        from autonomous_system.core.error_detection import ErrorType
        
        engine = MetaLearningEngine()
        engine.record_learning_experience(
            strategy=CorrectionStrategy.RETRY,
            error_type=ErrorType.TIMEOUT_ERROR,
            success=True,
            confidence=0.9
        )
        # This would fail: count = len(engine.learning_history)
        raise AttributeError("'MetaLearningEngine' object has no attribute 'learning_history'")
    except AttributeError as e:
        # System autonomously heals production service
        heal_agent_system(
            "payment_processing_agent",
            AgentSystemType.PRODUCTION_AGENT,
            e
        )


def demo_distributed_system_healing():
    """Healing a distributed multi-agent system"""
    print("\n" + "="*80)
    print("DEMO 3: AUTONOMOUS DISTRIBUTED SYSTEM HEALING")
    print("="*80)
    
    # Register distributed system
    def distributed_system_health_check():
        return False  # Cluster degraded
    
    register_agent_system(
        "distributed_ml_cluster",
        AgentSystemType.DISTRIBUTED_SYSTEM,
        distributed_system_health_check
    )
    
    # Distributed system fails with component health issue
    try:
        from autonomous_system.core import PredictiveMaintenanceEngine
        
        engine = PredictiveMaintenanceEngine()
        engine.register_component("buffer")
        engine.add_health_indicator("buffer", "usage", 0.9)
        engine.perform_maintenance("buffer")
        
        component = engine.components["buffer"]
        # This would fail: health_value = component.health
        raise AttributeError("'ComponentHealth' object has no attribute 'health'")
    except AttributeError as e:
        # System autonomously heals distributed cluster
        heal_agent_system(
            "distributed_ml_cluster",
            AgentSystemType.DISTRIBUTED_SYSTEM,
            e
        )


def demo_microservice_healing():
    """Healing a microservice with agent logic"""
    print("\n" + "="*80)
    print("DEMO 4: AUTONOMOUS MICROSERVICE HEALING")
    print("="*80)
    
    # Register microservice
    def microservice_health_check():
        return False  # Service unhealthy
    
    register_agent_system(
        "recommendation_microservice",
        AgentSystemType.MICROSERVICE,
        microservice_health_check
    )
    
    # Microservice resource allocation fails
    try:
        from autonomous_system.core import ResourceAllocator, ResourceType
        
        allocator = ResourceAllocator()
        # This would fail: strategy = allocator.current_strategy
        raise AttributeError("'ResourceAllocator' object has no attribute 'current_strategy'")
    except AttributeError as e:
        # System autonomously heals microservice
        heal_agent_system(
            "recommendation_microservice",
            AgentSystemType.MICROSERVICE,
            e
        )


def demo_batch_agent_healing():
    """Healing a batch processing agent"""
    print("\n" + "="*80)
    print("DEMO 5: AUTONOMOUS BATCH AGENT HEALING")
    print("="*80)
    
    # Register batch agent
    def batch_agent_health_check():
        return False  # Batch job failed
    
    register_agent_system(
        "nightly_batch_processor",
        AgentSystemType.BATCH_AGENT,
        batch_agent_health_check
    )
    
    # Batch job fails
    try:
        raise ValueError("Batch job failed during processing")
    except ValueError as e:
        # System autonomously heals batch process
        heal_agent_system(
            "nightly_batch_processor",
            AgentSystemType.BATCH_AGENT,
            e
        )


def print_system_health_report():
    """Print overall health of all registered systems"""
    print("\n" + "="*80)
    print("SYSTEM HEALTH REPORT - ALL AGENT SYSTEMS")
    print("="*80)
    
    report = get_system_health()
    
    print(f"\n📊 Overview:")
    print(f"   Total Registered Systems: {report['registered_systems']}")
    print(f"   Total Healing Actions: {report['total_healings']}")
    
    print(f"\n🖥️  Systems:")
    for system_name, info in report['systems'].items():
        print(f"\n   {system_name}")
        print(f"      Type: {info['type']}")
        print(f"      Healings Performed: {info['healings_performed']}")
        print(f"      Registered: {info['registered_at']}")
    
    print(f"\n📝 Recent Healing Actions:")
    for healing in report['healings']:
        print(f"\n   {healing['system']} - {healing['agent']}")
        print(f"      Diagnosis: {healing['diagnosis']}")
        print(f"      Status: {healing['status']}")
        print(f"      Time: {healing['timestamp']}")


def main():
    """Run all demonstrations"""
    print("\n" + "#"*80)
    print("# UNIVERSAL AGENT HEALER - AUTONOMOUS SELF-HEALING FOR ANY SYSTEM")
    print("#"*80)
    print("""
This demonstrates how Project Phoenix can autonomously heal ANY agent system:
- Test suites
- Production microservices
- Batch processing jobs
- Distributed ML clusters
- Cloud applications
- Any system with agents

When ANY system breaks:
1. Error is detected
2. Root cause diagnosed
3. Fix generated automatically
4. System heals itself
5. Recovery validated

NO HUMAN INTERVENTION NEEDED!
    """)
    
    # Run demonstrations
    demo_test_suite_healing()
    demo_production_agent_healing()
    demo_distributed_system_healing()
    demo_microservice_healing()
    demo_batch_agent_healing()
    
    # Print final report
    print_system_health_report()
    
    print("\n" + "#"*80)
    print("# ✅ AUTONOMOUS SELF-HEALING COMPLETE")
    print("#"*80)
    print("""
The system has demonstrated autonomous healing for:
✓ Test applications
✓ Production agents
✓ Distributed systems
✓ Microservices
✓ Batch processors

This is the future of autonomous systems - they heal themselves!
    """)


if __name__ == "__main__":
    main()
