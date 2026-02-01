"""
Transaction Simulator - Writes to transactions.csv

Generates realistic payment transactions and logs them to CSV.
Reads shared_config.json for routing rules and bank health.

Generates 2 transactions per second.
If a bank's health_status is "degraded", increases latency to 600ms and failure rate to 30%.
"""

import random
import time
import threading
import csv
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class TransactionSimulator:
    """Real-time payment transaction generator that writes to CSV."""
    
    def __init__(self):
        self.running = False
        self.interval_seconds = 2.0  # 1 transaction every 2 seconds
        self.lock = threading.Lock()
        self.thread = None
        self.csv_file = "transactions.csv"
        self.config_file = "shared_config.json"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load current configuration from shared_config.json."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Return default if file doesn't exist
        return {
            "banks": [],
            "routing_rules": {"chaos_mode": False, "chaos_failure_rate": 0.3},
            "global_config": {}
        }
    
    def start(self):
        """Start transaction generation (1 txn every 2 seconds)."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._generate_loop, daemon=True)
        self.thread.start()
        print(f"✓ Simulator started - 1 transaction every 2 seconds")
    
    def stop(self):
        """Stop transaction generation."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("✓ Simulator stopped")
    
    def _generate_loop(self):
        """Main generation loop running in background thread."""
        while self.running:
            try:
                transaction = self._generate_transaction()
                self._write_to_csv(transaction)
                time.sleep(self.interval_seconds)
            except Exception as e:
                print(f"Simulator error: {e}")
    
    def _generate_transaction(self) -> Dict[str, Any]:
        """Generate a single transaction based on shared_config.json."""
        config = self._load_config()
        banks = config.get('banks', [])
        
        # Filter enabled banks
        enabled_banks = [b for b in banks if b.get('enabled', True)]
        
        if not enabled_banks:
            # Use first bank if none enabled
            bank = banks[0] if banks else {
                'id': 'hdfc',
                'name': 'HDFC Bank',
                'weight': 100,
                'health_status': 'healthy',
                'metrics': {'success_rate': 0.95, 'avg_latency_ms': 150}
            }
        else:
            # Weighted random selection
            weights = [b.get('weight', 0) for b in enabled_banks]
            bank = random.choices(enabled_banks, weights=weights)[0]
        
        # Generate transaction details
        methods = ['UPI', 'Card', 'Net Banking']
        amounts = [100, 250, 500, 1000, 1500, 2500, 5000]
        
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'txn_id': f"txn_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'amount': random.choice(amounts),
            'bank': bank.get('name', 'Unknown'),
            'method': random.choice(methods),
        }
        
        # Process transaction (simulate with latency and potential failure)
        result = self._process_transaction(transaction, bank, config.get('routing_rules', {}))
        transaction.update(result)
        
        return transaction
    
    def _process_transaction(self, transaction: Dict, bank: Dict, routing_rules: Dict) -> Dict[str, Any]:
        """
        Simulate transaction processing with potential failures.
        
        DEGRADED bank logic:
        - If bank's health_status is "degraded", increase latency to 600ms and failure rate to 30%
        """
        base_latency = bank.get('metrics', {}).get('avg_latency_ms', 150)
        success_rate = bank.get('metrics', {}).get('success_rate', 0.95)
        
        # Check bank health status
        health_status = bank.get('health_status', 'healthy').lower()
        
        retry_count = random.choice([0, 0, 0, 1, 2]) if health_status == 'healthy' else random.choice([1, 2, 3])
        
        if health_status == 'degraded':
            # DEGRADED bank: 600ms latency, 30% failure rate
            latency_ms = 600
            success_rate = 0.7  # 30% failure rate = 70% success rate
            
            if random.random() > success_rate:
                return {
                    'status': 'Fail',
                    'latency_ms': latency_ms + random.randint(-50, 50),
                    'error_code': 'TIMEOUT',
                    'retry_count': 3
                }
            else:
                return {
                    'status': 'Success',
                    'latency_ms': latency_ms + random.randint(-50, 50),
                    'error_code': '',
                    'retry_count': retry_count
                }
        
        # Check if chaos mode is enabled
        chaos_mode = routing_rules.get('chaos_mode', False)
        chaos_rate = routing_rules.get('chaos_failure_rate', 0.3)
        
        if chaos_mode and random.random() < chaos_rate:
            # Chaos scenario - inject failure
            return {
                'status': 'Fail',
                'latency_ms': int(base_latency * random.uniform(2, 4)),
                'error_code': 'GATEWAY_ERROR',
                'retry_count': random.randint(1, 3)
            }
        
        # Normal processing
        if random.random() > success_rate:
            return {
                'status': 'Fail',
                'latency_ms': int(base_latency + random.gauss(0, 20)),
                'error_code': random.choice(['AUTH_FAILURE', 'INSUFFICIENT_FUNDS', 'GATEWAY_ERROR']),
                'retry_count': retry_count
            }
        
        # Success
        return {
            'status': 'Success',
            'latency_ms': int(base_latency * random.uniform(0.8, 1.2)),
            'error_code': '',
            'retry_count': retry_count
        }
    
    def _write_to_csv(self, transaction: Dict):
        """Write transaction to CSV file."""
        try:
            with self.lock:
                file_exists = os.path.exists(self.csv_file)
                with open(self.csv_file, 'a', newline='') as f:
                    fieldnames = [
                        'timestamp', 'txn_id', 'bank', 'method', 'status', 
                        'latency_ms', 'amount', 'error_code', 'retry_count'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerow({
                        'timestamp': transaction['timestamp'],
                        'txn_id': transaction['txn_id'],
                        'bank': transaction['bank'],
                        'method': transaction['method'],
                        'status': transaction['status'],
                        'latency_ms': transaction['latency_ms'],
                        'amount': transaction.get('amount', 0),
                        'error_code': transaction.get('error_code', ''),
                        'retry_count': transaction.get('retry_count', 0)
                    })
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def get_recent_transactions(self, count: int = 100) -> List[Dict[str, Any]]:
        """Read recent transactions from CSV."""
        try:
            with self.lock:
                if not os.path.exists(self.csv_file):
                    return []
                
                with open(self.csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    transactions = list(reader)
                    return transactions[-count:]
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []


# Global simulator instance
simulator = TransactionSimulator()


if __name__ == "__main__":
    print("Testing Transaction Simulator...")
    simulator.start()
    
    # Run for 10 seconds
    time.sleep(10)
    
    simulator.stop()
    
    # Show recent transactions
    recent = simulator.get_recent_transactions(5)
    print(f"\nLast {len(recent)} transactions:")
    for txn in recent:
        print(f"  {txn['timestamp']} | {txn['bank']:15} | {txn['method']:12} | {txn['status']:7} | {txn['latency_ms']}ms")
