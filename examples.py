"""
Simple Example Script - Quick Start Guide
Test the fuzzy name matching system with your own names
"""

from fuzzy_name_matching import (
    CommonKeyMethod,
    EditDistanceMethod,
    TwoPassHybridMethod,
    ListMethod
)


def example_1_phonetic_matching():
    """Example 1: Check if two names sound similar"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Phonetic Matching")
    print("="*60)
    
    name1 = "Catherine"
    name2 = "Katherine"
    
    # Get Soundex codes
    code1 = CommonKeyMethod.soundex(name1)
    code2 = CommonKeyMethod.soundex(name2)
    
    print(f"\nName 1: {name1} -> Soundex: {code1}")
    print(f"Name 2: {name2} -> Soundex: {code2}")
    
    if code1 == code2:
        print("✓ These names sound similar!")
    else:
        print("✗ These names sound different")


def example_2_similarity_score():
    """Example 2: Calculate similarity between two names"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Similarity Score")
    print("="*60)
    
    name1 = "Siddaramaiah"
    name2 = "Sidharamaiah"
    
    # Calculate different similarity metrics
    lev_dist = EditDistanceMethod.levenshtein_distance(name1, name2)
    jaro_sim = EditDistanceMethod.jaro_winkler_similarity(name1, name2)
    
    print(f"\nComparing: '{name1}' vs '{name2}'")
    print(f"Levenshtein Distance: {lev_dist} edits")
    print(f"Jaro-Winkler Similarity: {jaro_sim:.2%}")
    
    if jaro_sim > 0.9:
        print("✓ Very similar names!")
    elif jaro_sim > 0.8:
        print("✓ Similar names")
    else:
        print("△ Somewhat similar")


def example_3_generate_variations():
    """Example 3: Generate all possible variations of a name"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Generate Name Variations")
    print("="*60)
    
    name = "Nicholas"
    
    # Generate variations
    phonetic_vars = ListMethod.generate_phonetic_variations(name)
    spelling_vars = ListMethod.generate_spelling_variations(name)
    
    print(f"\nBase name: {name}")
    print(f"\nPhonetic variations ({len(phonetic_vars)}):")
    for var in sorted(phonetic_vars)[:10]:
        print(f"  - {var}")
    
    print(f"\nSpelling variations ({len(spelling_vars)}):")
    for var in sorted(spelling_vars)[:10]:
        print(f"  - {var}")


def example_4_search_database():
    """Example 4: Search for names in a database"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Search Database")
    print("="*60)
    
    # Create search engine
    search = TwoPassHybridMethod()
    
    # Build a sample database
    database = [
        "Catherine Williams",
        "Katherine Wilson",
        "Kathryn Walsh",
        "John Smith",
        "Jon Smith",
        "Jonathan Smith",
        "Siddaramaiah",
        "Sidharamaiah",
        "Siddharamaiah"
    ]
    
    print("\nBuilding database with names:")
    for name in database:
        search.add_to_database(name)
        print(f"  ✓ Added: {name}")
    
    # Search for similar names
    query = "Katherine"
    print(f"\n🔍 Searching for: '{query}'")
    print("-" * 60)
    
    matches = search.search(query, threshold=0.6)
    
    if matches:
        print(f"Found {len(matches)} matches:\n")
        for i, (name, score) in enumerate(matches, 1):
            bar = "█" * int(score * 20)
            print(f"{i}. {name:25} {bar} {score:.1%}")
    else:
        print("No matches found")


def example_5_typo_correction():
    """Example 5: Find correct name even with typos"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Typo Correction")
    print("="*60)
    
    # Create search engine
    search = TwoPassHybridMethod()
    
    # Add correct names
    correct_names = [
        "Abdul Rasheed",
        "Muhammad Ali",
        "Catherine Jones",
        "Nicholas Brown"
    ]
    
    for name in correct_names:
        search.add_to_database(name)
    
    # Try with typos
    typos = [
        "Abdual Rasheed",  # typo: 'Abdual' instead of 'Abdul'
        "Muhammed Ali",    # typo: extra 'm'
        "Katheryn Jones",  # typo: different spelling
        "Nikolas Brown"    # typo: 'k' instead of 'ch'
    ]
    
    print("\nCorrecting typos:")
    print("-" * 60)
    
    for typo in typos:
        matches = search.search(typo, threshold=0.7)
        if matches:
            best_match, score = matches[0]
            print(f"'{typo}' -> '{best_match}' ({score:.1%} match)")
        else:
            print(f"'{typo}' -> No correction found")


def custom_search():
    """Interactive: Search your own names"""
    print("\n" + "="*60)
    print("CUSTOM SEARCH (Interactive)")
    print("="*60)
    
    # Create search engine
    search = TwoPassHybridMethod()
    
    # Sample database
    database = [
        "Siddaramaiah", "Sidharamaiah", "Siddharamaiah",
        "Catherine", "Katherine", "Kathryn",
        "Nicholas", "Nick", "Nicolas",
        "Abdul Rasheed", "Abd al Rasheed",
        "John Smith", "Jon Smith", "Jonathan Smith"
    ]
    
    for name in database:
        search.add_to_database(name)
    
    print("\nDatabase loaded with sample names.")
    print("\nTry searching for:")
    print("  - Siddaramaiah")
    print("  - Katherine")
    print("  - Nick")
    print("  - Abdul Rasheed")
    print("\nOr enter your own name to search:")
    
    # You can uncomment below for interactive mode
    # query = input("\nEnter name to search: ")
    # For demo, using a predefined query
    query = "Siddaramaiah"
    
    print(f"\n🔍 Searching for: '{query}'")
    matches = search.search(query, threshold=0.5)
    
    if matches:
        print(f"\nFound {len(matches)} matches:")
        for i, (name, score) in enumerate(matches, 1):
            stars = "⭐" * min(5, int(score * 5))
            print(f"{i}. {name:20} [{stars:5}] {score:.1%}")
    else:
        print("No matches found")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("FUZZY NAME MATCHING - QUICK EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates 5 common use cases:")
    print("1. Phonetic matching")
    print("2. Similarity scoring")
    print("3. Name variation generation")
    print("4. Database search")
    print("5. Typo correction")
    
    # Run all examples
    example_1_phonetic_matching()
    example_2_similarity_score()
    example_3_generate_variations()
    example_4_search_database()
    example_5_typo_correction()
    custom_search()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE!")
    print("="*60)
    print("\nFor more details, see:")
    print("  - fuzzy_name_matching.py (full implementation)")
    print("  - assignment_suite.py (all 9 assignments)")
    print("  - README.md (documentation)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()