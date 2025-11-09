import streamlit as st
from personas import PersonaGenerator
from intelligence import IntelligenceExtractor
from conversation import ConversationManager
import json
import plotly.graph_objects as go



# Page config
st.set_page_config(
    page_title="Scam Engagement Bot",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .scammer-msg {
        background-color: #ff4b4b;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        color: white;
    }
    .bot-msg {
        border: 2px solid #4CAF50;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .stats-box {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
    }
     .stats-box h4 {
        color: white;
    }
    .stats-box p {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🛡️ Scam Engagement Bot")
st.markdown("**AI-Powered Counter-Intelligence System**")
st.markdown("---")

# Initialize session state
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
    st.session_state.messages = []
    st.session_state.intel_log = []

# Sidebar - Setup
with st.sidebar:
    st.header("⚙️ Configuration")
    
    scam_type = st.selectbox(
        "Select Scam Type",
        ["phishing", "tech_support", "romance", "crypto_investment"],
        help="Choose the type of scam to simulate"
    )
    
    st.markdown("---")
    
    if st.button("🎭 Generate New Persona", use_container_width=True):
        with st.spinner("Generating victim persona..."):
            generator = PersonaGenerator()
            persona = generator.generate_persona(scam_type)
            st.session_state.persona = persona
            st.session_state.extractor = IntelligenceExtractor()
            st.session_state.manager = ConversationManager(
                persona, 
                st.session_state.extractor
            )
            st.session_state.conversation_started = True
            st.session_state.messages = []
            st.session_state.intel_log = []
            st.success("Persona generated!")
            st.rerun()
    
    # Show persona if generated
    if 'persona' in st.session_state:
        st.markdown("---")
        st.subheader("👤 Current Persona")
        p = st.session_state.persona
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Age:** {p['age']}")
        st.write(f"**Occupation:** {p['occupation']}")
        st.write(f"**Tech Literacy:** {p['tech_literacy']}/10")
        
        with st.expander("View Full Profile"):
            st.json(p)
    
    st.markdown("---")
    
    if st.session_state.conversation_started and st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.intel_log = []
        st.session_state.manager = ConversationManager(
            st.session_state.persona,
            st.session_state.extractor
        )
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📖 How It Works
    1. Generate a victim persona
    2. Send scammer messages
    3. Watch the bot engage
    4. View extracted intelligence
    
    ### 🎯 Goal
    Waste scammer's time while extracting threat intelligence
    """)

# Main content area
if not st.session_state.conversation_started:
    # Landing page
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## Welcome to the Scam Engagement Bot
        
        This AI-powered system engages scammers to:
        - 🕐 **Waste their time** - Keep them busy with fake victims
        - 🔍 **Extract intelligence** - Gather URLs, tactics, and IOCs
        - 🛡️ **Protect real victims** - While scammers talk to bots
        
        ### Getting Started
        
        1. Choose a **scam type** from the sidebar
        2. Click **Generate New Persona** to create a victim
        3. Start sending scammer messages
        4. Watch the bot engage naturally
        
        ---
        
        ### Example Scam Messages to Try:
        
        **Phishing:**
```
        Hello! This is Commonwealth Bank security. 
        We detected suspicious activity on your account.
```
        
        **Tech Support:**
```
        This is Microsoft support. Your computer 
        has been infected with a virus.
```
        
        **Romance:**
```
        Hi! I saw your profile and would love to 
        get to know you better.
```
        """)

else:
    # Conversation interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Conversation")
        
        # Display conversation
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.info("👋 Start the conversation by entering a scammer message below!")
            
            for msg in st.session_state.messages:
                if msg['role'] == 'scammer':
                    st.markdown(f"""
                    <div class="scammer-msg">
                        <strong>🚨 SCAMMER:</strong><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="bot-msg">
                        <strong>🤖 {st.session_state.persona['name'].upper()}:</strong><br>
                        {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input area
        st.markdown("---")
        
        with st.form("message_form", clear_on_submit=True):
            scammer_input = st.text_area(
                "Enter scammer message:",
                placeholder="Type what the scammer would say...",
                height=100,
                key="scammer_input"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 2])
            with col_a:
                submit = st.form_submit_button("📤 Send", use_container_width=True)
            with col_b:
                quick_fill = st.form_submit_button("⚡ Quick Fill", use_container_width=True)
        
        if quick_fill:
            # Provide example messages
            examples = {
                "phishing": "Your bank account has been compromised. Click here to verify: https://secure-bank-verify.com",
                "tech_support": "This is Microsoft support. Your computer has a virus. Download this tool to fix it.",
                "romance": "Hi beautiful! I'm working overseas but would love to get to know you. Can we chat?",
                "crypto_investment": "I can help you make $10,000 a week with crypto trading. Just send me $500 to start."
            }
            st.info(f"💡 Example: {examples.get(scam_type, 'Hello, this is a scam message.')}")
        
        if submit and scammer_input:
            with st.spinner(f"{st.session_state.persona['name']} is typing..."):
                # Add scammer message
                st.session_state.messages.append({
                    'role': 'scammer',
                    'content': scammer_input
                })
                
                # Generate bot response
                bot_response = st.session_state.manager.generate_response(scammer_input)
                
                # Add bot message
                st.session_state.messages.append({
                    'role': 'bot',
                    'content': bot_response
                })
                
                # Store intelligence
                st.session_state.intel_log = st.session_state.manager.intel_log
                
            st.rerun()
    
    with col2:
        st.subheader("📊 Intelligence Dashboard")
        
        # Stats
        summary = st.session_state.manager.get_conversation_summary()
        
        st.markdown(f"""
        <div class="stats-box">
            <h4>📈 Engagement Metrics</h4>
            <p><strong>Turns:</strong> {summary['total_turns']}</p>
            <p><strong>Time Wasted:</strong> ~{summary['estimated_time_wasted']}</p>
            <p><strong>State:</strong> {summary['final_state']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Extracted Intelligence
        if st.session_state.intel_log:
            st.markdown("### 🎯 Extracted IOCs")
            
            report = st.session_state.extractor.generate_report(st.session_state.intel_log)
            unique_iocs = report['summary']['unique_iocs']
            
            if unique_iocs:
                for ioc_type, values in unique_iocs.items():
                    with st.expander(f"📌 {ioc_type.upper()} ({len(values)})"):
                        for value in values:
                            st.code(value)
            else:
                st.info("No IOCs extracted yet")
            
            st.markdown("---")
            
            # Latest tactics
            if st.session_state.intel_log:
                st.markdown("### ⚠️ Threat Analysis")
                latest = st.session_state.intel_log[-1]['tactics']
                
                st.metric("Sophistication", f"{latest.get('sophistication', 0)}/10")
                st.write(f"**Tactic:** {latest.get('primary_tactic', 'Unknown')}")
                st.write(f"**Impersonation:** {latest.get('impersonation', 'None')}")
                
                if latest.get('red_flags'):
                    st.markdown("**🚩 Red Flags:**")
                    for flag in latest['red_flags']:
                        st.write(f"• {flag}")
        
        st.markdown("---")

        #Dashboard

        if len(st.session_state.messages) > 2:
            st.markdown("---")
            
            
            # Calculate turns and get sophistication scores
            num_turns = len(st.session_state.messages) // 2
            turns = list(range(1, num_turns + 1))
            
            # Get sophistication scores from intelligence log
            sophistication_scores = []
            for intel in st.session_state.intel_log:
                score = intel.get('tactics', {}).get('sophistication', 5)
                sophistication_scores.append(score)
            
            # Pad if needed (in case intel_log is shorter)
            while len(sophistication_scores) < len(turns):
                sophistication_scores.append(5)
            
            # Create figure
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=turns,
                y=sophistication_scores,
                mode='lines+markers',
                name='Threat Level',
                line=dict(color='#ff4b4b', width=3),
                marker=dict(size=8, color='#ff4b4b')
            ))
            
            # Update layout with properly labeled axes
            fig.update_layout(
                title="Scammer Sophistication Over Time",
                xaxis_title="Conversation Turn Number",
                yaxis_title="Sophistication Level (1-10)",
                yaxis=dict(range=[0, 10]),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=300,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export button
        if st.session_state.messages:
            if st.button("📥 Export Conversation", use_container_width=True):
                export_data = {
                    "persona": st.session_state.persona,
                    "scam_type": scam_type,
                    "messages": st.session_state.messages,
                    "intelligence": st.session_state.intel_log,
                    "summary": summary
                }
                
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"scam_conversation_{scam_type}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    Counter-Intelligence System for Fraud Prevention
</div>
""", unsafe_allow_html=True)