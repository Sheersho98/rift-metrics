import streamlit as st
import pandas as pd

from utils.helpers import get_champion_icon_url
from ui.summary_component import display_ai_summary_button

def render_matchup_analysis(selected_queue_display):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Matchup Analysis")
    
    st.markdown("---")
    # Get matchup data from filtered context
    if st.session_state.current_filtered_context:
        matchup_data = st.session_state.current_filtered_context.get('matchup_data', {})
        
        if not matchup_data:
            st.warning(f"Not enough matchup data available for {selected_queue_display}. Play more games!")
        else:
            # Filter matchups with at least 2 games
            valid_matchups = {k: v for k, v in matchup_data.items() if v['games'] >= 2}
            
            if not valid_matchups:
                st.info(f"Need at least 2 games per matchup to show reliable stats in {selected_queue_display}.")
            else:
                # Sort by win rate
                sorted_matchups = sorted(valid_matchups.items(), key=lambda x: x[1]['win_rate'], reverse=True)
                
                st.markdown("### :material/trophy:    Best Matchups (60%+ Win Rate)")
                
                best_matchups = [(k, v) for k, v in sorted_matchups if v['win_rate'] >= 60]
                
                if best_matchups:
                    for matchup_key, data in best_matchups[:5]:
                        matchup_header = f"""
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 15px">
                        <img src="{get_champion_icon_url(data['my_champion'])}" width="30" style="border-radius: 50%;">
                        <span style="font-weight: bold;">{data['my_champion']}</span>
                        <span>vs</span>
                        <img src="{get_champion_icon_url(data['opponent'])}" width="30" style="border-radius: 50%;">
                        <span style="font-weight: bold;">{data['opponent']}</span>
                        <span style="margin-left: 8px;">- {data['win_rate']:.0f}% WR ({data['games']} games)</span>
                    </div>
                    """
                        st.markdown(matchup_header, unsafe_allow_html=True)
                        expander_title = f"{data['my_champion']} vs {data['opponent']} Details"

                        with st.expander(" :material/check_circle:    " + expander_title, expanded=False):
                            display_matchup_details(data)
                else:
                    st.info("No matchups with 60%+ win rate yet. Keep playing!")
                
                st.markdown("---")
                
                st.markdown("### :material/dangerous:    Worst Matchups (Below 40% Win Rate)")
                
                worst_matchups = [(k, v) for k, v in sorted_matchups if v['win_rate'] < 40]
                
                if worst_matchups:
                    for matchup_key, data in reversed(worst_matchups[-5:]):
                        with st.expander(f" :material/warning:    {data['my_champion']} vs {data['opponent']} - {data['win_rate']:.0f}% WR ({data['games']} games)"):
                            display_matchup_details(data)
                else:
                    st.success("No particularly bad matchups! Great job adapting.")
                
                st.markdown("---")
                
                st.markdown("### :material/swords:    All Matchups")
                
                matchup_df = pd.DataFrame([
                    {
                        'Your Champion': v['my_champion'],
                        'Opponent': v['opponent'],
                        'Role': 'SUPPORT' if v.get('role') == 'UTILITY' else v.get('role', 'N/A'),
                        'Games': v['games'],
                        'WR': f"{v['win_rate']:.0f}%",
                        'KDA': f"{v['avg_kda']:.2f}",
                        'DPM': f"{v.get('avg_dpm', 0):.0f}",
                    }
                    for k, v in sorted_matchups
                ])
                
                st.dataframe(matchup_df, use_container_width=True, hide_index=True)
                # AI Summary Button
                st.markdown("---")
                display_ai_summary_button('matchup_analysis', "✨ Get AI Matchup Summary")
    else:
        st.error("Context not loaded. Please fetch match data first.")


def display_matchup_details(data: dict):
    """Helper function to display matchup details based on role"""
    role = data.get('role', 'UNKNOWN')
    
    # Top row: Core stats (ALWAYS SHOWN)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("KDA", f"{data['avg_kda']:.2f}", help="Kill/Death/Assist ratio in this matchup")
    
    with col2:
        st.metric("Win Rate", f"{data['win_rate']:.0f}%", help="Your success rate in this matchup")
    
    with col3:
        st.metric("Games", f"{data['games']}", help="Sample size for this matchup")
    
    with col4:
        st.metric("Avg DPM", f"{data['avg_dpm']:.0f}", help="Average damage per minute")
    
    st.markdown("---")
    
    # Bottom row: Role-specific stats
    if role in ['TOP', 'MIDDLE', 'BOTTOM']:
        # LANER stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**CS Diff @10**")
            st.write(f"{data.get('avg_cs_diff', 0):+.0f}")
            st.caption("CS advantage at 10 min")
        
        with col2:
            st.write("**Avg CS**")
            st.write(f"{data['avg_cs']:.0f}")
            st.caption("Total CS per game")
        
        with col3:
            st.write("**Avg Damage**")
            st.write(f"{data['avg_damage']:,.0f}")
            st.caption("Damage to champions")
    
    elif role == 'JUNGLE':
        # JUNGLE stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Jungle CS Diff @10**")
            st.write(f"{data.get('avg_jungle_cs_diff', 0):+.0f}")
            st.caption("Jungle CS advantage")
        
        with col2:
            st.write("**Avg Epic Monsters**")
            st.write(f"{data.get('avg_epic_monsters', 0):.1f}")
            st.caption("Dragons + Barons")
        
        with col3:
            st.write("**Scuttle Control**")
            st.write(f"{data.get('avg_scuttles', 0):.1f}")
            st.caption("Scuttles per game")
    
    elif role == 'UTILITY':
        # SUPPORT stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Vision @10**")
            st.write(f"{data.get('avg_vision_at_10', 0):.1f}")
            st.caption("Vision score at 10 min")
        
        with col2:
            st.write("**Avg Vision Score**")
            st.write(f"{data.get('avg_cs', 0):.0f}")  # This should be actual vision score, need to track separately
            st.caption("Total vision per game")
        
        with col3:
            st.write("**Heal/Shield**")
            st.write(f"{data.get('avg_heal_shield', 0):,.0f}")
            st.caption("Effective healing/shielding")
    
    # Matchup Status (role-aware with fallback)
    col1, col2, col3 = st.columns(3)
    with col3:
        st.write("**Matchup Status**")
        
        # Determine role with fallback
        if role in ['TOP', 'MIDDLE', 'BOTTOM']:
            # Laner: based on CS diff and KDA
            is_dominant = data.get('avg_cs_diff', 0) > 10 and data.get('avg_kda', 0) > 3
            is_struggling = data.get('avg_cs_diff', 0) < -10 or data.get('avg_kda', 0) < 2
        elif role == 'JUNGLE':
            # Jungler: based on jungle CS diff and epic monsters
            is_dominant = data.get('avg_jungle_cs_diff', 0) > 5 and data.get('avg_epic_monsters', 0) > 1.5
            is_struggling = data.get('avg_jungle_cs_diff', 0) < -5 or data.get('avg_epic_monsters', 0) < 0.8
        elif role == 'UTILITY':
            # Support: based on vision and KDA
            is_dominant = data.get('avg_vision_at_10', 0) > 8 and data.get('avg_kda', 0) > 3
            is_struggling = data.get('avg_vision_at_10', 0) < 5 or data.get('avg_kda', 0) < 2
        else:
            # Fallback for old data without role: use KDA and damage only
            is_dominant = data.get('avg_kda', 0) > 3.5 and data.get('avg_damage', 0) > 15000
            is_struggling = data.get('avg_kda', 0) < 2
        
        if is_dominant:
            st.success(" :material/mode_heat:    Dominant")
            st.caption("Winning matchup")
        elif is_struggling:
            st.error(" :material/warning:    Struggling")
            st.caption("Difficult matchup")
        else:
            st.info(" :material/swords:    Competitive")
            st.caption("Even matchup")