"""
Comprehensive Usage Examples
Demonstrates all features of the Entity Resolution System
"""

import pandas as pd
from entity_resolution import (
    EntityResolver,
    quick_match,
    compare_two_names,
    TextPreprocessor,
    SimilarityScorer
)


print("=" * 70)
print("ENTITY RESOLUTION SYSTEM - USAGE EXAMPLES")
print("=" * 70)


# ============================================================================
# EXAMPLE 1: Quick Name Comparison
# ============================================================================

print("\n" + "=" * 70)
print("EXAMPLE 1: Quick Name Comparison")
print("=" * 70)

pairs = [
    ("Microsoft Corporation", "Microsoft Corp"),
    ("Apple Inc", "Apple Incorporated"),
    ("John Smith", "Smith, John"),
    ("Google LLC", "Alphabet Inc"),
]

for name1, name2 in pairs:
    result = compare_two_names(name1, name2)
    print(f"\n{name1}")
    print(f"  vs {name2}")
    print(f"  Score: {result['similarity_score']:.1f}/100")
    print(f"  Type: {result['match_type']}")
    print(f"  Why: {result['explanation']}")


# ============================================================================
# EXAMPLE 2: Simple Batch Processing
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 2: Simple Batch Processing")
print("=" * 70)

# Create sample dataset
companies = pd.DataFrame({
    'name': [
        'Microsoft Corporation',
        'Microsoft Corp',
        'Apple Inc',
        'Apple Incorporated',
        'Amazon.com Inc',
        'Amazon Inc',
    ]
})

print(f"\nInput: {len(companies)} companies")
print(companies['name'].tolist())

# Find matches
matches, stats = quick_match(companies, 'name', name_type='organization')

print(f"\nResults:")
print(f"  Matches found: {stats['total_matches']}")
print(f"  Strong matches: {stats['strong_matches']}")
print(f"  Candidate pairs evaluated: {stats['candidate_pairs']}")

if len(matches) > 0:
    print(f"\nTop Matches:")
    for _, row in matches.head(3).iterrows():
        print(f"  • {row['name_1']} ↔ {row['name_2']}")
        print(f"    Score: {row['similarity_score']:.1f} ({row['match_type']})")


# ============================================================================
# EXAMPLE 3: Custom Configuration
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 3: Custom Configuration")
print("=" * 70)

# Create resolver with custom settings
resolver = EntityResolver(
    strong_threshold=90,      # Higher threshold for strong matches
    weak_threshold=75,        # Higher threshold for possible matches
    blocking_strategy='token' # Fast token-based blocking
)

print("\nConfiguration:")
print(f"  Strong match threshold: 90")
print(f"  Possible match threshold: 75")
print(f"  Blocking strategy: token")

# Process
matches, stats = resolver.resolve_entities(
    companies,
    name_column='name',
    name_type='organization'
)

print(f"\nResults with strict thresholds:")
print(f"  Matches: {stats['total_matches']}")
print(f"  Strong: {stats['strong_matches']}")
print(f"  Possible: {stats['possible_matches']}")


# ============================================================================
# EXAMPLE 4: Person Name Matching
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 4: Person Name Matching")
print("=" * 70)

people = pd.DataFrame({
    'person': [
        'Dr. John Smith',
        'John Smith',
        'Smith, John',
        'J. Smith',
        'Catherine Williams',
        'Katherine Williams',
        'Prof. Robert Johnson',
        'Robert Johnson',
    ]
})

print(f"\nInput: {len(people)} people")

matches, stats = quick_match(
    people,
    'person',
    name_type='person',  # Handles honorifics
    strong_threshold=85,
    weak_threshold=70
)

print(f"\nResults:")
print(f"  Matches found: {stats['total_matches']}")

if len(matches) > 0:
    print(f"\nPerson Matches:")
    for _, row in matches.iterrows():
        print(f"  • {row['name_1']} ↔ {row['name_2']}")
        print(f"    Score: {row['similarity_score']:.1f}")


# ============================================================================
# EXAMPLE 5: Working with Additional Columns
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 5: Including Additional Columns")
print("=" * 70)

companies_with_data = pd.DataFrame({
    'company': [
        'Microsoft Corporation',
        'Microsoft Corp',
        'Apple Inc',
        'Apple Incorporated',
    ],
    'city': [
        'Redmond',
        'Seattle',
        'Cupertino',
        'Cupertino',
    ],
    'revenue': [
        '168B',
        '168B',
        '394B',
        '394B',
    ]
})

print("\nInput data:")
print(companies_with_data)

resolver = EntityResolver()
resolver.process_dataframe(
    companies_with_data,
    name_column='company',
    name_type='organization',
    additional_columns=['city', 'revenue']  # Keep these columns
)

print(f"\nProcessed {len(resolver.df_processed)} records with additional data")


# ============================================================================
# EXAMPLE 6: Understanding Similarity Scores
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 6: Understanding Similarity Scores")
print("=" * 70)

scorer = SimilarityScorer()

test_pairs = [
    ("Microsoft", "Microsoft"),           # Perfect match
    ("Microsoft Corp", "Microsoft Corporation"),  # Abbreviation
    ("John Smith", "Smith John"),         # Reordered
    ("ABC Company", "ABC Co"),            # Shortened
    ("Apple", "Orange"),                  # Different
]

print("\nDetailed Score Breakdown:")
for name1, name2 in test_pairs:
    from entity_resolution.preprocessing import TextPreprocessor
    
    prep = TextPreprocessor()
    norm1 = prep.clean_text(name1)
    norm2 = prep.clean_text(name2)
    tokens1 = prep.get_tokens(norm1)
    tokens2 = prep.get_tokens(norm2)
    
    final_score, scores = scorer.hybrid_score(norm1, norm2, tokens1, tokens2)
    
    print(f"\n{name1} vs {name2}")
    print(f"  Levenshtein:  {scores['levenshtein']:.1f}")
    print(f"  Token Sort:   {scores['token_sort']:.1f}")
    print(f"  Token Set:    {scores['token_set']:.1f}")
    print(f"  Jaccard:      {scores['jaccard']:.1f}")
    print(f"  ─────────────────────")
    print(f"  FINAL SCORE:  {final_score:.1f}")


# ============================================================================
# EXAMPLE 7: Blocking Performance
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 7: Blocking Performance Comparison")
print("=" * 70)

# Create larger dataset
large_dataset = pd.DataFrame({
    'company': [
        f"Company {chr(65 + i//10)}{i}"
        for i in range(100)
    ]
})

print(f"\nDataset: {len(large_dataset)} records")
print(f"Without blocking: {len(large_dataset) * (len(large_dataset)-1) // 2:,} comparisons")

strategies = ['first_letter', 'token', 'multi']

for strategy in strategies:
    resolver = EntityResolver(blocking_strategy=strategy)
    resolver.process_dataframe(large_dataset, 'company')
    stats = resolver.create_blocks()
    
    print(f"\nBlocking strategy: {strategy}")
    print(f"  Blocks created: {stats['total_blocks']}")
    print(f"  Candidate pairs: {stats['candidate_pairs']:,}")
    print(f"  Reduction: {stats['reduction_ratio']*100:.1f}%")


# ============================================================================
# EXAMPLE 8: Custom Weights
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 8: Custom Scoring Weights")
print("=" * 70)

scorer = SimilarityScorer()

# Default weights
print("Default weights:")
print(f"  {scorer.weights}")

# Custom weights - emphasize exact character matching
custom_weights = {
    'levenshtein': 0.5,  # More weight on character similarity
    'token_sort': 0.2,
    'token_set': 0.2,
    'jaccard': 0.1
}

scorer.set_weights(custom_weights)
print(f"\nCustom weights:")
print(f"  {scorer.weights}")

# Compare scores
from entity_resolution.preprocessing import TextPreprocessor
prep = TextPreprocessor()

name1, name2 = "Microsoft Corp", "Microsoft Corporation"
norm1, norm2 = prep.clean_text(name1), prep.clean_text(name2)
tokens1, tokens2 = prep.get_tokens(norm1), prep.get_tokens(norm2)

score_custom, _ = scorer.hybrid_score(norm1, norm2, tokens1, tokens2)

# Reset to default
scorer.set_weights({
    'levenshtein': 0.3,
    'token_sort': 0.3,
    'token_set': 0.2,
    'jaccard': 0.2
})
score_default, _ = scorer.hybrid_score(norm1, norm2, tokens1, tokens2)

print(f"\n{name1} vs {name2}")
print(f"  Default weights score:  {score_default:.1f}")
print(f"  Custom weights score:   {score_custom:.1f}")


# ============================================================================
# EXAMPLE 9: Finding Matches for Specific Record
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 9: Finding Matches for Specific Record")
print("=" * 70)

companies = pd.DataFrame({
    'company': [
        'Microsoft Corporation',
        'Microsoft Corp',
        'Microsoft',
        'Apple Inc',
        'Google LLC',
    ]
})

resolver = EntityResolver()
matches, _ = resolver.resolve_entities(companies, 'company', 'organization')

# Find all matches for record 0 (Microsoft Corporation)
print("\nFinding matches for: 'Microsoft Corporation' (record_id=0)")

record_matches = resolver.get_matches_for_record(0, min_score=70)

if len(record_matches) > 0:
    print(f"\nFound {len(record_matches)} matches:")
    for _, row in record_matches.iterrows():
        other_name = row['name_2'] if row['record_id_1'] == 0 else row['name_1']
        print(f"  • {other_name}: {row['similarity_score']:.1f}")


# ============================================================================
# EXAMPLE 10: Export Results
# ============================================================================

print("\n\n" + "=" * 70)
print("EXAMPLE 10: Exporting Results")
print("=" * 70)

companies = pd.DataFrame({
    'company': [
        'Microsoft Corporation',
        'Microsoft Corp',
        'Apple Inc',
        'Apple Incorporated',
    ]
})

matches, stats = quick_match(companies, 'company', name_type='organization')

if len(matches) > 0:
    # Save to CSV
    output_file = '/home/claude/entity_resolution/matches_output.csv'
    matches.to_csv(output_file, index=False)
    print(f"\n✓ Results saved to: {output_file}")
    
    # Show what was saved
    print(f"\nColumns saved:")
    for col in matches.columns:
        print(f"  • {col}")
    
    print(f"\nFirst row:")
    print(matches.iloc[0].to_dict())


print("\n" + "=" * 70)
print("ALL EXAMPLES COMPLETE!")
print("=" * 70)
print("\nKey Takeaways:")
print("  1. Use quick_match() for simple cases")
print("  2. Use EntityResolver for custom configuration")
print("  3. Adjust thresholds based on your data quality")
print("  4. Use 'multi' blocking for best accuracy")
print("  5. Use 'person' or 'organization' name_type for better preprocessing")
print("=" * 70 + "\n")
