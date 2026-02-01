"""
Agent Engine - LangGraph with Structured Reasoning and Memory
"""

import os
import csv
import json
import time
from typing import TypedDict, List, Dict, Any
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv

import tools

# Load environment variables
load_dotenv()

# Global variable to store reasoning details for UI
last_reasoning = {
    'timestamp': None,
    'reasoning': '',
    'reasoning_details': None,
    'actions': [],
    'feedback': {}
}


class AgentState(TypedDict):
    """State passed between nodes in the graph."""
    observations: Dict[str, Any]
    memory: List[Dict[str, Any]]
    structured_response: Dict[str, Any]
    reasoning: str  # Kept for UI back-compat
    reasoning_details: Any
    actions: List[str]
    feedback: Dict[str, Any]


def create_llm():
    """Create Groq LLM client - Fast and free tier friendly."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set in .env file. Get one free at https://console.groq.com/keys")
    
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=api_key,
        temperature=0.4,
        max_retries=3
    )


def observe_node(state: AgentState) -> AgentState:
    """
    Observe Node: Read transactions and compute advanced metrics.
    Looking for: Success Rate, Latency, Error Codes, Retry Counts
    """
    print("📊 Observe: Reading transactions...")
    
    transactions = []
    try:
        with open('transactions.csv', 'r') as f:
            reader = csv.DictReader(f)
            all_txns = list(reader)
            transactions = all_txns[-30:]  # Last 30 transactions for better sample
    except Exception as e:
        print(f"Error reading CSV: {e}")
        transactions = []
    
    if not transactions:
        state['observations'] = {
            'total_count': 0,
            'success_rate': 0,
            'avg_latency': 0,
            'bank_metrics': {}
        }
        return state
    
    # Calculate metrics
    total = len(transactions)
    successful = sum(1 for t in transactions if t.get('status') == 'Success')
    
    total_latency = sum(float(t.get('latency_ms', 0)) for t in transactions)
    avg_latency = total_latency / total if total > 0 else 0
    
    # Bank-wise metrics with Error Code analysis
    bank_metrics = {}
    for txn in transactions:
        bank = txn.get('bank', 'Unknown')
        if bank not in bank_metrics:
            bank_metrics[bank] = {
                'count': 0,
                'success': 0,
                'fail': 0,
                'total_latency': 0,
                'error_codes': {},
                'high_latency_count': 0
            }
        
        metrics = bank_metrics[bank]
        metrics['count'] += 1
        latency = float(txn.get('latency_ms', 0))
        metrics['total_latency'] += latency
        
        if latency > 300:
            metrics['high_latency_count'] += 1
        
        if txn.get('status') == 'Success':
            metrics['success'] += 1
        else:
            metrics['fail'] += 1
            error = txn.get('error_code', 'UNKNOWN')
            metrics['error_codes'][error] = metrics['error_codes'].get(error, 0) + 1
    
    # Calculate per-bank averages
    for bank, metrics in bank_metrics.items():
        if metrics['count'] > 0:
            metrics['avg_latency'] = metrics['total_latency'] / metrics['count']
            metrics['success_rate'] = metrics['success'] / metrics['count']
    
    observations = {
        'total_count': total,
        'success_count': successful,
        'fail_count': total - successful,
        'success_rate': successful / total if total > 0 else 0,
        'avg_latency': avg_latency,
        'bank_metrics': bank_metrics,
        'timestamp': datetime.now().isoformat()
    }
    
    state['observations'] = observations
    return state


def reason_node(state: AgentState) -> AgentState:
    """
    Reason Node: Analyze metrics + History -> Structured Decision
    """
    print("🧠 Reason: Analyzing with Context...")
    
    obs = state['observations']
    
    # Load Memory (Recent Actions)
    history = tools.get_agent_history(5)
    formatted_history = []
    for h in history:
        # Simplify history for prompt
        time_diff = "recently"
        try:
            ts = datetime.fromisoformat(h['timestamp'])
            mins = (datetime.now() - ts).total_seconds() / 60
            time_diff = f"{mins:.1f} mins ago"
        except:
            pass
        formatted_history.append(f"- [{time_diff}] {h['action']} ({h['details']})")
    
    # Format bank observations
    bank_details = []
    for bank, m in obs['bank_metrics'].items():
        errors = ", ".join([f"{k}:{v}" for k,v in m['error_codes'].items()])
        bank_details.append(
            f"  - {bank}: {m['success_rate']*100:.0f}% SR, {m['avg_latency']:.0f}ms LATENCY. "
            f"({m['high_latency_count']} slow txns). Errors: {errors or 'None'}"
        )
    
    system_prompt = f"""You are Payment Sentinel, an autonomous AI reliability engineer.
    
CONTEXT:
You manage a payment router connected to banks (HDFC, SBI, ICICI, etc.).
Your goal: Maximize Success Rate (>95%) and minimize Latency (<300ms).

CURRENT OBSERVATIONS (Last 30 txns):
- System SR: {obs['success_rate']*100:.1f}% | Avg Latency: {obs['avg_latency']:.0f}ms
- Detailed Bank Status:
{chr(10).join(bank_details)}

RECENT AGENT ACTIONS (Memory):
{chr(10).join(formatted_history) if formatted_history else "No recent actions."}

TASK:
Analyze the data. Identify specific failure patterns (e.g. "HDFC TIMEOUTS", "SBI GATEWAY_ERROR").
Decide if intervention is needed.
Consider TRADE-OFFS: Rerouting costs liquidity. Retries increase load.

OUTPUT FORMAT (JSON ONLY):
{{
    "hypothesis": "One sentence summary of the problem (e.g. 'HDFC is experiencing degraded latency due to timeouts')",
    "confidence_score": 0.0-1.0,
    "analysis": "Detailed explanation of evidence. Mention explicit metrics.",
    "decision": "NO_ACTION" or "INTERVENE",
    "actions": [
        {{
            "type": "reroute_traffic" or "set_retry_policy" or "toggle_chaos",
            "params": {{ ...args... }}
        }}
    ],
    "explanation_for_user": "User-friendly reason for the action"
}}

RULES:
1. If everything is >95% SR and <300ms latency, decision MUST be "NO_ACTION".
2. If we just intervened <1 min ago for the same issue, be cautious (don't flap).
3. "reroute_traffic" params: "bank", "target" (valid: hdfc, sbi, icici, axis, bob, idfc, pnb).
4. "set_retry_policy" params: "bank", "level" (low, normal, high).
"""

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            llm = create_llm()
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Analyze status and output JSON.")
            ]
            
            response = llm.invoke(messages)
            content = response.content
            
            # Clean markdown json if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            structured = json.loads(content)
            
            # Backwards compatibility for UI text
            state['reasoning'] = f"**HYPOTHESIS:** {structured.get('hypothesis')}\n\n**ANALYSIS:** {structured.get('analysis')}\n\n**DECISION:** {structured.get('decision')}"
            state['structured_response'] = structured
            state['reasoning_details'] = structured
            
            print(f"  ✓ Reasoning confidence: {structured.get('confidence_score')}")
            return state
            
        except Exception as e:
            error_str = str(e)
            if '429' in error_str and attempt < max_attempts - 1:
                wait_time = (attempt + 1) * 10  # 10s, 20s, 30s
                print(f"  ⚠️ Rate limited. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(wait_time)
                continue
            print(f"  ✗ Reasoning Error: {e}")
            state['reasoning'] = f"Error generating reasoning: {e}"
            state['structured_response'] = {}
            state['reasoning_details'] = {'error': error_str}
    
    return state


def act_node(state: AgentState) -> AgentState:
    """
    Act Node: Execute structured actions with Guardrails.
    """
    print("🎯 Act: Evaluating protocols...")
    
    response = state.get('structured_response', {})
    decision = response.get('decision', 'NO_ACTION')
    actions_to_run = response.get('actions', [])
    
    actions_taken = []
    
    if decision == "INTERVENE" and actions_to_run:
        # GUARDRAIL: Check if we are flapping
        history = tools.get_agent_history(1)
        last_time = None
        if history:
            try:
                last_time = datetime.fromisoformat(history[0]['timestamp'])
            except:
                pass
        
        # GUARDRAIL: Safe Mode / Dry Run
        config = tools.get_config()
        safe_mode = config.get('global_config', {}).get('safe_mode', False)
        
        # Cooldown: 20 seconds between actions
        if last_time and (datetime.now() - last_time).total_seconds() < 20:
            print("  ⚠️ GUARDRAIL: Action skipped (Cooldown Active)")
            actions_taken.append("SKIPPED: Cooldown active (20s)")
        elif safe_mode:
            print(f"  🛡️ GUARDRAIL: Safe Mode Active. Would have executed: {actions_to_run}")
            actions_taken.append(f"DRY RUN (Safe Mode): {actions_to_run}")
        else:
            for action in actions_to_run:
                try:
                    atype = action.get('type')
                    params = action.get('params', {})
                    
                    res = None
                    if atype == 'reroute_traffic':
                        res = tools.reroute_traffic(params.get('bank'), params.get('target'))
                    elif atype == 'set_retry_policy':
                        res = tools.set_retry_policy(params.get('bank'), params.get('level'))
                    elif atype == 'toggle_chaos':
                        res = tools.toggle_chaos_mode(params.get('enabled'), 0.3)
                    
                    if res and res.get('success'):
                        actions_taken.append(f"{atype}({params})")
                        print(f"  ✓ Executed: {atype} {params}")
                    else:
                        print(f"  ✗ Failed: {atype} - {res}")
                        
                except Exception as e:
                    print(f"  ✗ Execution Exception: {e}")
                    actions_taken.append(f"Error: {e}")
    
    if not actions_taken:
        actions_taken = ["NONE"]
    
    state['actions'] = actions_taken
    state['feedback'] = {'status': 'done'}
    return state


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("observe", observe_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("act", act_node)
    
    workflow.set_entry_point("observe")
    workflow.add_edge("observe", "reason")
    workflow.add_edge("reason", "act")
    workflow.add_edge("act", END)
    
    return workflow.compile()


def run_agent_cycle() -> Dict[str, Any]:
    global last_reasoning
    
    print("\n" + "="*60)
    print("🤖 Starting Agent Cycle (v2 - Structured)")
    print("="*60)
    
    initial_state = {
        'observations': {},
        'memory': [],
        'structured_response': {},
        'reasoning': '',
        'reasoning_details': None,
        'actions': [],
        'feedback': {}
    }
    
    try:
        graph = build_graph()
        result = graph.invoke(initial_state)
        
        last_reasoning = {
            'timestamp': datetime.now().isoformat(),
            'reasoning': result.get('reasoning', ''),
            'reasoning_details': result.get('reasoning_details'),
            'actions': result.get('actions', []),
            'feedback': result.get('feedback', {})
        }
        
        # Persist state
        try:
            with open('agent_state.json', 'w') as f:
                json.dump(last_reasoning, f, indent=2)
        except Exception as e:
            print(f"Error saving agent state: {e}")
            
        print("="*60)
        print("✓ Agent Cycle Complete")
        print("="*60 + "\n")
        
        return last_reasoning
        
    except Exception as e:
        print(f"✗ Error in agent cycle: {e}")
        error_result = {
            'timestamp': datetime.now().isoformat(),
            'reasoning': f'Error: {str(e)}',
            'reasoning_details': None,
            'actions': [],
            'feedback': {'status': 'error'}
        }
        last_reasoning = error_result
        return error_result


def read_agent_state() -> Dict[str, Any]:
    """Read the latest agent state from disk."""
    try:
        if os.path.exists('agent_state.json'):
            with open('agent_state.json', 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

if __name__ == "__main__":
    run_agent_cycle()
