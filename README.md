# Entity Resolution System

A scalable, production-level fuzzy name matching system with a Streamlit UI.

---

## Architecture

```
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

### Module responsibilities

| Module | Responsibility |
|---|---|
| `preprocessing.py` | Normalize text: strip accents, lowercase, remove punctuation. All other modules call `normalize()` before any comparison. |
| `blocking.py` | Group names into blocks by a key so only likely pairs are compared. Reduces O(n²) to O(n·k). |
| `matching.py` | Four independent similarity functions, each returning [0, 1]. |
| `scoring.py` | Weighted fusion of the four signals, threshold classification, explainability, batch processing. |
| `app.py` | Streamlit UI: CSV upload, slider controls, tabbed results, CSV export. |

---

## Similarity Algorithms

| Algorithm | What it catches | Library |
|---|---|---|
| **Levenshtein** | Typos, misspellings | RapidFuzz |
| **Token Sort** | First/last name swaps | RapidFuzz |
| **Jaccard (bigrams)** | Character-level OCR noise | Pure Python |
| **Phonetic** (Soundex + Metaphone + NYSIIS) | Sound-alike variants | Jellyfish |

Final score = `0.35·lev + 0.30·tok + 0.20·jac + 0.15·pho` (weights adjustable)

---

## Blocking Strategies

| Strategy | Key | Use when |
|---|---|---|
| `first_letter` | First character | Fastest, good default |
| `token` | Each word in the name | Better recall, slightly slower |
| `ngram` | Leading N characters | Middle ground |

---

## Setup

```bash
pip install -r requirements.txt
```

## Run the UI

```bash
streamlit run app.py
```

## Run tests

```bash
pytest tests.py -v
```

---

## Scalability

- **Blocking** cuts comparisons from O(n²) to O(n·k) where k = avg block size
- **Batch processing**: `resolve_in_batches()` processes in configurable chunks with progress callbacks — streams into Streamlit progress bars without memory spikes
- **RapidFuzz** replaces fuzzywuzzy with C-level implementations (10-100× faster)
- **Corpus index** is built once per run and reused across all query batches

---

## Thresholds

| Classification | Default score range |
|---|---|
| Strong Match | ≥ 0.85 |
| Possible Match | ≥ 0.60 |
| No Match | < 0.60 |

All thresholds are adjustable via the Streamlit sidebar sliders.
