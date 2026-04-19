import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="FRD AI Assistant", layout="wide")
st.title("📄 FRD AI Assistant")

# ---------------- STATE ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "start"

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Enter your requirement...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------- START FLOW ----------------
    if st.session_state.mode == "start":

        response = requests.post(
            f"{API_BASE}/start_clarification",
            json={"text": user_input}
        ).json()

        st.session_state.session_id = response["session_id"]
        question = response["question"]

        st.session_state.messages.append({
            "role": "assistant",
            "content": question
        })

        with st.chat_message("assistant"):
            st.markdown(question)

        st.session_state.mode = "chat"

    # ---------------- CHAT FLOW ----------------
    elif st.session_state.mode == "chat":

        response = requests.post(
            f"{API_BASE}/answer",
            json={
                "session_id": st.session_state.session_id,
                "answer": user_input
            }
        ).json()

        # ---------- DONE ----------
        if response.get("done"):

            st.session_state.messages.append({
                "role": "assistant",
                "content": "✅ Generating FRD..."
            })

            with st.chat_message("assistant"):
                st.markdown("✅ Generating FRD...")

            # -------- GENERATE FRD --------
            frd = requests.post(
                f"{API_BASE}/generate",
                json={"session_id": st.session_state.session_id}
            ).json()

            st.divider()
            st.header("📄 FRD Generated")

            st.subheader(frd.get("frd_text", ""))

            sections = frd.get("sections", {})

            st.markdown("### 📌 Overview")
            st.write(sections.get("overview", ""))

            st.markdown("### 🎯 Objectives")
            st.write(sections.get("objectives", ""))

            st.markdown("### ⚙️ Functional Requirements")
            for req in sections.get("functional_requirements", []):
                st.write(f"{req.get('id')}. {req.get('description')}")

            st.markdown("### 🔒 Non-Functional Requirements")
            for req in sections.get("non_functional_requirements", []):
                st.write(f"{req.get('id')}. {req.get('description')}")

            # -------- SCORE --------
            score = requests.post(
                f"{API_BASE}/score",
                json={"session_id": st.session_state.session_id}
            ).json()

            st.divider()
            st.header("📊 FRD Health Score")

            st.subheader(f"Score: {score.get('overall_score', 0)} / 100")

            st.markdown("### ✅ Strengths")
            for s in score.get("strengths", []):
                st.write(f"- {s}")

            st.markdown("### ⚠️ Improvements")
            for i in score.get("improvements", []):
                st.write(f"- {i}")

            st.session_state.mode = "done"

        # ---------- CONTINUE ----------
        else:
            question = response.get("question", "")

            st.session_state.messages.append({
                "role": "assistant",
                "content": question
            })

            with st.chat_message("assistant"):
                st.markdown(question)

# ---------------- RESET ----------------
if st.button("🔄 Restart"):
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.mode = "start"
    st.rerun()