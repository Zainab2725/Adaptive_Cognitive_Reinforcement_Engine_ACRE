import math
import streamlit as st

# ---------------------------------------------------------
# ACRE Streamlit prototype
# Uses the existing fitted Flexible ACRE parameters supplied
# in the project conversation. No training is performed here.
# ---------------------------------------------------------

S0 = 2.74537833e-04
ALPHA = 5.103140000075937
BETA = 0.18597599869112888
FLOOR = 0.5

st.set_page_config(
    page_title="ACRE | Revision Assistant",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 ACRE — Adaptive Cognitive Reinforcement Engine")
st.caption("Research prototype • Flexible ACRE")

st.info(
    "This interface uses your existing fitted Flexible ACRE parameters. "
    "The model was evaluated on response correctness, not validated delayed recall. "
    "Treat revision timing as an experimental estimate, not a proven forgetting prediction."
)

with st.sidebar:
    st.header("About this prototype")
    st.write("No model training happens when you use this app.")
    st.write("Current model floor: 0.50")
    st.write("Recall threshold is a provisional setting (default 80%).")
    st.warning(
        "The fitted stability parameter is extremely small, so revision-time "
        "estimates may be unrealistically short. This is shown transparently."
    )

st.subheader("Student learning history")

col1, col2 = st.columns(2)
with col1:
    correct_count = st.number_input(
        "Correct answers for this skill",
        min_value=0,
        max_value=10000,
        value=5,
        step=1,
    )
with col2:
    incorrect_count = st.number_input(
        "Incorrect answers for this skill",
        min_value=0,
        max_value=10000,
        value=2,
        step=1,
    )

elapsed_days = st.number_input(
    "Days since this skill was last practised",
    min_value=0.0,
    max_value=36500.0,
    value=0.0,
    step=0.25,
    help="Enter time since the student's previous practice of the SAME skill, not since any unrelated question.",
)

threshold = st.slider(
    "Recall probability threshold (experimental)",
    min_value=0.51,
    max_value=0.95,
    value=0.80,
    step=0.01,
)

def estimate_stability_days(correct, incorrect):
    stability = S0 * (1.0 + ALPHA * math.log1p(correct)) * math.exp(-BETA * incorrect)
    return max(float(stability), 1e-12)

def recall_probability(stability_days, elapsed_time_days):
    # Flexible ACRE form: floor + (1-floor) * exp(-t/S)
    exponent = max(-700.0, min(0.0, -elapsed_time_days / stability_days))
    p = FLOOR + (1.0 - FLOOR) * math.exp(exponent)
    return min(1.0 - 1e-6, max(1e-6, p))

if st.button("Estimate recall and revision time", type="primary", use_container_width=True):
    stability = estimate_stability_days(correct_count, incorrect_count)
    recall = recall_probability(stability, elapsed_days)

    # Solve threshold = floor + (1-floor) * exp(-t/S)
    if threshold <= FLOOR or threshold >= 1.0:
        revision_days = None
    else:
        revision_days = -stability * math.log((threshold - FLOOR) / (1.0 - FLOOR))

    st.subheader("ACRE estimate")
    a, b = st.columns(2)
    a.metric("Estimated recall probability", f"{recall:.1%}")
    b.metric("Provisional threshold", f"{threshold:.0%}")

    if revision_days is not None:
        st.metric("Calculated time to threshold", f"{revision_days * 1440:.2f} minutes")
        st.caption(
            f"Equivalent to {revision_days:.8f} days under the current mathematical model."
        )

    st.write(f"Estimated stability: **{stability:.8f} days**")

    if recall <= threshold:
        st.warning(
            "The model estimate is at or below the selected threshold. "
            "A revision could be suggested by this prototype, but the timing is not validated."
        )
    else:
        st.success(
            "The model estimate is above the selected threshold at the entered elapsed time. "
            "Continue monitoring; this is not proof that the student will remember."
        )

    if stability < 0.01 or (revision_days is not None and revision_days < 1 / 1440):
        st.error(
            "Model diagnostic warning: the calculated stability/revision interval is extremely short. "
            "Do not use this as a real student schedule until the time feature and delayed-recall "
            "performance have been validated."
        )

with st.expander("Model details and limitations"):
    st.markdown(
        """
        **Flexible ACRE formula**

        - Stability: `S = S0 × (1 + alpha × log(1 + correct)) × exp(-beta × incorrect)`
        - Recall estimate: `p = floor + (1 - floor) × exp(-elapsed_days / S)`

        **Current fitted parameters**

        - `S0 = 0.0002745378`
        - `alpha = 5.10314`
        - `beta = 0.185976`
        - `floor = 0.50`

        **Important limitations**

        1. The existing evaluation predicts correctness on the ASSISTments dataset; it does not directly establish when a learner forgets.
        2. The app asks for time since the SAME skill was last practised. The dataset's existing elapsed-time feature must be verified to match that definition before claiming this app is validated.
        3. The fitted `S0` is very small and the floor is at its fitting boundary, so the resulting schedule may be unrealistic.
        4. The 80% threshold is provisional and should be justified or tested in a delayed-recall study.
        """
    )

st.divider()
st.caption("ACRE research prototype • Do not use the displayed timing as a validated educational intervention.")
