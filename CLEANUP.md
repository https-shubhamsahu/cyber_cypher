# Cleanup script to fix corrupted data and reset system

## Issue
The old simulator was running and created infinity/overflow values in routing_config.json.
This is causing "int too large to convert to float" errors.

## Solution

1. **Stop the old app:**
   - Press Ctrl+C in the terminal running `streamlit run app.py`

2. **Reset shared_config.json:**
   - The new system uses `shared_config.json` (not routing_config.json)
   - This file is already clean

3. **Clear old transactions.csv:**
   - Optional: Delete to start fresh

4. **Restart with new system:**
   ```bash
   streamlit run app.py
   ```

## Quick Fix Commands

```powershell
# Stop current streamlit (Ctrl+C in terminal)

# Optional: Clear old transaction data
Remove-Item transactions.csv -ErrorAction SilentlyContinue

# Optional: Archive old routing_config.json
Move-Item routing_config.json routing_config.json.old -ErrorAction SilentlyContinue

# Restart new system
streamlit run app.py
```

## What Changed

**OLD SYSTEM:**
- Used `routing_config.json`
- Simulator stored metrics in memory and updated JSON
- Exponential moving average caused overflow

**NEW SYSTEM:**
- Uses `shared_config.json` (clean, no overflow)
- Simulator writes to `transactions.csv`
- Agent reads CSV and updates config
- Tools manage config safely

## The Error Explained

```
Simulator error: int too large to convert to float
Simulator error: cannot convert float infinity to integer
```

**Cause:** 
- Old simulator's exponential moving average formula
- After many transactions: `new_latency = 0.3 * latency + 0.7 * old_latency`
- `old_latency` grew to infinity over thousands of iterations

**In routing_config.json line 21:**
```json
"avg_latency_ms": 135803683478571622444480188... (400+ digits!)
```

**Fix:**
- New system doesn't use that file
- Uses fresh `shared_config.json` instead
- CSV-based metrics don't accumulate errors

## Clean Start Steps

1. **Kill old app:** Ctrl+C
2. **Verify new config exists:**
   ```bash
   cat shared_config.json  # Should show clean data
   ```
3. **Start new app:**
   ```bash
   streamlit run app.py
   ```
4. **In dashboard:**
   - Click "▶️ Start" to start new simulator
   - New simulator writes to CSV and reads shared_config.json
   - NO MORE ERRORS!
