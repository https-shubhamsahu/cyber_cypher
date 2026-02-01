"""
Tools - Functions to modify shared_config.json

Provides deterministic action functions for the agent to update routing rules and bank health.
"""

import json
import os
import time
from typing import Dict, Any, List
from datetime import datetime

CONFIG_FILE = "shared_config.json"


def get_config() -> Dict[str, Any]:
    """Load current configuration from shared_config.json."""
    for attempt in range(3):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    content = f.read()
                    if content.strip():
                        return json.loads(content)
            time.sleep(0.1)
        except Exception as e:
            if attempt < 2:
                time.sleep(0.1)
                continue
            print(f"Error loading config: {e}")
    
    # Return default
    return {
        "banks": [],
        "routing_rules": {},
        "global_config": {},
        "agent_history": []
    }


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to shared_config.json."""
    for attempt in range(3):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return
        except Exception as e:
            if attempt < 2:
                time.sleep(0.1)
                continue
            print(f"Error saving config: {e}")


def reroute_traffic(bank: str, target: str) -> Dict[str, Any]:
    """
    Reroute traffic from one bank to another by shifting 50% of the source bank's weight.
    
    Args:
        bank: Source bank ID (e.g., 'hdfc', 'sbi')
        target: Destination bank ID
    
    Returns:
        Result of the operation
    """
    config = get_config()
    banks_list = config.get('banks', [])
    
    source_bank = next((b for b in banks_list if b['id'] == bank), None)
    target_bank = next((b for b in banks_list if b['id'] == target), None)
    
    if not source_bank:
        return {'success': False, 'error': f'Source bank {bank} not found'}
    
    if not target_bank:
        return {'success': False, 'error': f'Target bank {target} not found'}
    
    # Shift 50% of source bank's weight to target
    shift_amount = source_bank['weight'] // 2
    source_bank['weight'] = max(5, source_bank['weight'] - shift_amount)  # Min 5% weight
    target_bank['weight'] += shift_amount
    
    # Normalize weights to sum to 100
    enabled_banks = [b for b in banks_list if b.get('enabled', True)]
    total_weight = sum(b['weight'] for b in enabled_banks)
    if total_weight > 0:
        for b in enabled_banks:
            b['weight'] = int((b['weight'] / total_weight) * 100)
    
    # Log action
    config.setdefault('agent_history', []).append({
        'timestamp': datetime.now().isoformat(),
        'action': 'reroute_traffic',
        'details': {
            'from': bank,
            'to': target,
            'new_weights': {b['id']: b['weight'] for b in banks_list}
        }
    })
    config['agent_history'] = config['agent_history'][-100:]
    
    save_config(config)
    
    return {
        'success': True,
        'source_bank': bank,
        'target_bank': target,
        'source_weight': source_bank['weight'],
        'target_weight': target_bank['weight']
    }


def set_retry_policy(bank: str, level: str) -> Dict[str, Any]:
    """
    Set retry policy for a specific bank.
    
    Args:
        bank: Target bank ID (e.g., 'hdfc', 'sbi')
        level: Retry level - 'low' (1 retry), 'normal' (3 retries), 'high' (5 retries)
    
    Returns:
        Result of the operation
    """
    config = get_config()
    banks_list = config.get('banks', [])
    
    target_bank = next((b for b in banks_list if b['id'] == bank), None)
    if not target_bank:
        return {'success': False, 'error': f'Bank {bank} not found'}
    
    # Set retry parameters based on level
    retry_config = {
        'low': {'max_retries': 1, 'backoff_ms': 500},
        'normal': {'max_retries': 3, 'backoff_ms': 1000},
        'high': {'max_retries': 5, 'backoff_ms': 2000}
    }
    
    if level not in retry_config:
        return {'success': False, 'error': f'Invalid level: {level}. Use low/normal/high'}
    
    policy = retry_config[level]
    target_bank['retry_policy']['level'] = level
    target_bank['retry_policy']['max_retries'] = policy['max_retries']
    target_bank['retry_policy']['backoff_ms'] = policy['backoff_ms']
    
    # Log action
    config.setdefault('agent_history', []).append({
        'timestamp': datetime.now().isoformat(),
        'action': 'set_retry_policy',
        'details': {
            'bank': bank,
            'level': level,
            'max_retries': policy['max_retries'],
            'backoff_ms': policy['backoff_ms']
        }
    })
    config['agent_history'] = config['agent_history'][-100:]
    
    save_config(config)
    
    return {
        'success': True,
        'bank': bank,
        'level': level,
        'policy': target_bank['retry_policy']
    }


def update_bank_health(bank: str, health_status: str, enabled: bool = None) -> Dict[str, Any]:
    """
    Update bank health status. If set to "degraded", simulator will use 600ms latency and 30% failure rate.
    
    Args:
        bank: Target bank ID
        health_status: Health status ('healthy', 'degraded', 'down')
        enabled: Whether bank should be enabled (optional)
    
    Returns:
        Result of the operation
    """
    config = get_config()
    banks_list = config.get('banks', [])
    
    target_bank = next((b for b in banks_list if b['id'] == bank), None)
    if not target_bank:
        return {'success': False, 'error': f'Bank {bank} not found'}
    
    target_bank['health_status'] = health_status
    if enabled is not None:
        target_bank['enabled'] = enabled
    
    # Auto-disable if down
    if health_status == 'down':
        target_bank['enabled'] = False
        target_bank['circuit_breaker']['state'] = 'open'
    elif health_status == 'healthy':
        target_bank['circuit_breaker']['state'] = 'closed'
    
    # Log action
    config.setdefault('agent_history', []).append({
        'timestamp': datetime.now().isoformat(),
        'action': 'update_bank_health',
        'details': {'bank': bank, 'health_status': health_status, 'enabled': enabled}
    })
    config['agent_history'] = config['agent_history'][-100:]
    
    save_config(config)
    
    return {
        'success': True,
        'bank': bank,
        'health_status': health_status,
        'enabled': target_bank['enabled']
    }


def toggle_chaos_mode(enabled: bool, failure_rate: float = 0.3) -> Dict[str, Any]:
    """
    Toggle chaos mode in routing rules.
    
    Args:
        enabled: Whether to enable chaos mode
        failure_rate: Failure injection rate (0-1)
    
    Returns:
        Result of the operation
    """
    config = get_config()
    
    if 'routing_rules' not in config:
        config['routing_rules'] = {}
    
    config['routing_rules']['chaos_mode'] = enabled
    config['routing_rules']['chaos_failure_rate'] = min(1.0, max(0.0, failure_rate))
    
    # Log action
    config.setdefault('agent_history', []).append({
        'timestamp': datetime.now().isoformat(),
        'action': 'toggle_chaos_mode',
        'details': {'enabled': enabled, 'failure_rate': failure_rate}
    })
    config['agent_history'] = config['agent_history'][-100:]
    
    save_config(config)
    
    return {
        'success': True,
        'chaos_mode': enabled,
        'failure_rate': failure_rate
    }


def get_all_banks() -> List[Dict[str, Any]]:
    """Get list of all banks from config."""
    config = get_config()
    return config.get('banks', [])


if __name__ == "__main__":
    print("Testing Tools...")
    
    print("\n1. Get all banks:")
    banks = get_all_banks()
    for bank in banks:
        print(f"  - {bank['name']} ({bank['id']}): {bank['weight']}% weight, {bank['health_status']}")
    
    print("\n2. Set HDFC to degraded:")
    result = update_bank_health('hdfc', 'degraded')
    print(f"  Result: {result}")
    
    print("\n3. Reroute traffic from SBI to ICICI:")
    result = reroute_traffic('sbi', 'icici')
    print(f"  Result: {result}")
    
    print("\n4. Set high retry policy for AXIS:")
    result = set_retry_policy('axis', 'high')
    print(f"  Result: {result}")
    
    print("\n5. Enable chaos mode:")
    result = toggle_chaos_mode(True, 0.4)
    print(f"  Result: {result}")
    
    print("\nDone! Check shared_config.json for changes.")
