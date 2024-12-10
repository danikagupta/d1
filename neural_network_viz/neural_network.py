import numpy as np

class NeuralNetwork:
    def __init__(self):
        # Initialize weights and biases
        self.weights1 = np.random.randn(2, 3)  # 2 input nodes to 3 hidden nodes
        self.weights2 = np.random.randn(3, 1)  # 3 hidden nodes to 1 output node
        self.bias1 = np.random.randn(3)  # bias for hidden layer
        self.bias2 = np.random.randn(1)  # bias for output layer

        # For storing intermediate values
        self.layer1 = None
        self.output = None
        self.error = None
        self.loss = None
        self.previous_weights1 = None
        self.previous_weights2 = None
        self.previous_bias1 = None
        self.previous_bias2 = None

        # For storing training history
        self.loss_history = []
        self.epoch_losses = {'initial': [], 'final': []}

        self.weight_changes = {
            'weights1': None,
            'weights2': None,
            'bias1': None,
            'bias2': None
        }
        self.gradients = {
            'weights1': None,
            'weights2': None,
            'bias1': None,
            'bias2': None
        }

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def calculate_loss(self, y_true, y_pred):
        return np.mean(np.square(y_true - y_pred))

    def store_previous_parameters(self):
        self.previous_weights1 = self.weights1.copy()
        self.previous_weights2 = self.weights2.copy()
        self.previous_bias1 = self.bias1.copy()
        self.previous_bias2 = self.bias2.copy()

    def calculate_parameter_changes(self):
        self.weight_changes['weights1'] = self.weights1 - self.previous_weights1
        self.weight_changes['weights2'] = self.weights2 - self.previous_weights2
        self.weight_changes['bias1'] = self.bias1 - self.previous_bias1
        self.weight_changes['bias2'] = self.bias2 - self.previous_bias2

    def forward(self, X):
        # Forward propagation
        self.layer1 = self.sigmoid(np.dot(X, self.weights1) + self.bias1)
        self.output = self.sigmoid(np.dot(self.layer1, self.weights2) + self.bias2)
        return self.output

    def backward(self, X, y, learning_rate=0.1):
        # Store previous parameters
        self.store_previous_parameters()

        # Calculate initial loss
        initial_loss = self.calculate_loss(y, self.output)
        self.epoch_losses['initial'].append(initial_loss)

        # Backward propagation
        self.error = y - self.output
        d_output = self.error * self.sigmoid_derivative(self.output)

        self.gradients['weights2'] = np.dot(self.layer1.T, d_output)
        self.gradients['bias2'] = np.sum(d_output, axis=0)

        d_hidden = np.dot(d_output, self.weights2.T) * self.sigmoid_derivative(self.layer1)
        self.gradients['weights1'] = np.dot(X.T, d_hidden)
        self.gradients['bias1'] = np.sum(d_hidden, axis=0)

        # Update weights and biases
        self.weights1 += learning_rate * self.gradients['weights1']
        self.weights2 += learning_rate * self.gradients['weights2']
        self.bias1 += learning_rate * self.gradients['bias1']
        self.bias2 += learning_rate * self.gradients['bias2']

        # Calculate parameter changes
        self.calculate_parameter_changes()

        # Calculate final loss
        final_loss = self.calculate_loss(y, self.forward(X))
        self.epoch_losses['final'].append(final_loss)
        self.loss_history.append(final_loss)

        return initial_loss, final_loss, self.error

    def reset_history(self):
        """Reset all training history"""
        self.loss_history = []
        self.epoch_losses = {'initial': [], 'final': []}
