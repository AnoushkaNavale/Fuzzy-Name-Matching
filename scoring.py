"""
Scoring Module
Implements multiple similarity metrics using RapidFuzz
"""

from rapidfuzz import fuzz, distance
from typing import List, Dict, Tuple


class SimilarityScorer:
    """Calculate various similarity scores between two strings"""
    
    def __init__(self):
        # Default weights for hybrid scoring
        self.weights = {
            'levenshtein': 0.3,
            'token_sort': 0.3,
            'token_set': 0.2,
            'jaccard': 0.2
        }
    
    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """
        Normalized Levenshtein distance (0-100)
        Measures character-level edit distance
        """
        return fuzz.ratio(s1, s2)
    
    def token_sort_similarity(self, s1: str, s2: str) -> float:
        """
        Token sort ratio (0-100)
        Handles word order differences
        Example: "John Smith" vs "Smith John" = 100
        """
        return fuzz.token_sort_ratio(s1, s2)
    
    def token_set_similarity(self, s1: str, s2: str) -> float:
        """
        Token set ratio (0-100)
        Handles partial matches and extra words
        Example: "John Smith Jr" vs "John Smith" = high score
        """
        return fuzz.token_set_ratio(s1, s2)
    
    def jaccard_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Jaccard similarity (0-100)
        Measures overlap between token sets
        """
        if not tokens1 or not tokens2:
            return 0.0
        
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return (intersection / union) * 100
    
    def partial_ratio_similarity(self, s1: str, s2: str) -> float:
        """
        Partial ratio (0-100)
        Good for substring matches
        Example: "Microsoft" vs "Microsoft Corporation" = high score
        """
        return fuzz.partial_ratio(s1, s2)
    
    def calculate_all_scores(
        self, 
        text1: str, 
        text2: str,
        tokens1: List[str],
        tokens2: List[str]
    ) -> Dict[str, float]:
        """
        Calculate all similarity scores
        
        Returns:
            Dictionary with all individual scores
        """
        scores = {
            'levenshtein': self.levenshtein_similarity(text1, text2),
            'token_sort': self.token_sort_similarity(text1, text2),
            'token_set': self.token_set_similarity(text1, text2),
            'jaccard': self.jaccard_similarity(tokens1, tokens2),
            'partial': self.partial_ratio_similarity(text1, text2),
        }
        
        return scores
    
    def hybrid_score(
        self,
        text1: str,
        text2: str,
        tokens1: List[str],
        tokens2: List[str],
        weights: Dict[str, float] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate weighted hybrid similarity score
        
        Args:
            text1, text2: Normalized text strings
            tokens1, tokens2: Token lists
            weights: Custom weights dict (optional)
        
        Returns:
            - Final hybrid score (0-100)
            - Dictionary with all component scores
        """
        if weights is None:
            weights = self.weights
        
        # Calculate all scores
        scores = self.calculate_all_scores(text1, text2, tokens1, tokens2)
        
        # Calculate weighted average
        final_score = (
            weights.get('levenshtein', 0) * scores['levenshtein'] +
            weights.get('token_sort', 0) * scores['token_sort'] +
            weights.get('token_set', 0) * scores['token_set'] +
            weights.get('jaccard', 0) * scores['jaccard']
        )
        
        scores['hybrid'] = final_score
        
        return final_score, scores
    
    def set_weights(self, weights: Dict[str, float]):
        """Update scoring weights"""
        # Validate weights sum to 1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        self.weights = weights


def classify_match(score: float, strong_threshold: float = 85, weak_threshold: float = 70) -> str:
    """
    Classify match quality based on score
    
    Args:
        score: Similarity score (0-100)
        strong_threshold: Threshold for strong match
        weak_threshold: Threshold for possible match
    
    Returns:
        'strong_match', 'possible_match', or 'no_match'
    """
    if score >= strong_threshold:
        return 'strong_match'
    elif score >= weak_threshold:
        return 'possible_match'
    else:
        return 'no_match'


def explain_match(scores: Dict[str, float], threshold: float = 70) -> str:
    """
    Generate human-readable explanation of why records matched
    
    Args:
        scores: Dictionary of all similarity scores
        threshold: Minimum score to be considered significant
    
    Returns:
        Explanation string
    """
    explanations = []
    
    # Check each component
    if scores.get('levenshtein', 0) >= threshold:
        explanations.append(f"Similar character sequences (Levenshtein: {scores['levenshtein']:.1f})")
    
    if scores.get('token_sort', 0) >= threshold:
        explanations.append(f"Same words in different order (Token Sort: {scores['token_sort']:.1f})")
    
    if scores.get('token_set', 0) >= threshold:
        explanations.append(f"Shared word set (Token Set: {scores['token_set']:.1f})")
    
    if scores.get('jaccard', 0) >= threshold:
        explanations.append(f"High token overlap (Jaccard: {scores['jaccard']:.1f})")
    
    if scores.get('partial', 0) >= 90:
        explanations.append(f"One name contains the other (Partial: {scores['partial']:.1f})")
    
    if not explanations:
        return f"Overall similarity: {scores.get('hybrid', 0):.1f}"
    
    return " | ".join(explanations)


def get_top_contributing_scores(scores: Dict[str, float], top_n: int = 3) -> List[Tuple[str, float]]:
    """
    Get the top N contributing similarity scores
    
    Args:
        scores: Dictionary of scores
        top_n: Number of top scores to return
    
    Returns:
        List of (score_name, value) tuples
    """
    # Exclude hybrid and partial from ranking
    scorable = {k: v for k, v in scores.items() if k not in ['hybrid', 'partial']}
    
    # Sort by value
    sorted_scores = sorted(scorable.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_scores[:top_n]


# Optimized batch scoring for large datasets
def score_pairs_batch(
    pairs: List[Tuple[str, str, List[str], List[str]]],
    scorer: SimilarityScorer = None
) -> List[Dict]:
    """
    Score multiple pairs efficiently
    
    Args:
        pairs: List of (text1, text2, tokens1, tokens2) tuples
        scorer: SimilarityScorer instance
    
    Returns:
        List of score dictionaries
    """
    if scorer is None:
        scorer = SimilarityScorer()
    
    results = []
    
    for text1, text2, tokens1, tokens2 in pairs:
        final_score, scores = scorer.hybrid_score(text1, text2, tokens1, tokens2)
        results.append(scores)
    
    return results
