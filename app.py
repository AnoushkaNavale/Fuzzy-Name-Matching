"""
Streamlit Web Interface for Entity Resolution
"""

import streamlit as st
import pandas as pd
import time

# IMPORTANT:
# compare_two_names is inside matching.py
from matching import EntityResolver, compare_two_names

# Page configuration
st.set_page_config(
    page_title="Entity Resolution System",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }

    .result-box {
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }

    .strong {
        background-color: #d4edda;
        color: #155724;
    }

    .possible {
        background-color: #fff3cd;
        color: #856404;
    }

    .weak {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)


def main():

    st.markdown(
        '<div class="main-header">Entity Resolution System</div>',
        unsafe_allow_html=True
    )

    with st.sidebar:

        st.header("Configuration")

        mode = st.radio(
            "Select Mode",
            ["Batch Processing", "Quick Compare"]
        )

        st.markdown("---")

        strong_threshold = st.slider(
            "Strong Match Threshold",
            min_value=70,
            max_value=100,
            value=85
        )

        weak_threshold = st.slider(
            "Possible Match Threshold",
            min_value=50,
            max_value=90,
            value=70
        )

        st.markdown("---")

        blocking_strategy = st.selectbox(
            "Blocking Strategy",
            ["multi", "token", "soundex", "first_letter"]
        )

        st.markdown("---")

        name_type = st.selectbox(
            "Name Type",
            ["general", "person", "organization"]
        )

    if mode == "Batch Processing":

        batch_processing_interface(
            strong_threshold,
            weak_threshold,
            blocking_strategy,
            name_type
        )

    else:
        quick_compare_interface()


def batch_processing_interface(
    strong_threshold,
    weak_threshold,
    blocking_strategy,
    name_type
):

    st.header("Batch Entity Resolution")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:
            df = pd.read_csv(uploaded_file)

            st.success(f"Loaded {len(df)} records")

            with st.expander("Preview Data"):
                st.dataframe(df.head())

            name_column = st.selectbox(
                "Select Name Column",
                options=df.columns.tolist()
            )

            other_columns = [
                col for col in df.columns
                if col != name_column
            ]

            additional_columns = st.multiselect(
                "Additional Columns",
                options=other_columns
            )

            if st.button("Find Matches", type="primary"):

                process_batch(
                    df,
                    name_column,
                    name_type,
                    additional_columns,
                    strong_threshold,
                    weak_threshold,
                    blocking_strategy
                )

        except Exception as e:
            st.error(f"Error: {str(e)}")

    else:

        st.info("Upload a CSV file to begin")

        if st.button("Load Sample Data"):

            df_sample = create_sample_data()

            st.dataframe(df_sample)

            if st.button("Process Sample Data"):

                process_batch(
                    df_sample,
                    "company_name",
                    "organization",
                    [],
                    strong_threshold,
                    weak_threshold,
                    blocking_strategy
                )


def process_batch(
    df,
    name_column,
    name_type,
    additional_columns,
    strong_threshold,
    weak_threshold,
    blocking_strategy
):

    with st.spinner("Processing records..."):

        progress_bar = st.progress(0)

        resolver = EntityResolver(
            strong_threshold=strong_threshold,
            weak_threshold=weak_threshold,
            blocking_strategy=blocking_strategy
        )

        # STEP 1
        progress_bar.progress(20)

        resolver.process_dataframe(
            df,
            name_column,
            name_type,
            additional_columns
        )

        # STEP 2
        progress_bar.progress(50)

        blocking_stats = resolver.create_blocks()

        # STEP 3
        progress_bar.progress(80)

        df_matches = resolver.find_matches()

        progress_bar.progress(100)

        time.sleep(0.5)

        progress_bar.empty()

    st.success(f"Found {len(df_matches)} matches")

    display_statistics(df, df_matches, blocking_stats)

    display_matches(df_matches)


def display_statistics(df, df_matches, blocking_stats):

    st.subheader("Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", len(df))

    with col2:
        st.metric(
            "Candidate Pairs",
            blocking_stats["candidate_pairs"]
        )

    with col3:

        strong_count = len(
            df_matches[
                df_matches["match_type"] == "strong_match"
            ]
        ) if len(df_matches) > 0 else 0

        st.metric("Strong Matches", strong_count)

    with col4:

        possible_count = len(
            df_matches[
                df_matches["match_type"] == "possible_match"
            ]
        ) if len(df_matches) > 0 else 0

        st.metric("Possible Matches", possible_count)

    st.markdown("---")

    reduction = blocking_stats["reduction_ratio"] * 100

    st.metric(
        "Comparison Reduction",
        f"{reduction:.2f}%"
    )


def display_matches(df_matches):

    st.subheader("Match Results")

    if len(df_matches) == 0:
        st.warning("No matches found")
        return

    match_filter = st.multiselect(
        "Filter Match Type",
        ["strong_match", "possible_match"],
        default=["strong_match", "possible_match"]
    )

    filtered_df = df_matches[
        df_matches["match_type"].isin(match_filter)
    ]

    st.write(f"Showing {len(filtered_df)} matches")

    for _, row in filtered_df.iterrows():

        score = row["similarity_score"]

        with st.expander(
            f"{row['name_1']} ↔ {row['name_2']} | Score: {score:.1f}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write("### Match Information")

                st.write(f"Match Type: `{row['match_type']}`")
                st.write(f"Similarity Score: `{score:.1f}`")

            with col2:

                st.write("### Component Scores")

                st.write(
                    f"Levenshtein: {row['levenshtein_score']:.1f}"
                )

                st.write(
                    f"Token Sort: {row['token_sort_score']:.1f}"
                )

                st.write(
                    f"Token Set: {row['token_set_score']:.1f}"
                )

                st.write(
                    f"Jaccard: {row['jaccard_score']:.1f}"
                )

            st.info(row["explanation"])

    st.markdown("---")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="matches.csv",
        mime="text/csv"
    )


def quick_compare_interface():

    st.header("Quick Compare")

    col1, col2 = st.columns(2)

    with col1:
        name1 = st.text_input(
            "First Name",
            placeholder="Enter first name"
        )

    with col2:
        name2 = st.text_input(
            "Second Name",
            placeholder="Enter second name"
        )

    if name1 and name2:

        if st.button("Compare Names", type="primary"):

            result = compare_two_names(
                name1,
                name2,
                return_details=True
            )

            score = result["similarity_score"]
            match_type = result["match_type"]

            if match_type == "strong_match":

                st.markdown(
                    f"""
                    <div class="result-box strong">
                    <h3>Strong Match</h3>
                    <h2>Score: {score:.1f}/100</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif match_type == "possible_match":

                st.markdown(
                    f"""
                    <div class="result-box possible">
                    <h3>Possible Match</h3>
                    <h2>Score: {score:.1f}/100</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"""
                    <div class="result-box weak">
                    <h3>No Match</h3>
                    <h2>Score: {score:.1f}/100</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("---")

            st.subheader("Detailed Scores")

            scores = result["detailed_scores"]

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Levenshtein",
                    f"{scores['levenshtein']:.1f}"
                )

            with c2:
                st.metric(
                    "Token Sort",
                    f"{scores['token_sort']:.1f}"
                )

            with c3:
                st.metric(
                    "Token Set",
                    f"{scores['token_set']:.1f}"
                )

            with c4:
                st.metric(
                    "Jaccard",
                    f"{scores['jaccard']:.1f}"
                )

            st.markdown("---")

            st.subheader("Explanation")

            st.info(result["explanation"])

    with st.expander("Example Comparisons"):

        st.code("Microsoft Corporation ↔ Microsoft Corp")
        st.code("John Smith ↔ Smith John")
        st.code("Apple Inc ↔ Apple Incorporated")
        st.code("Tesla Motors ↔ Tesla Inc")


def create_sample_data():

    data = {
        "company_name": [
            "Microsoft Corporation",
            "Microsoft Corp",
            "Apple Inc",
            "Apple Incorporated",
            "Google LLC",
            "Alphabet Inc",
            "Amazon.com Inc",
            "Amazon Inc",
            "Meta Platforms Inc",
            "Facebook Inc",
            "Tesla Motors",
            "Tesla Inc"
        ]
    }

    return pd.DataFrame(data)


if __name__ == "__main__":
    main()
