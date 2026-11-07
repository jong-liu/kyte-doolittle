"""
Kyte–Doolittle Hydropathy Scale Calculator

Reference:
  Kyte J., Doolittle R.F.
  "A simple method for displaying the hydropathic character of a protein"
  J. Mol. Biol. 157:105-132 (1982)

Hydropathy values for 20 standard amino acids (from the paper).
"""

from typing import List, Tuple
import math


# Kyte-Doolittle hydropathy scale values (standard 20 amino acids)
KYTE_DOOLITTLE_SCALE = {
    'A': 1.8,   # Alanine
    'R': -4.5,  # Arginine
    'N': -3.5,  # Asparagine
    'D': -3.5,  # Aspartic acid
    'C': 2.5,   # Cysteine
    'Q': -3.5,  # Glutamine
    'E': -3.5,  # Glutamic acid
    'G': -0.4,  # Glycine
    'H': -3.2,  # Histidine
    'I': 4.5,   # Isoleucine
    'L': 3.8,   # Leucine
    'K': -3.9,  # Lysine
    'M': 1.9,   # Methionine
    'F': 2.8,   # Phenylalanine
    'P': -1.6,  # Proline
    'S': -0.8,  # Serine
    'T': -0.7,  # Threonine
    'W': -0.9,  # Tryptophan
    'Y': -1.3,  # Tyrosine
    'V': 4.2,   # Valine
}


def validate_sequence(sequence: str) -> str:
    """
    Validate and normalize protein sequence.

    Args:
        sequence: Protein sequence (may contain whitespace, lowercase)

    Returns:
        Normalized uppercase sequence

    Raises:
        ValueError: If sequence contains invalid characters
    """
    seq = sequence.upper().replace(" ", "").replace("\n", "")
    invalid_chars = set(seq) - set(KYTE_DOOLITTLE_SCALE.keys()) - {'X', 'U', 'B', 'Z', 'J', 'O'}
    if invalid_chars:
        raise ValueError(f"Invalid amino acid characters: {invalid_chars}")
    return seq


def calculate_hydropathy_window(sequence: str, window_size: int = 9,
                               edge_weight: float = 100, weight_model: str = "linear") -> float:
    """
    Calculate hydropathy score for a sequence window using weighted average.

    Args:
        sequence: Amino acid sequence (typically window_size characters)
        window_size: Original window size (for edge weight calculation)
        edge_weight: Relative weight of edges vs center (0-100, default 100)
        weight_model: "linear" or "exponential" (if edge_weight < 100)

    Returns:
        Weighted average hydropathy score
    """
    if len(sequence) != window_size:
        raise ValueError(f"Sequence length {len(sequence)} != window_size {window_size}")

    if window_size < 3 or window_size % 2 == 0:
        raise ValueError("window_size must be odd and >= 3")

    if not 0 <= edge_weight <= 100:
        raise ValueError("edge_weight must be 0-100")

    scores = [KYTE_DOOLITTLE_SCALE.get(aa, 0) for aa in sequence]

    if edge_weight == 100:
        # Uniform weight
        return sum(scores) / len(scores)

    # Calculate position weights based on edge_weight and model
    n = len(scores)
    center_idx = n // 2
    weights = []

    for i in range(n):
        dist_from_center = abs(i - center_idx) / center_idx

        if weight_model == "linear":
            w = 100 - (100 - edge_weight) * dist_from_center
        elif weight_model == "exponential":
            w = 100 - (100 - edge_weight) * (dist_from_center ** 2)
        else:
            raise ValueError("weight_model must be 'linear' or 'exponential'")

        weights.append(w)

    # Normalize weights to sum to 1
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    return sum(s * w for s, w in zip(scores, weights))


def calculate_hydropathy(sequence: str, window_size: int = 9, edge_weight: float = 100,
                        weight_model: str = "linear", normalize: bool = False) -> Tuple[List[float], dict]:
    """
    Calculate hydropathy scores for each position in a protein sequence.

    Args:
        sequence: Protein sequence (FASTA or raw string)
        window_size: Sliding window size, must be odd (default 9)
        edge_weight: Relative weight of window edges (0-100, default 100)
        weight_model: "linear" or "exponential" (if edge_weight < 100)
        normalize: Normalize scores to 0-1 range (default False)

    Returns:
        Tuple of:
          - List of hydropathy scores (position-by-position)
          - Dict with metadata (length, min, max, mean, std)

    Raises:
        ValueError: If sequence is invalid or parameters are out of range
    """
    seq = validate_sequence(sequence)

    if len(seq) < window_size:
        raise ValueError(f"Sequence length {len(seq)} < window_size {window_size}")

    # Calculate score for each position (sliding window centered at position)
    scores = []
    half_window = window_size // 2

    for i in range(len(seq)):
        start = max(0, i - half_window)
        end = min(len(seq), i + half_window + 1)
        window = seq[start:end]

        # Pad window if at edges
        if len(window) < window_size:
            if start == 0:
                # Pad left
                window = 'X' * (window_size - len(window)) + window
            else:
                # Pad right
                window = window + 'X' * (window_size - len(window))

        score = calculate_hydropathy_window(window, window_size, edge_weight, weight_model)
        scores.append(score)

    # Calculate statistics
    if normalize:
        if len(scores) > 0:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                scores = [(s - min_score) / (max_score - min_score) for s in scores]
            else:
                scores = [0.5] * len(scores)

    metadata = {
        "sequence_length": len(seq),
        "window_size": window_size,
        "edge_weight": edge_weight,
        "weight_model": weight_model,
        "normalize": normalize,
        "min": min(scores) if scores else 0,
        "max": max(scores) if scores else 0,
        "mean": sum(scores) / len(scores) if scores else 0,
    }

    if len(scores) > 1:
        variance = sum((s - metadata["mean"]) ** 2 for s in scores) / len(scores)
        metadata["std"] = math.sqrt(variance)
    else:
        metadata["std"] = 0

    return scores, metadata


if __name__ == "__main__":
    # Example: Test with a small peptide
    test_seq = "MVLSPADKTNVIRAAQNCYSTEIN"
    scores, meta = calculate_hydropathy(test_seq)

    print(f"Sequence: {test_seq}")
    print(f"Length: {meta['sequence_length']}")
    print(f"Window size: {meta['window_size']}")
    print(f"Statistics: min={meta['min']:.2f}, max={meta['max']:.2f}, mean={meta['mean']:.2f}, std={meta['std']:.2f}")
    print(f"Scores: {[f'{s:.2f}' for s in scores[:10]]}...")
