"""
Preprocessing Module
Handles data cleaning, normalization, and preparation for matching
"""

import re
import pandas as pd
from typing import List, Optional


class TextPreprocessor:
    """Clean and normalize text data for entity resolution"""
    
    def __init__(self, lowercase: bool = True, remove_punctuation: bool = True):
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        
        # Common company/organization suffixes to standardize
        self.org_suffixes = {
            'corporation': 'corp',
            'incorporated': 'inc',
            'company': 'co',
            'limited': 'ltd',
            'limited liability company': 'llc',
            'and': '&',
        }
        
        # Honorifics to remove
        self.honorifics = ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam']
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove punctuation if specified
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', ' ', text)
            text = ' '.join(text.split())
        
        return text.strip()
    
    def remove_honorifics(self, text: str) -> str:
        """Remove common honorifics from names"""
        words = text.split()
        cleaned_words = [w for w in words if w not in self.honorifics]
        return ' '.join(cleaned_words)
    
    def normalize_organization(self, text: str) -> str:
        """Normalize organization names"""
        text = self.clean_text(text)
        
        # Replace common suffixes
        for full, abbr in self.org_suffixes.items():
            text = text.replace(f' {full}', f' {abbr}')
            text = text.replace(f'{full} ', f'{abbr} ')
        
        return text.strip()
    
    def normalize_name(self, text: str) -> str:
        """Normalize person names"""
        text = self.clean_text(text)
        text = self.remove_honorifics(text)
        return text.strip()
    
    def get_tokens(self, text: str) -> List[str]:
        """Extract tokens from text"""
        text = self.clean_text(text)
        return [t for t in text.split() if len(t) > 0]
    
    def preprocess_dataframe(
        self, 
        df: pd.DataFrame, 
        column: str,
        name_type: str = 'general'
    ) -> pd.DataFrame:
        """
        Preprocess a dataframe column
        
        Args:
            df: Input dataframe
            column: Column name to preprocess
            name_type: 'person', 'organization', or 'general'
        
        Returns:
            DataFrame with new 'normalized' column
        """
        df = df.copy()
        
        # Apply appropriate normalization
        if name_type == 'person':
            df['normalized'] = df[column].apply(self.normalize_name)
        elif name_type == 'organization':
            df['normalized'] = df[column].apply(self.normalize_organization)
        else:
            df['normalized'] = df[column].apply(self.clean_text)
        
        # Add tokens column for token-based matching
        df['tokens'] = df['normalized'].apply(self.get_tokens)
        
        return df


def prepare_for_matching(
    df: pd.DataFrame,
    name_column: str,
    name_type: str = 'general',
    additional_columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Main preprocessing function
    
    Args:
        df: Input dataframe
        name_column: Column containing names to match
        name_type: Type of names ('person', 'organization', 'general')
        additional_columns: Other columns to keep
    
    Returns:
        Preprocessed dataframe ready for matching
    """
    preprocessor = TextPreprocessor()
    
    # Select relevant columns
    columns_to_keep = [name_column]
    if additional_columns:
        columns_to_keep.extend(additional_columns)
    
    df_processed = df[columns_to_keep].copy()
    df_processed.rename(columns={name_column: 'original_name'}, inplace=True)
    
    # Preprocess
    df_processed = preprocessor.preprocess_dataframe(
        df_processed, 
        'original_name',
        name_type
    )
    
    # Add unique ID if not present
    df_processed['record_id'] = range(len(df_processed))
    
    return df_processed
