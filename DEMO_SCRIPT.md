# 🎬 DEMO SCRIPT - Payment Sentinel System

## Complete Demo Flow

### 🎯 Objective
Demonstrate AI-powered autonomous payment operations with real-time adaptation.

---

## ✅ System Setup (DONE)

- **Simulator:** 2 transactions per second ✅
- **Checkout:** Shows degraded banks with warnings (not hidden) ✅
- **Dashboard:** Real-time monitoring with AI reasoning ✅

---

## 📋 Demo Script

### Part 1: Healthy System (Green State)
**Duration: 30 seconds**

1. **Open Dashboard** (http://localhost:8501)
   - Point to metrics: "Success Rate 99%, Latency ~130ms"
   - Show latency chart: "All banks performing normally"
   - Status: **"Everything is Green"**

2. **Show Transaction Flow**
   - "Simulator generating 2 transactions per second"
   - Point to Plotly chart: "All lines below 300ms threshold"
   - **"System is healthy, optimal performance"**

---

### Part 2: Trigger Chaos
**Duration: 10 seconds**

3. **Click "💥 BREAK HDFC"** button
   - HDFC status changes: 🟢 HEALTHY → 🟡 DEGRADED
   - **"Simulating a bank degradation"**

4. **Watch Latency Spike**
   - HDFC line (red) jumps to ~600ms on chart
   - Success rate starts dropping
   - **"HDFC is now experiencing high latency"**

---

### Part 3: Sentinel Acts (AI Response)
**Duration: 20 seconds**

5. **Click "🔄 Run Analysis Now"**
   - Agent analyzes last 20 transactions
   - **Point to "Sentinel Mind" sidebar**

6. **Show AI Reasoning**
   - Reasoning box displays:
     ```
     ANALYSIS: HDFC Bank latency spiked to 600ms with 30% failure rate.
     DECISION: YES - Taking action to prevent customer impact
     ACTIONS: Rerouting traffic from HDFC to ICICI
     ```
   - **"The AI detected the problem and is taking action autonomously"**

7. **Show Actions Executed**
   - Expand actions list:
     ```python
     reroute_traffic(hdfc → icici)
     ```
   - **"Traffic is being moved away from HDFC before failures escalate"**

---

### Part 4: Checkout Magic (Real-time Adaptation)
**Duration: 30 seconds**

8. **Open Checkout Demo** (http://localhost:8502)
   - **Before AI action:** HDFC visible with "⚠️ Slow - Not Recommended"
   - Yellow warning box: "HDFC Bank experiencing high latency"

9. **Show Bank Selection**
   - ICICI has "⚡ Recommended" badge
   - SBI, AXIS, BOB, etc. all healthy
   - **"The checkout page is guiding customers to faster options"**

10. **Select HDFC (degraded)**
    - Red error message appears:
      ```
      ⚠️ Warning: HDFC Bank is currently experiencing high latency (~600ms).
      Payment may take longer. We recommend selecting a different bank.
      ```
    - **"Users are warned in real-time based on AI decisions"**

11. **Select ICICI (recommended)**
    - Green success message:
      ```
      ✓ Excellent choice! ICICI Bank is currently our fastest processor
      with ~140ms response time.
      ```
    - **"Customers are guided to the best performing option"**

---

### Part 5: The Result (Recovery)
**Duration: 20 seconds**

12. **Back to Dashboard**
    - Point to Plotly chart: "ICICI line shows increased traffic"
    - HDFC line flattens (less traffic)
    - **"Less load on HDFC = fewer failures"**

13. **Show Metrics Recovering**
    - Success rate improving
    - Average latency dropping
    - **"The system is self-healing through intelligent routing"**

14. **Click "🔧 HEAL HDFC"**
    - HDFC status: 🟡 DEGRADED → 🟢 HEALTHY
    - Latency returns to ~120ms
    - **"Bank recovered, AI can route traffic back when ready"**

---

## 🎯 Key Talking Points

### 1. Autonomous Decision-Making
- "The AI **detects**, **reasons**, and **acts** without human intervention"
- "From problem detection to traffic rerouting in seconds"

### 2. Customer Experience Protection
- "Customers never see failures - they're **guided away from problem banks**"
- "Transparent warnings, not hidden failures"
- "**Fastest option always highlighted**"

### 3. Closed Feedback Loop
- "Simulator generates data → Agent analyzes → Config updates → Checkout adapts"
- "Every part of the system is synced in **real-time**"

### 4. Real Business Value
- "**99%+ uptime** despite individual bank failures"
- "**Sub-300ms** latency maintained system-wide"
- "**Zero customer-facing errors** through proactive routing"

---

## 💡 Demo Variations

### Scenario A: Show Agent Auto-Run
1. Enable "⚡ Auto-Analyze (10s)" checkbox
2. Break HDFC
3. Wait 10 seconds - agent runs automatically
4. Show continuous monitoring in Sentinel Mind

### Scenario B: Show Multiple Banks Degraded
1. Break HDFC
2. Use tools.py to break another bank
3. Show AI routing to the last healthy bank
4. Demonstrate prioritization logic

### Scenario C: Show Checkout Transaction
1. Complete a payment through checkout
2. Show transaction appears instantly in dashboard log
3. Point out: "This transaction is now part of AI's analysis data"

---

## 🎬 30-Second Elevator Pitch Version

1. **Start:** "Everything green, 99% success"
2. **Break:** Click BREAK HDFC → Red spike on chart
3. **AI Acts:** Run Analysis → Show reasoning: "Moving traffic to ICICI"
4. **Customer View:** Open checkout → HDFC warned, ICICI recommended
5. **Result:** Chart recovers, fewer failures, self-healing complete

**Tagline:** "AI that sees problems before customers do, and fixes them automatically."

---

## 📊 Expected Results

| Metric | Before Degradation | During (No AI) | During (With AI) |
|--------|-------------------|----------------|------------------|
| Success Rate | 99% | 70% | 95%+ |
| Avg Latency | 130ms | 350ms | 180ms |
| Failed Txns | <1% | 30% | 5% |
| Customer Impact | None | High | Minimal |

---

## 🚀 Your System Is Demo-Ready!

**Both UIs running:**
- Dashboard: http://localhost:8501
- Checkout: http://localhost:8502

**All features working:**
- ✅ 2 txn/sec simulator
- ✅ Degraded bank warnings in checkout
- ✅ Real-time AI reasoning display
- ✅ Self-healing traffic rerouting
- ✅ Live latency visualization

**Follow the script above for maximum impact!** 🎉
