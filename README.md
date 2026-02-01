# 🤖 Smart Payment Operations - Agentic AI System

An autonomous AI-powered payment gateway management system built with **LangGraph**, **OpenRouter**, and **Streamlit**.

## 🎯 Overview

This system uses an intelligent agent that continuously monitors payment transactions and autonomously manages gateway routing to maximize success rates and minimize latency. The agent follows an **Observe → Reason → Act → Learn** cycle powered by LangGraph and OpenRouter's LLM.

## ✨ Key Features

- 🧠 **Autonomous Decision Making** - LangGraph agent with 4-node cognitive cycle
- 🎯 **Intelligent Routing** - Dynamic traffic distribution across payment gateways
- 🔄 **Circuit Breakers** - Automatic failure detection and rerouting
- 📊 **Real-time Monitoring** - Dark-themed dashboard with live Plotly charts
- 🔥 **Chaos Engineering** - Controllable failure injection for testing
- 💳 **Demo Checkout** - Merchant payment page for end-to-end testing

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Demo Gateway   │────▶│   Simulator     │
│ (Checkout UI)   │     │ (Transaction    │
└─────────────────┘     │  Generator)     │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │ LangGraph Agent │
                        │ ┌─────────────┐ │
                        │ │  Observe    │ │
                        │ └──────┬──────┘ │
                        │ ┌──────▼──────┐ │
                        │ │  Reason     │◀┼── OpenRouter LLM
                        │ └──────┬──────┘ │
                        │ ┌──────▼──────┐ │
                        │ │    Act      │ │
                        │ └──────┬──────┘ │
                        │ ┌──────▼──────┐ │
                        │ │   Learn     │ │
                        │ └─────────────┘ │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │     Tools       │
                        │ routing_config  │
                        └─────────────────┘
```

## 📁 Project Structure

```
cyber cypher/
├── app.py                  # Main Streamlit dashboard
├── agent.py                # LangGraph agent (Observe-Reason-Act-Learn)
├── simulator.py            # Transaction generator with chaos toggle
├── tools.py                # Gateway management functions
├── demo_gateway.py         # Merchant checkout page
├── routing_config.json     # Shared gateway configuration
├── requirements.txt        # Python dependencies
└── .env                    # API keys and configuration
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=your_actual_key_here
```

Get your key from: https://openrouter.ai/

### 3. Run the Dashboard

```bash
streamlit run app.py
```

Opens at: http://localhost:8501

### 4. Run the Demo Gateway (Optional)

In a separate terminal:

```bash
streamlit run demo_gateway.py --server.port 8502
```

Opens at: http://localhost:8502

## 🎮 Usage Guide

### Main Dashboard (app.py)

1. **Start Simulator** - Click "▶️ Start" to begin transaction generation
2. **Toggle Chaos** - Enable "🔥 Chaos" mode to inject failures (30% failure rate)
3. **Run Agent** - Click "🔄 Run Agent Cycle" to let the AI analyze and act
4. **Enable Auto-Run** - Check "Auto-run every 10s" for continuous monitoring

### What to Watch

- **Success Rate** - Should stay above 95% (agent will act if it drops)
- **Latency** - Monitor average and P95 latency across gateways
- **Gateway Health** - See which gateways are enabled and their traffic weights
- **Agent Reasoning** - Read the AI's analysis and decisions in real-time
- **Actions Taken** - View specific commands executed (reroute, throttle, etc.)

### Chaos Testing Workflow

1. Start with normal operation (Chaos: OFF)
2. Let metrics stabilize (~30 seconds)
3. Enable Chaos mode
4. Watch success rate drop
5. Run agent cycle
6. Observe agent reroute traffic to healthy gateways
7. Verify success rate recovers

### Demo Gateway (demo_gateway.py)

1. Fill in payment details (default values provided)
2. Click "🔒 Pay Securely"
3. Transaction is processed through agent-managed gateways
4. View confirmation or error message
5. Switch to main dashboard to see the transaction

## 🔧 System Components

### Agent (agent.py)

**LangGraph State Machine:**

- **Observe Node** - Collects metrics, transaction data, gateway status
- **Reason Node** - Uses OpenRouter LLM (Nvidia Nemotron) to analyze and decide
- **Act Node** - Executes decisions via tools (reroute, throttle, circuit breaker)
- **Learn Node** - Evaluates outcomes and measures improvement

### Tools (tools.py)

**Available Actions:**

- `reroute_traffic(from, to, percentage)` - Shift traffic between gateways
- `throttle_retries(gateway_id, max_retries, backoff_ms)` - Adjust retry policy
- `open_circuit_breaker(gateway_id)` - Disable failing gateway
- `close_circuit_breaker(gateway_id)` - Re-enable recovered gateway
- `update_gateway_metrics()` - Track performance in real-time

### Simulator (simulator.py)

**Features:**

- Generates 5 TPS (configurable)
- Weighted gateway selection
- Chaos toggle with 30% failure injection
- Realistic error scenarios (timeouts, network errors, declined payments)
- Real-time metrics calculation

### Configuration (routing_config.json)

**Shared State:**

- 3 payment gateways (Stripe, PayPal, Razorpay)
- Dynamic traffic weights
- Circuit breaker states
- Retry policies
- Performance metrics
- Agent action history

## 📊 Metrics Explained

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Success Rate | % of successful transactions | Target: 95%+ |
| Avg Latency | Mean processing time | Good: <150ms |
| P95 Latency | 95th percentile latency | Good: <250ms |
| Current TPS | Transactions per second | Set to 5 |
| Gateway Weight | % of traffic routed to gateway | Sum: 100% |

## 🧪 Testing Scenarios

### Scenario 1: Normal Operations

```
✅ Success rate: 96-98%
✅ All gateways healthy
✅ Agent: "No actions needed"
```

### Scenario 2: Chaos Mode

```
🔥 Success rate drops to 70-80%
⚠️ Gateway A fails frequently
🤖 Agent detects issue
✅ Agent reroutes traffic to Gateway B & C
✅ Success rate recovers to 90%+
```

### Scenario 3: Gateway Recovery

```
⚠️ Gateway was disabled by circuit breaker
✅ Failure rate decreases
🤖 Agent detects recovery
✅ Agent re-enables gateway
✅ Traffic gradually restored
```

## 🎨 UI Highlights

- **Dark Theme** - Professional `#0f1419` background with `#6366f1` accents
- **Live Charts** - Plotly time-series graphs updating every 2 seconds
- **Color-Coded Status** - Green (healthy), Red (failed), Amber (warning)
- **Agent Reasoning Box** - Displays LLM thought process in real-time
- **Gateway Cards** - Visual health indicators with metrics

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM reasoning | Yes |

## 🛠️ Customization

### Adjust Transaction Rate

In `app.py`, modify:
```python
simulator.simulator.start(tps=10)  # Change from 5 to 10
```

### Change LLM Model

In `agent.py`, modify:
```python
model="nvidia/nemotron-3-nano-30b-a3b:free"  # Try other OpenRouter models
```

### Adjust Chaos Failure Rate

In `app.py`, modify:
```python
simulator.simulator.toggle_chaos(enabled=True, failure_rate=0.5)  # 50% failures
```

## 🐛 Troubleshooting

**Agent shows "Error in reasoning"**
- Check `.env` has valid `OPENROUTER_API_KEY`
- Verify internet connection
- Check OpenRouter API status

**No transactions appearing**
- Click "▶️ Start" to start the simulator
- Wait 5-10 seconds for data generation

**Charts not updating**
- Streamlit auto-refreshes every 2 seconds
- Try manually refreshing browser (F5)

**Import errors**
- Run `pip install -r requirements.txt`
- Ensure Python 3.9+

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent framework
- [OpenRouter](https://openrouter.ai/) - LLM API
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive charts

---

**Made with ❤️ for autonomous payment operations**
