# Smart Payment Operations - Updated System

## ✅ Complete! New Configuration Ready

### Indian Banks Configured

The system now works with **7 Indian banks**:

1. **HDFC Bank** - 20% weight
2. **SBI Bank** - 18% weight  
3. **ICICI Bank** - 17% weight
4. **BOB Bank** - 15% weight
5. **AXIS Bank** - 15% weight
6. **IDFC Bank** - 10% weight
7. **PNB Bank** - 5% weight

---

## Simulator Configuration

**Transaction Rate:** 1 transaction every 2 seconds

**Fields Generated:**
- `timestamp` - ISO format timestamp
- `txn_id` - Unique transaction ID
- `bank` - Bank name (HDFC, SBI, ICICI, BOB, AXIS, IDFC, PNB)
- `method` - Payment method (UPI, Card, Net Banking)
- `status` - Success or Fail
- `latency_ms` - Latency in milliseconds
- `amount` - Transaction amount

**Degraded Bank Logic:**
When a bank's `health_status` is set to `"degraded"` in `shared_config.json`:
- Latency increases to **600ms**
- Failure rate increases to **30%**

---

## Tools Available

### 1. `reroute_traffic(bank, target)`
**Purpose:** Shift traffic from one bank to another

**Example:**
```python
import tools
tools.reroute_traffic('sbi', 'hdfc')
# Shifts 50% of SBI's weight to HDFC
```

**Effect:**
- Reduces source bank weight by 50%
- Increases target bank weight accordingly
- Normalizes all weights to sum to 100%
- Logs action to `agent_history`

### 2. `set_retry_policy(bank, level)`
**Purpose:** Adjust retry policy for a specific bank

**Levels:**
- `'low'` - 1 retry, 500ms backoff
- `'normal'` - 3 retries, 1000ms backoff (default)
- `'high'` - 5 retries, 2000ms backoff

**Example:**
```python
import tools
tools.set_retry_policy('axis', 'high')
# Sets AXIS bank to high retry (5 retries)
```

**Effect:**
- Updates `retry_policy.level`
- Updates `retry_policy.max_retries`
- Updates `retry_policy.backoff_ms`
- Logs action to `agent_history`

### 3. `update_bank_health(bank, health_status, enabled)`
**Purpose:** Update bank health status

**Statuses:**
- `'healthy'` - Normal operation
- `'degraded'` - **600ms latency, 30% failure rate**
- `'down'` - Disabled, circuit breaker open

**Example:**
```python
import tools
tools.update_bank_health('sbi', 'degraded')
# SBI will now have 600ms latency and 30% failures
```

### 4. `toggle_chaos_mode(enabled, failure_rate)`
**Purpose:** Enable/disable chaos mode

**Example:**
```python
import tools
tools.toggle_chaos_mode(True, 0.3)
# Enables chaos with 30% failure injection
```

---

## Testing the System

### Test 1: Normal Operation
```bash
# Terminal 1: Start dashboard
streamlit run app.py

# In dashboard:
1. Click "▶️ Start" to start simulator
2. Watch transactions appear (1 every 2 seconds)
3. Observe success rates and latency
```

### Test 2: Degraded Bank Scenario
```python
# In Python console or agent:
import tools

# Set SBI to degraded
tools.update_bank_health('sbi', 'degraded')

# Monitor dashboard - SBI transactions will have:
# - 600ms latency (instead of ~150ms)
# - 30% failure rate (instead of ~4%)
```

### Test 3: Traffic Rerouting
```python
import tools

# SBI is degraded, reroute traffic to HDFC
tools.reroute_traffic('sbi', 'hdfc')

# Check shared_config.json:
# - SBI weight reduced (e.g., 18% → 9%)
# - HDFC weight increased (e.g., 20% → 29%)
```

### Test 4: Retry Policy Adjustment
```python
import tools

# Increase retries for unstable bank
tools.set_retry_policy('bob', 'high')

# BOB will now retry up to 5 times with 2s backoff
```

---

## File Structure

```
shared_config.json     → Bank configs, routing rules, agent history
transactions.csv       → Real-time transaction log (1 txn/2s)
simulator.py          → Transaction generator
tools.py              → reroute_traffic(), set_retry_policy()
agent_engine.py       → LangGraph + OpenRouter reasoning
app.py                → Streamlit dashboard
```

---

## Quick Start Commands

```bash
# Test simulator (generates 5 txns over 10 seconds)
python simulator.py

# Test tools
python tools.py

# Launch dashboard
streamlit run app.py
```

---

## Key Features

✅ **7 Indian Banks** - HDFC, SBI, ICICI, BOB, AXIS, IDFC, PNB  
✅ **Degraded Bank Logic** - 600ms latency, 30% failure when degraded  
✅ **Traffic Rerouting** - `reroute_traffic(source, target)`  
✅ **Retry Policies** - `set_retry_policy(bank, 'low'|'normal'|'high')`  
✅ **CSV Logging** - All transactions in `transactions.csv`  
✅ **Weighted Routing** - Probabilistic bank selection  
✅ **Payment Methods** - UPI, Card, Net Banking  

---

## Next Steps

1. ✅ Simulator and Tools are working
2. ✅ shared_config.json configured with 7 banks
3. ⏭️ Update agent_engine.py to use new tools
4. ⏭️ Launch dashboard with `streamlit run app.py`
5. ⏭️ Test degraded bank scenarios

**System is ready to launch!** 🚀
