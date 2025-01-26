import streamlit as st
import numpy as np
from neural_network import NeuralNetwork
import matplotlib.pyplot as plt
import time
import pandas as pd

st.set_page_config(page_title="Neural Network Training Visualization", layout="wide")
st.title("Neural Network Training Visualization")

# Initialize neural network in session state if not exists
if 'nn' not in st.session_state:
    st.session_state.nn = NeuralNetwork()
    st.session_state.epoch = 0
    st.session_state.training = False
    st.session_state.show_weight_changes = True  # Toggle for showing weight changes

# Function to parse input data
def parse_input_data(input_text, output_text):
    try:
        # Parse input data
        input_rows = [row.strip().split(',') for row in input_text.strip().split('\n')]
        X = np.array([[float(val) for val in row] for row in input_rows])

        # Parse output data
        output_rows = [row.strip() for row in output_text.strip().split('\n')]
        y = np.array([[float(val)] for val in output_rows])

        if X.shape[1] != 2:
            st.error("Input data must have exactly 2 features per row")
            return None, None
        if X.shape[0] != y.shape[0]:
            st.error("Number of input and output rows must match")
            return None, None

        return X, y
    except:
        st.error("Invalid data format. Please check your input.")
        return None, None

def create_network_plot():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')
    return fig, ax

def create_loss_plot():
    """Create a plot showing loss over epochs"""
    fig, ax = plt.subplots(figsize=(10, 4))

    # Plot only final loss for each epoch
    epochs = range(1, len(st.session_state.nn.loss_history) + 1)
    ax.plot(epochs, st.session_state.nn.loss_history,
            'b-', label='Loss', linewidth=2)

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title('Training Loss Over Time')
    ax.grid(True, alpha=0.3)
    ax.legend()

    return fig

def draw_network(ax, nn):
    ax.clear()
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')

    # Add legend at the top right
    legend_elements = [
        plt.Line2D([0], [0], color='black', label='Old Value'),
        plt.Line2D([0], [0], color='blue', label='New Value')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Node positions
    input_pos = [(0, 0.5), (0, 2.5)]
    hidden_pos = [(1.5, i) for i in [0.5, 1.5, 2.5]]
    output_pos = [(3, 1.5)]

    node_radius = 0.2  # Radius of the nodes

    # Draw nodes with labels
    for i, pos in enumerate(input_pos):
        ax.add_patch(plt.Circle(pos, node_radius, color='lightblue'))
        ax.text(pos[0] - 0.3, pos[1], f'Input {i+1}', fontsize=12)

    for i, pos in enumerate(hidden_pos):
        ax.add_patch(plt.Circle(pos, node_radius, color='lightgreen'))
        if hasattr(nn, 'previous_bias1'):
            ax.text(pos[0] - 0.1, pos[1] - 0.3, f'b: {nn.previous_bias1[i]:.2f}',
                   fontsize=12, color='black')
            ax.text(pos[0] - 0.1, pos[1] - 0.5, f'b: {nn.bias1[i]:.2f}',
                   fontsize=12, color='blue')
        else:
            ax.text(pos[0] - 0.1, pos[1] - 0.3, f'b: {nn.bias1[i]:.2f}', fontsize=12)

    for pos in output_pos:
        ax.add_patch(plt.Circle(pos, node_radius, color='lightcoral'))
        if hasattr(nn, 'previous_bias2'):
            ax.text(pos[0] - 0.1, pos[1] - 0.3, f'b: {nn.previous_bias2[0]:.2f}',
                   fontsize=12, color='black')
            ax.text(pos[0] - 0.1, pos[1] - 0.5, f'b: {nn.bias2[0]:.2f}',
                   fontsize=12, color='blue')
        else:
            ax.text(pos[0] - 0.1, pos[1] - 0.3, f'b: {nn.bias2[0]:.2f}', fontsize=12)

    # Function to calculate edge point
    def calculate_edge_point(p1, p2, radius):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = (dx**2 + dy**2)**0.5
        if dist == 0:
            return p1  # Avoid division by zero
        scale = radius / dist
        return (p1[0] + dx * scale, p1[1] + dy * scale)

    # Draw connections with weights and changes
    for i, input_p in enumerate(input_pos):
        for j, hidden_p in enumerate(hidden_pos):
            start = calculate_edge_point(input_p, hidden_p, node_radius)
            end = calculate_edge_point(hidden_p, input_p, node_radius)
            weight = nn.weights1[i, j]
            ax.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1],
                     color='gray', linewidth=2, head_width=0.05, head_length=0.1, length_includes_head=True)
            if hasattr(nn, 'previous_weights1'):
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2,
                        f'w: {nn.previous_weights1[i, j]:.2f}', fontsize=12, color='black')
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2 - 0.2,
                        f'w: {weight:.2f}', fontsize=12, color='blue')
            else:
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2,
                        f'w: {weight:.2f}', fontsize=12)

    for i, hidden_p in enumerate(hidden_pos):
        for j, output_p in enumerate(output_pos):
            start = calculate_edge_point(hidden_p, output_p, node_radius)
            end = calculate_edge_point(output_p, hidden_p, node_radius)
            weight = nn.weights2[i, j]
            ax.arrow(start[0], start[1], end[0]-start[0], end[1]-start[1],
                     color='gray', linewidth=2, head_width=0.05, head_length=0.1, length_includes_head=True)
            if hasattr(nn, 'previous_weights2'):
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2,
                        f'w: {nn.previous_weights2[i, j]:.2f}', fontsize=12, color='black')
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2 - 0.2,
                        f'w: {weight:.2f}', fontsize=12, color='blue')
            else:
                ax.text((start[0] + end[0]) / 2,
                        (start[1] + end[1]) / 2,
                        f'w: {weight:.2f}', fontsize=12)

def display_results_table(X, y_actual, y_pred):
    import pandas as pd
    import streamlit as st

    error = y_actual - y_pred
    results_df = pd.DataFrame({
        'Input X': [list(x) for x in X],
        'Y Predicted': y_pred.flatten(),
        'Y Actual': y_actual.flatten(),
        'Error': error.flatten()
    })

    st.subheader("Results")
    st.dataframe(results_df)


# Weight changes toggle
st.sidebar.header("Visualization Settings")
st.session_state.show_weight_changes = st.sidebar.checkbox("Show Weight Changes", value=False)

# Sidebar for data input
st.sidebar.header("Training Data Input")
st.sidebar.markdown("""
Input Format:
- Input data: Two comma-separated values per line
- Output data: One value per line
""")

# Example data
example_input = "0,0\n0,1\n1,0\n1,1"
example_output = "0\n2\n3\n5"  # y = 2 * x1 + 3 * x2

input_data = st.sidebar.text_area("Input Data (X)",
                                 value=example_input,
                                 height=150)
output_data = st.sidebar.text_area("Output Data (y)",
                                  value=example_output,
                                  height=150)

# Parse input data when provided
X, y = parse_input_data(input_data, output_data)


trainingCount=0

# Training controls
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Train One Epoch", disabled=X is None or y is None):
        st.session_state.training = True
        trainingCount=1


with col2:
    if st.button("Train Ten Epochs", disabled=X is None or y is None):
        st.session_state.training = True
        trainingCount=10

with col3:
    if st.button("Train 100 Epochs", disabled=X is None or y is None):
        st.session_state.training = True
        trainingCount=100

with col4:
    if st.button("Reset Network"):
        st.session_state.nn = NeuralNetwork(weights_init=0.0)  # Initialize weights to zero
        st.session_state.epoch = 0
        st.session_state.training = False

# Display current epoch
st.write(f"Current Epoch: {st.session_state.epoch}")

# Training visualization
if st.session_state.training and X is not None and y is not None:
    # Network visualization
    net_col, loss_col = st.columns([3, 2])

    with net_col:
        st.subheader("Network State")
        fig, ax = create_network_plot()

        # Forward pass
        final_loss = None
        for _ in range(trainingCount):
            output = st.session_state.nn.forward(X)
            initial_loss, final_loss, error = st.session_state.nn.backward(X, y)

        # Display metrics
        metrics_col1, metrics_col2 = st.columns(2)
        #with metrics_col1:
        #    st.write(f"Initial Loss: {initial_loss:.4f}")
        with metrics_col2:
            if final_loss is not None:
                st.write(f"Loss: {final_loss:.4f}")

        # Update visualization
        draw_network(ax, st.session_state.nn)
        st.pyplot(fig)
        plt.close(fig)

    with loss_col:
        st.subheader("Training Progress")
        loss_fig = create_loss_plot()
        st.pyplot(loss_fig)
        plt.close(loss_fig)
        # Show the results table
        y_pred = st.session_state.nn.forward(X)  # Predicted outputs
        display_results_table(X, y, y_pred)     # Call the results table function


    # Increment epoch
    st.session_state.epoch += trainingCount
