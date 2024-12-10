import streamlit as st
import numpy as np
from neural_network import NeuralNetwork
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

st.set_page_config(page_title="Neural Network Training Visualization", layout="wide")
st.title("Neural Network Training Visualization")

# Initialize neural network
nn = NeuralNetwork()

def create_network_plot():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')
    return fig, ax

def draw_network(ax, nn, show_gradients=False):
    # Clear previous plot
    ax.clear()
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.5, 3.5)
    ax.axis('off')

    # Node positions
    input_pos = [(0, 0.5), (0, 2.5)]
    hidden_pos = [(1.5, i) for i in [0.5, 1.5, 2.5]]
    output_pos = [(3, 1.5)]

    # Draw nodes
    for i, pos in enumerate(input_pos):
        ax.add_patch(plt.Circle(pos, 0.2, color='lightblue'))
        ax.text(pos[0]-0.3, pos[1], f'Input {i+1}', fontsize=8)

    for i, pos in enumerate(hidden_pos):
        ax.add_patch(plt.Circle(pos, 0.2, color='lightgreen'))
        ax.text(pos[0]-0.1, pos[1]-0.3, f'b: {nn.bias1[i]:.2f}', fontsize=8)

    for pos in output_pos:
        ax.add_patch(plt.Circle(pos, 0.2, color='lightcoral'))
        if nn.error is not None:
            ax.text(3.3, 1.5, f'Error: {nn.error[0]:.4f}', fontsize=8)
            ax.text(pos[0]-0.1, pos[1]-0.3, f'b: {nn.bias2[0]:.2f}', fontsize=8)

    # Draw weights and gradients
    for i, input_p in enumerate(input_pos):
        for j, hidden_p in enumerate(hidden_pos):
            weight = nn.weights1[i, j]
            color = 'gray'
            if show_gradients and nn.gradients['weights1'] is not None:
                gradient = nn.gradients['weights1'][i, j]
                color = 'red' if gradient < 0 else 'green'
                alpha = min(abs(gradient), 1.0)
            else:
                alpha = abs(weight) / max(abs(nn.weights1.max()), 1)

            ax.plot([input_p[0], hidden_p[0]], [input_p[1], hidden_p[1]],
                   color=color, alpha=alpha)
            ax.text((input_p[0] + hidden_p[0])/2,
                   (input_p[1] + hidden_p[1])/2,
                   f'w: {weight:.2f}', fontsize=8)
            if show_gradients and nn.gradients['weights1'] is not None:
                ax.text((input_p[0] + hidden_p[0])/2,
                       (input_p[1] + hidden_p[1])/2 - 0.2,
                       f'∇: {nn.gradients["weights1"][i, j]:.2f}',
                       fontsize=8, color='red')

    for i, hidden_p in enumerate(hidden_pos):
        for j, output_p in enumerate(output_pos):
            weight = nn.weights2[i, j]
            color = 'gray'
            if show_gradients and nn.gradients['weights2'] is not None:
                gradient = nn.gradients['weights2'][i, j]
                color = 'red' if gradient < 0 else 'green'
                alpha = min(abs(gradient), 1.0)
            else:
                alpha = abs(weight) / max(abs(nn.weights2.max()), 1)

            ax.plot([hidden_p[0], output_p[0]], [hidden_p[1], output_p[1]],
                   color=color, alpha=alpha)
            ax.text((hidden_p[0] + output_p[0])/2,
                   (hidden_p[1] + output_p[1])/2,
                   f'w: {weight:.2f}', fontsize=8)
            if show_gradients and nn.gradients['weights2'] is not None:
                ax.text((hidden_p[0] + output_p[0])/2,
                       (hidden_p[1] + output_p[1])/2 - 0.2,
                       f'∇: {nn.gradients["weights2"][i, j]:.2f}',
                       fontsize=8, color='red')

# Training data (XOR function)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

if st.button("Train Network"):
    fig, ax = create_network_plot()
    plot_placeholder = st.empty()

    progress_bar = st.progress(0)
    epochs = 100

    for epoch in range(epochs):
        # Forward pass
        nn.forward(X)
        draw_network(ax, nn, show_gradients=False)
        plot_placeholder.pyplot(fig)
        time.sleep(0.2)

        # Backward pass with gradient visualization
        error = nn.backward(X, y)
        draw_network(ax, nn, show_gradients=True)
        plot_placeholder.pyplot(fig)
        time.sleep(0.2)

        # Update progress
        progress_bar.progress((epoch + 1) / epochs)

    plt.close(fig)
