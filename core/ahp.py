# core/ahp.py
"""AHP (Analytic Hierarchy Process) algorithms for criteria weighting."""

import numpy as np
from typing import Dict

RI_TABLE: Dict[int, float] = {
    1: 0.00, 2: 0.00, 3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35,
    8: 1.40, 9: 1.45, 10: 1.49, 11: 1.52, 12: 1.54, 13: 1.56,
}


def preferences_to_matrix(answers, mode: str) -> np.ndarray:
    """Convert user preferences to reciprocal comparison matrix.
    
    Args:
        answers: List/array of preference values
        mode: 'comparison' (pairwise Saaty 1-9) or 'ranking' (ordinal ranks)
        
    Returns:
        Reciprocal matrix (n x n)
        
    Raises:
        ValueError: If mode is invalid
    """
    mode = str(mode).lower()

    if mode == "comparison":
        k = len(answers)
        n = int((1 + np.sqrt(1 + 8 * k)) / 2)
        matrix = np.ones((n, n))
        idx = 0
        for i in range(n):
            for j in range(i + 1, n):
                val = float(answers[idx])
                matrix[i, j] = val
                matrix[j, i] = 1.0 / val
                idx += 1
        return matrix

    if mode == "ranking":
        ranking = np.asarray(answers, dtype=float)
        n = len(ranking)
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                if ranking[i] == ranking[j]:
                    val = 1.0
                else:
                    d = int(max(ranking[i], ranking[j]) / min(ranking[i], ranking[j]))
                    d = min(d, 9)
                    val = d if ranking[i] < ranking[j] else 1.0 / d
                matrix[i, j] = val
                matrix[j, i] = 1.0 / val
        return matrix

    raise ValueError("mode must be either 'comparison' or 'ranking'")


def compute_cr(A: np.ndarray) -> float:
    """Compute Consistency Ratio for AHP matrix.
    
    Args:
        A: Reciprocal comparison matrix
        
    Returns:
        Consistency Ratio (CR < 0.10 is acceptable)
    """
    vals, _ = np.linalg.eig(A)
    lam_max = max(vals.real)
    n = A.shape[0]
    CI = float((lam_max - n) / (n - 1)) if n > 1 else 0.0
    RI = RI_TABLE.get(n, 1.35)
    CR = float(CI / RI) if RI else 0.0
    return CR


def project_to_consistent(A: np.ndarray) -> np.ndarray:
    """Project inconsistent matrix to nearest consistent matrix.
    
    Uses logarithmic projection method from Gaceta R. Soc. Mat. Esp.
    
    Args:
        A: Reciprocal matrix
        
    Returns:
        Consistent reciprocal matrix
    """
    n = A.shape[0]
    M = np.log(A)
    ones = np.ones((n, n))
    M1 = M @ ones
    P = (1.0 / n) * (M1 - M1.T)
    B = np.exp(P)
    B = (B + 1.0 / B.T) / 2.0
    np.fill_diagonal(B, 1.0)
    return B


def compute_weights(A: np.ndarray) -> np.ndarray:
    """Compute priority weights from comparison matrix.
    
    Uses principal eigenvector method.
    
    Args:
        A: Reciprocal comparison matrix
        
    Returns:
        Normalized weight vector (sums to 1)
    """
    vals, vecs = np.linalg.eig(A)
    w = np.abs(vecs[:, np.argmax(vals.real)])
    return w / w.sum()


def preferences_to_weights(answers: np.ndarray, mode: str) -> np.ndarray:
    """Complete AHP pipeline: preferences → matrix → weights.
    
    Automatically projects to consistent matrix if CR > 0.10.
    Handles zero values by excluding them from AHP computation.
    
    Args:
        answers: User preference values (can include 0 for "no importance")
        mode: 'comparison' or 'ranking'
        
    Returns:
        Normalized weight vector (criteria with 0 input get 0 weight)
    """
    answers = np.asarray(answers, dtype=float)
    n = len(answers)
    
    # Identify non-zero criteria
    nonzero_mask = answers > 0
    nonzero_indices = np.where(nonzero_mask)[0]
    
    # Handle edge cases
    if len(nonzero_indices) == 0:
        # All zeros → equal weights
        return np.ones(n) / n
    
    if len(nonzero_indices) == 1:
        # Only one non-zero → give it full weight
        weights = np.zeros(n)
        weights[nonzero_indices[0]] = 1.0
        return weights
    
    # Extract non-zero answers and compute their weights
    nonzero_answers = answers[nonzero_mask]
    A = preferences_to_matrix(nonzero_answers, mode)
    A = A if compute_cr(A) < 0.1 else project_to_consistent(A)
    nonzero_weights = compute_weights(A)
    
    # Reconstruct full weight vector
    weights = np.zeros(n)
    weights[nonzero_indices] = nonzero_weights
    
    return weights
