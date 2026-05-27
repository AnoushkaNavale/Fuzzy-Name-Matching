"""
Blocking Module
Reduces O(n²) comparisons by grouping similar records into blocks
"""

import pandas as pd
from typing import List, Tuple, Set
from collections import defaultdict


class BlockingStrategy:
    """Base class for blocking strategies"""
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """Create blocks from dataframe. Override in subclasses."""
        raise NotImplementedError


class FirstLetterBlocking(BlockingStrategy):
    """Block records by first letter of normalized name"""
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """
        Group records by first letter
        
        Args:
            df: DataFrame with 'normalized' column
        
        Returns:
            Dictionary: {block_key: [record_ids]}
        """
        blocks = defaultdict(list)
        
        for idx, row in df.iterrows():
            text = row['normalized']
            if text and len(text) > 0:
                key = text[0].lower()
                blocks[key].append(row['record_id'])
        
        return dict(blocks)


class FirstNCharsBlocking(BlockingStrategy):
    """Block records by first N characters"""
    
    def __init__(self, n: int = 3):
        self.n = n
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """Group records by first N characters"""
        blocks = defaultdict(list)
        
        for idx, row in df.iterrows():
            text = row['normalized']
            if text and len(text) >= self.n:
                key = text[:self.n].lower()
                blocks[key].append(row['record_id'])
        
        return dict(blocks)


class TokenBlocking(BlockingStrategy):
    """Block records by shared tokens (words)"""
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """
        Group records that share at least one token
        More flexible than character-based blocking
        """
        blocks = defaultdict(set)
        
        for idx, row in df.iterrows():
            tokens = row['tokens']
            record_id = row['record_id']
            
            # Add record to block for each token
            for token in tokens:
                if len(token) > 2:  # Skip very short tokens
                    blocks[token].add(record_id)
        
        # Convert sets to lists
        return {k: list(v) for k, v in blocks.items()}


class SoundexBlocking(BlockingStrategy):
    """Block records by Soundex phonetic code"""
    
    @staticmethod
    def soundex(name: str) -> str:
        """Generate Soundex code for blocking"""
        if not name:
            return ""
        
        name = name.upper()
        soundex = name[0]
        
        # Soundex digit mapping
        mapping = {
            'BFPV': '1', 'CGJKQSXZ': '2', 'DT': '3',
            'L': '4', 'MN': '5', 'R': '6'
        }
        
        for char in name[1:]:
            for group, digit in mapping.items():
                if char in group and (not soundex or soundex[-1] != digit):
                    soundex += digit
        
        return (soundex + '000')[:4]
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """Group records by Soundex code"""
        blocks = defaultdict(list)
        
        for idx, row in df.iterrows():
            # Use first word for Soundex
            tokens = row['tokens']
            if tokens:
                code = self.soundex(tokens[0])
                blocks[code].append(row['record_id'])
        
        return dict(blocks)


class MultiBlockingStrategy:
    """
    Combines multiple blocking strategies to improve recall
    A record pair is compared if they appear in ANY block together
    """
    
    def __init__(self, strategies: List[BlockingStrategy]):
        self.strategies = strategies
    
    def create_blocks(self, df: pd.DataFrame) -> dict:
        """Merge blocks from all strategies"""
        all_blocks = defaultdict(set)
        
        for i, strategy in enumerate(self.strategies):
            strategy_blocks = strategy.create_blocks(df)
            
            # Add strategy prefix to keys to avoid collision
            for key, record_ids in strategy_blocks.items():
                merged_key = f"strategy_{i}_{key}"
                all_blocks[merged_key].update(record_ids)
        
        return {k: list(v) for k, v in all_blocks.items()}


def generate_candidate_pairs(blocks: dict) -> Set[Tuple[int, int]]:
    """
    Generate candidate pairs from blocks
    
    Args:
        blocks: Dictionary of {block_key: [record_ids]}
    
    Returns:
        Set of (id1, id2) tuples where id1 < id2 (no duplicates)
    """
    candidate_pairs = set()
    
    for block_key, record_ids in blocks.items():
        # Generate all pairs within this block
        n = len(record_ids)
        for i in range(n):
            for j in range(i + 1, n):
                id1, id2 = record_ids[i], record_ids[j]
                # Always store smaller ID first to avoid duplicates
                pair = (min(id1, id2), max(id1, id2))
                candidate_pairs.add(pair)
    
    return candidate_pairs


def get_blocking_stats(df: pd.DataFrame, blocks: dict) -> dict:
    """Get statistics about blocking performance"""
    total_records = len(df)
    total_possible_pairs = (total_records * (total_records - 1)) // 2
    
    candidate_pairs = generate_candidate_pairs(blocks)
    num_candidate_pairs = len(candidate_pairs)
    
    # Calculate reduction ratio
    if total_possible_pairs > 0:
        reduction_ratio = 1 - (num_candidate_pairs / total_possible_pairs)
    else:
        reduction_ratio = 0
    
    # Block size statistics
    block_sizes = [len(ids) for ids in blocks.values()]
    
    stats = {
        'total_records': total_records,
        'total_blocks': len(blocks),
        'total_possible_pairs': total_possible_pairs,
        'candidate_pairs': num_candidate_pairs,
        'reduction_ratio': reduction_ratio,
        'avg_block_size': sum(block_sizes) / len(block_sizes) if block_sizes else 0,
        'max_block_size': max(block_sizes) if block_sizes else 0,
        'min_block_size': min(block_sizes) if block_sizes else 0,
    }
    
    return stats


def create_optimal_blocks(
    df: pd.DataFrame,
    strategy: str = 'multi'
) -> Tuple[dict, Set[Tuple[int, int]], dict]:
    """
    Main blocking function with optimal strategy
    
    Args:
        df: Preprocessed dataframe
        strategy: 'first_letter', 'token', 'soundex', 'multi'
    
    Returns:
        - blocks dictionary
        - candidate pairs set
        - blocking statistics
    """
    # Select strategy
    if strategy == 'first_letter':
        blocker = FirstLetterBlocking()
    elif strategy == 'token':
        blocker = TokenBlocking()
    elif strategy == 'soundex':
        blocker = SoundexBlocking()
    elif strategy == 'multi':
        # Combine multiple strategies for better coverage
        blocker = MultiBlockingStrategy([
            FirstNCharsBlocking(n=2),
            TokenBlocking(),
            SoundexBlocking()
        ])
    else:
        blocker = TokenBlocking()  # default
    
    # Create blocks
    blocks = blocker.create_blocks(df)
    
    # Generate candidate pairs
    candidate_pairs = generate_candidate_pairs(blocks)
    
    # Get statistics
    stats = get_blocking_stats(df, blocks)
    
    return blocks, candidate_pairs, stats
