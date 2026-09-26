import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Battery QC Check")
st.title("First 20 Cycles: Battery QC Check")
st.write(
    "Pick a battery. The app fits a trend line to its early cycles and estimates "
    "when it will wear out (1.4 Ah). If that's too soon, the battery is flagged HOLD."
)

df = pd.read_csv("app_data/capacity.csv")

battery = st.selectbox("Battery", sorted(df["battery_id"].unique()))
k = st.slider("Early cycles to use", 10, 40, 20)
spec = st.slider("Minimum life required (cycles)", 80, 160, 120)

g = df[df["battery_id"] == battery]
early = g[g["cycle"] <= k]

slope, intercept = np.polyfit(early["cycle"], early["capacity"], 1)
projected = (1.4 - intercept) / slope if slope < 0 else np.inf
flag = "HOLD" if projected < spec else "PASS"

below = g[g["capacity"] < 1.4]
actual = int(below["cycle"].iloc[0]) if len(below) else None

c1, c2, c3 = st.columns(3)
c1.metric("Flag", flag)
c2.metric("Projected end of life", f"cycle {projected:.0f}" if np.isfinite(projected) else "no fade yet")
c3.metric("Actual end of life", f"cycle {actual}" if actual else "not reached")

if flag == "HOLD":
    st.error(f"{battery} is projected to wear out before cycle {spec}. Hold for inspection.")
else:
    st.success(f"{battery} is projected to last past cycle {spec}.")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(g["cycle"], g["capacity"], color="lightgray", label="Later cycles (not used)")
ax.plot(early["cycle"], early["capacity"], "o", ms=3, color="tab:blue", label=f"First {k} cycles")

end = int(min(max(g["cycle"].max(), projected if np.isfinite(projected) else 0), 300)) + 10
x = np.arange(1, end)
ax.plot(x, intercept + slope * x, "--", color="tab:blue", label="Trend line")

ax.axhline(1.4, color="red", linestyle="--", label="End of life (1.4 Ah)")
ax.axvline(spec, color="orange", linestyle=":", label=f"Required life ({spec})")
ax.set_ylim(1.1, 2.1)
ax.set_xlabel("Cycle")
ax.set_ylabel("Capacity (Ah)")
ax.legend(fontsize=8)
st.pyplot(fig)

st.caption("Data: NASA Ames Li-ion Battery Aging Dataset. Only the first cycles are used for the decision.")