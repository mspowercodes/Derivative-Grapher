import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(page_title="Derivative Slope Grapher", layout="wide")

st.title("🎲 Interactive Derivative Slope Grapher")
st.write("Click a point on the upper curve, adjust the slider to tilt your tangent line, and plot your guess to map out the derivative function!")

# --- INITIALIZE SESSION STATE (Persistent memory across runs) ---
if 'func_type' not in st.session_state:
    st.session_state.func_type = 'poly'
    st.session_state.coeffs = [0.4, 0.0, -1.5]
    st.session_state.func_str = "f(x) = 0.4x³ - 1.5x"
    st.session_state.history_x = []
    st.session_state.history_y_guess = []
    st.session_state.selected_x = 0.0

# --- MATH HELPER FUNCTIONS ---
def evaluate_func(func_type, coeffs, x):
    if func_type == 'poly':
        return coeffs[0]*x**3 + coeffs[1]*x**2 + coeffs[2]*x
    elif func_type == 'rational':
        return (coeffs[0]*x) / (x**2 + coeffs[1]) + coeffs[2]
    return 0

def evaluate_deriv(func_type, coeffs, x):
    if func_type == 'poly':
        return 3*coeffs[0]*x**2 + 2*coeffs[1]*x + coeffs[2]
    elif func_type == 'rational':
        num = coeffs[0] * (coeffs[1] - x**2)
        den = (x**2 + coeffs[1])**2
        return num / den
    return 0

def generate_new_function():
    if random.choice(['poly', 'rational']) == 'poly':
        st.session_state.func_type = 'poly'
        a = round(random.choice([-0.4, -0.2, 0.2, 0.4]), 2)
        b = round(random.choice([-0.5, 0.0, 0.5]), 2)
        c = round(random.uniform(-2.0, 1.0), 2)
        st.session_state.coeffs = [a, b, c]
        b_str = f" + {b}x²" if b != 0 else ""
        c_str = f" + {c}x" if c >= 0 else f" - {abs(c)}x"
        st.session_state.func_str = f"f(x) = {a}x³{b_str}{c_str}"
    else:
        st.session_state.func_type = 'rational'
        a = round(random.uniform(2.0, 5.0) * random.choice([-1, 1]), 1)
        b = round(random.uniform(1.0, 3.0), 1)
        c = round(random.uniform(-1.0, 1.0), 1)
        st.session_state.coeffs = [a, b, c]
        st.session_state.func_str = f"f(x) = ({a}x) / (x² + {b}) + {c}"
    
    st.session_state.history_x = []
    st.session_state.history_y_guess = []
    st.session_state.selected_x = 0.0

# --- APP LAYOUT: SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ App Controls")
    
    if st.button("🎲 Generate Random Function", use_container_width=True):
        generate_new_function()
        st.rerun()
        
    st.info(f"**Current:**\n{st.session_state.func_str}")
    st.markdown("---")
    
    # Target X coordinate selection using a slider
    st.session_state.selected_x = st.slider("1. Pick an X Coordinate to analyze:", 
                                            min_value=-2.5, max_value=2.5, 
                                            value=float(st.session_state.selected_x), step=0.1)
    
    # Interactive Tangent Slope Slider
    input_slope = st.slider("2. Adjust Tangent Slope Estimate:", 
                            min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
    
    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Plot My Slope", type="primary", use_container_width=True):
            st.session_state.history_x.append(st.session_state.selected_x)
            st.session_state.history_y_guess.append(input_slope)
            
            # Instant feedback calculation
            actual = evaluate_deriv(st.session_state.func_type, st.session_state.coeffs, st.session_state.selected_x)
            if abs(input_slope - actual) < 0.3:
                st.success(f"🎯 Great! True slope: {actual:.1f}")
            else:
                st.warning(f"Plotted! True slope: {actual:.1f}")
                
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history_x = []
            st.session_state.history_y_guess = []
            st.rerun()
            
    st.markdown("---")
    show_answer = st.checkbox("Show True Derivative Curve", value=False)

# --- CALCULATE PLOT DATA ---
x_vals = np.linspace(-3.0, 3.0, 200)
y_vals = evaluate_func(st.session_state.func_type, st.session_state.coeffs, x_vals)
dy_vals = evaluate_deriv(st.session_state.func_type, st.session_state.coeffs, x_vals)

# Setup viewport layout padding
y_min, y_max = np.min(y_vals) - 1.0, np.max(y_vals) + 1.0
dy_min, dy_max = np.min(dy_vals) - 1.0, np.max(dy_vals) + 1.0

# --- MAIN PAGE: TWIN PLOT RENDERING ---
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    # --- UPPER GRAPH (Function & Tangent) ---
    fig_upper = go.Figure()
    fig_upper.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='#17A2B8', width=3)))
    
    # Calculate live moving tangent line segments
    sel_x = st.session_state.selected_x
    sel_y = evaluate_func(st.session_state.func_type, st.session_state.coeffs, sel_x)
    tangent_x = np.linspace(sel_x - 0.6, sel_x + 0.6, 10)
    tangent_y = input_slope * (tangent_x - sel_x) + sel_y
    
    fig_upper.add_trace(go.Scatter(x=tangent_x, y=tangent_y, mode='lines', name='Tangent Line Preview', line=dict(color='#DC3545', width=3, dash='dash')))
    fig_upper.add_trace(go.Scatter(x=[sel_x], y=[sel_y], mode='markers', name='Selected Point', marker=dict(color='#DC3545', size=11)))
    
    fig_upper.update_layout(title="Function View Window: f(x)", xaxis_title="x", yaxis_title="y", showlegend=False, height=400)
    fig_upper.update_xaxes(range=[-3.0, 3.0])
    fig_upper.update_yaxes(range=[y_min, y_max])
    st.plotly_chart(fig_upper, use_container_width=True)

with graph_col2:
    # --- LOWER GRAPH (Derivative Canvas) ---
    fig_lower = go.Figure()
    
    # Conditionally toggle background helper guide line
    line_color = '#EBF0F5' if show_answer else 'rgba(0,0,0,0)'
    fig_lower.add_trace(go.Scatter(x=x_vals, y=dy_vals, mode='lines', name="Actual f'(x)", line=dict(color=line_color, width=2.5)))
    
    # Draw submitted student data points
    fig_lower.add_trace(go.Scatter(x=st.session_state.history_x, y=st.session_state.history_y_guess, mode='markers', name='Your Slopes', marker=dict(color='#007BFF', size=12)))
    
    fig_lower.update_layout(title="Derivative Plotting Area: f'(x)", xaxis_title="x", yaxis_title="Slope Value (y')", showlegend=False, height=400)
    fig_lower.update_xaxes(range=[-3.0, 3.0])
    fig_lower.update_yaxes(range=[dy_min, dy_max])
    st.plotly_chart(fig_lower, use_container_width=True)
