from difflib import SequenceMatcher

# ---------------- Normalization ----------------
def normalize_name(name):
    """
    Handles obstacles like case sensitivity and extra spaces
    """
    return name.lower().strip()

# ---------------- Soundex Algorithm ----------------
def soundex(name):
    """
    Handles phonetic variations in names
    """
    name = name.upper()
    soundex_code = name[0]

    mappings = {
        "BFPV": "1",
        "CGJKQSXZ": "2",
        "DT": "3",
        "L": "4",
        "MN": "5",
        "R": "6"
    }

    def get_digit(char):
        for key in mappings:
            if char in key:
                return mappings[key]
        return "0"

    for char in name[1:]:
        digit = get_digit(char)
        if digit != soundex_code[-1]:
            soundex_code += digit

    soundex_code = soundex_code.replace("0", "")
    return soundex_code[:4].ljust(4, "0")

# ---------------- Similarity ----------------
def similarity_score(name1, name2):
    return SequenceMatcher(None, name1, name2).ratio()

# ---------------- Matching Logic ----------------
def match_names(list_a, list_b, threshold=0.85):
    matches = []

    for a in list_a:
        for b in list_b:
            norm_a = normalize_name(a)
            norm_b = normalize_name(b)

            similarity = similarity_score(norm_a, norm_b)
            phonetic_match = soundex(norm_a) == soundex(norm_b)

            if similarity >= threshold or phonetic_match:
                matches.append({
                    "Name_1": a,
                    "Name_2": b,
                    "Similarity": round(similarity, 2),
                    "Phonetic_Match": phonetic_match
                })
    return matches

# ---------------- Sample Data ----------------
dataset_1 = [
    "Anoushka Navale",
    "Rohit Sharma",
    "Siddharth Mehta"
]

dataset_2 = [
    "Anushka Navale",
    "Rohit K Sharma",
    "Sid Mehta"
]

# ---------------- Execution ----------------
results = match_names(dataset_1, dataset_2)

for result in results:
    print(result)
