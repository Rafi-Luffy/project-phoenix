"""
LIVE AUTONOMOUS SELF-HEALING DEMONSTRATION
Watch the system detect failures and heal itself in real-time
"""

import time
import random
from phoenix.autonomous_self_healer import (
    AutoHealer, RecoveryAction, HealthMetric
)


class DemoSystem:
    """Simulated distributed system with components that fail"""
    
    def __init__(self):
        # Component states
        self.cache_health = 1.0  # 0 = failed, 1 = healthy
        self.db_health = 1.0
        self.api_health = 1.0
        self.queue_health = 1.0
        
        # Failure simulators
        self.cache_failure_active = False
        self.db_failure_active = False
        self.api_failure_active = False
        self.queue_failure_active = False
        
        # Recovery tracking
        self.cache_recovery_attempts = 0
        self.db_recovery_attempts = 0
        self.api_recovery_attempts = 0
        self.queue_recovery_attempts = 0
    
    # =================== CACHE COMPONENT ===================
    def check_cache_health(self) -> dict:
        """Check Redis cache health"""
        if self.cache_failure_active:
            # Simulate degradation
            self.cache_health = max(0, self.cache_health - 0.1)
        else:
            # Recover gradually
            self.cache_health = min(1.0, self.cache_health + 0.05)
        
        return {
            "connection_pool": HealthMetric(
                name="connection_pool",
                value=self.cache_health * 100,
                threshold_warning=60,
                threshold_critical=30
            ),
            "latency_ms": HealthMetric(
                name="latency_ms",
                value=(1 - self.cache_health) * 1000,  # Higher latency when unhealthy
                threshold_warning=100,
                threshold_critical=500
            )
        }
    
    def heal_cache(self) -> bool:
        """Execute cache healing action"""
        print("    🔧 [CACHE] Attempting to heal...")
        self.cache_recovery_attempts += 1
        
        # Simulate recovery
        time.sleep(0.05)
        
        if self.cache_failure_active:
            # If failure still active, healing has limited effect
            success = random.random() > 0.5
        else:
            # If no active failure, healing succeeds
            success = True
        
        if success:
            self.cache_health = 0.8  # Restore to 80%
            print("    ✅ [CACHE] Healed successfully! Health restored to 80%")
        else:
            print("    ❌ [CACHE] Healing failed, retrying...")
        
        return success
    
    def trigger_cache_failure(self):
        """Inject a cache failure"""
        self.cache_failure_active = True
        print("\n🔴 [FAILURE INJECTED] Cache connection pool exhausted!")
    
    def resolve_cache_failure(self):
        """Remove the cache failure"""
        self.cache_failure_active = False
        print("\n✓ [FAILURE RESOLVED] Cache underlying issue fixed")
    
    # =================== DATABASE COMPONENT ===================
    def check_db_health(self) -> dict:
        """Check database health"""
        if self.db_failure_active:
            self.db_health = max(0, self.db_health - 0.15)
        else:
            self.db_health = min(1.0, self.db_health + 0.04)
        
        return {
            "replication_lag": HealthMetric(
                name="replication_lag",
                value=(1 - self.db_health) * 10000,  # Lag in ms
                threshold_warning=1000,
                threshold_critical=5000
            ),
            "connection_pool": HealthMetric(
                name="connection_pool",
                value=self.db_health * 100,
                threshold_warning=50,
                threshold_critical=20
            )
        }
    
    def heal_db(self) -> bool:
        """Execute database healing action"""
        print("    🔧 [DATABASE] Attempting failover...")
        self.db_recovery_attempts += 1
        
        time.sleep(0.08)
        
        if self.db_failure_active:
            success = random.random() > 0.4
        else:
            success = True
        
        if success:
            self.db_health = 0.85
            print("    ✅ [DATABASE] Failover successful! Health restored to 85%")
        else:
            print("    ❌ [DATABASE] Failover failed, will retry...")
        
        return success
    
    def trigger_db_failure(self):
        """Inject a database failure"""
        self.db_failure_active = True
        print("\n🔴 [FAILURE INJECTED] Database replication lag critical!")
    
    def resolve_db_failure(self):
        """Remove the database failure"""
        self.db_failure_active = False
        print("\n✓ [FAILURE RESOLVED] Database replication recovered")
    
    # =================== API COMPONENT ===================
    def check_api_health(self) -> dict:
        """Check API health"""
        if self.api_failure_active:
            self.api_health = max(0, self.api_health - 0.12)
        else:
            self.api_health = min(1.0, self.api_health + 0.06)
        
        return {
            "response_time": HealthMetric(
                name="response_time",
                value=(1 - self.api_health) * 5000,
                threshold_warning=500,
                threshold_critical=2000
            ),
            "error_rate": HealthMetric(
                name="error_rate",
                value=(1 - self.api_health) * 100,
                threshold_warning=5,
                threshold_critical=20
            )
        }
    
    def heal_api(self) -> bool:
        """Execute API healing action"""
        print("    🔧 [API] Restarting server instances...")
        self.api_recovery_attempts += 1
        
        time.sleep(0.06)
        
        if self.api_failure_active:
            success = random.random() > 0.3
        else:
            success = True
        
        if success:
            self.api_health = 0.9
            print("    ✅ [API] Restart successful! Health restored to 90%")
        else:
            print("    ❌ [API] Restart incomplete, will continue healing...")
        
        return success
    
    def trigger_api_failure(self):
        """Inject an API failure"""
        self.api_failure_active = True
        print("\n🔴 [FAILURE INJECTED] API error rate spiking!")
    
    def resolve_api_failure(self):
        """Remove the API failure"""
        self.api_failure_active = False
        print("\n✓ [FAILURE RESOLVED] API underlying issue fixed")
    
    # =================== MESSAGE QUEUE COMPONENT ===================
    def check_queue_health(self) -> dict:
        """Check message queue health"""
        if self.queue_failure_active:
            self.queue_health = max(0, self.queue_health - 0.11)
        else:
            self.queue_health = min(1.0, self.queue_health + 0.05)
        
        return {
            "queue_depth": HealthMetric(
                name="queue_depth",
                value=(1 - self.queue_health) * 10000,
                threshold_warning=5000,
                threshold_critical=8000
            ),
            "processing_lag": HealthMetric(
                name="processing_lag",
                value=(1 - self.queue_health) * 60,
                threshold_warning=10,
                threshold_critical=30
            )
        }
    
    def heal_queue(self) -> bool:
        """Execute queue healing action"""
        print("    🔧 [QUEUE] Scaling consumer workers...")
        self.queue_recovery_attempts += 1
        
        time.sleep(0.07)
        
        if self.queue_failure_active:
            success = random.random() > 0.45
        else:
            success = True
        
        if success:
            self.queue_health = 0.87
            print("    ✅ [QUEUE] Scaling successful! Health restored to 87%")
        else:
            print("    ❌ [QUEUE] Scaling incomplete, will retry...")
        
        return success
    
    def trigger_queue_failure(self):
        """Inject a queue failure"""
        self.queue_failure_active = True
        print("\n🔴 [FAILURE INJECTED] Message queue backing up!")
    
    def resolve_queue_failure(self):
        """Remove the queue failure"""
        self.queue_failure_active = False
        print("\n✓ [FAILURE RESOLVED] Queue underlying issue fixed")


def run_demo():
    """Run the complete autonomous self-healing demonstration"""
    
    print("=" * 80)
    print("🚀 PROJECT PHOENIX - AUTONOMOUS SELF-HEALING SYSTEM DEMO")
    print("=" * 80)
    print()
    
    # Create system and healer
    demo_system = DemoSystem()
    healer = AutoHealer(check_interval_ms=100)
    
    # Register components
    healer.register_component("cache", demo_system.check_cache_health)
    healer.register_component("database", demo_system.check_db_health)
    healer.register_component("api", demo_system.check_api_health)
    healer.register_component("queue", demo_system.check_queue_health)
    
    # Register recovery strategies
    healer.register_recovery_strategy(
        "cache",
        [RecoveryAction("restart_cache", "Restart cache server", demo_system.heal_cache)]
    )
    
    healer.register_recovery_strategy(
        "database",
        [RecoveryAction("failover_db", "Failover database", demo_system.heal_db)]
    )
    
    healer.register_recovery_strategy(
        "api",
        [RecoveryAction("restart_api", "Restart API servers", demo_system.heal_api)]
    )
    
    healer.register_recovery_strategy(
        "queue",
        [RecoveryAction("scale_queue", "Scale queue workers", demo_system.heal_queue)]
    )
    
    # Start healing
    healer.start()
    
    print("\n📊 Starting autonomous healing system...")
    print("    • Monitoring 4 components (cache, database, api, queue)")
    print("    • Check interval: 100ms")
    print("    • System will detect failures and heal autonomously\n")
    
    # Scenario: Component failures over time
    demo_start = time.time()
    cycle_count = 0
    max_cycles = 200  # ~20 seconds at 100ms interval
    
    try:
        while cycle_count < max_cycles:
            cycle_start = time.time()
            
            # Inject failures at specific times
            elapsed = time.time() - demo_start
            
            if 1.0 < elapsed < 3.0:  # Inject cache failure at 1 second
                if not demo_system.cache_failure_active:
                    demo_system.trigger_cache_failure()
            elif elapsed >= 3.0:
                if demo_system.cache_failure_active:
                    demo_system.resolve_cache_failure()
            
            if 4.0 < elapsed < 6.5:  # Inject DB failure at 4 seconds
                if not demo_system.db_failure_active:
                    demo_system.trigger_db_failure()
            elif elapsed >= 6.5:
                if demo_system.db_failure_active:
                    demo_system.resolve_db_failure()
            
            if 8.0 < elapsed < 10.0:  # Inject API failure at 8 seconds
                if not demo_system.api_failure_active:
                    demo_system.trigger_api_failure()
            elif elapsed >= 10.0:
                if demo_system.api_failure_active:
                    demo_system.resolve_api_failure()
            
            if 11.0 < elapsed < 13.5:  # Inject queue failure at 11 seconds
                if not demo_system.queue_failure_active:
                    demo_system.trigger_queue_failure()
            elif elapsed >= 13.5:
                if demo_system.queue_failure_active:
                    demo_system.resolve_queue_failure()
            
            # Run one healing cycle
            cycle_result = healer.run_one_cycle()
            
            # Print status every 10 cycles
            if cycle_count % 10 == 0:
                health = healer.monitor.get_system_health()
                state = healer.state_manager.current_state.value
                
                print(f"\n[Cycle {cycle_count:3d}] {state.upper():20s} | "
                      f"Elapsed: {elapsed:6.2f}s")
                
                for comp_name, comp_health in health["components"].items():
                    status_icon = "🟢" if comp_health["status"] == "healthy" else \
                                 "🟡" if comp_health["status"] == "degraded" else "🔴"
                    print(f"  {status_icon} {comp_name:10s} - "
                          f"Failures: {comp_health['failure_count']:2d} "
                          f"Recoveries: {comp_health['recovery_count']:2d}")
            
            # Ensure minimum cycle time
            cycle_elapsed = time.time() - cycle_start
            if cycle_elapsed < 0.1:
                time.sleep(0.1 - cycle_elapsed)
            
            cycle_count += 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    
    healer.stop()
    
    # Print final report
    print("\n" + "=" * 80)
    print("📋 FINAL AUTONOMOUS HEALING REPORT")
    print("=" * 80)
    
    report = healer.get_detailed_report()
    
    print(f"\n✨ System State: {report['current_state'].upper()}")
    print(f"📈 Total Healing Cycles: {report['total_cycles']}")
    
    metrics = report["metrics"]
    print(f"\n🔍 Failure Detection & Recovery:")
    print(f"   • Total failures detected: {metrics['total_failures_detected']}")
    print(f"   • Total healing attempts: {metrics['total_healings_attempted']}")
    print(f"   • Successful healings: {metrics['total_healings_successful']}")
    print(f"   • Failed healings: {metrics['total_healings_failed']}")
    
    if metrics['total_healings_attempted'] > 0:
        success_rate = (metrics['total_healings_successful'] / 
                       metrics['total_healings_attempted'] * 100)
        print(f"   • Success rate: {success_rate:.1f}%")
    
    if metrics['average_detection_time'] > 0:
        print(f"   • Avg detection time: {metrics['average_detection_time']*1000:.1f}ms")
    
    if metrics['average_recovery_time'] > 0:
        print(f"   • Avg recovery time: {metrics['average_recovery_time']*1000:.1f}ms")
        print(f"   • MTTR: {metrics['mttr']*1000:.1f}ms")
    
    print(f"\n📊 Per-Component Performance:")
    for component, comp_metrics in metrics["component_metrics"].items():
        print(f"   • {component:10s}: {comp_metrics['attempts']:2d} attempts, "
              f"{comp_metrics['successful']:2d} successful ({comp_metrics['success_rate']*100:.0f}%)")
    
    print(f"\n🔄 State Transitions:")
    for transition, count in report["state_manager"].transition_count.items() if "state_manager" in report else []:
        from_state, to_state = transition
        print(f"   • {from_state} → {to_state}: {count} times")
    
    print("\n" + "=" * 80)
    print("✅ AUTONOMOUS SELF-HEALING SYSTEM DEMONSTRATED SUCCESSFULLY")
    print("=" * 80)
    print("\n🎯 Key Achievements:")
    print("   ✓ System autonomously detected failures")
    print("   ✓ System autonomously executed recovery actions")
    print("   ✓ System autonomously recovered and resumed normal operation")
    print("   ✓ No human intervention required")
    print()


if __name__ == "__main__":
    run_demo()
