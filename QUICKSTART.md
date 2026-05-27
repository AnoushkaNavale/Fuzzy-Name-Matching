# Quick Start Guide

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python example.py
```

## Running the Streamlit UI

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## Command Line Usage

### Quick Deduplication

```python
from matching import find_duplicates

# Your data
records = [
    {'name': 'Apple Inc'},
    {'name': 'Apple Computer Inc'},
    {'name': 'Microsoft Corp'},
]

# Find duplicates
matches = find_duplicates(records, field='name', threshold=0.70)

# Print results
for match in matches:
    print(f"{match['text_1']} ↔ {match['text_2']}: {match['overall']:.1%}")
```

### Advanced Usage

```python
from matching import EntityResolver

# Initialize with custom settings
resolver = EntityResolver(
    strong_threshold=0.85,      # 85%+ = auto-merge safe
    possible_threshold=0.70,    # 70-85% = needs review
    blocking_strategy='multi'   # Best recall
)

# Find duplicates
matches = resolver.deduplicate(records, field='name')

# Get statistics
stats = resolver.get_statistics()
print(f"Found {stats['matches_found']} matches")
print(f"Saved {stats['comparisons_saved']:,} comparisons")
```

## Using Sample Data

The system includes `sample_companies.csv` for testing:

```bash
# Option 1: In Streamlit UI
# - Click "Upload CSV file"
# - Select sample_companies.csv
# - Click "Find Duplicates"

# Option 2: Command line
python -c "
import pandas as pd
from matching import find_duplicates

df = pd.read_csv('sample_companies.csv')
records = df.to_dict('records')
matches = find_duplicates(records, field='name')

print(f'Found {len(matches)} matches')
for m in matches[:5]:
    print(f\"{m['text_1']} ↔ {m['text_2']}: {m['overall']:.1%}\")
"
```

## Understanding Results

### Match Types

| Type | Score | Meaning |
|------|-------|---------|
| 🟢 **Strong Match** | ≥85% | Very likely the same entity |
| 🟡 **Possible Match** | 70-85% | Needs manual review |
| 🔴 **No Match** | <70% | Different entities |

### Similarity Metrics

Each match shows 4 scores:

1. **Edit Distance** (30% weight)
   - How many character changes needed
   - "Apple" → "Appel" = 1 change = 90% similar

2. **Token Set** (30% weight)
   - Compares unique words
   - "Apple Inc" vs "Inc Apple" = 100% (same words)

3. **Token Sort** (20% weight)
   - Sorts words then compares
   - Good for different word orders

4. **Jaccard** (20% weight)
   - Character n-gram overlap
   - Catches spelling variations

### Example Output

```
🟢 Strong Match #1 (92% confidence)
Record 1: microsoft corp
Record 2: microsoft corporation

Scores:
  - Edit Distance: 85%
  - Token Set: 100%
  - Token Sort: 95%
  - Jaccard: 88%

Explanation: Shared words match (100%) | Very similar strings (85%)
```

## Adjusting Thresholds

### Conservative (Fewer False Positives)

```python
resolver = EntityResolver(
    strong_threshold=0.95,
    possible_threshold=0.85
)
```

Use when: Precision is critical (financial records, legal documents)

### Aggressive (More Recall)

```python
resolver = EntityResolver(
    strong_threshold=0.75,
    possible_threshold=0.60
)
```

Use when: You can manually review results, don't want to miss matches

### Balanced (Recommended)

```python
resolver = EntityResolver(
    strong_threshold=0.85,
    possible_threshold=0.70
)
```

Use when: Standard deduplication tasks

## Blocking Strategies

Choose based on your data:

### Multi (Default)
```python
blocking_strategy='multi'
```
- Combines all strategies
- Best recall
- Slightly slower
- **Use when**: Data quality varies

### Token
```python
blocking_strategy='token'
```
- Groups by shared words
- Good for varied word orders
- **Use when**: "Microsoft Corp" vs "Corp Microsoft"

### First Letter
```python
blocking_strategy='first_letter'
```
- Groups by first character
- Fastest
- **Use when**: Very large datasets (100K+ records)

### Sorted Neighborhood
```python
blocking_strategy='sorted'
```
- Sliding window on sorted data
- Catches near-misses
- **Use when**: Names are mostly similar

## Performance Tips

### For Large Datasets (100K+ records)

1. **Use first-letter blocking**
   ```python
   blocking_strategy='first_letter'
   ```

2. **Process in chunks**
   ```python
   chunk_size = 10000
   for i in range(0, len(records), chunk_size):
       chunk = records[i:i+chunk_size]
       matches = resolver.deduplicate(chunk)
   ```

3. **Lower thresholds cautiously**
   - Lower thresholds = more comparisons
   - Start at 0.70, adjust as needed

### For Real-Time Matching

```python
# Pre-build the database
for record in existing_records:
    resolver.add(record['name'])

# Match new records quickly
new_record = {'name': 'Apple Computer'}
matches = resolver.search(new_record['name'])
```

## Troubleshooting

### "No matches found"
- ✅ Lower `possible_threshold` to 0.60
- ✅ Check if field name is correct
- ✅ Try `blocking_strategy='multi'`

### "Too many false positives"
- ✅ Raise `strong_threshold` to 0.90+
- ✅ Review preprocessing (remove business suffixes)
- ✅ Check sample results to understand why

### "System is slow"
- ✅ Use `blocking_strategy='first_letter'`
- ✅ Process in smaller chunks
- ✅ Ensure RapidFuzz is installed (10x faster)

### "Import errors"
```bash
# Install missing dependencies
pip install streamlit pandas rapidfuzz
```

## CSV Format Requirements

Your CSV should have at least one text column:

```csv
id,name,other_data
1,Apple Inc,USA
2,Apple Computer Inc,USA
```

- **Required**: At least one text column (name, company, person, etc.)
- **Optional**: ID column, additional metadata
- **Encoding**: UTF-8 recommended

## Next Steps

1. **Try the examples**
   ```bash
   python example.py
   ```

2. **Test with your data**
   - Export your database to CSV
   - Upload to Streamlit UI
   - Adjust thresholds based on results

3. **Integrate into your workflow**
   - Use as Python library
   - Build API endpoint
   - Schedule batch jobs

4. **Read full documentation**
   - See `README.md` for architecture details
   - Check module docstrings for API reference

## Support

For issues or questions:
1. Check `README.md` for detailed explanations
2. Review `example.py` for usage patterns
3. Examine module source code (well-commented)

## Common Use Cases

### 1. Customer Deduplication
```python
# Find duplicate customers
customers = load_from_database()
duplicates = find_duplicates(customers, field='customer_name')
```

### 2. Vendor Matching
```python
# Match vendors across systems
crm_vendors = load_crm_data()
erp_vendors = load_erp_data()

resolver = EntityResolver()
matches = resolver.match_datasets(
    crm_vendors, erp_vendors,
    field1='vendor_name',
    field2='supplier_name'
)
```

### 3. Product Catalog Cleanup
```python
# Find duplicate products
products = load_products()
duplicates = find_duplicates(products, field='product_name', threshold=0.75)
```

## Best Practices

1. **Always preprocess** - Use built-in cleaning functions
2. **Start conservative** - High thresholds first, lower if needed
3. **Review samples** - Check 20-30 matches manually
4. **Export results** - Download CSV for further analysis
5. **Iterate** - Adjust thresholds based on feedback

---

**You're ready to go! Start with `streamlit run app.py` or `python example.py`**
