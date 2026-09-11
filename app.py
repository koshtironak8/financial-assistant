import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Inclusion Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ `GEMINI_API_KEY` is missing! Please configure your Gemini API key in the `.env` file.")
    st.stop()

# --- Initialize Accessibility State ---
if "font_size" not in st.session_state:
    st.session_state.font_size = "Standard"

# --- Sidebar: Accessibility Controls & Toolkit ---
with st.sidebar:
    st.markdown("### 🏛️ Finclusion AI")
    st.markdown(
        """
        <div class="sidebar-info-card">
            <span class="sdg-pill">SDG 1 • No Poverty</span>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.88rem; color: #334155; line-height: 1.45;">
                Democratizing financial literacy for low-income households, unbanked communities, and students.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )



    st.markdown("#### 🎯 Focus Pillars")
    st.markdown(
        """
        - 🪙 **Micro-Savings & Emergency Funds**
        - 🛡️ **Predatory Debt & Scam Prevention**
        - 🏦 **Fair Banking & Credit Rights**
        - 💼 **Microfinance & Livelihood Grants**
        """
    )

    st.divider()

    # Accessible Micro-Budget Calculator
    with st.expander("🧮 Student Budget Calculator (50/30/20)", expanded=False):
        st.caption("Target monthly allowance / income breakdown")
        income = st.number_input("Monthly Income / Allowance (₹)", min_value=0, value=10000, step=500)
        if income > 0:
            needs = income * 0.50
            wants = income * 0.30
            savings = income * 0.20
            st.markdown(
                f"""
                <div class="calc-breakdown">
                    <div><b>Essential Needs (50%):</b> <span>₹{needs:,.2f}</span></div>
                    <div><b>Flexible Spending (30%):</b> <span>₹{wants:,.2f}</span></div>
                    <div><b>Savings & Emergency (20%):</b> <span style="color: #047857; font-weight:700;">₹{savings:,.2f}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    st.markdown("#### ♿ Accessibility Settings")
    selected_font = st.radio(
        "Reading Font Size",
        options=["Standard", "Large (Enhanced Legibility)"],
        index=0 if st.session_state.font_size == "Standard" else 1,
        help="Adjust text scaling for enhanced readability and WCAG accessibility compliance.",
    )
    st.session_state.font_size = selected_font

    st.divider()

    st.markdown("#### ⚙️ System Status")
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #065F46; font-weight: 600;">
            <span style="height: 10px; width: 10px; background-color: #10B981; border-radius: 50%; display: inline-block;"></span>
            Gemini 3.5 Flash Lite (Operational)
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- Dynamic Font Size Rules based on Accessibility Toggle ---
font_multiplier = "1.12rem" if st.session_state.font_size.startswith("Large") else "1rem"
chat_font_size = "1.15rem" if st.session_state.font_size.startswith("Large") else "1rem"
line_height = "1.75" if st.session_state.font_size.startswith("Large") else "1.6"

# --- High-Contrast Accessible Light Mode Styles ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
        font-size: {font_multiplier};
        line-height: {line_height};
        color: #0F172A;
    }}

    /* Light Mode Base */
    .stApp {{
        background: #F8FAFC;
        color: #0F172A;
    }}

    /* Hide redundant Streamlit UI */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background-color: transparent;
    }}

    /* Sidebar High Contrast */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }}

    .sidebar-info-card {{
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #059669;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 1rem;
    }}

    .sdg-pill {{
        display: inline-block;
        background-color: #059669;
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
    }}

    .calc-breakdown {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.85rem;
        color: #1E293B;
        line-height: 1.6;
    }}

    /* Hero Banner - Accessible Light Mode */
    .hero-box {{
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 5px solid #059669;
        border-radius: 16px;
        padding: 2rem 2.2rem 1.6rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.06);
    }}

    .hero-badge {{
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        border: 1px solid #A7F3D0;
        margin-bottom: 0.75rem;
    }}

    .hero-heading {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 0.5rem 0;
        line-height: 1.25;
    }}

    .hero-subtext {{
        font-size: 1.05rem;
        color: #334155;
        line-height: 1.6;
        margin: 0;
        max-width: 780px;
    }}

    /* Metrics Grid */
    .metrics-row {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 1.4rem;
    }}

    .metric-card {{
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
    }}

    .metric-title {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #475569;
        letter-spacing: 0.04em;
        margin-bottom: 0.2rem;
    }}

    .metric-stat {{
        font-size: 1.1rem;
        font-weight: 800;
        color: #0F172A;
    }}

    /* High Contrast Chat Messages */
    div[data-testid="stChatMessage"] {{
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        font-size: {chat_font_size} !important;
        line-height: {line_height} !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}

    /* User Bubble - Accessible High-Contrast Slate/Blue */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {{
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E3A8A;
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p {{
        color: #1E3A8A !important;
        font-weight: 500;
    }}

    /* Assistant Bubble - Clean Accessible Mint/White */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {{
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-left: 4px solid #059669;
        color: #0F172A;
    }}
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) p,
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) li {{
        color: #0F172A !important;
    }}

    /* Quick Prompt Cards */
    .stButton button {{
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.1rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        text-align: left !important;
        height: auto !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton button:hover {{
        background-color: #ECFDF5 !important;
        border-color: #059669 !important;
        color: #065F46 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(5, 150, 105, 0.12) !important;
    }}

    /* Input Bar */
    div[data-testid="stChatInput"] {{
        border-radius: 16px;
        background-color: #FFFFFF;
        border: 1px solid #94A3B8;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }}
    div[data-testid="stChatInput"] textarea {{
        color: #0F172A !important;
        font-size: 1rem !important;
    }}
    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #64748B !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Page Title & One-Line Caption ---
st.title("💰 Financial Inclusion Assistant")
st.caption("A friendly financial literacy assistant for Indian college students and beginners, advancing SDG 1: No Poverty.")

# --- Hero Banner ---
st.markdown(
    """
    <div class="hero-box">
        <span class="hero-badge">SDG 1 • No Poverty</span>
        <h2 class="hero-heading" style="font-size: 1.6rem; margin-bottom: 0.35rem;">Empowering Your Financial Future</h2>
        <p class="hero-subtext">
            Practical, accessible guidance designed for college students and low-income individuals. 
            Ask about budgeting your allowance, building an emergency buffer, escaping debt traps, or understanding banking resources.
        </p>
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-title">Target Goal</div>
                <div class="metric-stat">SDG 1: Zero Poverty</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Audience</div>
                <div class="metric-stat">Students & Beginners</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Support</div>
                <div class="metric-stat">100% Free & Open</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Gemini Client Verification ---
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Role:
A friendly financial-literacy assistant for Indian college students and people who want to improve their basic financial knowledge.

Task:
Help users understand budgeting, saving, basic financial literacy, and relevant public-support resources.

Context:
Use simple English and explain financial concepts with practical examples that beginners can understand.
Always use Indian Rupees (₹) for all monetary examples, amounts, and budgets. Never use dollars ($).

Rules:
- Do not pretend to be a professional financial advisor.
- Do not give personalized investment, loan, tax, or financial advice.
- If unsure, say "I'm not sure."
- Keep answers simple and under 150 words.
- Give one useful example when appropriate, strictly using Indian Rupees (₹).
- Always use Indian Rupees (₹ / INR) instead of dollars ($).
- For questions outside the topic, redirect the user toward financial literacy and poverty-related support.
"""

# --- Reset on Shared Link or Fresh URL ---
if any(param in st.query_params for param in ["clean", "new", "reset"]):
    st.session_state.messages = []
    st.query_params.clear()

# --- Initialize Messages ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "model",
            "content": (
                "👋 **Namaste! Welcome to your Financial Inclusion Assistant.**\n\n"
                "I am here to help Indian college students and beginners build practical money skills:\n"
                "- **Budgeting & saving** from allowance or part-time earnings\n"
                "- **Building an emergency buffer** even on a tight budget\n"
                "- **Staying protected** against loan app scams and hidden fees\n"
                "- **Exploring public resources** and zero-balance banking (e.g. Jan Dhan accounts)\n\n"
                "Ask any financial question below to get started!"
            ),
        }
    ]

# --- Quick Suggestion Prompts ---
selected_prompt = None
if len(st.session_state.messages) <= 1:
    st.markdown("##### 💡 Frequently Asked Questions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🪙 How can a student save with a ₹5,000 allowance?", use_container_width=True):
            selected_prompt = "How can an Indian college student budget and save money with a monthly allowance of ₹5,000?"
        if st.button("🛡️ How do I stay safe from predatory loan apps & UPI fraud?", use_container_width=True):
            selected_prompt = "How can I identify and avoid predatory instant loan apps and UPI scams in India?"
    with col2:
        if st.button("📊 Explain the 50/30/20 rule with a ₹10,000 example", use_container_width=True):
            selected_prompt = "Explain the 50/30/20 budgeting rule with a clear practical example using ₹10,000."
        if st.button("🏦 What public support resources (like Jan Dhan) exist?", use_container_width=True):
            selected_prompt = "What basic banking and government financial inclusion resources like PM Jan Dhan Yojana are available for low-income individuals in India?"

# --- Display Messages (Replay history on each rerun) ---
for message in st.session_state.messages:
    with st.chat_message("assistant" if message["role"] == "model" else "user"):
        st.markdown(message["content"])

# --- User Input & Response Processing ---
user_input = st.chat_input("Type your financial question here (e.g., budgeting, saving, or student money tips)...")
prompt_to_process = selected_prompt or user_input

if prompt_to_process:
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # Build full history using types.Content with roles "user" / "model"
    history_contents = [
        types.Content(
            role=msg["role"],
            parts=[types.Part.from_text(text=msg["content"])],
        )
        for msg in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=history_contents,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                assistant_reply = response.text
                st.markdown(assistant_reply)
                st.session_state.messages.append({"role": "model", "content": assistant_reply})
            except APIError as e:
                # Friendly message for wrong or unauthorized API keys
                if e.code in (400, 401, 403):
                    st.error("🔑 Invalid API Key: Your Gemini API key is missing, unauthorized, or invalid. Please check your `.env` file.")
                # Friendly message for rate limits
                elif e.code == 429:
                    st.error("⏳ Rate limit reached: Too many requests in a short time. Please wait a moment and try again.")
                elif e.code == 503:
                    # Automatic fallback to gemini-2.5-flash if 503 high demand occurs
                    try:
                        fallback_response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=history_contents,
                            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                        )
                        assistant_reply = fallback_response.text
                        st.markdown(assistant_reply)
                        st.session_state.messages.append({"role": "model", "content": assistant_reply})
                    except Exception:
                        st.warning("⚠️ High server demand: Gemini is experiencing temporary high traffic. Please try again shortly.")
                else:
                    st.error(f"⚠️ API Error ({e.code}): {e.message or str(e)}")
            except Exception as e:
                st.error(f"⚠️ An unexpected error occurred: {e}")

