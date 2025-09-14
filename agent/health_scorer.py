import numpy as np

class HealthScorer:
    """Calculates the composite health score for a container."""
    def __init__(self, config):
        self.z_threshold = config['z_score_threshold']
        self.decay_steepness = config['decay_steepness']
        self.weights = config['metric_weights']

    def calculate_score(self, metrics, baseliner, container_id):
        composite_score = 0.0
        for metric_name, value in metrics.items():
            mean, std_dev = baseliner.get_baseline(container_id, metric_name)
            
            if std_dev < 1e-6: # Avoid division by zero
                z_score = 0
            else:
                z_score = abs(value - mean) / std_dev

            # Inverse sigmoid to map z-score to a metric health score (0-1)
            metric_score = 1 / (1 + np.exp(self.decay_steepness * (z_score - self.z_threshold)))
            
            composite_score += self.weights.get(metric_name, 0) * metric_score
        
        return composite_score