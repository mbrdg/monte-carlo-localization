import numpy as np

def systematic_resampling(weights):
    num_particles = len(weights)
    cumulative_weights = np.cumsum(weights)
    step = 1.0 / num_particles
    positions = np.random.uniform(0, step, size=num_particles)
    indices = np.zeros(num_particles, dtype=int)

    for i in range(num_particles):
        indices[i] = np.searchsorted(cumulative_weights, positions[i])

    return indices

# Example usage
# Assuming 'scores' represent the weights of particles
scores = np.array([0.2, 0.1, 0.4, 0.05, 0.15, 0.1])
indices = systematic_resampling(scores)

print(indices)
