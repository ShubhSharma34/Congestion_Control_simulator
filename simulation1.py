import streamlit as st
import matplotlib.pyplot as plt
import time

# ---- SESSION STATE FOR PAUSE ----
if "paused" not in st.session_state:
    st.session_state.paused = False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Congestion Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-size: 18px;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #111 0%, #000 100%);
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #050505;
    border-right: 2px solid #d4ff00;
}
.stButton>button {
    background-color: transparent;
    border: 2px solid #d4ff00;
    color: #d4ff00;
    border-radius: 10px;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #d4ff00;
    color: black;
    box-shadow: 0 0 20px #d4ff00;
}
button[role="tab"] {
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Simulation Controls")

users = st.sidebar.slider("Users", 1, 20, 5)
capacity = st.sidebar.slider("Capacity", 1, 10, 2)
queue_size = st.sidebar.slider("Queue Size", 1, 20, 8)
algo = st.sidebar.selectbox("Algorithm", ["Tahoe", "Reno", "New Reno"])

# ---------------- RECOMMENDATION ----------------
load = users / capacity

if load > 2:
    suggested_algo = "New Reno"
    reason = "High load detected. New Reno improves recovery from packet loss and reduces buffering."
    st.sidebar.warning(f"Suggested: {suggested_algo}")
elif load > 1:
    suggested_algo = "Reno"
    reason = "Moderate congestion. Reno balances throughput and recovery using fast retransmit."
    st.sidebar.info(f"Suggested: {suggested_algo}")
else:
    suggested_algo = "Tahoe"
    reason = "Low congestion. Tahoe is simple and performs well with minimal packet loss."
    st.sidebar.success(f"Suggested: {suggested_algo}")

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;color:#d4ff00;'>OTT Congestion Control Dashboard</h1>", unsafe_allow_html=True)

# ---------------- EXPLANATION ----------------
st.markdown(f"""
### Why {suggested_algo}?

{reason}
""")

# ---------------- CONGESTION SCORE ----------------
congestion_score = (users * 10) / (capacity * queue_size)

st.markdown(f"""
<h3 style='color:#ff00ff;'>Congestion Score: {round(congestion_score,2)}</h3>
""", unsafe_allow_html=True)

if congestion_score > 5:
    st.error("Severe congestion risk")
elif congestion_score > 2:
    st.warning("Moderate congestion")
else:
    st.success("Low congestion")

# ---------------- PREDICTED QUALITY ----------------
if load > 2:
    st.error("Expected Streaming: Buffering (480p)")
elif load > 1:
    st.warning("Expected Streaming: 720p")
else:
    st.success("Expected Streaming: 1080p")

# ---------------- SIMULATION FUNCTION ----------------
def run_simulation(algo, users, capacity, queue_size):
    cwnd, ssthresh, queue = 1, 8, 0
    queue_data, cwnd_data = [], []

    for _ in range(30):
        sent = cwnd

        if queue + sent > queue_size:
            ssthresh = max(cwnd // 2, 1)
            if algo == "Tahoe":
                cwnd = 1
            elif algo == "Reno":
                cwnd = ssthresh
            else:
                cwnd = ssthresh + 1
            queue = queue_size
        else:
            queue += sent
            cwnd = cwnd*2 if cwnd < ssthresh else cwnd+1

        queue -= min(queue, capacity)

        queue_data.append(queue)
        cwnd_data.append(cwnd)

    return queue_data, cwnd_data

# ---------------- NETWORK DRAW ----------------
def draw_network(queue, queue_size, users):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.set_xlim(0,10)
    ax.set_ylim(0,10)

    for i in range(users):
        ax.scatter(1, 1 + i*(8/max(users,1)), color="white")

    ax.add_patch(plt.Rectangle((4,3),1,4, fill=False, edgecolor="yellow"))

    color = "green" if queue < queue_size*0.3 else "orange" if queue < queue_size*0.7 else "red"

    for i in range(int(queue)):
        ax.add_patch(plt.Rectangle((4.2,3+i*0.3),0.6,0.2,color=color))

    ax.scatter(8,5, color="cyan", s=150)

    ax.set_title("Buffering" if color=="red" else "720p" if color=="orange" else "1080p", color=color)
    ax.axis('off')
    return fig

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["Simulation", "Graphs"])

# ---------------- SIMULATION ----------------
with tab1:
    col1, col2 = st.columns([2,1])

    # CONTROL BUTTONS
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("Pause / Resume"):
            st.session_state.paused = not st.session_state.paused

    with col_btn2:
        if st.button("Reset"):
            st.session_state.paused = False

    # MAIN SIMULATION
    with col1:
        if st.button("Run Simulation"):
            cwnd, ssthresh, queue = 1, 8, 0
            placeholder = st.empty()

            for _ in range(20):

                if st.session_state.paused:
                    st.warning("Simulation Paused")
                    st.stop()

                current_load = users / max(capacity, 1)

                if current_load > 2:
                    algo = "New Reno"
                elif current_load > 1:
                    algo = "Reno"

                st.write(f"Active Algorithm: {algo}")

                sent = cwnd

                if queue + sent > queue_size:
                    ssthresh = max(cwnd // 2, 1)
                    cwnd = 1 if algo=="Tahoe" else ssthresh if algo=="Reno" else ssthresh+1
                    queue = queue_size
                else:
                    queue += sent
                    cwnd = cwnd*2 if cwnd < ssthresh else cwnd+1

                queue -= min(queue, capacity)

                placeholder.pyplot(draw_network(queue, queue_size, users))
                time.sleep(0.4)

    with col2:
        st.metric("Users", users)
        st.metric("Capacity", capacity)
        st.metric("Queue Size", queue_size)
        st.metric("Algorithm", algo)

# ---------------- GRAPHS ----------------
with tab2:
    if st.button("Generate Graphs"):
        q, c = run_simulation(algo, users, capacity, queue_size)

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#000')
            ax.set_facecolor('#000')
            ax.plot(q, color="#ff3131")
            ax.tick_params(colors='white')
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('#000')
            ax.set_facecolor('#000')
            ax.plot(c, color="#d4ff00")
            ax.tick_params(colors='white')
            st.pyplot(fig)

# ---------------- OPTIMIZATION ----------------
st.subheader("Optimization")

if st.button("Optimize Network"):

    st.subheader("Before Optimization")
    cwnd, ssthresh, queue = 1, 8, 0
    placeholder1 = st.empty()

    for _ in range(10):
        sent = cwnd

        if queue + sent > queue_size:
            ssthresh = max(cwnd // 2, 1)
            cwnd = 1 if algo=="Tahoe" else ssthresh if algo=="Reno" else ssthresh+1
            queue = queue_size
        else:
            queue += sent
            cwnd = cwnd*2 if cwnd < ssthresh else cwnd+1

        queue -= min(queue, capacity)

        placeholder1.pyplot(draw_network(queue, queue_size, users))
        time.sleep(0.3)

    st.subheader("After Optimization (New Reno + Increased Capacity)")

    cwnd, ssthresh, queue = 1, 8, 0
    placeholder2 = st.empty()

    for _ in range(10):
        sent = cwnd

        if queue + sent > queue_size:
            ssthresh = max(cwnd // 2, 1)
            cwnd = ssthresh + 1
            queue = queue_size
        else:
            queue += sent
            cwnd = cwnd*2 if cwnd < ssthresh else cwnd+1

        queue -= min(queue, capacity + 1)

        placeholder2.pyplot(draw_network(queue, queue_size, users))
        time.sleep(0.3)

    st.success("Congestion visibly reduced after optimization")

# ---------------- COMPARISON ----------------
if st.button("Compare All Algorithms"):
    algos = ["Tahoe", "Reno", "New Reno"]

    for a in algos:
        q, _ = run_simulation(a, users, capacity, queue_size)
        st.write(f"{a} → Final Queue: {q[-1]}")