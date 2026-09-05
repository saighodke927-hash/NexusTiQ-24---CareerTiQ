import streamlit as st
from openai import OpenAI

# Page Config
st.set_page_config(page_title="Triage AI", page_icon="🏥")
st.title("🏥 Patient Intake Triage Assistant")

# Sidebar for API Key
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")

# --- TRIAGE RULES (The Knowledge Base) ---
TRIAGE_RULES = """
- RULE-CP-01 (Chest Pain): Any chest pain > 5 mins or radiating to arm/jaw = EMERGENCY (ER).
- RULE-BR-01 (Breathing): Difficulty breathing at rest or speaking in fragments = EMERGENCY (ER).
- RULE-FE-01 (Fever): Fever > 103F or confusion = URGENT CARE.
- RULE-IN-01 (Injury): Visible bone, heavy bleeding, or loss of consciousness = EMERGENCY (ER).
- RULE-AB-01 (Abdominal): Rigid abdomen, vomiting blood, or severe localized pain = URGENT CARE.
"""

# --- SYSTEM PROMPT (The Guardrails) ---
SYSTEM_PROMPT = f"""
You are a Medical Triage Assistant. Your goal is NOT to diagnose, but to prioritize patients.
1. RULES: Use these rules strictly: {TRIAGE_RULES}
2. BEHAVIOR: Ask relevant follow-up questions to fill in missing information (e.g., duration, severity).
3. SAFETY: NEVER DIAGNOSE. If the case is high-risk or ambiguous, escalate to a human immediately.
4. CITATION: Every recommendation MUST cite the Rule ID (e.g., RULE-CP-01).
5. FORMAT: If the user asks for a summary or if you have enough info, generate a note:
   - Recommended Urgency Level (Emergency/Urgent/Routine)
   - Recommended Department
   - Rule Cited
   - Reported vs Established Facts
   - What remains Unknown
"""

if api_key:
    client = OpenAI(api_key=api_key)
    
    # Initialize Session History
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Display Chat
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Explain your symptoms..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.warning("Please enter your OpenAI API key in the sidebar to begin.")