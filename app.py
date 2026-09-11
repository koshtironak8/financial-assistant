import os
import math
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Page Configuration ---
st.set_page_config(
    page_title="FinAdvisor Pro - AI Wealth & Financial Advisor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ `GEMINI_API_KEY` is missing! Please configure your Gemini API key in the `.env` file.")
    st.stop()

# --- Initialize Session States ---
if "font_size" not in st.session_state:
    st.session_state.font_size = "Standard"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "model",
            "content": (
                "👋 **Namaste! Main hoon aapka AI Financial Advisor & Wealth Mentor.**\n\n"
                "Main sirf generic kitabi baatein nahi, balki aapki **actual financial situation** ke hisaab se customized strategy banata hoon:\n\n"
                "🔹 **Debt Elimination**: Credit cards aur high-interest loans se azaadi (Snowball vs. Avalanche strategy)\n"
                "🔹 **Smart Wealth Building**: Index funds (Nifty 50), compounding SIPs aur asset allocation\n"
                "🔹 **Emergency Safety Shield**: 3-tier liquid buffer taaki kisi se udhar na lena pade\n"
                "🔹 **Tax Planning**: New vs. Old Tax Regime, 80C, 80D aur NPS smart deductions\n"
                "🔹 **Realistic Budgeting**: Real-world cash flows (bina kisi rigid 50/30/20 ke force kiye!)\n\n"
                "Niche diye gaye quick questions par click karein ya apna sawal type karein!"
            ),
        }
    ]

if "pending_chat_prompt" not in st.session_state:
    st.session_state.pending_chat_prompt = None

# --- Dynamic Font Scaling based on Accessibility Toggle ---
font_multiplier = "1.12rem" if st.session_state.font_size.startswith("Large") else "1rem"
chat_font_size = "1.15rem" if st.session_state.font_size.startswith("Large") else "1rem"
line_height = "1.75" if st.session_state.font_size.startswith("Large") else "1.6"

# --- Premium Accessible Styling ---
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

    .stApp {{
        background: #F8FAFC;
        color: #0F172A;
    }}

    /* Clean Streamlit chrome */
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

    .advisor-badge {{
        display: inline-block;
        background-color: #059669;
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
    }}

    .sidebar-card {{
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 4px solid #059669;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 1rem;
    }}

    /* Hero Banner */
    .hero-box {{
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 5px solid #059669;
        border-radius: 16px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05);
    }}

    .hero-badge {{
        display: inline-block;
        background-color: #ECFDF5;
        color: #047857;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        border: 1px solid #A7F3D0;
        margin-bottom: 0.6rem;
    }}

    .hero-heading {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0 0 0.4rem 0;
    }}

    .hero-subtext {{
        font-size: 1rem;
        color: #334155;
        line-height: 1.55;
        margin: 0;
    }}

    /* Tool Result Cards */
    .tool-result-box {{
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }}

    .result-metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-top: 0.8rem;
    }}

    .metric-chip {{
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }}

    .metric-chip-title {{
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .metric-chip-value {{
        font-size: 1.25rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 0.2rem;
    }}

    /* Chat Messages */
    div[data-testid="stChatMessage"] {{
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.85rem;
        font-size: {chat_font_size} !important;
        line-height: {line_height} !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {{
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #1E3A8A;
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {{
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-left: 4px solid #059669;
        color: #0F172A;
    }}

    /* Buttons */
    .stButton button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 💎 FinAdvisor Pro")
    st.markdown(
        """
        <div class="sidebar-card">
            <span class="advisor-badge">AI Wealth & Financial Advisor</span>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.86rem; color: #334155; line-height: 1.45;">
                Actionable financial strategies, debt relief solutions, and wealth building beyond one-size-fits-all formulas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📚 Advisor Rules of Thumb")
    with st.expander("💡 Essential Golden Rules", expanded=True):
        st.markdown(
            """
            - **Rule of 72**: $72 \\div \\text{Return Rate} = $ Years to double money (e.g. at 12%, money doubles in 6 yrs).
            - **3X to 6X Safety Rule**: Keep 3 to 6 months of mandatory living expenses strictly in liquid/savings funds before risking money.
            - **High-Interest Debt Alert**: Any debt >12-14% (Credit cards, personal loans) is a financial emergency. Clear it before equity investing!
            - **Term & Health Insurance**: Base of the financial pyramid. Protect downside risk before pursuing upside wealth.
            """
        )

    st.divider()

    st.markdown("#### ♿ Reading Comfort")
    selected_font = st.radio(
        "Display Size",
        options=["Standard", "Large (Enhanced Legibility)"],
        index=0 if st.session_state.font_size == "Standard" else 1,
    )
    st.session_state.font_size = selected_font

    st.divider()

    st.markdown("#### ⚙️ Advisor Engine")
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #065F46; font-weight: 600;">
            <span style="height: 10px; width: 10px; background-color: #10B981; border-radius: 50%; display: inline-block;"></span>
            Gemini 2.5 Flash (Active)
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Reset Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_chat_prompt = None
        st.rerun()

# --- Main App Header ---
st.markdown(
    """
    <div class="hero-box">
        <span class="hero-badge">Next-Gen Wealth Advisory</span>
        <h1 class="hero-heading">AI Financial Advisor & Wealth Toolkit</h1>
        <p class="hero-subtext">
            Practical, customized money guidance. Calculate wealth compounding, strategize debt payoff, 
            structure your emergency buffer, and consult your dedicated AI Financial Mentor.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Gemini Client Setup ---
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """You are 'FinAdvisor Pro', a top-tier, practical, and highly empathetic personal financial advisor and wealth mentor.

CRITICAL INSTRUCTION REGARDING 50/30/20:
- DO NOT default to or mindlessly recite the "50/30/20 rule"! Users are tired of hearing this generic cliché. Real-world finances are nuanced: people deal with high metro rents, student loans, credit card debt, low entry-level allowances, or variable freelancing incomes where 50/30/20 is completely impractical.
- Only discuss 50/30/20 if the user explicitly asks for it by name. Otherwise, focus on realistic cash flows and personalized strategies.

YOUR CORE ADVISORY FRAMEWORK:
1. Protection First: Emphasize pure Term Insurance (if family has dependents) + Comprehensive Health Insurance (base of financial pyramid). Never recommend ULIPs or endowment policies.
2. Emergency Safety Buffer: 3 to 6 months of mandatory expenses parked safely across (1) Savings account, (2) Sweep-in FD, and (3) Liquid Mutual Funds.
3. High-Interest Debt Elimination: Treat credit cards (36-42% APR) and personal loans as financial emergencies. Guide users through Debt Avalanche (saving maximum interest) and Debt Snowball (fast psychological wins).
4. Wealth Creation & Compounding:
   - For beginners: Low-cost broad market Index Funds (e.g., Nifty 50 index fund), Public Provident Fund (PPF), or Sovereign Gold Bonds/Gold ETFs.
   - Demystify SIPs, compounding horizons (10-15+ years), and resisting market panic.
5. Tax Optimization: Guide on Section 80C, 80D, 80CCD(1B) NPS, and comparing the New vs Old Tax Regime based on deductions.
6. Multilingual & Natural Tone:
   - If the user talks in Hinglish / Hindi ("bhai loan kaise chukau", "kaha invest karu"), respond warmly in relatable, professional Hinglish with clear terms.
   - If in English, provide structured, clear English.
   - Format with bold numbers, clear bullet points, actionable step 1-2-3 roadmaps, and realistic Indian Rupee (₹) amounts.
   - Maintain a friendly, supportive tone without preachy moralizing.
"""

# --- Navigation Tabs: AI Chat vs Interactive Advisory Toolkits ---
main_tab_chat, main_tab_tools = st.tabs(["💬 AI Advisor Chat", "🧮 Interactive Wealth Toolkits"])

# ==============================================================================
# TAB 1: AI FINANCIAL ADVISOR CHAT
# ==============================================================================
with main_tab_chat:
    # Frequently Asked High-Value Financial Questions
    if len(st.session_state.messages) <= 1:
        st.markdown("##### 💡 Strategic Advisor Scenarios")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("🚀 How to start investing ₹2,000/month as a total beginner?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "Main ek complete beginner hoon aur har mahine ₹2,000 invest karna chahta hoon. "
                    "Mujhe zero-risk se lekar moderate-risk options samjhao (Index funds, PPF, FD) aur step-by-step roadmap do."
                )
            if st.button("💳 Snowball vs Avalanche: Fastest way to eliminate credit card & EMI debt?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "Mere upar loan aur credit card ki EMI hai. Debt Avalanche aur Debt Snowball method kya hain, "
                    "aur sabse tez tareeka kya hai high-interest debt se bahar aane ka?"
                )
            if col_q1.button("🎯 How do I plan for a ₹10 Lakh goal in 5 years?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "Mujhe agle 5 saal me ₹10 Lakh ka fund banana hai (higher education / business / marriage ke liye). "
                    "Kitni monthly SIP karni hogi aur asset allocation (Equity vs Debt) kaisa rakhna chahiye?"
                )
        with col_q2:
            if st.button("🛡️ Emergency Fund: How to split between Savings, Sweep-in FD, and Liquid Funds?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "Emergency fund kitna bada hona chahiye aur use exactly kahan park karna chahiye? "
                    "Savings account, Sweep-in FD aur Liquid Mutual Funds ka ideal 3-tier split samjhao."
                )
            if st.button("⚖️ New Tax Regime vs Old Tax Regime: Which saves more money?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "New Tax Regime vs Old Tax Regime me kya fark hai? Kis salary bracket me Old Regime better hoti hai "
                    "aur kab New Regime choose karni chahiye? 80C aur 80D ka impact bhi batao."
                )
            if col_q2.button("🪙 Nifty 50 Index Funds vs Active Mutual Funds: Which is better?", use_container_width=True):
                st.session_state.pending_chat_prompt = (
                    "Nifty 50 Index Fund aur Active Mutual Fund me kya difference hai? "
                    "Expense ratio aur long-term returns ke hisaab se beginners ke liye kaunsa better rehta hai?"
                )

    # Replay Chat Messages
    for message in st.session_state.messages:
        with st.chat_message("assistant" if message["role"] == "model" else "user"):
            st.markdown(message["content"])

    # Chat input & prompt detection
    user_chat_input = st.chat_input("Ask your financial advisor (e.g. SIP strategy, clearing loans, emergency fund, tax tips)...")
    prompt_to_run = st.session_state.pending_chat_prompt or user_chat_input

    if prompt_to_run:
        # Clear temporary pending prompt
        st.session_state.pending_chat_prompt = None

        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Build conversation history
        history_contents = [
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["content"])],
            )
            for msg in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            with st.spinner("FinAdvisor is analyzing your financial query..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=history_contents,
                        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                    )
                    reply_text = response.text
                    st.markdown(reply_text)
                    st.session_state.messages.append({"role": "model", "content": reply_text})
                except APIError as e:
                    if e.code in (400, 401, 403):
                        st.error("🔑 Invalid API Key: Check your `GEMINI_API_KEY` in `.env`.")
                    elif e.code == 429:
                        st.error("⏳ Rate limit reached. Please wait a moment and try again.")
                    elif e.code == 503:
                        # Fallback to flash-lite
                        try:
                            fallback = client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=history_contents,
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                            )
                            st.markdown(fallback.text)
                            st.session_state.messages.append({"role": "model", "content": fallback.text})
                        except Exception:
                            st.warning("⚠️ High server demand. Please try again shortly.")
                    else:
                        st.error(f"⚠️ API Error ({e.code}): {e.message or str(e)}")
                except Exception as e:
                    st.error(f"⚠️ An error occurred: {e}")

# ==============================================================================
# TAB 2: INTERACTIVE FINANCIAL ADVISOR TOOLKITS
# ==============================================================================
with main_tab_tools:
    st.markdown("### 🛠️ Practical Wealth & Financial Toolkit")
    st.caption("Crunch real numbers, test scenarios, and build a solid financial defense and offense.")

    subtool_1, subtool_2, subtool_3, subtool_4, subtool_5 = st.tabs([
        "📈 SIP & Wealth Builder",
        "💥 Debt Freedom Strategist",
        "🛡️ Emergency Safety Buffer",
        "⚖️ Dynamic Budget Planner",
        "🩺 Financial Health Scorecard",
    ])

    # --------------------------------------------------------------------------
    # SUBTOOL 1: SIP & WEALTH COMPOUNDING CALCULATOR
    # --------------------------------------------------------------------------
    with subtool_1:
        st.markdown("#### 📈 Systematic Investment Plan (SIP) & Compounding Engine")
        st.caption("Calculate how small, consistent investments compound into life-changing wealth over time.")

        c1, c2, c3 = st.columns(3)
        with c1:
            sip_amount = st.number_input("Monthly SIP Investment (₹)", min_value=500, value=5000, step=500)
        with c2:
            sip_rate = st.slider(
                "Expected Annual Return Rate (%)",
                min_value=4.0,
                max_value=20.0,
                value=12.0,
                step=0.5,
                help="FDs: ~6.5-7%, Balanced/Hybrid: ~9-10%, Nifty 50 / Equity Index: ~12-14%",
            )
        with c3:
            sip_years = st.slider("Investment Horizon (Years)", min_value=1, max_value=35, value=10, step=1)

        include_inflation = st.checkbox("Adjust for Inflation (Purchasing Power Reality Check)", value=True)
        inflation_rate = 6.0
        if include_inflation:
            inflation_rate = st.slider("Assumed Inflation Rate (%)", min_value=3.0, max_value=9.0, value=6.0, step=0.5)

        # SIP Calculation Formula
        # FV = P * [ (1 + i)^n - 1 ] / i * (1 + i)
        monthly_rate = (sip_rate / 100) / 12
        months = sip_years * 12
        future_value = sip_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
        total_invested = sip_amount * months
        wealth_gain = future_value - total_invested
        inflation_adjusted_fv = future_value / ((1 + (inflation_rate / 100)) ** sip_years) if include_inflation else future_value

        st.markdown(
            f"""
            <div class="tool-result-box">
                <div style="font-weight: 700; color: #059669; font-size: 1rem;">✨ Compounding Projection ({sip_years} Years)</div>
                <div class="result-metric-grid">
                    <div class="metric-chip">
                        <div class="metric-chip-title">Total Invested</div>
                        <div class="metric-chip-value">₹{total_invested:,.0f}</div>
                    </div>
                    <div class="metric-chip">
                        <div class="metric-chip-title">Wealth Generated</div>
                        <div class="metric-chip-value" style="color: #059669;">+₹{wealth_gain:,.0f}</div>
                    </div>
                    <div class="metric-chip">
                        <div class="metric-chip-title">Total Future Value</div>
                        <div class="metric-chip-value" style="color: #1D4ED8;">₹{future_value:,.0f}</div>
                    </div>
                    <div class="metric-chip">
                        <div class="metric-chip-title">Real Purchasing Power ({inflation_rate}% Inf.)</div>
                        <div class="metric-chip-value" style="color: #7C3AED;">₹{inflation_adjusted_fv:,.0f}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Yearly growth projection chart
        chart_data = []
        for y in range(1, sip_years + 1):
            m_count = y * 12
            fv_y = sip_amount * (((1 + monthly_rate) ** m_count - 1) / monthly_rate) * (1 + monthly_rate)
            inv_y = sip_amount * m_count
            gain_y = fv_y - inv_y
            chart_data.append({"Year": f"Year {y}", "Invested (₹)": round(inv_y), "Wealth Gain (₹)": round(gain_y)})

        df_growth = pd.DataFrame(chart_data).set_index("Year")
        st.markdown("##### 📊 Year-on-Year Growth Projection")
        st.bar_chart(df_growth, color=["#94A3B8", "#10B981"])

    # --------------------------------------------------------------------------
    # SUBTOOL 2: DEBT FREEDOM STRATEGIST (SNOWBALL VS AVALANCHE)
    # --------------------------------------------------------------------------
    with subtool_2:
        st.markdown("#### 💥 Debt Freedom & Interest Savings Strategist")
        st.caption("Calculate how prepaying just a little extra each month saves thousands in interest and shaves off years.")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            debt_balance = st.number_input("Outstanding Loan / Card Balance (₹)", min_value=5000, value=150000, step=5000)
            debt_apr = st.number_input(
                "Interest Rate (% p.a.)",
                min_value=5.0,
                max_value=48.0,
                value=18.0,
                step=0.5,
                help="Credit card: 36-42%, Personal loan: 12-20%, Education loan: 8-11%, Home loan: 8.5-9.5%",
            )
        with d_col2:
            monthly_interest = (debt_balance * (debt_apr / 100)) / 12
            min_possible_emi = math.ceil(monthly_interest + 100)
            current_emi = st.number_input(
                "Current Monthly Payment (₹)",
                min_value=int(min_possible_emi),
                value=int(max(5000, min_possible_emi)),
                step=500,
                help=f"Must be greater than monthly interest of ₹{monthly_interest:,.0f} to ever pay off the loan.",
            )
            extra_prepayment = st.number_input(
                "Extra Monthly Prepayment You Can Add (₹)",
                min_value=0,
                value=1500,
                step=250,
                help="Every extra rupee goes 100% towards principal reduction!",
            )

        # Amortization computation function
        def calc_payoff(principal, apr, monthly_payment):
            r = (apr / 100) / 12
            if monthly_payment <= principal * r:
                return None, None
            # n = -ln(1 - P*r/M) / ln(1+r)
            n_months = -math.log(1 - (principal * r) / monthly_payment) / math.log(1 + r)
            n_months = math.ceil(n_months)
            total_paid = n_months * monthly_payment
            total_interest = total_paid - principal
            return n_months, total_interest

        months_curr, interest_curr = calc_payoff(debt_balance, debt_apr, current_emi)
        months_accelerated, interest_accelerated = calc_payoff(debt_balance, debt_apr, current_emi + extra_prepayment)

        if months_curr and months_accelerated:
            months_saved = months_curr - months_accelerated
            interest_saved = interest_curr - interest_accelerated
            years_curr = months_curr / 12
            years_accel = months_accelerated / 12

            st.markdown(
                f"""
                <div class="tool-result-box">
                    <div style="font-weight: 700; color: #DC2626; font-size: 1rem;">🔥 Prepayment Impact Analysis</div>
                    <div class="result-metric-grid">
                        <div class="metric-chip">
                            <div class="metric-chip-title">Standard Payoff Time</div>
                            <div class="metric-chip-value">{months_curr} Months ({years_curr:.1f} yrs)</div>
                        </div>
                        <div class="metric-chip">
                            <div class="metric-chip-title">Accelerated Payoff Time</div>
                            <div class="metric-chip-value" style="color: #059669;">{months_accelerated} Months ({years_accel:.1f} yrs)</div>
                        </div>
                        <div class="metric-chip">
                            <div class="metric-chip-title">Time Freedom Gained</div>
                            <div class="metric-chip-value" style="color: #059669;">⚡ {months_saved} Months Faster</div>
                        </div>
                        <div class="metric-chip">
                            <div class="metric-chip-title">Total Interest Saved</div>
                            <div class="metric-chip-value" style="color: #1D4ED8;">💰 ₹{interest_saved:,.0f} Saved</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("##### 🥊 Snowball vs. Avalanche: Which strategy fits you?")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.info(
                "**🏔️ Debt Avalanche (Mathematically Optimal)**:\n\n"
                "- Pay minimum on all loans, then put all extra cash towards the loan with the **highest interest rate (APR %)**.\n"
                "- **Best For**: Maximum mathematical savings when you have high-rate credit cards (36%+) or expensive personal loans."
            )
        with col_s2:
            st.success(
                "**⛄ Debt Snowball (Psychological Momentum)**:\n\n"
                "- Pay minimum on all loans, then put all extra cash towards the loan with the **smallest balance**, regardless of rate.\n"
                "- **Best For**: Clearing small loans quickly to feel motivated and gain immediate financial breathing room."
            )

    # --------------------------------------------------------------------------
    # SUBTOOL 3: EMERGENCY SAFETY BUFFER & INSURANCE AUDITOR
    # --------------------------------------------------------------------------
    with subtool_3:
        st.markdown("#### 🛡️ Emergency Safety Buffer & 3-Tier Allocation")
        st.caption("Never depend on predatory loans, relatives, or breaking long-term investments during a medical or career emergency.")

        e1, e2 = st.columns(2)
        with e1:
            monthly_needs = st.number_input(
                "Monthly Mandatory Expenses (Rent, Food, Utilities, Minimum EMIs) (₹)",
                min_value=2000,
                value=25000,
                step=1000,
            )
        with e2:
            career_stability = st.selectbox(
                "Employment / Income Risk Profile",
                options=[
                    "Stable Government / Secure Corporate Job (3 Months Buffer)",
                    "Private Sector / Startup / Variable Commission (6 Months Buffer)",
                    "Freelancer / Business Owner / Single Breadwinner (9-12 Months Buffer)",
                ],
                index=1,
            )

        months_needed = 3 if "3 Months" in career_stability else (6 if "6 Months" in career_stability else 9)
        total_emergency_fund = monthly_needs * months_needed

        tier_1 = total_emergency_fund * 0.20  # Instant cash / Savings
        tier_2 = total_emergency_fund * 0.40  # Sweep-in FD / 7-day deposit
        tier_3 = total_emergency_fund * 0.40  # Liquid Mutual Fund

        st.markdown(
            f"""
            <div class="tool-result-box">
                <div style="font-weight: 700; color: #047857; font-size: 1.05rem;">
                    🛡️ Total Recommended Safety Shield: ₹{total_emergency_fund:,.0f} ({months_needed} Months Coverage)
                </div>
                <p style="margin: 0.4rem 0 1rem 0; font-size: 0.88rem; color: #475569;">
                    Do not keep all emergency money in a single standard savings account where it tempts casual spending. Split it using the 3-Tier Rule:
                </p>
                <div class="result-metric-grid">
                    <div class="metric-chip" style="border-left: 4px solid #10B981;">
                        <div class="metric-chip-title">Tier 1: Instant Cash (20%)</div>
                        <div class="metric-chip-value">₹{tier_1:,.0f}</div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.3rem;">Secondary savings bank account / UPI for immediate hospital or auto repairs.</div>
                    </div>
                    <div class="metric-chip" style="border-left: 4px solid #0284C7;">
                        <div class="metric-chip-title">Tier 2: Sweep-in FD (40%)</div>
                        <div class="metric-chip-value">₹{tier_2:,.0f}</div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.3rem;">Bank Auto-Sweep FD (earns 6.5-7% interest with instant auto-breakage upon demand).</div>
                    </div>
                    <div class="metric-chip" style="border-left: 4px solid #8B5CF6;">
                        <div class="metric-chip-title">Tier 3: Liquid Mutual Fund (40%)</div>
                        <div class="metric-chip-value">₹{tier_3:,.0f}</div>
                        <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.3rem;">Overnight or Liquid fund with T+1 instant redemption feature (zero equity volatility).</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # SUBTOOL 4: DYNAMIC BUDGET PLANNER (BEYOND 50/30/20)
    # --------------------------------------------------------------------------
    with subtool_4:
        st.markdown("#### ⚖️ Dynamic Budgeting Framework (Tailored to Your Life)")
        st.caption("No single formula fits everyone. Choose a framework that matches your current income and life stage.")

        b_income = st.number_input("Total Monthly In-Hand Income / Allowance (₹)", min_value=1000, value=35000, step=1000)

        budget_strategy = st.radio(
            "Select Your Budgeting Strategy",
            options=[
                "🔥 Aggressive Wealth Builder (40% Needs, 20% Wants, 40% Investments)",
                "🏙️ High Metro Rent / Student Starter (70% Needs, 15% Wants, 15% Savings)",
                "⚡ Pay Yourself First (30% Auto-Invested First, 50% Needs, 20% Guilt-Free)",
                "🎨 Custom Allocation (Set your own percentages)",
                "📖 Classic 50/30/20 (Traditional Textbook Rule)",
            ],
            index=0,
        )

        if "Aggressive" in budget_strategy:
            p_needs, p_wants, p_save = 40, 20, 40
        elif "High Metro" in budget_strategy:
            p_needs, p_wants, p_save = 70, 15, 15
        elif "Pay Yourself First" in budget_strategy:
            p_needs, p_wants, p_save = 50, 20, 30
        elif "Classic" in budget_strategy:
            p_needs, p_wants, p_save = 50, 30, 20
        else:
            col_sl1, col_sl2, col_sl3 = st.columns(3)
            with col_sl1:
                p_needs = st.slider("Essentials %", 20, 80, 50)
            with col_sl2:
                p_wants = st.slider("Lifestyle / Wants %", 0, 50, 25)
            with col_sl3:
                p_save = max(0, 100 - (p_needs + p_wants))
                st.metric("Calculated Savings %", f"{p_save}%")

        val_needs = b_income * (p_needs / 100)
        val_wants = b_income * (p_wants / 100)
        val_save = b_income * (p_save / 100)

        st.markdown(
            f"""
            <div class="tool-result-box">
                <div style="font-weight: 700; color: #1E293B; font-size: 1rem;">
                    💡 Monthly Budget Breakdown for ₹{b_income:,.0f}
                </div>
                <div class="result-metric-grid">
                    <div class="metric-chip">
                        <div class="metric-chip-title">Essentials & Living ({p_needs}%)</div>
                        <div class="metric-chip-value">₹{val_needs:,.0f}</div>
                        <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.2rem;">Rent, food, utilities, transport, EMIs</div>
                    </div>
                    <div class="metric-chip">
                        <div class="metric-chip-title">Lifestyle & Fun ({p_wants}%)</div>
                        <div class="metric-chip-value" style="color: #EA580C;">₹{val_wants:,.0f}</div>
                        <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.2rem;">Dining out, movies, subscriptions, hobbies</div>
                    </div>
                    <div class="metric-chip">
                        <div class="metric-chip-title">Wealth Building ({p_save}%)</div>
                        <div class="metric-chip-value" style="color: #059669;">₹{val_save:,.0f}</div>
                        <div style="font-size: 0.76rem; color: #64748B; margin-top: 0.2rem;">Emergency fund, SIPs, PPF, Debt payoff</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # SUBTOOL 5: FINANCIAL HEALTH SCORECARD (0 TO 100)
    # --------------------------------------------------------------------------
    with subtool_5:
        st.markdown("#### 🩺 Comprehensive Financial Health Diagnostic")
        st.caption("Answer 4 key financial health markers to calculate your overall financial fitness score.")

        h_col1, h_col2 = st.columns(2)
        with h_col1:
            q_emergency = st.select_slider(
                "1. How many months of expenses do you currently have in liquid savings?",
                options=["0 months (Zero buffer)", "1 month", "2-3 months", "4-5 months", "6+ months"],
                value="2-3 months",
            )
            q_savings_rate = st.select_slider(
                "2. What percentage of your monthly income do you consistently invest/save?",
                options=["Under 5%", "5% - 15%", "15% - 25%", "25% - 40%", "40%+"],
                value="15% - 25%",
            )
        with h_col2:
            q_debt = st.radio(
                "3. Do you carry high-interest debt (Credit cards, personal loans, instant loan apps)?",
                options=["Yes, active unpaid high-interest debt", "Only low-rate loans (Education / Home loan)", "Zero debt / No outstanding loans"],
                index=1,
            )
            q_insurance = st.radio(
                "4. Do you have dedicated Health Insurance independent of your employer?",
                options=["No health insurance at all", "Only employer-provided group coverage", "Yes, personal comprehensive policy (₹5L+)"],
                index=1,
            )

        # Scoring Logic (Max 100 points)
        score = 0

        # Emergency Fund (Max 25)
        ef_scores = {
            "0 months (Zero buffer)": 2,
            "1 month": 8,
            "2-3 months": 15,
            "4-5 months": 21,
            "6+ months": 25,
        }
        score += ef_scores.get(q_emergency, 10)

        # Savings Rate (Max 25)
        sr_scores = {
            "Under 5%": 3,
            "5% - 15%": 12,
            "15% - 25%": 18,
            "25% - 40%": 23,
            "40%+": 25,
        }
        score += sr_scores.get(q_savings_rate, 12)

        # Debt Score (Max 25)
        if "Zero debt" in q_debt:
            score += 25
        elif "low-rate loans" in q_debt:
            score += 18
        else:
            score += 4

        # Insurance Score (Max 25)
        if "personal comprehensive" in q_insurance:
            score += 25
        elif "employer-provided" in q_insurance:
            score += 15
        else:
            score += 2

        # Grade interpretation
        if score >= 85:
            grade_title = "🏆 Financial Fortress (Excellent)"
            grade_color = "#059669"
            advice_summary = "Aapka financial base bohot strong hai. Ab advanced wealth compounding aur tax optimization par focus karein."
        elif score >= 65:
            grade_title = "🛡️ Stable Foundation (Good)"
            grade_color = "#0284C7"
            advice_summary = "Aap achhe track par hain. Bas high-interest debt se dur rahein aur emergency fund ko 6 months tak push karein."
        elif score >= 45:
            grade_title = "⚠️ Vulnerable Zone (Action Needed)"
            grade_color = "#D97706"
            advice_summary = "Kisi bhi emergency me debt trap me fasne ka risk hai. Sabse pehle 1-2 month buffer aur health insurance secure karein."
        else:
            grade_title = "🚨 Critical Alarm (Immediate Priority)"
            grade_color = "#DC2626"
            advice_summary = "High priority: Kisi bhi tarah ke credit card/instant loan apps se bachein aur minimum ₹15,000 ka cash reserve banayein."

        st.markdown(
            f"""
            <div class="tool-result-box" style="border-left: 5px solid {grade_color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <span style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: #64748B;">Financial Health Score</span>
                        <div style="font-size: 2.2rem; font-weight: 800; color: {grade_color};">{score} <span style="font-size: 1.1rem; color: #94A3B8;">/ 100</span></div>
                    </div>
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 700; color: {grade_color};">
                        {grade_title}
                    </div>
                </div>
                <p style="margin: 0.8rem 0 0 0; font-size: 0.92rem; color: #334155; line-height: 1.5;">
                    <b>Diagnostic Assessment:</b> {advice_summary}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        diagnostic_prompt_text = (
            f"Maine apna Financial Health Diagnostic complete kiya hai. Mera Score hai: {score}/100 ({grade_title}).\n"
            f"- Emergency Fund: {q_emergency}\n"
            f"- Monthly Savings Rate: {q_savings_rate}\n"
            f"- Debt Status: {q_debt}\n"
            f"- Health Insurance: {q_insurance}\n\n"
            "Mera ek personalized step-by-step financial plan banao ki agle 6 mahine me mujhe kya 3 concrete steps lene chahiye."
        )

        if st.button("📋 Send This Diagnostic to AI Advisor for 1-on-1 Plan", use_container_width=True):
            st.session_state.pending_chat_prompt = diagnostic_prompt_text
            st.success("✅ Diagnostic report sent to AI Advisor! Check Tab 1.")
            st.rerun()
