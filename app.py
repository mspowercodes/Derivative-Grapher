import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(page_title="Mystery Derivative Slope Grapher", layout="wide")

st.title("🕵️‍♂️ Mystery Derivative Slope Grapher")
st.write("Click any point along the upper curve to select it, use the **➕** and **➖** buttons to tilt the red tangent line, then plot your guess!")

# --- INITIALIZE SESSION STATE ---
if 'func_type' not in st.session_state:
    st.session_state.func_type = 'poly'
    # Default initial function: f(x) = 0.2x^3 - x
    st.session_state.coeffs = [0.2, 0.0, -1.0, 0.0, 0.0]  # [x^3, x^2, x, const, rational singularity x0]
    st.session_state.history_x = []
    st.session_state.history_y_guess = []
    st.session_state.selected_x = 0.0
    st.session_state.input_slope = 0.0

# --- MATH HELPER FUNCTIONS ---
def evaluate_func(func_type, coeffs, x):
    # coeffs = [c3, c2, c1, c0, singularity_x0]
    c3, c2, c1, c0, x0 = coeffs
    if func_type == 'poly':
        return c3*x**3 + c2*x**2 + c1*x + c0
    elif func_type == 'rational':
        # Singularity at x0: f(x) = c1 / (x - x0) + c0
        # Prevent division by zero errors on individual scalar points or numpy elements
        with np.errstate(divide='ignore', invalid='ignore'):
            res = c1 / (x - x0) + c0
            if isinstance(x, np.ndarray):
                res[np.abs(x - x0) < 0.05] = np.nan  # Mask singularity for visual break
            elif np.abs(x - x0) < 0.05:
                return None
            return res
    return 0

def evaluate_deriv(func_type, coeffs, x):
    c3, c2, c1, c0, x0 = coeffs
    if func_type == 'poly':
        return 3*c3*x**2 + 2*c2*x + c1
    elif func_type == 'rational':
        # f'(x) = -c1 / (x - x0)^2
        with np.errstate(divide='ignore', invalid='ignore'):
            res = -c1 / (x - x0)**2
            if isinstance(x, np.ndarray):
                res[np.abs(x - x0) < 0.05] = np.nan
            elif np.abs(x - x0) < 0.05:
                return 0
            return res
    return 0

def generate_new_function():
    ftype = random.choice(['poly', 'rational'])
    st.session_state.func_type = ftype
    st.session_state.history_x = []
    st.session_state.history_y_guess = []
    st.session_state.selected_x = 0.0
    st.session_state.input_slope = 0.0
    
    if ftype == 'poly':
        order = random.choice([0, 1, 2, 3, 4])
        # Random coefficients tailored to stay bounded beautifully inside the window frame
        c3 = round(random.uniform(-0.15, 0.15), 3) if order >= 3 else 0.0
        c2 = round(random.uniform(-0.4, 0.4), 2) if order >= 2 else 0.0
        c1 = round(random.uniform(-1.5, 1.5), 2) if order >= 1 else 0.0
        c0 = round(random.uniform(-1.5, 1.5), 2)
        # For an order 4 effect, add a subtle x^4 curve if desired, otherwise standard 0-3 polynomials work nicely
        if order == 4:
            # Re-use c3/c2 parameters to mock higher order balances
            c2, c3 = round(random.uniform(-0.1, 0.1), 3), round(random.uniform(-0.2, 0.2), 2)
        st.session_state.coeffs = [c3, c2, c1, c0, 0.0]
    else:
        # Rational function with a random singularity visible on screen (-1.5 to 1.5)
        x0 = round(random.uniform(-1.5, 1.5), 1)
        # Avoid exactly 0 to keep interactions interesting
        if abs(x0) < 0.2: x0 = 0.8
        c1 = random.choice([-1.0, -0.5, 0.5, 1.0]) # Scale amplitude
        c0 = round(random.uniform(-1.0, 1.0), 1) # Shift vertical
        st.session_state.coeffs = [0.0, 0.0, c1, c0, x0]

# --- APP LAYOUT: SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    if st.button("🎲 Generate Next Mystery Function", use_container_width=True):
        generate_new_function()
        st.rerun()
        
    st.markdown("---")
    st.write(f"**Selected Target Point:** `x = {st.session_state.selected_x:.1f}`")
    
    # Tactile Slope Buttons instead of the Slider
    st.write("**Adjust Tangent Slope:**")
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("➕ Increase (+0.2)", use_container_width=True):
            st.session_state.input_slope = round(st.session_state.input_slope + 0.2, 1)
    with b_col2:
        if st.button("➖ Decrease (-0.2)", use_container_width=True):
            st.session_state.input_slope = round(st.session_state.input_slope - 0.2, 1)
            
    st.metric(label="Current Slope Value", value=f"{st.session_state.input_slope:.1f}")
    
    st.markdown("---")
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Plot Slope", type="primary", use_container_width=True):
            st.session_state.history_x.append(st.session_state.selected_x)
            st.session_state.history_y_guess.append(st.session_state.input_slope)
            
            actual = evaluate_deriv(st.session_state.func_type, st.session_state.coeffs, st.session_state.selected_x)
            if actual is not None and abs(st.session_state.input_slope - actual) < 0.4:
                st.success("🎯 Spot on!")
            else:
                st.warning("Plotted!")
                
    with col2:
        if st.button("🗑️ Clear Dots", use_container_width=True):
            st.session_state.history_x = []
            st.session_state.history_y_guess = []
            st.rerun()
            
    st.markdown("---")
    show_answer = st.checkbox("Reveal Target Derivative Shape", value=False)

# --- CALCULATE BACKGROUND DATA PLOTS ---
x_base = np.linspace(-3.0, 3.0, 300)
y_base = evaluate_func(st.session_state.func_type, st.session_state.coeffs, x_base)
dy_base = evaluate_deriv(st.session_state.func_type, st.session_state.coeffs, x_base)

# Generate distinct discrete clickable dot targets spaced every 0.2 units
x_clickable = np.arange(-2.6, 2.7, 0.2)
y_clickable = evaluate_func(st.session_state.func_type, st.session_state.coeffs, x_clickable)

# Dynamic viewport adjustments
y_clean = y_base[~np.isnan(y_base)] if isinstance(y_base, np.ndarray) else [-3, 3]
dy_clean = dy_base[~np.isnan(dy_base)] if isinstance(dy_base, np.ndarray) else [-3, 3]
y_min, y_max = float(np.clip(np.min(y_clean) - 1.0, -8, 8)), float(np.clip(np.max(y_clean) + 1.0, -8, 8))
dy_min, dy_max = float(np.clip(np.min(dy_clean) - 1.0, -8, 8)), float(np.clip(np.max(dy_clean) + 1.0, -8, 8))

# --- UPPER PLOT CONFIGURATION (Function Canvas) ---
fig_upper = go.Figure()
# Smooth main curve
fig_upper.add_trace(go.Scatter(x=x_base, y=y_base, mode='lines', name='Function', line=dict(color='#17A2B8', width=3), hoverinfo='skip'))

# Add the clickable transparent dots along the line
fig_upper.add_trace(go.Scatter(
    x=x_clickable, y=y_clickable, mode='markers', name='Click Targets',
    marker=dict(size=10, color='rgba(23, 162, 184, 0.3)', line=dict(color='rgba(0,0,0,0.1)', width=1)),
    hovertemplate="Click to select: x = %{x:.1f}<extra></extra>"
))

# Calculate and trace the moving custom tangent line preview line segment
sel_x = st.session_state.selected_x
sel_y = evaluate_func(st.session_state.func_type, st.session_state.coeffs, sel_x)
if sel_y is not None:
    tangent_x = np.linspace(sel_x - 0.6, sel_x + 0.6, 10)
    tangent_y = st.session_state.input_slope * (tangent_x - sel_x) + sel_y
    fig_upper.add_trace(go.Scatter(x=tangent_x, y=tangent_y, mode='lines', line=dict(color='#DC3545', width=3, dash='dash'), hoverinfo='skip'))
    fig_upper.add_trace(go.Scatter(x=[sel_x], y=[sel_y], mode='markers', marker=dict(color='#DC3545', size=12), hoverinfo='skip'))

fig_upper.update_layout(title="Mystery Function: f(x)", xaxis_title="x", yaxis_title="y", showlegend=False, height=340, margin=dict(t=40, b=40, l=60, r=40), clickmode='event+select')
fig_upper.update_xaxes(range=[-3.0, 3.0])
fig_upper.update_yaxes(range=[y_min, y_max])

# --- CAPTURE THE LIVE GRAPH CLICK SELECTION ---
# Streamlit's selection tracking triggers when user clicks a click-target dot marker
selected_points = st.plotly_chart(fig_upper, use_container_width=True, on_select="rerun")

if selected_points and "selection" in selected_points and "points" in selected_points["selection"]:
    points = selected_points["selection"]["points"]
    if len(points) > 0:
        new_clicked_x = round(points[0]["x"], 1)
        if new_clicked_x != st.session_state.selected_x:
            st.session_state.selected_x = new_clicked_x
            st.rerun()

# --- LOWER PLOT CONFIGURATION (Derivative Canvas) ---
fig_lower = go.Figure()

# Background guide toggle line indicator
line_color = '#EBF0F5' if show_answer else 'rgba(0,0,0,0)'
fig_lower.add_trace(go.Scatter(x=x_base, y=dy_base, mode='lines', line=dict(color=line_color, width=2.5), hoverinfo='skip'))

# Draw the student's plotted history dots
fig_lower.add_trace(go.Scatter(x=st.session_state.history_x, y=st.session_state.history_y_guess, mode='markers', marker=dict(color='#007BFF', size=12), hoverinfo='skip'))

fig_lower.update_layout(title="Derivative Plotting Area: f'(x) [Aligned vertically with plot above]", xaxis_title="x", yaxis_title="Slope Value (y')", showlegend=False, height=340, margin=dict(t=40, b=40, l=60, r=40))
fig_lower.update_xaxes(range=[-3.0, 3.0])
fig_lower.update_yaxes(range=[dy_min, dy_max])
st.plotly_chart(fig_lower, use_container_width=True)
