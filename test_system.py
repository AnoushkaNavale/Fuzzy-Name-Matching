"""
Test Script - Demonstrates Entity Resolution System
"""

import pandas as pd
from entity_resolution import EntityResolver, quick_match, compare_two_names


def test_quick_compare():
    """Test quick comparison of two names"""
    print("\n" + "="*60)
    print("TEST 1: Quick Name Comparison")
    print("="*60)
    
    test_pairs = [
        ("Microsoft Corporation", "Microsoft Corp"),
        ("John Smith", "Smith, John"),
        ("Apple Inc", "Google LLC"),
        ("Catherine Williams", "Katherine Williams"),
    ]
    
    for name1, name2 in test_pairs:
        result = compare_two_names(name1, name2, return_details=True)
        print(f"\n{name1} ↔ {name2}")
        print(f"  Score: {result['similarity_score']:.1f}")
        print(f"  Type: {result['match_type']}")
        print(f"  Reason: {result['explanation']}")


def test_batch_processing():
    """Test batch entity resolution"""
    print("\n" + "="*60)
    print("TEST 2: Batch Processing")
    print("="*60)
    
    # Create sample data
    data = {
        'company': [
            'Microsoft Corporation',
            'Microsoft Corp',
            'Apple Inc',
            'Apple Incorporated',
            'Google LLC',
            'Alphabet Inc',
            'Amazon.com Inc',
            'Amazon Inc',
            'Tesla Motors',
            'Tesla Inc',
            'Meta Platforms',
            'Facebook Inc',
        ]
    }
    
    df = pd.DataFrame(data)
    print(f"\nProcessing {len(df)} records...")
    
    # Quick match
    df_matches, stats = quick_match(
        df,
        name_column='company',
        strong_threshold=85,
        weak_threshold=70,
        name_type='organization'
    )
    
    print(f"\nStatistics:")
    print(f"  Total Records: {stats['total_records']}")
    print(f"  Candidate Pairs: {stats['candidate_pairs']:,}")
    print(f"  Total Matches: {stats['total_matches']}")
    print(f"  Strong Matches: {stats['strong_matches']}")
    print(f"  Possible Matches: {stats['possible_matches']}")
    print(f"  Blocking Reduction: {stats['blocking_reduction']*100:.1f}%")
    print(f"  Avg Similarity: {stats['avg_similarity']:.1f}")
    
    print(f"\nTop Matches:")
    if len(df_matches) > 0:
        for idx, row in df_matches.head(5).iterrows():
            print(f"\n  {row['name_1']} ↔ {row['name_2']}")
            print(f"    Score: {row['similarity_score']:.1f} ({row['match_type']})")
            print(f"    {row['explanation']}")


def test_custom_resolver():
    """Test custom entity resolver with configuration"""
    print("\n" + "="*60)
    print("TEST 3: Custom Configuration")
    print("="*60)
    
    # Create resolver with custom settings
    resolver = EntityResolver(
        strong_threshold=90,
        weak_threshold=75,
        blocking_strategy='multi'
    )
    
    # Sample names
    data = {
        'name': [
            'Dr. John Smith',
            'John Smith',
            'J. Smith',
            'Smith, John',
            'Catherine O\'Brien',
            'Katherine O\'Brien',
            'Catherine OBrien',
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Process
    df_matches, stats = resolver.resolve_entities(
        df,
        name_column='name',
        name_type='person'
    )
    
    print(f"\nFound {len(df_matches)} matches with custom thresholds")
    
    if len(df_matches) > 0:
        print("\nMatches:")
        for idx, row in df_matches.iterrows():
            print(f"  {row['name_1']} ↔ {row['name_2']}: {row['similarity_score']:.1f}")


def test_performance():
    """Test performance on larger dataset"""
    print("\n" + "="*60)
    print("TEST 4: Performance Test")
    print("="*60)
    
    import time
    
    # Create larger dataset
    names = [
        'Microsoft Corporation', 'Microsoft Corp', 'Microsoft',
        'Apple Inc', 'Apple Incorporated', 'Apple Computer',
        'Google LLC', 'Google Inc', 'Alphabet Inc',
        'Amazon.com Inc', 'Amazon Inc', 'Amazon',
        'Tesla Motors', 'Tesla Inc', 'Tesla',
        'Meta Platforms', 'Facebook Inc', 'Facebook',
        'IBM Corporation', 'IBM Corp', 'International Business Machines',
        'Oracle Corporation', 'Oracle Corp', 'Oracle',
    ]
    
    # Duplicate to make larger
    names = names * 5  # 120 records
    
    df = pd.DataFrame({'company': names})
    
    print(f"\nTesting with {len(df)} records...")
    
    start_time = time.time()
    
    resolver = EntityResolver(blocking_strategy='multi')
    df_matches, stats = resolver.resolve_entities(df, 'company', 'organization')
    
    elapsed = time.time() - start_time
    
    print(f"\nPerformance:")
    print(f"  Time: {elapsed:.2f} seconds")
    print(f"  Records/second: {len(df)/elapsed:.1f}")
    print(f"  Pairs evaluated: {stats['candidate_pairs']:,}")
    print(f"  Blocking reduction: {stats['blocking_reduction']*100:.1f}%")
    print(f"  Matches found: {stats['total_matches']}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ENTITY RESOLUTION SYSTEM - TEST SUITE")
    print("="*60)
    
    test_quick_compare()
    test_batch_processing()
    test_custom_resolver()
    test_performance()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
