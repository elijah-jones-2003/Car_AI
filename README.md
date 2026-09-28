# Car AI: A Level Computer Science Project

> **Archived project.** I wrote this for my A Level Computer Science coursework around 2020 and uploaded it here later, after finishing, as a record of my progress. It isn't maintained, and I've kept the code as I submitted it.

## What it is

A Pygame simulation in which cars learn to drive around a race track. Each car is controlled by a small neural network I wrote from scratch with NumPy. There's no backpropagation: the networks improve through a simple genetic algorithm, one generation at a time.

## How it works

- **Sensors:** each car casts 7 "radar" lines, spaced from -90° to +90°, and measures how far each one travels before it hits a wall (green pixels on the track image).
- **Network:** 7 inputs → two hidden layers of 8 neurons → 4 outputs (accelerate, brake, turn left, turn right). The hidden layers use a leaky ReLU. Each pair of outputs is normalised against each other and then thresholded to give on/off controls.
- **Fitness:** the distance a car travels before it crashes or the 10-second timer runs out.
- **Evolution:** after each generation of 10 cars, the 3 fittest carry over unchanged. The rest of the new generation is built by mixing weights and biases from those 3 at random, with a small chance of each value mutating.
- **Tracks:** Paradis, Star Circuit, Nascar, Monza, Silverstone and Monaco, chosen from a menu when the program starts.

## Running it

Requires Python 3, `pygame` and `numpy`.

```bash
pip install pygame numpy
cd carai
python "Car AI Code.py"
```

**Note:** the `images/` folder (the track and car images) isn't in this repository, so the program won't start without it. It loads its images from `images/` and `images/f1/`, relative to wherever it's run from.

Controls: press `K` or click **Kill** to end the current generation early, and `Esc` to quit.

## Looking back

This was one of my first larger programs, and it shows. Everything is in one file, the code relies on global state, there are no tests, and a few names don't quite match what they do (the `softmax` function, for example, isn't a true softmax). I've left it as it was so it gives an honest picture of where I started.

## Acknowledgements

The code for calculating the car's corners is adapted from a solution by NeuralNine, as the source comments note.
