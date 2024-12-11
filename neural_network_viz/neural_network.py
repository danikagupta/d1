import numpy as np

class NeuralNetwork:
    def __init__(self, weights_init=None):
        if weights_init is not None:
            self.weights1 = np.full((2, 3), weights_init)
            self.weights2 = np.full((3, 1), weights_init)
            self.bias1 = np.full(3, weights_init)
            self.bias2 = np.full(1, weights_init)
        else:
            self.weights1 = np.random.randn(2, 3)
            self.weights2 = np.random.randn(3, 1)
            self.bias1 = np.random.randn(3)
            self.bias2 = np.random.randn(1)

        self.loss_history = []
        self.weight_changes = {
            "weights1": None,
            "weights2": None,
            "bias1": None,
            "bias2": None,
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
        self.layer1 = self.sigmoid(np.dot(X, self.weights1) + self.bias1)
        self.output = self.sigmoid(np.dot(self.layer1, self.weights2) + self.bias2)
        return self.output

    def backward(self, X, y, learning_rate=0.1):
        # Store previous parameters
        self.store_previous_parameters()

        # Calculate initial loss
        initial_loss = self.calculate_loss(y, self.output)

        # Backward propagation
        self.error = y - self.output
        delta_output = self.error * self.sigmoid_derivative(self.output)

        delta_hidden = np.dot(delta_output, self.weights2.T) * self.sigmoid_derivative(self.layer1)

        # Update weights and biases
        self.weights2 += learning_rate * np.dot(self.layer1.T, delta_output)
        self.weights1 += learning_rate * np.dot(X.T, delta_hidden)
        self.bias2 += learning_rate * np.sum(delta_output, axis=0)
        self.bias1 += learning_rate * np.sum(delta_hidden, axis=0)

        # Calculate parameter changes
        self.calculate_parameter_changes()

        # Calculate final loss
        final_loss = self.calculate_loss(y, self.forward(X))
        self.loss_history.append(final_loss)

        return initial_loss, final_loss, self.error

    def reset_history(self):
        """Reset all training history"""
        self.loss_history = []
