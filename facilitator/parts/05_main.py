def main():
    x, target, x_test, target_test = load_data()
    model = NeuralNetwork(784, 128, 10)
    learning_rate = 0.1
    epochs = 10

    for epoch in range(1, epochs + 1):
        # 1. FORWARD PASS: make a guess.
        prediction = model.forward(x)

        # 2. LOSS: measure how wrong the guess was.
        loss = torch.nn.functional.cross_entropy(prediction, target)

        # 3. BACKPROPAGATION: find every weight's gradient.
        loss.backward()

        # 4. UPDATE WEIGHTS: take one small step downhill.
        with torch.no_grad():
            for parameter in model.parameters():
                parameter -= learning_rate * parameter.grad

        # 5. CLEAR the gradients, then repeat.
        for parameter in model.parameters():
            parameter.grad.zero_()

        if epoch == 1 or epoch % 5 == 0 or epoch == epochs:
            report(epoch, loss, model, x_test, target_test)


if __name__ == "__main__":
    main()
