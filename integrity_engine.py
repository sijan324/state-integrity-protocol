import numpy as np

def measure_state_decay(original_vector, current_vector):
    """
    State Integrity Protocol (SIP) - Core Metric
    Calculates the fidelity loss between initial intent and agent output.
    """
    dot_product = np.dot(original_vector, current_vector)
    norm_a = np.linalg.norm(original_vector)
    norm_b = np.linalg.norm(current_vector)
    
    # Cosine Similarity
    fidelity = dot_product / (norm_a * norm_b)
    
    # State Decay Score (0 = Perfect Integrity, 1 = Total Decay)
    decay_score = 1 - fidelity
    return decay_score

# Example Threshold for Enterprise AI
THRESHOLD = 0.15

def audit_pipeline(steps):
    for i, score in enumerate(steps):
        if score > THRESHOLD:
            print(f"CRITICAL FAILURE at Step {i}: State Decay detected at {score:.4f}")
        else:
            print(f"Step {i}: Fidelity passing at {1-score:.4f}")

# Sample Audit Data (Simulating a 5-step agent chain)
mock_decay_profile = [0.02, 0.05, 0.09, 0.16, 0.22]
audit_pipeline(mock_decay_profile)
