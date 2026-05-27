"""
Streamlit Web Interface for Entity Resolution
"""

import streamlit as st
import pandas as pd
import time
from entity_resolution import EntityResolver, compare_two_names

# Page configuration
st.set_page_config(
    page_title="Entity Resolution System",
    page_icon="🔍",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .strong-match {
        background-color: #d4edda;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        color: #155724;
    }
    .possible-match {
        background-color: #fff3cd;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<div class="main-header">🔍 Entity Resolution System</div>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        mode = st.radio(
            "Select Mode",
            ["Batch Processing", "Quick Compare"],
            help="Batch: Upload CSV file | Quick: Compare two names"
        )
        
        st.markdown("---")
        
        # Threshold settings
        st.subheader("Similarity Thresholds")
        strong_threshold = st.slider(
            "Strong Match",
            min_value=70,
            max_value=100,
            value=85,
            help="Score above this = Strong Match"
        )
        
        weak_threshold = st.slider(
            "Possible Match",
            min_value=50,
            max_value=90,
            value=70,
            help="Score above this = Possible Match"
        )
        
        st.markdown("---")
        
        # Blocking strategy
        st.subheader("Blocking Strategy")
        blocking_strategy = st.selectbox(
            "Strategy",
            ["multi", "token", "soundex", "first_letter"],
            help="Multi = combination of strategies for best results"
        )
        
        st.markdown("---")
        
        # Name type
        name_type = st.selectbox(
            "Name Type",
            ["general", "person", "organization"],
            help="Affects preprocessing rules"
        )
    
    # Main content
    if mode == "Batch Processing":
        batch_processing_interface(
            strong_threshold, 
            weak_threshold, 
            blocking_strategy,
            name_type
        )
    else:
        quick_compare_interface()


def batch_processing_interface(strong_threshold, weak_threshold, blocking_strategy, name_type):
    """Interface for batch CSV processing"""
    
    st.header("📊 Batch Entity Resolution")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help="Upload a CSV file with names to match"
    )
    
    if uploaded_file is not None:
        # Load data
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✓ Loaded {len(df)} records")
            
            # Show preview
            with st.expander("Preview Data"):
                st.dataframe(df.head(10))
            
            # Column selection
            name_column = st.selectbox(
                "Select column with names",
                options=df.columns.tolist()
            )
            
            # Additional columns to keep
            other_columns = [col for col in df.columns if col != name_column]
            if other_columns:
                additional_columns = st.multiselect(
                    "Additional columns to include (optional)",
                    options=other_columns
                )
            else:
                additional_columns = None
            
            # Process button
            if st.button("🚀 Find Matches", type="primary"):
                process_batch(
                    df, name_column, name_type, additional_columns,
                    strong_threshold, weak_threshold, blocking_strategy
                )
        
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
    
    else:
        # Show sample data option
        st.info("💡 Upload a CSV file or try with sample data")
        
        if st.button("Load Sample Data"):
            df_sample = create_sample_data()
            st.session_state['sample_data'] = df_sample
            st.dataframe(df_sample)
            
            if st.button("Process Sample Data"):
                process_batch(
                    df_sample, 'company_name', 'organization', None,
                    strong_threshold, weak_threshold, blocking_strategy
                )


def process_batch(df, name_column, name_type, additional_columns, 
                  strong_threshold, weak_threshold, blocking_strategy):
    """Process batch matching"""
    
    with st.spinner("Processing..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize resolver
        resolver = EntityResolver(
            strong_threshold=strong_threshold,
            weak_threshold=weak_threshold,
            blocking_strategy=blocking_strategy
        )
        
        # Step 1: Preprocessing
        status_text.text("Step 1/3: Preprocessing data...")
        progress_bar.progress(20)
        time.sleep(0.3)
        
        resolver.process_dataframe(df, name_column, name_type, additional_columns)
        
        # Step 2: Blocking
        status_text.text("Step 2/3: Creating blocks...")
        progress_bar.progress(50)
        time.sleep(0.3)
        
        blocking_stats = resolver.create_blocks()
        
        # Step 3: Matching
        status_text.text("Step 3/3: Finding matches...")
        progress_bar.progress(80)
        time.sleep(0.3)
        
        df_matches = resolver.find_matches()
        
        progress_bar.progress(100)
        status_text.text("✓ Complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
    
    # Display results
    st.success(f"✓ Found {len(df_matches)} matches!")
    
    # Statistics
    display_statistics(df, df_matches, blocking_stats)
    
    # Matches
    display_matches(df_matches)


def display_statistics(df, df_matches, blocking_stats):
    """Display statistics in metrics"""
    
    st.subheader("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Candidate Pairs", f"{blocking_stats['candidate_pairs']:,}")
    
    with col3:
        strong_count = len(df_matches[df_matches['match_type'] == 'strong_match']) if len(df_matches) > 0 else 0
        st.metric("Strong Matches", strong_count)
    
    with col4:
        possible_count = len(df_matches[df_matches['match_type'] == 'possible_match']) if len(df_matches) > 0 else 0
        st.metric("Possible Matches", possible_count)
    
    # Additional stats
    col5, col6, col7 = st.columns(3)
    
    with col5:
        reduction = blocking_stats['reduction_ratio'] * 100
        st.metric("Comparison Reduction", f"{reduction:.1f}%")
    
    with col6:
        avg_score = df_matches['similarity_score'].mean() if len(df_matches) > 0 else 0
        st.metric("Avg Similarity", f"{avg_score:.1f}")
    
    with col7:
        st.metric("Total Blocks", blocking_stats['total_blocks'])


def display_matches(df_matches):
    """Display match results"""
    
    if len(df_matches) == 0:
        st.warning("No matches found above the threshold")
        return
    
    st.subheader("🎯 Matches Found")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        match_filter = st.multiselect(
            "Filter by match type",
            options=['strong_match', 'possible_match'],
            default=['strong_match', 'possible_match']
        )
    
    with col2:
        min_display_score = st.slider(
            "Minimum score to display",
            min_value=0,
            max_value=100,
            value=70
        )
    
    # Filter dataframe
    df_filtered = df_matches[
        (df_matches['match_type'].isin(match_filter)) &
        (df_matches['similarity_score'] >= min_display_score)
    ]
    
    st.write(f"Showing {len(df_filtered)} of {len(df_matches)} matches")
    
    # Display matches
    for idx, row in df_filtered.iterrows():
        with st.expander(
            f"**{row['name_1']}** ↔ **{row['name_2']}** "
            f"(Score: {row['similarity_score']:.1f})"
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Details:**")
                st.write(f"• Match Type: `{row['match_type']}`")
                st.write(f"• Overall Score: `{row['similarity_score']:.1f}`")
            
            with col2:
                st.write("**Component Scores:**")
                st.write(f"• Levenshtein: `{row['levenshtein_score']:.1f}`")
                st.write(f"• Token Sort: `{row['token_sort_score']:.1f}`")
                st.write(f"• Token Set: `{row['token_set_score']:.1f}`")
                st.write(f"• Jaccard: `{row['jaccard_score']:.1f}`")
            
            st.write("**Explanation:**")
            st.info(row['explanation'])
    
    # Download results
    st.markdown("---")
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name="entity_matches.csv",
        mime="text/csv"
    )


def quick_compare_interface():
    """Interface for comparing two names"""
    
    st.header("⚡ Quick Name Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name1 = st.text_input("Name 1", placeholder="Enter first name...")
    
    with col2:
        name2 = st.text_input("Name 2", placeholder="Enter second name...")
    
    if name1 and name2:
        if st.button("Compare", type="primary"):
            result = compare_two_names(name1, name2, return_details=True)
            
            # Display result
            st.markdown("---")
            
            score = result['similarity_score']
            match_type = result['match_type']
            
            # Score display with color
            if match_type == 'strong_match':
                st.success(f"### Strong Match! (Score: {score:.1f}/100)")
            elif match_type == 'possible_match':
                st.warning(f"### Possible Match (Score: {score:.1f}/100)")
            else:
                st.error(f"### No Match (Score: {score:.1f}/100)")
            
            # Detailed scores
            st.subheader("Detailed Scores")
            
            scores = result['detailed_scores']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Levenshtein", f"{scores['levenshtein']:.1f}")
            with col2:
                st.metric("Token Sort", f"{scores['token_sort']:.1f}")
            with col3:
                st.metric("Token Set", f"{scores['token_set']:.1f}")
            with col4:
                st.metric("Jaccard", f"{scores['jaccard']:.1f}")
            
            # Explanation
            st.info(f"**Why this score?** {result['explanation']}")
    
    # Examples
    with st.expander("💡 Try These Examples"):
        st.write("**High Similarity:**")
        st.code("Microsoft Corporation ↔ Microsoft Corp")
        st.code("John Smith ↔ Smith, John")
        
        st.write("\n**Medium Similarity:**")
        st.code("Catherine Williams ↔ Katherine Williams")
        st.code("ABC Inc ↔ ABC Company")
        
        st.write("\n**Low Similarity:**")
        st.code("Apple Inc ↔ Microsoft Corp")


def create_sample_data():
    """Create sample data for demonstration"""
    data = {
        'company_name': [
            'Microsoft Corporation',
            'Microsoft Corp',
            'Apple Inc',
            'Apple Incorporated',
            'Google LLC',
            'Alphabet Inc',
            'Amazon.com Inc',
            'Amazon Inc',
            'Meta Platforms Inc',
            'Facebook Inc',
            'Tesla Motors',
            'Tesla Inc',
        ]
    }
    return pd.DataFrame(data)


if __name__ == "__main__":
    main()
