# New Architecture - Smart Payment Operations

## ✅ Complete Structure Created

### Files Created

| File | Purpose | Status |
|------|---------|--------|
| `shared_config.json` | Stores routing rules and bank health | ✅ Created |
| `transactions.csv` | Real-time transaction log | ✅ Created |
| `simulator.py` | Generates transactions, writes to CSV, reads config | ✅ Created |
| `agent_engine.py` | LangGraph with OpenRouter reasoning | ✅ Created |
| `tools.py` | Functions to modify shared_config.json | ✅ Created |
| `app.py` | Main Streamlit "War Room" dashboard | ⏳ To update |
| `checkout_ui.py` | Merchant payment page | ✅ Created |

### Renamed Files

- `agent.py` → `agent_engine.py` ✅
- `demo_gateway.py` → `checkout_ui.py` ✅

---

## Data Flow Contract

```
┌─────────────────┐
│  checkout_ui.py │  (Merchant Payment Page)
└────────┬────────┘
         │ writes
         ▼
┌─────────────────┐
│transactions.csv │  (Real-time Log)
└────────┬────────┘
         │ reads
         ▼
┌─────────────────┐
│ agent_engine.py │  (LangGraph + OpenRouter)
└────────┬────────┘
         │ uses
         ▼
┌─────────────────┐
│    tools.py     │  (Modify Config)
└────────┬────────┘
         │ updates
         ▼
┌─────────────────┐
│shared_config.   │  (Routing Rules & Health)
│     json        │
└────────┬────────┘
         │ reads
         ▼
┌─────────────────┐
│  simulator.py   │  (Transaction Generator)
└────────┬────────┘
         │ writes
         ▼
    transactions.csv
```

---

## Component Details

### 1. shared_config.json
**Purpose:** Central configuration store

**Structure:**
```json
{
  "banks": [
    {
      "id": "bank_a",
      "name": "Stripe Gateway",
      "weight": 50,
      "enabled": true,
      "health_status": "healthy",
      "circuit_breaker": {...},
      "retry_policy": {...},
      "metrics": {...}
    }
  ],
  "routing_rules": {
    "primary_bank": "bank_a",
    "fallback_strategy": "weighted_round_robin",
    "chaos_mode": false,
    "chaos_failure_rate": 0.3
  },
  "agent_history": [...]
}
```

**Read by:** simulator.py, checkout_ui.py  
**Written by:** tools.py (via agent_engine.py)

### 2. transactions.csv
**Purpose:** Real-time transaction log

**Columns:**
- timestamp
- transaction_id
- amount, currency, type
- bank_id, bank_name
- status (success/failed)
- latency_ms
- error_code, error_message

**Written by:** simulator.py, checkout_ui.py  
**Read by:** agent_engine.py

### 3. simulator.py
**Functionality:**
- ✅ Reads `shared_config.json` for routing rules
- ✅ Generates realistic transactions (5 TPS default)
- ✅ Respects bank weights and enabled status
- ✅ Honors chaos mode setting
- ✅ Writes all transactions to `transactions.csv`
- ✅ Thread-safe CSV writing

**Key Methods:**
- `start(tps)` - Begin generation
- `stop()` - Stop generation
- `_load_config()` - Read shared_config.json
- `_write_to_csv(transaction)` - Append to CSV

### 4. agent_engine.py
**Functionality:**
- ✅ LangGraph with 4-node cycle (Observe → Reason → Act → Learn)
- ✅ OpenRouter integration (`nvidia/nemotron-3-nano-30b-a3b:free`)
- ✅ Reasoning details enabled
- ✅ Reads transactions.csv for observation
- ✅ Calculates metrics from CSV data
- ✅ Uses tools to update shared_config.json

**Nodes:**
1. **Observe**: Reads CSV, calculates metrics, gets bank status
2. **Reason**: OpenRouter LLM analyzes patterns with reasoning_details
3. **Act**: Executes tools to modify shared_config.json
4. **Learn**: Evaluates outcomes

### 5. tools.py
**Functions:**
- ✅ `get_config()` - Load shared_config.json
- ✅ `save_config()` - Save shared_config.json
- ✅ `reroute_traffic()` - Adjust bank weights
- ✅ `update_bank_health()` - Set health status (healthy/degraded/down)
- ✅ `toggle_chaos_mode()` - Enable/disable failure injection
- ✅ `adjust_retry_policy()` - Modify retry settings

**All functions:**
- Update shared_config.json
- Log actions to agent_history
- Return success/error status

### 6. checkout_ui.py
**Functionality:**
- ✅ Merchant payment page (Streamlit)
- ✅ Reads shared_config.json for bank routing
- ✅ Weighted bank selection
- ✅ Writes completed transactions to transactions.csv
- ✅ Dark-themed UI
- ✅ Success/failure feedback

**Launch:**
```bash
streamlit run checkout_ui.py --server.port 8502
```

### 7. app.py (Main Dashboard)
**Status:** Needs update to work with new architecture

**Required changes:**
- Import `agent_engine` instead of `agent`
- Read transactions from CSV instead of simulator memory
- Use `shared_config.json` instead of `routing_config.json`
- Update controls for new tools

---

## Shared Contract Summary

**Contract Flow:**

1. **Simulator/Checkout** → Writes to `transactions.csv`
2. **Agent** → Reads `transactions.csv`
3. **Agent** → Analyzes and reasons
4. **Agent** → Uses **Tools** to update `shared_config.json`
5. **Simulator** → Reads `shared_config.json`
6. **Simulator** → Adjusts behavior accordingly
7. **Loop continues...**

---

## Key Features

✅ **CSV-based logging** - Persistent transaction history  
✅ **Shared config** - Single source of truth  
✅ **OpenRouter reasoning** - reasoning_details enabled for transparency  
✅ **Decoupled components** - Agent, simulator, and checkout are independent  
✅ **File-based coordination** - No tight coupling between processes  
✅ **Bank health tracking** - healthy/degraded/down states  
✅ **Routing rules** - Centralized in shared_config.json  

---

## Next Steps

1. **Test the new architecture:**
   ```bash
   # Terminal 1: Checkout UI
   streamlit run checkout_ui.py --server.port 8502
   
   # Terminal 2: Main dashboard (after updating app.py)
   streamlit run app.py
   ```

2. **Verify data flow:**
   - Submit payment in checkout_ui.py
   - Check transactions.csv for new entry
   - Run agent cycle
   - Check shared_config.json for updates
   - Observe simulator behavior change

3. **Update app.py** to work with new architecture

---

## Files Summary

**Created/Updated:**
- ✅ shared_config.json (80 lines)
- ✅ transactions.csv (header only)
- ✅ simulator.py (218 lines) - CSV writer
- ✅ agent_engine.py (375 lines) - CSV reader
- ✅ tools.py (209 lines) - Config updater
- ✅ checkout_ui.py (233 lines) - CSV writer
- ⏳ app.py - Needs update

**Total new architecture code:** ~1,115 lines
