# Quick Start Guide - Smart Payment Operations

## ✅ Setup Complete

All components are configured and ready to use!

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  New CSV-Based Architecture with OpenRouter Reasoning       │
└─────────────────────────────────────────────────────────────┘

simulator.py ──writes──> transactions.csv
                              │
                              │ reads
                              ▼
                         agent_engine.py
                         (OpenRouter + LangGraph)
                              │
                              │ uses
                              ▼
                          tools.py
                              │
                              │ updates
                              ▼
                      shared_config.json
                              │
                              │ reads
                              ▼
                         simulator.py
```

## Files Overview

| File | Purpose | Lines |
|------|---------|-------|
| `shared_config.json` | Central routing config & bank health | Config |
| `transactions.csv` | Real-time transaction log | Data |
| `simulator.py` | Transaction generator | 218 |
| `agent_engine.py` | LangGraph + OpenRouter reasoning | 375 |
| `tools.py` | Config modification functions | 209 |
| `app.py` | Main dashboard (War Room) | 418 |
| `checkout_ui.py` | Merchant payment page | 233 |

**Total:** ~1,453 lines of code

## Launch Instructions

### 1. Ensure API Key is Set

Edit `.env`:
```bash
OPENROUTER_API_KEY=your_actual_key_here
```

Get a free key at: https://openrouter.ai/

### 2. Launch the Main Dashboard

```bash
streamlit run app.py
```

Access at: http://localhost:8501

### 3. Launch the Checkout UI (Optional)

In a separate terminal:

```bash
streamlit run checkout_ui.py --server.port 8502
```

Access at: http://localhost:8502

## Usage Guide

### Using the Main Dashboard (app.py)

**Control Panel (Sidebar):**

1. **Start Simulator**
   - Click "▶️ Start" to begin transaction generation
   - Generates 5 transactions per second
   - Writes to `transactions.csv`

2. **Toggle Chaos Mode**
   - Click "Chaos: ✨ OFF" to enable failure injection
   - Becomes "Chaos: 🔥 ON"
   - Injects 30% failure rate (timeouts, errors, etc.)

3. **Run Agent Cycle**
   - Click "🔄 Run Agent Cycle" to analyze transactions
   - Agent reads from `transactions.csv`
   - Uses OpenRouter (Nvidia Nemotron) with reasoning_details
   - Updates `shared_config.json` with recommended actions

4. **Auto-Run Mode**
   - Check "Auto-run every 10s"
   - Agent automatically analyzes every 10 seconds

**Main Dashboard:**

- **Metrics Cards**: Success rate, latency, TPS, system status
- **Live Charts**: Success rate and latency over time from CSV
- **Bank Health**: Current status of all payment banks
- **Error Breakdown**: Types and counts of failures
- **Agent Reasoning**: LLM analysis and recommended actions
- **Reasoning Details**: OpenRouter reasoning transparency
- **Actions Log**: What the agent did and results

### Using the Checkout UI (checkout_ui.py)

**Submit Test Payments:**

1. Enter amount (pre-filled: $99.99)
2. Card details are pre-filled for testing
3. Click "🔒 Pay Securely"
4. Transaction is written to `transactions.csv`
5. Agent will analyze it in next cycle

**Bank Routing:**
- Reads `shared_config.json` for current weights
- Selects bank based on weighted distribution
- Respects enabled/disabled status
- Shows available banks at bottom

## Testing Scenarios

### Scenario 1: Normal Operation

```bash
# Terminal 1: Main dashboard
streamlit run app.py

# In dashboard sidebar:
1. Click "▶️ Start" simulator
2. Watch success rate (should be ~95-98%)
3. Click "🔄 Run Agent Cycle"
4. Agent should report "No actions needed"
```

### Scenario 2: Chaos Testing

```bash
# In dashboard sidebar:
1. Ensure simulator is running
2. Click "Chaos: ✨ OFF" → becomes "🔥 ON"
3. Watch success rate drop to ~70%
4. Click "🔄 Run Agent Cycle"
5. Agent should:
   - Detect low success rate
   - Identify failing banks
   - Reroute traffic or disable unhealthy banks
   - Update shared_config.json
6. Check Bank Health panel for changes
```

### Scenario 3: Merchant Payments

```bash
# Terminal 1: Main dashboard
streamlit run app.py

# Terminal 2: Checkout UI
streamlit run checkout_ui.py --server.port 8502

# In checkout UI:
1. Submit multiple payments
2. Check main dashboard for new transactions
3. Run agent cycle to analyze patterns
```

### Scenario 4: Agent Decision-Making

```bash
# With chaos mode ON:
1. Wait for ~50-100 failed transactions
2. Run agent cycle
3. Observe reasoning panel shows:
   - "REASONING: Success rate is below 95%..."
   - "ACTIONS: Rerouting traffic from bank_a..."
4. Check Bank Health - weights should change
5. Turn chaos OFF
6. Run agent again - should recover banks
```

## Data Flow Verification

**Verify the system is working:**

### 1. Check CSV Logging

```bash
# View recent transactions
tail -n 20 transactions.csv
```

Should show: timestamp, transaction_id, status, bank info

### 2. Check Config Updates

```bash
# View current config
cat shared_config.json
```

Should show: banks, routing_rules, agent_history

### 3. Monitor Agent Actions

In dashboard:
- Look at "🧠 Agent Reasoning & Actions" section
- Should show OpenRouter reasoning
- Should show actions taken (if any)
- Reasoning details available if enabled

## Troubleshooting

### Issue: "OPENROUTER_API_KEY not set"

**Solution:**
```bash
# Edit .env file
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Issue: No transactions appearing

**Solution:**
1. Start simulator in dashboard sidebar
2. Or submit payments via checkout_ui.py
3. Check `transactions.csv` exists and has data

### Issue: Agent not taking actions

**Solution:**
- System may be healthy (no action needed)
- Enable chaos mode to create issues
- Check success rate < 95% or latency > 200ms

### Issue: Import errors

**Solution:**
```bash
pip install -r requirements.txt
```

## Advanced Features

### Reasoning Details

Enable in OpenRouter API call (already configured):
```python
model_kwargs={"reasoning": {"enabled": True}}
```

View in dashboard after running agent cycle.

### Custom Tools

Add new functions in `tools.py`:
```python
def my_custom_action(args):
    config = get_config()
    # Modify config
    save_config(config)
    return {'success': True}
```

Register in `agent_engine.py` act_node.

### Bank Health States

- **healthy**: Normal operation (green)
- **degraded**: Performance issues (yellow)
- **down**: Not operational (red, auto-disabled)

Agent automatically manages transitions based on metrics.

## Key Metrics to Monitor

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Success Rate | >95% | 90-95% | <90% |
| Avg Latency | <150ms | 150-250ms | >250ms |
| TPS | >0 | - | 0 |
| Enabled Banks | 2-3 | 1 | 0 |

## Next Steps

1. ✅ Set OPENROUTER_API_KEY
2. ✅ Launch app.py
3. ✅ Start simulator
4. ✅ Run agent cycle
5. ✅ Enable chaos mode
6. ✅ Watch agent optimize routing
7. ✅ Submit test payments via checkout_ui.py

## File Locations

All files in: `c:\Users\shubh\cyber cypher\`

**Config:** `shared_config.json`  
**Data:** `transactions.csv`  
**Logs:** agent_history in shared_config.json  

---

**System is ready! Start with `streamlit run app.py` 🚀**
