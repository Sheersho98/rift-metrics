import streamlit as st
from agents.context_manager import set_context
from agents.agents import initialize_chat_coach

def render_ai_coach(filtered_game_count, selected_queue_display):
    #st.markdown("## :material/robot_2:    AI Coaching Session")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## AI Coaching Session")
    
    st.markdown("---")

    st.caption(" :material/robot_2:   Ask your personal AI coach anything about your performance, champions, or how to improve!")
    
    

    if filtered_game_count < 10:
        st.info(f"Need **at least 10 games** in {selected_queue_display} to provide meaningful AI analysis. You have only **{filtered_game_count}** game(s) recorded.")
        st.caption("Play a few more games in this queue and come back for a full analysis!")

    elif st.session_state.current_filtered_context and st.session_state.champ_insights is not None:
        # Update context with filtered data
        set_context(st.session_state.current_filtered_context, st.session_state.champ_insights)

        with st.expander(" :material/info:    What stats does the AI coach have access to?"):
            st.markdown(f"""
            Your coach has access to **comprehensive data from {selected_queue_display}** including:
            - :material/check_box:    **Combat**: KDA, damage dealt/taken, kill participation
            - :material/check_box:    **Farming**: CS, gold earned, CS@10 minutes
            - :material/check_box:    **Vision**: Vision score, wards placed/destroyed
            - :material/check_box:    **Win vs Loss**: All stats compared between wins and losses
            - :material/check_box:    **Champion Pool**: Performance on each champion
            - :material/check_box:    **Match History**: Full details of your recent games
            
            Ask specific questions like:
            - "Why do I die more in losses?"
            - "How's my CS compared to my rank?"
            - "What's my weakest stat?"
            - "Should I focus on vision or damage?"
            """)
        
        # (Rest of your AI coaching code remains the same)
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        st.caption("Example questions: 'Why do I die more in losses?' • 'How's my farming?' • 'What should I improve?'")
        if prompt := st.chat_input("Ask your coach anything about your performance..."):
            
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
            
            with chat_container:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    
                    try:
                        with st.spinner("Coach is analyzing your stats..."):
                            coach = initialize_chat_coach()
                            coach_response = coach(prompt)
                            full_response = str(coach_response)
                        
                        message_placeholder.markdown(full_response)
                        
                    except Exception as e:
                        error_msg = f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
                        message_placeholder.markdown(error_msg)
                        full_response = error_msg
            
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        
        if len(st.session_state.chat_history) > 0:
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button(" :material/delete:    Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()