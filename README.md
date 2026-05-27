# Entity Resolution System

A scalable, production-level fuzzy name matching and entity resolution system with a Streamlit UI.

This project performs intelligent duplicate detection and fuzzy entity matching using multiple similarity algorithms, blocking strategies, and weighted score fusion.

---

# Features

- Production-ready modular architecture
- Streamlit UI for interactive matching
- Fast fuzzy matching with RapidFuzz
- Multi-algorithm similarity scoring
- Blocking strategies to avoid O(n²) comparisons
- Explainable match scoring
- Batch processing support
- CSV upload and export
- Adjustable thresholds and weights
- Scalable architecture for large datasets

---

# Architecture

```text
entity_resolution_v2/
│
├── preprocessing.py   # Text cleaning & normalization
├── blocking.py        # Candidate pair reduction (anti-O(n²))
├── matching.py        # Individual similarity algorithms
├── scoring.py         # Weighted fusion, classification, batch resolver
├── app.py             # Streamlit UI
├── tests.py           # Full pytest test suite
└── requirements.txt
```

---

# Module Responsibilities

| Module | Responsibility |
|---|---|
| `preprocessing.py` | Normalize text: lowercase, remove punctuation, strip accents, normalize whitespace |
| `blocking.py` | Reduce candidate comparisons using blocking strategies |
| `matching.py` | Independent similarity algorithms returning scores between 0 and 1 |
| `scoring.py` | Weighted score fusion, threshold classification, explainability |
| `app.py` | Streamlit application with CSV upload, controls, tabs, export |
| `tests.py` | Automated test suite |

---

# Similarity Algorithms

| Algorithm | Purpose | Library |
|---|---|---|
| Levenshtein | Handles typos and misspellings | RapidFuzz |
| Token Sort | Handles first/last name swaps | RapidFuzz |
| Jaccard (bigrams) | Handles OCR and character-level noise | Pure Python |
| Phonetic Matching | Handles sound-alike names | Jellyfish |

---

# Final Scoring Formula

```text
Final Score =
0.35 × Levenshtein
+ 0.30 × Token Sort
+ 0.20 × Jaccard
+ 0.15 × Phonetic
```

Weights are fully configurable.

---

# Blocking Strategies

Blocking drastically reduces comparisons.

Without blocking:

```text
O(n²)
```

With blocking:

```text
O(n · k)
```

where:

- `n` = total records
- `k` = average block size

---

## Supported Blocking Methods

| Strategy | Description | Best Use Case |
|---|---|---|
| `first_letter` | Groups by first character | Fastest |
| `token` | Groups by words/tokens | Better recall |
| `ngram` | Groups by leading characters | Balanced |
| `phonetic` | Groups by phonetic code | Sound-alike names |

---

# Scalability Features

- RapidFuzz provides C-level optimized fuzzy matching
- Blocking reduces unnecessary comparisons
- Batch processing avoids memory spikes
- Corpus index reused across batches
- Streamlit progress bars for large datasets
- Efficient candidate pair generation

---

# Setup

## Clone Repository

```bash
git clone https://github.com/AnoushkaNavale/Fuzzy-Name-Matching.git
cd Fuzzy-Name-Matching
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Run the Streamlit UI

```bash
python -m streamlit run app.py
```

App will launch at:

```text
http://localhost:8501
```

---

# Run Tests

```bash
pytest tests.py -v
```

---

# Streamlit Features

## Upload CSV

- Upload datasets
- Select target column
- Configure thresholds
- Run matching

---

## Adjustable Thresholds

| Classification | Default Threshold |
|---|---|
| Strong Match | ≥ 0.85 |
| Possible Match | ≥ 0.60 |
| No Match | < 0.60 |

---

## Export Results

- Download matched pairs
- Export explanations and scores
- CSV output support

---

# Example Usage

## Compare Two Names

```python
from scoring import compare_two_names

result = compare_two_names(
    "Jon Smith",
    "John Smyth"
)

print(result)
```

---

## Batch Entity Resolution

```python
from scoring import resolve_entities

matches = resolve_entities(
    names,
    threshold=0.85
)
```

---

# Example Output

| Name 1 | Name 2 | Score | Classification |
|---|---|---|---|
| John Smith | Jon Smyth | 0.91 | Strong Match |
| Microsoft Corp | Microsoft Corporation | 0.96 | Strong Match |
| Apple Inc | Apply Ink | 0.62 | Possible Match |

---

# Project Workflow

```text
Raw Names
   ↓
Preprocessing
   ↓
Blocking
   ↓
Candidate Generation
   ↓
Similarity Scoring
   ↓
Weighted Fusion
   ↓
Threshold Classification
   ↓
Results + Explainability
```

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Frontend UI |
| RapidFuzz | Fast fuzzy matching |
| Jellyfish | Phonetic encoding |
| Pandas | Data handling |
| Pytest | Testing |

---

# Performance

| Dataset Size | Approx Comparisons After Blocking |
|---|---|
| 1,000 | ~5k |
| 10,000 | ~50k |
| 100,000 | ~500k |

Blocking reduces comparisons by up to 99%.

---

# Future Improvements

- GPU acceleration
- Embedding-based semantic similarity
- Distributed batch processing
- API deployment
- Real-time matching service
- Active learning feedback loop

---

# Use Cases

- Customer deduplication
- CRM cleanup
- Master Data Management
- Fraud detection
- Identity resolution
- Healthcare record linkage
- Search systems

---

# License

MIT License

---

# Author

Anoushka Navale

GitHub:
https://github.com/AnoushkaNavale/Fuzzy-Name-Matching