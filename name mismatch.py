"""
Fuzzy Name Matching System
Implementation of various name matching techniques to handle:
- Phonetic similarities
- Transliteration variations
- Nicknames and short forms
- Misspellings and typos
- Cultural variations
"""

import re
import itertools
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class CommonKeyMethod:
    """
    Implements phonetic encoding methods (Soundex and Metaphone)
    to convert names into keys based on pronunciation.
    """
    
    @staticmethod
    def soundex(name: str) -> str:
        """
        Generate Soundex code for a name.
        Similar sounding names produce the same code.
        """
        name = name.upper()
        soundex_mapping = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        # Keep first letter
        soundex = name[0]
        
        # Convert remaining letters
        for char in name[1:]:
            if char in soundex_mapping:
                code = soundex_mapping[char]
                # Avoid consecutive duplicates
                if not soundex or soundex[-1] != code:
                    soundex += code
        
        # Remove vowels and some consonants
        soundex = soundex[0] + ''.join([c for c in soundex[1:] if c.isdigit()])
        
        # Pad with zeros or truncate to 4 characters
        soundex = (soundex + '000')[:4]
        
        return soundex
    
    @staticmethod
    def simple_metaphone(name: str) -> str:
        """
        Simplified Metaphone algorithm for phonetic encoding.
        """
        name = name.upper()
        
        # Basic metaphone transformations
        transformations = [
            ('PH', 'F'),
            ('GH', 'F'),
            ('CK', 'K'),
            ('SCH', 'SK'),
            ('CH', 'X'),
            ('TH', '0'),
            ('SH', 'X'),
        ]
        
        for old, new in transformations:
            name = name.replace(old, new)
        
        # Remove vowels except at the beginning
        if len(name) > 1:
            name = name[0] + ''.join([c for c in name[1:] if c not in 'AEIOU'])
        
        return name


class ListMethod:
    """
    Generates all possible variations of a name based on:
    - Phonetic similarities
    - Common misspellings
    - Cultural variations
    - Nicknames
    """
    
    @staticmethod
    def generate_phonetic_variations(name: str) -> Set[str]:
        """
        Generate phonetic variations by replacing similar sounding letters.
        """
        variations = set([name])
        
        # Define phonetic substitutions
        substitutions = [
            ('ph', 'f'), ('f', 'ph'),
            ('c', 'k'), ('k', 'c'),
            ('s', 'z'), ('z', 's'),
            ('i', 'y'), ('y', 'i'),
            ('ee', 'ea'), ('ea', 'ee'),
            ('tion', 'shun'),
        ]
        
        temp_variations = set([name.lower()])
        
        for old, new in substitutions:
            new_set = set()
            for variant in temp_variations:
                if old in variant:
                    new_set.add(variant.replace(old, new))
            temp_variations.update(new_set)
        
        # Capitalize variations
        for var in temp_variations:
            variations.add(var.capitalize())
            variations.add(var.title())
        
        return variations
    
    @staticmethod
    def generate_spelling_variations(name: str) -> Set[str]:
        """
        Generate common misspelling patterns.
        """
        variations = set([name])
        name_lower = name.lower()
        
        # Double/single consonant variations
        consonants = 'bcdfghjklmnpqrstvwxyz'
        for i, char in enumerate(name_lower):
            if char in consonants:
                # Add double consonant
                doubled = name_lower[:i] + char + name_lower[i:]
                variations.add(doubled.capitalize())
                
                # Remove double consonant if exists
                if i < len(name_lower) - 1 and name_lower[i] == name_lower[i+1]:
                    single = name_lower[:i] + name_lower[i+1:]
                    variations.add(single.capitalize())
        
        return variations
    
    @staticmethod
    def generate_syllable_permutations(syllables: List[str]) -> Set[str]:
        """
        Generate permutations from syllable combinations.
        Example: ["Cath", "er", "ine"] -> Catherine, Cathrine, etc.
        """
        variations = set()
        
        # Generate all combinations
        for combo in itertools.product(*[ListMethod._get_syllable_variants(syl) for syl in syllables]):
            variations.add(''.join(combo))
        
        return variations
    
    @staticmethod
    def _get_syllable_variants(syllable: str) -> List[str]:
        """
        Get phonetic variants for a syllable.
        """
        variants = [syllable]
        
        syllable_map = {
            'cath': ['cath', 'kath'],
            'er': ['er', 'ary', 'ry', 'rin'],
            'ine': ['ine', 'yne', 'in', 'yn'],
            'sid': ['sid', 'sidh', 'siddh'],
            'da': ['da', 'dha'],
            'ra': ['ra', 'rama', 'ram'],
            'maiah': ['maiah', 'maya', 'maia', 'mayah'],
        }
        
        return syllable_map.get(syllable.lower(), [syllable])


class EditDistanceMethod:
    """
    Implements various edit distance algorithms to measure
    similarity between names.
    """
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance (insert, delete, substitute).
        Returns the minimum number of single-character edits required.
        """
        if len(s1) < len(s2):
            return EditDistanceMethod.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def damerau_levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Damerau-Levenshtein distance (includes transposition).
        Faster than standard Levenshtein as it handles adjacent swaps.
        """
        len1, len2 = len(s1), len(s2)
        big_int = len1 + len2
        
        # Create dictionary of unique characters
        da = defaultdict(int)
        
        # First row and column (represent adding all letters from other string)
        max_dist = len1 + len2
        H = {}
        H[-1, -1] = max_dist
        
        for i in range(0, len1 + 1):
            H[i, -1] = max_dist
            H[i, 0] = i
        for j in range(0, len2 + 1):
            H[-1, j] = max_dist
            H[0, j] = j
        
        for i in range(1, len1 + 1):
            db = 0
            for j in range(1, len2 + 1):
                k = da[s2[j-1]]
                l = db
                if s1[i-1] == s2[j-1]:
                    cost = 0
                    db = j
                else:
                    cost = 1
                H[i, j] = min(
                    H[i-1, j] + 1,      # insertion
                    H[i, j-1] + 1,      # deletion
                    H[i-1, j-1] + cost, # substitution
                    H[k-1, l-1] + (i-k-1) + 1 + (j-l-1)  # transposition
                )
            da[s1[i-1]] = i
        
        return H[len1, len2]
    
    @staticmethod
    def hamming_distance(s1: str, s2: str) -> int:
        """
        Calculate Hamming distance (only substitutions, strings must be same length).
        """
        if len(s1) != len(s2):
            raise ValueError("Strings must be of equal length for Hamming distance")
        
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
    
    @staticmethod
    def jaro_similarity(s1: str, s2: str) -> float:
        """
        Calculate Jaro similarity (0.0 to 1.0, where 1.0 is exact match).
        """
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        
        if len1 == 0 or len2 == 0:
            return 0.0
        
        match_distance = max(len1, len2) // 2 - 1
        s1_matches = [False] * len1
        s2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Find matches
        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Find transpositions
        k = 0
        for i in range(len1):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        jaro = (matches / len1 + matches / len2 + 
                (matches - transpositions / 2) / matches) / 3
        
        return jaro
    
    @staticmethod
    def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
        """
        Calculate Jaro-Winkler similarity (gives more weight to common prefix).
        """
        jaro_sim = EditDistanceMethod.jaro_similarity(s1, s2)
        
        # Find common prefix length (up to 4 characters)
        prefix_len = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break
        
        return jaro_sim + prefix_len * prefix_scale * (1 - jaro_sim)


class StatisticalMethod:
    """
    Statistical similarity method using trained patterns.
    """
    
    def __init__(self):
        self.trained_pairs = []
        self.similarity_threshold = 0.8
    
    def train(self, name_pairs: List[Tuple[str, str, bool]]):
        """
        Train the model with name pairs and their similarity labels.
        
        Args:
            name_pairs: List of (name1, name2, is_similar) tuples
        """
        self.trained_pairs = name_pairs
    
    def calculate_similarity_score(self, name1: str, name2: str) -> float:
        """
        Calculate similarity score based on multiple factors.
        """
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        if n1 == n2:
            return 1.0
        
        # Multiple similarity measures
        lev_dist = EditDistanceMethod.levenshtein_distance(n1, n2)
        max_len = max(len(n1), len(n2))
        lev_score = 1 - (lev_dist / max_len) if max_len > 0 else 0
        
        jaro_score = EditDistanceMethod.jaro_winkler_similarity(n1, n2)
        
        # Phonetic similarity
        soundex_match = 1.0 if CommonKeyMethod.soundex(n1) == CommonKeyMethod.soundex(n2) else 0.0
        metaphone_match = 1.0 if CommonKeyMethod.simple_metaphone(n1) == CommonKeyMethod.simple_metaphone(n2) else 0.0
        
        # Weighted combination
        final_score = (
            0.3 * lev_score +
            0.3 * jaro_score +
            0.2 * soundex_match +
            0.2 * metaphone_match
        )
        
        return final_score
    
    def is_match(self, name1: str, name2: str) -> bool:
        """
        Determine if two names match based on similarity threshold.
        """
        return self.calculate_similarity_score(name1, name2) >= self.similarity_threshold


class WordEmbeddingMethod:
    """
    Handles semantically similar words (Company, Corporation, Group, etc.)
    Uses predefined semantic mappings.
    """
    
    def __init__(self):
        # Define semantic equivalence classes
        self.semantic_groups = {
            'organization': ['company', 'corporation', 'corp', 'inc', 'incorporated', 
                           'ltd', 'limited', 'group', 'enterprise', 'enterprises'],
            'honorifics': ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam'],
            'titles': ['phd', 'md', 'esq', 'jr', 'sr', 'iii', 'iv'],
            'location': ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr'],
        }
        
        # Create reverse mapping
        self.word_to_group = {}
        for group, words in self.semantic_groups.items():
            for word in words:
                self.word_to_group[word.lower()] = group
    
    def are_semantically_similar(self, word1: str, word2: str) -> bool:
        """
        Check if two words are semantically similar.
        """
        w1 = word1.lower().strip()
        w2 = word2.lower().strip()
        
        if w1 == w2:
            return True
        
        # Check if both belong to same semantic group
        group1 = self.word_to_group.get(w1)
        group2 = self.word_to_group.get(w2)
        
        return group1 is not None and group1 == group2
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by replacing semantic equivalents with standard forms.
        """
        words = text.lower().split()
        normalized = []
        
        for word in words:
            group = self.word_to_group.get(word)
            if group and self.semantic_groups[group]:
                # Use first word in group as standard form
                normalized.append(self.semantic_groups[group][0])
            else:
                normalized.append(word)
        
        return ' '.join(normalized)


class TwoPassHybridMethod:
    """
    Combines Common Key Method (encoding) with Statistical Method (matching).
    
    First Pass: Encode names using phonetic keys
    Second Pass: Match within phonetically similar groups using statistical measures
    """
    
    def __init__(self):
        self.common_key = CommonKeyMethod()
        self.statistical = StatisticalMethod()
        self.name_database = defaultdict(list)  # key -> list of names
    
    def encode(self, name: str) -> str:
        """
        First pass: Encode name into phonetic key.
        """
        return self.common_key.soundex(name)
    
    def add_to_database(self, name: str):
        """
        Add a name to the database under its phonetic key.
        """
        key = self.encode(name)
        if name not in self.name_database[key]:
            self.name_database[key].append(name)
    
    def search(self, query_name: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Second pass: Search for matches in database.
        
        Returns:
            List of (matched_name, similarity_score) tuples sorted by score
        """
        # First pass: Get phonetic key
        key = self.encode(query_name)
        
        # Get all names with same phonetic key
        candidates = self.name_database.get(key, [])
        
        # Second pass: Calculate similarity scores
        results = []
        for candidate in candidates:
            score = self.statistical.calculate_similarity_score(query_name, candidate)
            if score >= threshold:
                results.append((candidate, score))
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results


class NameVariationCalculator:
    """
    Calculate total number of variations for a name using mathematical formulas.
    """
    
    @staticmethod
    def calculate_variations(name: str, 
                           phonetic_count: int = 0,
                           cultural_count: int = 0,
                           misspelling_count: int = 0,
                           nickname_count: int = 0) -> Dict[str, int]:
        """
        Calculate total variations based on the mathematical formula:
        Total = Phonetic + Cultural + Misspellings + Nicknames
        
        For syllable-based phonetic: multiply variations per syllable
        """
        
        results = {
            'phonetic': phonetic_count,
            'cultural': cultural_count,
            'misspellings': misspelling_count,
            'nicknames': nickname_count,
            'total': phonetic_count + cultural_count + misspelling_count + nickname_count
        }
        
        return results
    
    @staticmethod
    def calculate_syllable_permutations(syllables: List[str], 
                                       variants_per_syllable: List[int]) -> int:
        """
        Calculate total permutations from syllable variations.
        Formula: ∏(variants per syllable)
        
        Example: ["Cath", "er", "ine"] with [4, 4, 4] variants = 4*4*4 = 64
        """
        if len(syllables) != len(variants_per_syllable):
            raise ValueError("Must provide variant count for each syllable")
        
        total = 1
        for count in variants_per_syllable:
            total *= count
        
        return total


# Example usage and demonstration
if __name__ == "__main__":
    print("=" * 70)
    print("FUZZY NAME MATCHING SYSTEM - DEMONSTRATION")
    print("=" * 70)
    
    # Test names
    test_names = [
        ("Catherine", "Katherine"),
        ("Siddaramaiah", "Sidharamaiah"),
        ("John Smith", "Jon Smith"),
        ("Abdul Rasheed", "Abd al Rasheed"),
    ]
    
    print("\n1. COMMON KEY METHOD (Phonetic Encoding)")
    print("-" * 70)
    for name1, name2 in test_names:
        soundex1 = CommonKeyMethod.soundex(name1)
        soundex2 = CommonKeyMethod.soundex(name2)
        match = "✓" if soundex1 == soundex2 else "✗"
        print(f"{name1:20} -> {soundex1} | {name2:20} -> {soundex2} [{match}]")
    
    print("\n2. EDIT DISTANCE METHODS")
    print("-" * 70)
    for name1, name2 in test_names:
        lev = EditDistanceMethod.levenshtein_distance(name1, name2)
        jaro = EditDistanceMethod.jaro_winkler_similarity(name1, name2)
        print(f"{name1} <-> {name2}")
        print(f"  Levenshtein: {lev}, Jaro-Winkler: {jaro:.3f}")
    
    print("\n3. LIST METHOD (Phonetic Variations)")
    print("-" * 70)
    variations = ListMethod.generate_phonetic_variations("Catherine")
    print(f"Phonetic variations of 'Catherine': {len(variations)} variations")
    print(f"Sample: {list(variations)[:10]}")
    
    print("\n4. TWO-PASS HYBRID METHOD")
    print("-" * 70)
    hybrid = TwoPassHybridMethod()
    
    # Build database
    database_names = [
        "Siddaramaiah", "Sidharamaiah", "Siddharamaiah",
        "Catherine", "Katherine", "Kathryn",
        "John Smith", "Jon Smith", "Jonathan Smith"
    ]
    
    for name in database_names:
        hybrid.add_to_database(name)
    
    # Test searches
    queries = ["Siddaramaiah", "Katherine", "John Smith"]
    for query in queries:
        matches = hybrid.search(query, threshold=0.7)
        print(f"\nQuery: '{query}'")
        for match_name, score in matches[:5]:
            print(f"  {match_name:25} (score: {score:.3f})")
    
    print("\n5. VARIATION CALCULATION")
    print("-" * 70)
    
    # Catherine example
    catherine_vars = NameVariationCalculator.calculate_variations(
        "Catherine",
        phonetic_count=64,  # 4*4*4
        cultural_count=4,
        misspelling_count=4,
        nickname_count=4
    )
    print(f"Catherine variations: {catherine_vars}")
    
    # Siddaramaiah example
    siddaramaiah_vars = NameVariationCalculator.calculate_variations(
        "Siddaramaiah",
        phonetic_count=8,
        cultural_count=5,
        misspelling_count=6,
        nickname_count=4
    )
    print(f"Siddaramaiah variations: {siddaramaiah_vars}")
    
    print("\n6. WORD EMBEDDING METHOD (Semantic Similarity)")
    print("-" * 70)
    embeddings = WordEmbeddingMethod()
    semantic_pairs = [
        ("Company", "Corporation"),
        ("Inc", "Incorporated"),
        ("Mr", "Dr"),
        ("Street", "Avenue")
    ]
    
    for word1, word2 in semantic_pairs:
        similar = embeddings.are_semantically_similar(word1, word2)
        symbol = "✓" if similar else "✗"
        print(f"{word1:15} <-> {word2:15} [{symbol}]")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)