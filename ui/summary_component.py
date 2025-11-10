import streamlit as st
from agents.context_manager import set_context
from agents.summary_agent import generate_page_summary


def display_ai_summary_button(
    page_name: str, 
    button_label: str = "✨ Get AI Summary",
    page_metrics: dict = None
):
    
    #Display an AI summary button that generates on-demand summaries.
    # Create a unique key for this page's summary state
    current_user_id = st.session_state.get('current_user_id', 'unknown')
    summary_key = f"{current_user_id}_{page_name}_summary"
    show_summary_key = f"{current_user_id}_{page_name}_show_summary"
    
    # Initialize state
    if summary_key not in st.session_state:
        st.session_state[summary_key] = None
    if show_summary_key not in st.session_state:
        st.session_state[show_summary_key] = False
    
    # Button to generate/toggle summary
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button(
            button_label, 
            key=f"summary_btn_{page_name}",
            use_container_width=True,
            type="secondary"
        ):
            # Toggle visibility
            if st.session_state[show_summary_key]:
                # Already showing, just hide it
                st.session_state[show_summary_key] = False
            else:
                # Generate new summary if not cached
                if st.session_state[summary_key] is None:
                    with st.spinner("🤖 AI is analyzing your stats..."):
                        # Ensure context is set
                        if st.session_state.get('current_filtered_context') and st.session_state.get('champ_insights') is not None:
                            set_context(
                                st.session_state.current_filtered_context, 
                                st.session_state.champ_insights
                            )
                            
                            summary = generate_page_summary(page_name, page_metrics)
                            st.session_state[summary_key] = summary
                        else:
                            st.session_state[summary_key] = "Error: Player data not loaded"
                
                # Show the summary
                st.session_state[show_summary_key] = True
            
            st.rerun()
    
    # Display summary if toggled on
    if st.session_state[show_summary_key] and st.session_state[summary_key]:
        st.markdown("---")
        st.info(f"**🤖 AI Analysis:**\n\n{st.session_state[summary_key]}")
        st.caption(" :material/lightbulb:    *This summary is based on the statistics shown on this page.*")
        st.markdown("---")