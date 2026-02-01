import streamlit as st
import json
import csv
import random
from datetime import datetime

# ==================== CONFIG ====================
PRIMARY_COLOR = "#2D5CF6"  # Razorpay Blue
BACKGROUND_COLOR = "#F8FAFC"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1A202C"
TEXT_SECONDARY = "#718096"
BORDER_COLOR = "#E2E8F0"
SUCCESS_COLOR = "#10B981"
WARNING_COLOR = "#F59E0B"

# ==================== HELPER FUNCTIONS ====================

def load_config():
    """Load bank configuration with health status"""
    try:
        with open('shared_config.json', 'r') as f:
            return json.load(f)
    except:
        return {'banks': []}

def get_available_banks():
    """Get banks with health status and recommendations"""
    config = load_config()
    banks = []
    
    for bank in config.get('banks', []):
        if bank.get('enabled', False):
            health = bank.get('health_status', 'unknown')
            # if health != 'down':  # NOW SHOWING ALL BANKS based on user request
            banks.append({
                'id': bank['id'],
                'name': bank['name'],
                'health': health,
                'weight': bank.get('weight', 0),
                'avg_latency': bank.get('metrics', {}).get('avg_latency_ms', 0),
                'is_degraded': health == 'degraded',
                'is_down': health == 'down'
            })
    
    # Sort by health (healthy first) then by weight
    # We want Down banks at the end usually, or just visually distinct. 
    # Let's simple sort by weight for now so layout is consistent
    banks.sort(key=lambda x: -x['weight'])
    return banks

def get_recommended_bank(banks):
    """Get the top recommended bank (highest weight among healthy banks)"""
    # Prioritize healthy banks
    healthy_banks = [b for b in banks if not b['is_degraded'] and not b.get('is_down', False)]
    if healthy_banks:
        return max(healthy_banks, key=lambda x: x['weight'])['id']
    return None

def append_transaction(bank_name, amount, method, status='Success'):
    """Append transaction to CSV"""
    try:
        timestamp = datetime.now().isoformat()
        txn_id = f"txn_{int(datetime.now().timestamp()*1000)}_{random.randint(1000, 9999)}"
        
        # Simulate latency based on bank health
        config = load_config()
        bank = next((b for b in config['banks'] if b['name'] == bank_name), None)
        
        if bank:
            if bank['health_status'] == 'degraded':
                latency = random.randint(550, 650)  # High latency for degraded
            else:
                latency = int(bank['metrics']['avg_latency_ms']) + random.randint(-20, 20)
        else:
            latency = random.randint(100, 200)
        
        with open('transactions.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            error_code = '' if status == 'Success' else 'GATEWAY_ERROR'
            retry_count = 0 if status == 'Success' else 1
            writer.writerow([timestamp, txn_id, bank_name, method, status, latency, amount, error_code, retry_count])
        
        return txn_id, latency
    except Exception as e:
        st.error(f"Transaction logging error: {e}")
        return None, None

def get_bank_icon(bank_id):
    """Return emoji icon for bank"""
    icons = {
        'sbi': '🏦',
        'icici': '🏛️',
        'hdfc': '🏦',
        'axis': '🏛️',
        'bob': '🏦',
        'pnb': '🏛️',
        'idfc': '🏦'
    }
    return icons.get(bank_id, '🏦')

# ==================== CUSTOM CSS ====================

def inject_custom_css():
    st.markdown(f"""
    <style>
        /* Global Styles */
        .stApp {{
            background-color: {BACKGROUND_COLOR};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Premium Card Container */
        .checkout-card {{
            background: {CARD_BG};
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 2rem;
            max-width: 480px;
            margin: 2rem auto;
        }}
        
        /* Header */
        .checkout-header {{
            background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, #1E40AF 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px 12px 0 0;
            margin: -2rem -2rem 2rem -2rem;
            text-align: center;
        }}
        
        .merchant-name {{
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .amount-display {{
            font-size: 2rem;
            font-weight: 800;
            color: {TEXT_PRIMARY};
            text-align: center;
            margin: 1.5rem 0;
        }}
        
        /* Payment Method Cards */
        .method-card {{
            background: white;
            border: 2px solid {BORDER_COLOR};
            border-radius: 12px;
            padding: 1rem;
            margin: 0.75rem 0;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .method-card:hover {{
            border-color: {PRIMARY_COLOR};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(45, 92, 246, 0.15);
        }}
        
        .method-icon {{
            font-size: 2rem;
        }}
        
        .method-text {{
            font-weight: 600;
            color: {TEXT_PRIMARY};
        }}
        
        /* Bank Grid */
        .bank-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        
        .bank-card {{
            background: white;
            border: 2px solid {BORDER_COLOR};
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }}
        
        .bank-card:hover {{
            border-color: {PRIMARY_COLOR};
            transform: scale(1.03);
            box-shadow: 0 4px 12px rgba(45, 92, 246, 0.15);
        }}
        
        .bank-card.recommended {{
            border-color: {SUCCESS_COLOR};
            background: linear-gradient(to bottom, white, #F0FDF4);
        }}
        
        .bank-card.degraded {{
            border-color: {WARNING_COLOR};
            background: linear-gradient(to bottom, white, #FFFBEB);
        }}

        .bank-card.down {{
            border-color: #EF4444;
            background: linear-gradient(to bottom, white, #FEF2F2);
            opacity: 0.9;
        }}
        
        .bank-icon {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .bank-name {{
            font-weight: 600;
            color: {TEXT_PRIMARY};
            font-size: 0.95rem;
        }}
        
        .bank-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }}
        
        .badge-recommended {{
            background: {SUCCESS_COLOR};
            color: white;
        }}
        
        .badge-warning {{
            background: {WARNING_COLOR};
            color: white;
        }}

        .badge-down {{
            background: #EF4444;
            color: white;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {PRIMARY_COLOR};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: #1E40AF;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(45, 92, 246, 0.3);
        }}
        
        /* Input Fields */
        .stTextInput > div > div > input {{
            border: 2px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {PRIMARY_COLOR};
            box-shadow: 0 0 0 3px rgba(45, 92, 246, 0.1);
        }}
        
        /* Success Screen */
        .success-screen {{
            text-align: center;
            padding: 2rem 0;
        }}
        
        .success-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        
        .success-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {SUCCESS_COLOR};
            margin-bottom: 0.5rem;
        }}
        
        .transaction-details {{
            background: {BACKGROUND_COLOR};
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
            text-align: left;
        }}
        
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid {BORDER_COLOR};
        }}
        
        .detail-row:last-child {{
            border-bottom: none;
        }}
        
        .detail-label {{
            color: {TEXT_SECONDARY};
            font-size: 0.875rem;
        }}
        
        .detail-value {{
            color: {TEXT_PRIMARY};
            font-weight: 600;
            font-size: 0.875rem;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==================== MAIN APP ====================

def main():
    st.set_page_config(
        page_title="Checkout - Powered by Sentinel AI",
        page_icon="💳",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    inject_custom_css()
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'phone' not in st.session_state:
        st.session_state.phone = ''
    if 'amount' not in st.session_state:
        st.session_state.amount = random.choice([500, 1000, 1500, 2500, 5000])
    if 'selected_method' not in st.session_state:
        st.session_state.selected_method = None
    if 'selected_bank' not in st.session_state:
        st.session_state.selected_bank = None
    if 'payment_complete' not in st.session_state:
        st.session_state.payment_complete = False
    if 'txn_details' not in st.session_state:
        st.session_state.txn_details = None
    
    # Main container
    container = st.container()
    
    with container:
        # Add link back to dashboard
        dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8501")
        st.sidebar.markdown("### 🛡️ Sentinel Ops")
        st.sidebar.link_button("📊 Back to Dashboard", dashboard_url, use_container_width=True)

        # Step 1: Contact Details
        if st.session_state.step == 1:
            st.markdown(f"""
            <div class="checkout-card">
                <div class="checkout-header">
                    <h1 class="merchant-name">🏪 Acme Corp</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Secure Checkout</p>
                </div>
                <div class="amount-display">₹{st.session_state.amount:,}</div>
                <p style="color: {TEXT_SECONDARY}; text-align: center; margin-bottom: 2rem;">
                    Enter your contact details to proceed
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            phone = st.text_input(
                "Phone Number",
                value=st.session_state.phone,
                placeholder="+91 98765 43210",
                max_chars=15,
                key="phone_input"
            )
            
            if st.button("Proceed to Payment", key="proceed_btn"):
                if phone and len(phone) >= 10:
                    st.session_state.phone = phone
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Please enter a valid phone number")
        
        # Step 2: Payment Method Selection
        elif st.session_state.step == 2:
            st.markdown(f"""
            <div class="checkout-card">
                <div class="checkout-header">
                    <h1 class="merchant-name">💳 Select Payment Method</h1>
                </div>
                <div class="amount-display">₹{st.session_state.amount:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Payment methods
            methods = [
                {"id": "card", "icon": "💳", "name": "Credit/Debit Card"},
                {"id": "upi", "icon": "📱", "name": "UPI (GPay/PhonePe)"},
                {"id": "netbanking", "icon": "🏦", "name": "Net Banking"},
                {"id": "wallet", "icon": "👛", "name": "Wallets"}
            ]
            
            for method in methods:
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"<div style='font-size: 2rem;'>{method['icon']}</div>", unsafe_allow_html=True)
                with col2:
                    if st.button(method['name'], key=f"method_{method['id']}", use_container_width=True):
                        st.session_state.selected_method = method['id']
                        st.session_state.step = 3
                        st.rerun()
            
            if st.button("← Back", key="back_from_methods"):
                st.session_state.step = 1
                st.rerun()
        
        # Step 3: Bank/Provider Selection
        elif st.session_state.step == 3 and not st.session_state.payment_complete:
            method = st.session_state.selected_method
            method_name = {
                "card": "Card Payment",
                "upi": "UPI Payment",
                "netbanking": "Net Banking",
                "wallet": "Wallet Payment" 
            }.get(method, "Payment")

            st.markdown(f"""
            <div class="checkout-card">
                <div class="checkout-header">
                    <h1 class="merchant-name">{method_name}</h1>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Secure Transaction</p>
                </div>
                <div class="amount-display">₹{st.session_state.amount:,}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Contextual Inputs
            if method == 'upi':
                st.markdown("### 📱 UPI Details")
                st.radio("Select App", ["Google Pay", "PhonePe", "Paytm", "BHIM"], horizontal=True, label_visibility="collapsed")
                st.text_input("UPI ID / VPA", placeholder="mobile@upi")
                st.info("ℹ️ Please select your linked bank account below to simulate the transaction.")
                
            elif method == 'card':
                st.markdown("### 💳 Card Details")
                c1, c2 = st.columns(2)
                c1.text_input("Card Number", placeholder="0000 0000 0000 0000")
                c2.text_input("Expiry", placeholder="MM/YY")
                st.text_input("Card Holder Name", placeholder="JOHN DOE")
                st.info("ℹ️ Select Card Issuer Bank to proceed.")

            elif method == 'wallet':
                st.info("ℹ️ Load Wallet from Bank Account.")

            st.markdown("### Select Bank")
            
            original_banks = get_available_banks()
            # If wallet/upi, maybe show only healthy? No, user wants to see failures.
            # We show all.
            
            recommended_bank = get_recommended_bank(original_banks)
            
            # Bank grid
            cols = st.columns(2)
            
            for idx, bank in enumerate(original_banks[:8]):  # Show more banks if needed
                with cols[idx % 2]:
                    is_recommended = bank['id'] == recommended_bank
                    is_degraded = bank['is_degraded']
                    is_down = bank.get('is_down', False)
                    
                    card_class = 'recommended' if is_recommended else ('degraded' if is_degraded else ('down' if is_down else ''))
                    
                    badge_html = ""
                    if is_recommended:
                        badge_html = f'<div class="bank-badge badge-recommended">⚡ Recommended</div>'
                    elif is_down:
                        badge_html = f'<div class="bank-badge badge-down">❌ Service Down</div>'
                    elif is_degraded:
                        badge_html = f'<div class="bank-badge badge-warning">⚠️ High Latency</div>'
                    
                    st.markdown(f"""
                    <div class="bank-card {card_class}">
                        <div class="bank-icon">{get_bank_icon(bank['id'])}</div>
                        <div class="bank-name">{bank['name']}</div>
                        {badge_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    btn_label = f"Pay via {bank['name']}"
                    if is_down:
                        btn_label = f"⚠️ Try {bank['name']}" # Warning on button text
                    
                    if st.button(btn_label, key=f"bank_{bank['id']}", use_container_width=True):
                        st.session_state.selected_bank = bank['name']
                        
                        # Simulate payment processing
                        with st.spinner('Contacting Bank Server...'):
                            import time
                            # Latency simulation
                            if is_down:
                                time.sleep(3.0) # Long timeout
                                success = False # Always fail
                                status_msg = "TIMEOUT_ERROR"
                            elif is_degraded:
                                time.sleep(2.0)
                                success = random.random() > 0.3 # High failure rate
                                status_msg = "Make sure your server is not overloaded."
                            else:
                                time.sleep(1.0)
                                success = random.random() > 0.05
                                status_msg = ""
                            
                            status = 'Success' if success else 'Fail'
                            
                            txn_id, latency = append_transaction(
                                bank['name'],
                                st.session_state.amount,
                                method_name, # Log the actual method type
                                status
                            )
                            
                            if success:
                                st.session_state.payment_complete = True
                                st.session_state.txn_details = {
                                    'txn_id': txn_id,
                                    'bank': bank['name'],
                                    'amount': st.session_state.amount,
                                    'method': method_name,
                                    'latency': latency,
                                    'timestamp': datetime.now().strftime("%d %b %Y, %I:%M %p")
                                }
                                st.rerun()
                            else:
                                st.error(f"❌ Payment Failed: {status_msg or 'Bank Server Error'}")
                                if is_down:
                                    st.warning(f"⚠️ {bank['name']} is currently DOWN. Please try a different bank.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Payment Methods", key="back_from_banks"):
                st.session_state.step = 2
                st.rerun()
        
        # Step 4: Success Screen
        elif st.session_state.payment_complete:
            txn = st.session_state.txn_details
            
            st.markdown(f"""
            <div class="checkout-card">
                <div class="success-screen">
                    <div class="success-icon">✅</div>
                    <h1 class="success-title">Payment Successful!</h1>
                    <p style="color: {TEXT_SECONDARY};">Your transaction has been completed</p>
                    
                    <div class="transaction-details">
                        <div class="detail-row">
                            <span class="detail-label">Transaction ID</span>
                            <span class="detail-value">{txn['txn_id']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Amount Paid</span>
                            <span class="detail-value">₹{txn['amount']:,}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bank</span>
                            <span class="detail-value">{txn['bank']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Processing Time</span>
                            <span class="detail-value">{txn['latency']}ms</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date & Time</span>
                            <span class="detail-value">{txn['timestamp']}</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Make Another Payment", key="new_payment"):
                # Reset session state
                st.session_state.step = 1
                st.session_state.selected_method = None
                st.session_state.selected_bank = None
                st.session_state.payment_complete = False
                st.session_state.txn_details = None
                st.session_state.amount = random.choice([500, 1000, 1500, 2500, 5000])
                st.rerun()

if __name__ == "__main__":
    main()
