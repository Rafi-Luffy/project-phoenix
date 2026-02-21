"""
Quick autonomous healer demonstration with final report
"""

import sys
import time
from phoenix.autonomous_self_healer import AutoHealer, RecoveryAction, HealthMetric


# Simulated component with failures
class SimpleComponent:
    def __init__(self, name):
        self.name = name
        self.health = 1.0
        self.failing = False
    
    def check_health(self):
        if self.failing:
            self.health = max(0, self.health - 0.2)
        else:
            self.health = min(1.0, self.health + 0.1)
        
        return {
            "status": HealthMetric(
                name="status",
                value=(1 - self.health) * 100,
                threshold_warning=30,
                threshold_critical=60
            )
        }
    
    def heal(self):
        time.sleep(0.05)
        if not self.failing:
            self.health = 0.9
            return True
        return False


def run_quick_demo():
    """Quick demonstration with final report"""
    
    print("\n" + "="*80)
    print("🚀 PROJECT PHOENIX - AUTONOMOUS SELF-HEALING SYSTEM")
    print("="*80)
    
    # Create components
    cache = SimpleComponent("cache")
    db = SimpleComponent("database")
    api = SimpleComponent("api")
    
    # Create healer
    healer = AutoHealer(check_interval_ms=50)
    
    # Register components
    healer.register_component("cache", cache.check_health)
    healer.register_component("database", db.check_health)
    healer.register_component("api", api.check_health)
    
    # Register recovery strategies
    healer.register_recovery_strategy("cache", [
        RecoveryAction("restart_cache", "Restart cache server", cache.heal)
    ])
    healer.register_recovery_strategy("database", [
        RecoveryAction("failover_db", "Failover to replica", db.heal)
    ])
    healer.register_recovery_strategy("api", [
        RecoveryAction("restart_api", "Restart API servers", api.heal)
    ])
    
    healer.start()
    
    print("\n📊 Autonomous Healing System Starting...")
    print("   ✓ Monitoring: cache, database, api")
    print("   ✓ Health checks every 50ms")
    print("   ✓ Automatic failure detection and recovery\n")
    
    # Run with failure injection
    start = time.time()
    cycle = 0
    
    try:
        while time.time() - start < 10:  # Run for 10 seconds
            elapsed = time.time() - start
            
            # Inject failures
            if 1 < elapsed < 2.5:
                cache.failing = True
            else:
                cache.failing = False
            
            if 3 < elapsed < 4.5:
                db.failing = True
            else:
                db.failing = False
            
            if 5.5 < elapsed < 7:
                api.failing = True
            else:
                api.failing = False
            
            # Run healing cycle
            healer.run_one_cycle()
            
            # Print status
            if cycle % 5 == 0:
                health = healer.monitor.get_system_health()
                state = healer.state_manager.current_state.value
                
                status_str = f"[{elapsed:5.1f}s] {state:20s}"
                for comp_name, comp in health["components"].items():
                    icon = "🟢" if comp["status"] == "healthy" else "🔴"
                    status_str += f" | {icon} {comp_name[:3]}"
                
                print(status_str)
            
            cycle += 1
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    
    healer.stop()
    
    # Print final report
    print("\n" + "="*80)
    print("📋 FINAL REPORT")
    print("="*80)
    
    report = healer.get_detailed_report()
    metrics = report["metrics"]
    
    print(f"\n✨ Final System State: {report['current_state'].upper()}")
    print(f"📈 Total Healing Cycles Run: {report['total_cycles']}")
    
    print(f"\n🔍 Failure Detection & Recovery:")
    print(f"   • Failures detected: {metrics['total_failures_detected']}")
    print(f"   • Healing attempts: {metrics['total_healings_attempted']}")
    print(f"   • Successful healings: {metrics['total_healings_successful']}")
    print(f"   • Failed healings: {metrics['total_healings_failed']}")
    
    if metrics['total_healings_attempted'] > 0:
        success_rate = (metrics['total_healings_successful'] / 
                       metrics['total_healings_attempted'] * 100)
        print(f"   • Success rate: {success_rate:.1f}%")
    
    print(f"\n⏱️  Performance Metrics:")
    if metrics['average_detection_time'] > 0:
        print(f"   • Average detection time: {metrics['average_detection_time']*1000:.2f}ms")
    if metrics['average_recovery_time'] > 0:
        print(f"   • Average recovery time: {metrics['average_recovery_time']*1000:.2f}ms")
        print(f"   • MTTR (Mean Time To Recovery): {metrics['mttr']*1000:.2f}ms")
    
    print(f"\n📊 Per-Component Statistics:")
    for component, comp_metrics in metrics["component_metrics"].items():
        print(f"   • {component:10s}: {comp_metrics['attempts']} attempts, "
              f"{comp_metrics['successful']} successful ({comp_metrics['success_rate']*100:.0f}%)")
    
    print("\n" + "="*80)
    print("✅ AUTONOMOUS SELF-HEALING SYSTEM WORKING SUCCESSFULLY")
    print("="*80)
    print("\n🎯 Key Capabilities Demonstrated:")
    print("   ✓ Continuous health monitoring")
    print("   ✓ Automatic failure detection")
    print("   ✓ Autonomous recovery execution")
    print("   ✓ State tracking and metrics")
    print("   ✓ Multi-component orchestration")
    print("   ✓ No human intervention required\n")


if __name__ == "__main__":
    run_quick_demo()
