"""
Agent Engine - LangGraph with OpenRouter Reasoning

Simple 3-node loop: Observe → Reason → Act
Reads transactions.csv, uses OpenRouter for decision-making, executes tools.
"""

import os
import csv
import json
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
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
    reasoning: str
    reasoning_details: Any
    actions: List[str]
    feedback: Dict[str, Any]


def create_llm():
    """Create OpenRouter LLM client with reasoning enabled."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env file")
    
    return ChatOpenAI(
        model="nvidia/nemotron-3-nano-30b-a3b:free",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        temperature=0.7,
        model_kwargs={
            "reasoning": {"enabled": True}
        }
    )


def observe_node(state: AgentState) -> AgentState:
    """
    Observe Node: Read last 20 lines of transactions.csv
    Calculate: Avg Latency, Success Rate, Bank-wise metrics
    """
    print("📊 Observe: Reading transactions...")
    
    transactions = []
    try:
        with open('transactions.csv', 'r') as f:
            reader = csv.DictReader(f)
            all_txns = list(reader)
            transactions = all_txns[-20:]  # Last 20 transactions
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
    
    # Bank-wise metrics
    bank_metrics = {}
    for txn in transactions:
        bank = txn.get('bank', 'Unknown')
        if bank not in bank_metrics:
            bank_metrics[bank] = {
                'count': 0,
                'success': 0,
                'fail': 0,
                'total_latency': 0
            }
        
        bank_metrics[bank]['count'] += 1
        bank_metrics[bank]['total_latency'] += float(txn.get('latency_ms', 0))
        
        if txn.get('status') == 'Success':
            bank_metrics[bank]['success'] += 1
        else:
            bank_metrics[bank]['fail'] += 1
    
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
        'bank_metrics': bank_metrics
    }
    
    print(f"  ✓ Analyzed {total} transactions")
    print(f"  ✓ Success Rate: {observations['success_rate']*100:.1f}%")
    print(f"  ✓ Avg Latency: {observations['avg_latency']:.0f}ms")
    
    state['observations'] = observations
    return state


def reason_node(state: AgentState) -> AgentState:
    """
    Reason Node: Use OpenRouter to analyze metrics
    Ask: "Is there a latency flicker? Should we reroute?"
    Capture reasoning_details for UI display
    """
    print("🧠 Reason: Analyzing with OpenRouter...")
    
    obs = state['observations']
    bank_metrics = obs.get('bank_metrics', {})
    
    # Build bank status summary
    bank_summary = []
    for bank, metrics in bank_metrics.items():
        bank_summary.append(
            f"  - {bank}: {metrics['count']} txns, "
            f"{metrics['success_rate']*100:.0f}% success, "
            f"{metrics['avg_latency']:.0f}ms latency"
        )
    
    # Create prompt
    system_prompt = f"""You are Payment Sentinel, an elite AI managing India's payment routing infrastructure.

🔍 **CURRENT SITUATION** (analyzing last 20 transactions):

Overall Performance:
  • Total Transactions: {obs['total_count']}
  • Success Rate: {obs['success_rate']*100:.1f}%
  • Average Latency: {obs['avg_latency']:.0f}ms

Bank-by-Bank Breakdown:
{chr(10).join(bank_summary)}

📊 **YOUR ANALYSIS TASK**:
Examine the metrics and explain your thinking in plain English, like you're briefing a payment operations manager.

⚠️ **ALERT THRESHOLDS**:
- Latency Concern: Any bank with >300ms average latency
- Success Rate Concern: Any bank with <90% success rate
- System Health: Overall success <95% or latency >200ms

💭 **RESPOND IN THIS FORMAT** (use plain, conversational English):

**OBSERVATION:**
What I'm seeing in the data right now...
[Describe the key patterns - which banks are performing well, which are struggling, any concerning trends]

**ANALYSIS:**
Here's what this means...
[Explain why certain metrics matter, what could be causing issues if any exist]

**DECISION:**
Based on this analysis, I recommend...
[Either "NO ACTION NEEDED - system is healthy" OR "TAKING ACTION - here's why..."]

**ACTIONS:**
[If action needed: "reroute_traffic from=<bank> to=<bank>" OR "set_retry_policy bank=<bank> level=high"]
[If no action: Just say "NONE"]

Be conversational but professional. Use specific numbers. Explain your reasoning clearly."""
    
    try:
        llm = create_llm()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Should we take any action based on current metrics?")
        ]
        
        response = llm.invoke(messages)
        
        # Extract reasoning
        reasoning_text = response.content if hasattr(response, 'content') else str(response)
        
        # Extract reasoning_details if available
        reasoning_details = None
        if hasattr(response, 'response_metadata'):
            reasoning_details = response.response_metadata.get('reasoning')
        
        print(f"  ✓ LLM Response received")
        print(f"  └─ Reasoning: {reasoning_text[:100]}...")
        
        state['reasoning'] = reasoning_text
        state['reasoning_details'] = reasoning_details
        
    except Exception as e:
        print(f"  ✗ Error calling OpenRouter: {e}")
        state['reasoning'] = f"Error: {str(e)}"
        state['reasoning_details'] = None
    
    return state


def act_node(state: AgentState) -> AgentState:
    """
    Act Node: Execute actions based on LLM decision
    Calls tools.py functions: reroute_traffic(), set_retry_policy()
    """
    print("🎯 Act: Executing decisions...")
    
    reasoning = state.get('reasoning', '')
    
    # Ensure reasoning is a string
    if not isinstance(reasoning, str):
        reasoning = str(reasoning)
    
    actions_taken = []
    
    # Check if LLM decided to take action
    reasoning_lower = reasoning.lower()
    
    if 'decision: yes' in reasoning_lower or 'take action' in reasoning_lower or 'reroute' in reasoning_lower:
        
        # Parse actions from reasoning
        if 'reroute_traffic' in reasoning_lower or 'reroute' in reasoning_lower:
            # Extract reroute command
            try:
                banks = ['hdfc', 'sbi', 'icici', 'bob', 'axis', 'idfc', 'pnb']
                
                from_bank = None
                to_bank = None
                
                # Look for bank names in reasoning
                for bank in banks:
                    if f'{bank} to' in reasoning_lower or f'from {bank}' in reasoning_lower:
                        if from_bank is None:
                            from_bank = bank
                    if f'to {bank}' in reasoning_lower:
                        to_bank = bank
                
                # If we found problematic bank but no target, reroute to ICICI (highest weight)
                if from_bank and not to_bank:
                    to_bank = 'icici'
                
                if from_bank and to_bank and from_bank != to_bank:
                    result = tools.reroute_traffic(from_bank, to_bank)
                    actions_taken.append(f"reroute_traffic({from_bank} → {to_bank})")
                    print(f"  ✓ Rerouted traffic: {from_bank} → {to_bank}")
            except Exception as e:
                print(f"  ✗ Error rerouting: {e}")
                actions_taken.append(f"Error rerouting: {e}")
        
        if 'retry' in reasoning_lower or 'set_retry_policy' in reasoning_lower:
            # Extract retry policy command
            try:
                banks = ['hdfc', 'sbi', 'icici', 'bob', 'axis', 'idfc', 'pnb']
                
                target_bank = None
                target_level = 'high'  # Default to high if mentioned
                
                # Find bank with issues
                for bank in banks:
                    if bank in reasoning_lower:
                        if target_bank is None:
                            target_bank = bank
                            break
                
                # Determine level
                if 'low' in reasoning_lower:
                    target_level = 'low'
                elif 'normal' in reasoning_lower:
                    target_level = 'normal'
                
                if target_bank:
                    result = tools.set_retry_policy(target_bank, target_level)
                    actions_taken.append(f"set_retry_policy({target_bank}, {target_level})")
                    print(f"  ✓ Set retry policy: {target_bank} → {target_level}")
            except Exception as e:
                print(f"  ✗ Error setting retry policy: {e}")
                actions_taken.append(f"Error setting retry: {e}")
    
    if not actions_taken:
        actions_taken = ["NONE"]
        print("  ✓ No action required")
    
    state['actions'] = actions_taken
    state['feedback'] = {
        'status': 'success' if not any('Error' in str(a) for a in actions_taken) else 'error',
        'actions_executed': len([a for a in actions_taken if a != "NONE"])
    }
    
    return state


def build_graph() -> StateGraph:
    """Build the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("observe", observe_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("act", act_node)
    
    # Define edges
    workflow.set_entry_point("observe")
    workflow.add_edge("observe", "reason")
    workflow.add_edge("reason", "act")
    workflow.add_edge("act", END)
    
    return workflow.compile()


def run_agent_cycle() -> Dict[str, Any]:
    """
    Run one complete agent cycle.
    Returns: Dictionary with reasoning, actions, and feedback for UI display.
    """
    global last_reasoning
    
    print("\n" + "="*60)
    print("🤖 Starting Agent Cycle")
    print("="*60)
    
    # Initialize state
    initial_state = {
        'observations': {},
        'reasoning': '',
        'reasoning_details': None,
        'actions': [],
        'feedback': {}
    }
    
    try:
        # Build and run graph
        graph = build_graph()
        result = graph.invoke(initial_state)
        
        # Update global reasoning for UI
        last_reasoning = {
            'timestamp': datetime.now().isoformat(),
            'reasoning': result.get('reasoning', ''),
            'reasoning_details': result.get('reasoning_details'),
            'actions': result.get('actions', []),
            'feedback': result.get('feedback', {})
        }
        
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


def get_last_reasoning() -> Dict[str, Any]:
    """Get the last reasoning details for UI display."""
    return last_reasoning


if __name__ == "__main__":
    print("Testing Agent Engine...")
    
    # Run one cycle
    result = run_agent_cycle()
    
    print("\n📋 Result Summary:")
    print(f"  Reasoning: {result['reasoning'][:200]}...")
    print(f"  Actions: {result['actions']}")
    print(f"  Feedback: {result['feedback']}")
    
    if result.get('reasoning_details'):
        print(f"  Reasoning Details Available: YES")
