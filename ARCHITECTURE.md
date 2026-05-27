# System Architecture

## High-Level Flow

```
INPUT DATA
    ↓
PREPROCESSING (preprocessing.py)
    • Normalize text
    • Remove punctuation
    • Extract tokens
    • Handle org suffixes
    ↓
BLOCKING (blocking.py)
    • Create blocks (First-letter, Token, Soundex, Multi)
    • Generate candidate pairs
    • Reduce comparisons from O(n²) to O(n·k)
    ↓
SCORING (scoring.py)
    • Calculate Levenshtein similarity
    • Calculate Token Sort/Set similarity
    • Calculate Jaccard similarity
    • Compute weighted hybrid score
    ↓
MATCHING (matching.py)
    • Apply thresholds
    • Classify matches (Strong/Possible/No)
    • Generate explanations
    ↓
OUTPUT
    • Matched pairs
    • Similarity scores
    • Match explanations
    • Statistics
```

## Module Breakdown

### 1. preprocessing.py
**Purpose**: Clean and normalize input data

**Key Classes**:
- `TextPreprocessor`: Main preprocessing logic

**Functions**:
- Text cleaning (lowercase, punctuation removal)
- Honorific removal (Mr., Dr., etc.)
- Organization suffix normalization (Corp → Corporation)
- Token extraction

**Output**: Normalized text + token list

### 2. blocking.py
**Purpose**: Reduce comparison space from O(n²) to O(n·k)

**Key Classes**:
- `FirstLetterBlocking`: Group by first character
- `TokenBlocking`: Group by shared words
- `SoundexBlocking`: Group by phonetic code
- `MultiBlockingStrategy`: Combine multiple strategies

**Functions**:
- `create_blocks()`: Generate blocks
- `generate_candidate_pairs()`: Create pairs to compare
- `get_blocking_stats()`: Performance metrics

**Example**:
```
Without blocking: 1000 records = 499,500 comparisons
With blocking:    1000 records ≈ 2,500 comparisons (99.5% reduction)
```

### 3. scoring.py
**Purpose**: Calculate similarity between text strings

**Key Classes**:
- `SimilarityScorer`: Multi-metric similarity calculation

**Metrics**:
- **Levenshtein**: Character-level edit distance
- **Token Sort**: Handles word order
- **Token Set**: Handles partial matches
- **Jaccard**: Token overlap
- **Partial**: Substring matching

**Hybrid Formula**:
```
Score = 0.3×Lev + 0.3×TokenSort + 0.2×TokenSet + 0.2×Jaccard
```

**Functions**:
- `calculate_all_scores()`: All individual scores
- `hybrid_score()`: Weighted combination
- `classify_match()`: Apply thresholds
- `explain_match()`: Generate explanations

### 4. matching.py
**Purpose**: Orchestrate the complete entity resolution pipeline

**Key Classes**:
- `EntityResolver`: Main engine

**Pipeline**:
1. `process_dataframe()`: Preprocess input
2. `create_blocks()`: Generate blocks
3. `find_matches()`: Score pairs and filter
4. `resolve_entities()`: Complete pipeline

**Functions**:
- `quick_match()`: Simple one-function interface
- `compare_two_names()`: Direct name comparison

### 5. app.py
**Purpose**: Streamlit web interface

**Features**:
- CSV file upload
- Interactive threshold adjustment
- Real-time processing
- Results visualization
- Download matched results

**Pages**:
- Batch Processing: Upload and process files
- Quick Compare: Compare two names instantly

## Data Flow Example

### Input
```csv
company_name
Microsoft Corporation
Microsoft Corp
Apple Inc
```

### After Preprocessing
```
record_id | original_name         | normalized          | tokens
0         | Microsoft Corporation | microsoft corp      | [microsoft, corp]
1         | Microsoft Corp        | microsoft corp      | [microsoft, corp]
2         | Apple Inc            | apple inc           | [apple, inc]
```

### After Blocking
```
Block 'm': [0, 1]  (Microsoft records)
Block 'a': [2]     (Apple record)

Candidate Pairs: (0, 1)  ← Only compare these!
```

### After Scoring
```
Pair (0, 1):
  Levenshtein: 100.0
  Token Sort: 100.0
  Token Set: 100.0
  Jaccard: 100.0
  ─────────────────
  Hybrid: 100.0
```

### After Matching
```
Match:
  name_1: Microsoft Corporation
  name_2: Microsoft Corp
  score: 100.0
  type: strong_match
  explanation: "Perfect match across all metrics"
```

## Performance Optimization Strategies

### 1. Blocking
- **Problem**: Comparing all pairs is O(n²)
- **Solution**: Group similar records, only compare within groups
- **Impact**: 90-99% reduction in comparisons

### 2. RapidFuzz
- **Problem**: fuzzywuzzy is slow
- **Solution**: Use RapidFuzz (C++ implementation)
- **Impact**: 5-10x faster

### 3. Batch Processing
- **Problem**: Processing one-by-one is inefficient
- **Solution**: Vectorized operations where possible
- **Impact**: Better memory usage

### 4. Early Stopping
- **Problem**: Computing all scores is wasteful
- **Solution**: Skip low-similarity pairs early
- **Impact**: Faster processing

## Scalability Considerations

### Small Datasets (< 1,000 records)
- Any blocking strategy works
- Processing time: < 5 seconds
- Memory: Minimal

### Medium Datasets (1,000 - 10,000 records)
- Use 'multi' blocking strategy
- Processing time: 10-60 seconds
- Memory: < 500MB

### Large Datasets (> 10,000 records)
- Use 'token' or 'multi' blocking
- Consider batch processing
- Processing time: Minutes
- Memory: 1-2GB

### Very Large Datasets (> 100,000 records)
- Process in chunks
- Use distributed processing
- Consider database integration
- Processing time: Hours

## Configuration Guidelines

### Thresholds

**Conservative (high precision)**:
```python
strong_threshold = 95
weak_threshold = 85
```

**Balanced (recommended)**:
```python
strong_threshold = 85
weak_threshold = 70
```

**Aggressive (high recall)**:
```python
strong_threshold = 75
weak_threshold = 60
```

### Blocking Strategies

**Best Accuracy**:
```python
blocking_strategy = 'multi'
```

**Best Speed**:
```python
blocking_strategy = 'first_letter'
```

**Good Balance**:
```python
blocking_strategy = 'token'
```

## Error Handling

The system handles:
- Missing values (converted to empty strings)
- Non-string data (converted to strings)
- Empty dataframes (returns empty results)
- Invalid thresholds (validation errors)
- Encoding issues (UTF-8 normalization)

## Testing Strategy

### Unit Tests (in test_system.py)
1. Quick name comparison
2. Batch processing
3. Custom configuration
4. Performance benchmarks

### Integration Tests
1. End-to-end pipeline
2. Multiple blocking strategies
3. Different name types

### Performance Tests
1. Scaling behavior
2. Memory usage
3. Blocking efficiency

## Extension Points

### Add New Similarity Metric
```python
# In scoring.py
def new_metric(self, s1: str, s2: str) -> float:
    # Your logic here
    return score
```

### Add New Blocking Strategy
```python
# In blocking.py
class CustomBlocking(BlockingStrategy):
    def create_blocks(self, df: pd.DataFrame) -> dict:
        # Your logic here
        return blocks
```

### Customize Preprocessing
```python
# In preprocessing.py
def custom_normalize(self, text: str) -> str:
    # Your logic here
    return normalized
```

## Dependencies

- **pandas**: Data manipulation
- **rapidfuzz**: Fast string matching
- **streamlit**: Web interface

All available via pip, no complex setup required.
