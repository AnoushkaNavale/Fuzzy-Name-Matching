"""
Matching Module
Orchestrates the entity resolution process
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional
from preprocessing import prepare_for_matching
from blocking import create_optimal_blocks
from scoring import SimilarityScorer, classify_match, explain_match


class EntityResolver:
    """
    Main entity resolution engine
    Combines preprocessing, blocking, and scoring
    """
    
    def __init__(
        self,
        strong_threshold: float = 85,
        weak_threshold: float = 70,
        blocking_strategy: str = 'multi'
    ):
        """
        Initialize entity resolver
        
        Args:
            strong_threshold: Score threshold for strong matches (0-100)
            weak_threshold: Score threshold for possible matches (0-100)
            blocking_strategy: 'first_letter', 'token', 'soundex', 'multi'
        """
        self.strong_threshold = strong_threshold
        self.weak_threshold = weak_threshold
        self.blocking_strategy = blocking_strategy
        self.scorer = SimilarityScorer()
        
        # Results storage
        self.df_processed = None
        self.blocks = None
        self.candidate_pairs = None
        self.blocking_stats = None
        self.matches = []
    
    def process_dataframe(
        self,
        df: pd.DataFrame,
        name_column: str,
        name_type: str = 'general',
        additional_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Preprocess input dataframe
        
        Returns:
            Processed dataframe
        """
        self.df_processed = prepare_for_matching(
            df, name_column, name_type, additional_columns
        )
        return self.df_processed
    
    def create_blocks(self) -> Dict:
        """
        Create blocking structure
        
        Returns:
            Blocking statistics
        """
        if self.df_processed is None:
            raise ValueError("Must call process_dataframe first")
        
        self.blocks, self.candidate_pairs, self.blocking_stats = create_optimal_blocks(
            self.df_processed,
            strategy=self.blocking_strategy
        )
        
        return self.blocking_stats
    
    def find_matches(self, min_score: Optional[float] = None) -> pd.DataFrame:
        """
        Find all matches above threshold
        
        Args:
            min_score: Minimum score to include (uses weak_threshold if None)
        
        Returns:
            DataFrame with all matches
        """
        if self.candidate_pairs is None:
            raise ValueError("Must call create_blocks first")
        
        if min_score is None:
            min_score = self.weak_threshold
        
        matches = []
        
        # Score each candidate pair
        for id1, id2 in self.candidate_pairs:
            # Get records
            rec1 = self.df_processed[self.df_processed['record_id'] == id1].iloc[0]
            rec2 = self.df_processed[self.df_processed['record_id'] == id2].iloc[0]
            
            # Calculate similarity
            score, all_scores = self.scorer.hybrid_score(
                rec1['normalized'],
                rec2['normalized'],
                rec1['tokens'],
                rec2['tokens']
            )
            
            # Filter by minimum score
            if score >= min_score:
                match_type = classify_match(score, self.strong_threshold, self.weak_threshold)
                explanation = explain_match(all_scores, threshold=70)
                
                matches.append({
                    'record_id_1': id1,
                    'record_id_2': id2,
                    'name_1': rec1['original_name'],
                    'name_2': rec2['original_name'],
                    'similarity_score': score,
                    'match_type': match_type,
                    'explanation': explanation,
                    'levenshtein_score': all_scores['levenshtein'],
                    'token_sort_score': all_scores['token_sort'],
                    'token_set_score': all_scores['token_set'],
                    'jaccard_score': all_scores['jaccard'],
                })
        
        self.matches = matches
        
        # Create DataFrame
        if matches:
            df_matches = pd.DataFrame(matches)
            # Sort by similarity score
            df_matches = df_matches.sort_values('similarity_score', ascending=False)
            return df_matches
        else:
            return pd.DataFrame()
    
    def resolve_entities(
        self,
        df: pd.DataFrame,
        name_column: str,
        name_type: str = 'general',
        additional_columns: Optional[List[str]] = None,
        min_score: Optional[float] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete entity resolution pipeline
        
        Args:
            df: Input dataframe
            name_column: Column with names to match
            name_type: 'person', 'organization', or 'general'
            additional_columns: Extra columns to preserve
            min_score: Minimum similarity score
        
        Returns:
            - DataFrame with matches
            - Dictionary with statistics
        """
        # Step 1: Preprocess
        self.process_dataframe(df, name_column, name_type, additional_columns)
        
        # Step 2: Create blocks
        blocking_stats = self.create_blocks()
        
        # Step 3: Find matches
        df_matches = self.find_matches(min_score)
        
        # Step 4: Compile statistics
        stats = {
            'total_records': len(self.df_processed),
            'candidate_pairs': len(self.candidate_pairs),
            'total_matches': len(df_matches),
            'strong_matches': len(df_matches[df_matches['match_type'] == 'strong_match']) if len(df_matches) > 0 else 0,
            'possible_matches': len(df_matches[df_matches['match_type'] == 'possible_match']) if len(df_matches) > 0 else 0,
            'blocking_reduction': blocking_stats['reduction_ratio'],
            'avg_similarity': df_matches['similarity_score'].mean() if len(df_matches) > 0 else 0,
        }
        
        return df_matches, stats
    
    def get_matches_for_record(self, record_id: int, min_score: float = 70) -> pd.DataFrame:
        """
        Get all matches for a specific record
        
        Args:
            record_id: ID of the record
            min_score: Minimum similarity score
        
        Returns:
            DataFrame with matches for this record
        """
        if not self.matches:
            return pd.DataFrame()
        
        df_matches = pd.DataFrame(self.matches)
        
        # Filter for this record (can be in either position)
        mask = (
            ((df_matches['record_id_1'] == record_id) | 
             (df_matches['record_id_2'] == record_id)) &
            (df_matches['similarity_score'] >= min_score)
        )
        
        return df_matches[mask].sort_values('similarity_score', ascending=False)


def quick_match(
    df: pd.DataFrame,
    name_column: str,
    strong_threshold: float = 85,
    weak_threshold: float = 70,
    name_type: str = 'general'
) -> Tuple[pd.DataFrame, Dict]:
    """
    Quick entity resolution with default settings
    
    Args:
        df: Input dataframe
        name_column: Column with names
        strong_threshold: Strong match threshold
        weak_threshold: Possible match threshold
        name_type: Type of names
    
    Returns:
        - Matches dataframe
        - Statistics dictionary
    """
    resolver = EntityResolver(
        strong_threshold=strong_threshold,
        weak_threshold=weak_threshold,
        blocking_strategy='multi'
    )
    
    return resolver.resolve_entities(df, name_column, name_type)


def compare_two_names(
    name1: str,
    name2: str,
    return_details: bool = True
) -> Dict:
    """
    Compare two names directly
    
    Args:
        name1, name2: Names to compare
        return_details: Include detailed scores
    
    Returns:
        Dictionary with comparison results
    """
    from preprocessing import TextPreprocessor
    
    preprocessor = TextPreprocessor()
    scorer = SimilarityScorer()
    
    # Normalize
    norm1 = preprocessor.clean_text(name1)
    norm2 = preprocessor.clean_text(name2)
    
    tokens1 = preprocessor.get_tokens(norm1)
    tokens2 = preprocessor.get_tokens(norm2)
    
    # Calculate scores
    final_score, all_scores = scorer.hybrid_score(norm1, norm2, tokens1, tokens2)
    
    result = {
        'name_1': name1,
        'name_2': name2,
        'similarity_score': final_score,
        'match_type': classify_match(final_score),
    }
    
    if return_details:
        result['explanation'] = explain_match(all_scores)
        result['detailed_scores'] = all_scores
    
    return result
