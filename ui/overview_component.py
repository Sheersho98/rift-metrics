import streamlit as st
import base64

def display_performance_overview(metrics):
    # Row 1
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        st.metric(
            label="Win Rate", 
            value=f"{metrics['win_rate']:.1f}%",
            help=f"Out of the last {metrics['total_games']} game(s)",
            delta=f"{metrics['recent_5_wr'] - metrics['win_rate']:.1f}% (Over last 5 games)",
        )
    with col2:
        st.metric(
            label="Average KDA",
            value=f"{metrics['avg_kda']:.2f}",
            delta=f"{metrics['recent_5_kda'] - metrics['avg_kda']:.2f} (Over last 5 games)"
        )
    with col3:
        st.metric(
            label="K / D / A", 
            value=f"{metrics['avg_kills']:.1f} / {metrics['avg_deaths']:.1f} / {metrics['avg_assists']:.1f}"
        )

        
def display_player_info_card(riot_id, tag_line, icon_id):
    from api.riot_api import get_profile_icon_url
    
    col1, col2 = st.columns([0.3, 2])
    
    with col1:
        st.image(get_profile_icon_url(icon_id), width=80)
    
    with col2:
        st.markdown(f"### {riot_id}")
        st.markdown(f"<span style='color: #888; font-weight: 300;'>#{tag_line}</span>", unsafe_allow_html=True)

def display_rank_info_card(rank_data):
    if rank_data:
        col1, col2 = st.columns([1, 1])
        with col1:
            # Solo/Duo rank with image
            if rank_data.get('solo'):
                solo = rank_data['solo']
                formatted_tier = solo['tier'].title()
                rank_img_path = f"assets/ranks/Rank={formatted_tier}.png"
                
                try:
                    with open(rank_img_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                    
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <div style='filter: drop-shadow(0 0 10px rgba(219, 196, 66, 0.5));'>
                                <img src='data:image/png;base64,{img_data}' style='width: 150px;'/>
                            </div>
                            <p style='font-weight: bold; margin-top: 10px; margin-bottom: 5px;'>SOLO/DUO</p>
                            <p style='margin: 0; color: #888;'>{solo['wins']} Wins | {solo['lp']} LP</p>
                        </div>
                    """, unsafe_allow_html=True)
                except:
                    st.write(f"{solo['tier']} {solo['rank']}")
            else:
                st.info("**Unranked**\nSolo/Duo")
        
        with col2:
            # Flex rank with image
            if rank_data.get('flex'):
                flex = rank_data['flex']
                formatted_tier = flex['tier'].title()
                rank_img_path = f"assets/ranks/Rank={formatted_tier}.png"
                
                try:
                    with open(rank_img_path, "rb") as f:
                        img_data = base64.b64encode(f.read()).decode()
                    
                    st.markdown(f"""
                        <div style='text-align: center;'>
                            <img src='data:image/png;base64,{img_data}' style='width: 150px;'/>
                            <p style='font-weight: bold; margin-top: 10px; margin-bottom: 5px;'>FLEX 5V5</p>
                            <p style='margin: 0; color: #888;'>{flex['wins']} Wins | {flex['lp']} LP</p>
                        </div>
                    """, unsafe_allow_html=True)
                except:
                    st.write(f"{flex['tier']} {flex['rank']}")
            else:
                st.info("**Unranked**\nFlex")

def display_playstyle_tags(tags: dict):
    strengths = tags.get('strengths', [])
    weaknesses = tags.get('weaknesses', [])
    neutral = tags.get('neutral', [])
    
    # Combine all tags - show all of them, no artificial limits
    all_tags = []
    
    for tag in strengths:  # Show all strengths
        all_tags.append({
            'label': tag['label'],
            'tooltip': tag['tooltip'],
            'type': 'strength'
        })
    
    for tag in weaknesses:  # Show all weaknesses
        all_tags.append({
            'label': tag['label'],
            'tooltip': tag['tooltip'],
            'type': 'weakness'
        })
    
    for tag in neutral:  # Show all neutral
        all_tags.append({
            'label': tag['label'],
            'tooltip': tag['tooltip'],
            'type': 'neutral'
        })
    
    if not all_tags:
        return ""  # Return empty string if no tags
    
    # Build compact HTML badges with flexbox for natural flow and tight grouping
    # Use proper HTML structure that won't be escaped
    badges_html = """<div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; margin-bottom: 12px; align-items: center;">"""
    # In your components.py display_playstyle_tags function, update the style:
    
    for tag in all_tags:
        if tag['type'] == 'strength':
            bg_color = 'rgba(26, 77, 46, 0.9)'
            text_color = '#2ecc71'
            border_color = 'rgba(46, 204, 113, 0.3)'
        elif tag['type'] == 'weakness':
            bg_color = 'rgba(77, 26, 26, 0.9)'
            text_color = '#e74c3c'
            border_color = 'rgba(231, 76, 60, 0.3)'
        else:  # neutral
            bg_color = 'rgba(77, 61, 26, 0.9)'
            text_color = '#f39c12'
            border_color = 'rgba(243, 156, 18, 0.3)'
        
        # Escape any HTML in label and tooltip
        label_escaped = tag['label'].replace('<', '&lt;').replace('>', '&gt;')
        tooltip_escaped = tag['tooltip'].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        badges_html += f"""<span style="display: inline-flex; align-items: center; justify-content: center; background-color: {bg_color}; color: {text_color}; padding: 5px 12px; border-radius: 12px; border: 1px solid {border_color}; font-size: 13px; font-weight: 600; white-space: nowrap; line-height: 1.2; cursor: default;" title="{tooltip_escaped}">{label_escaped}</span>"""
    
    badges_html += """</div>"""
    
    return badges_html

def render_overview_tab(data_package, queue_type):
    
    metrics = data_package['metrics']
    filtered_game_count = data_package['filtered_count']

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("## Overview")

    st.markdown("---")

    st.markdown("#### :material/sports_score:    Season Performance")
    # Rank display
    if 'rank_data' in st.session_state:
        display_rank_info_card(st.session_state.rank_data)
    else:
        st.info("Rank data not available")
    
    st.markdown("---")

    # Performance metrics
    display_performance_overview(metrics)
    st.markdown("---")
    
    # Playstyle section with generation logic
    st.markdown("#### :material/chess_knight:   Your Playstyle")
    current_user_id = st.session_state.get('current_user_id', 'unknown')
    #playstyle_key = f"playstyle_{current_user_id}" #_{queue_type}_{filtered_game_count}
    if filtered_game_count >= 10:
        
        playstyle, playstyle_desc = st.session_state.playstyle

        st.info(f"**{playstyle}**\n\n{playstyle_desc}")
        st.caption(" :material/lightbulb:    *This analysis is based on your performance patterns across all games.*")
        st.markdown("---")
    else:
        st.info("Play 10 or more games in ranked to get your AI powered Playstyle Analysis")
    

    
        
    