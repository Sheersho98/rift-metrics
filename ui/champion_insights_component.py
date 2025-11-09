import streamlit as st
import pandas as pd
from ui.summary_component import display_ai_summary_button
from utils.helpers import get_champion_icon_url

def render_champion_insights(champ_insights, metrics):
    #st.markdown("## :material/search_insights:    Champion Performance Breakdown")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Champion Insights")

    st.markdown("---")

    st.markdown("### :material/article:    Understanding the Tier System")
    
    with st.expander(":material/info:    **How are champions ranked into tiers?** Click to learn more", expanded=True):
        st.markdown("""
        Your champions are automatically sorted into **performance tiers** based on two key metrics:
        - **KDA (Kill/Death/Assist ratio)** - Your combat effectiveness
        - **Win Rate** - Your success rate with that champion
        
        Here's what each tier means:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **:material/crown:    A-Tier** - Your Best Picks
            - KDA ≥ 4.0 AND Win Rate ≥ 60%
            - **Requires 5+ games** for proven consistency
            - Exceptional performance
            - Play these when you want to win
            
            **:material/star:    B-Tier** - Strong Performers  
            - KDA ≥ 3.0 AND Win Rate ≥ 50%
            - **Requires 3+ games** minimum
            - Reliable, solid performance
            - Safe picks for ranked
            """)
        
        with col2:
            st.markdown("""
            **:material/trending_down:    C-Tier** - Average Performance
            - KDA ≥ 2.0
            - Room for improvement
            - Practice to move up tiers
            
            **:material/dangerous:    D-Tier** - Struggling
            - KDA < 2.0
            - Below average performance
            - Consider dropping or practicing
            """)
        
        st.info(" :material/lightbulb:    **Important:** Champions with only 1-2 games may rank high but need more matches for reliable data.")
    
    st.markdown("---")
    
    # Champion tier list (rest of your existing champion insights code)
    st.markdown("### :material/format_list_numbered:    Your Champion Tier List")
    
    tier_counts = champ_insights['Tier'].value_counts()
    
    tier_info = {
        'A-Tier': {'icon': ':material/crown:', 'color': '#FFD700', 'desc': 'Elite Performance', 'badge': ':material/trophy:    Mastered'},
        'B-Tier': {'icon': ':material/star:', 'color': '#C0C0C0', 'desc': 'Strong Pick', 'badge': ':material/exercise:    Strong'},
        'C-Tier': {'icon': ':material/trending_down:', 'color': '#CD7F32', 'desc': 'Average', 'badge': ':material/rule:    Improving'},
        'D-Tier': {'icon': ':material/dangerous:', 'color': '#808080', 'desc': 'Needs Work', 'badge': ':material/warning:    Practice'}
    }
    
    for tier in ['A-Tier', 'B-Tier', 'C-Tier', 'D-Tier']:
        tier_champs = champ_insights[champ_insights['Tier'] == tier]
        if len(tier_champs) > 0:
            tier_data = tier_info[tier]
            
            expander_title = f"{tier_data['icon']} **{tier}** ({len(tier_champs)} champions) - {tier_data['desc']}"
            
            with st.expander(expander_title, expanded=(tier in ['A-Tier', 'B-Tier'])):
                for _, row in tier_champs.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1.5, 1.5, 1, 1.5])

                    with col1:
                        st.image(get_champion_icon_url(row['Champion']), width=40)
                    with col2:
                        st.markdown(f"**{row['Champion']}**")
                    with col3:
                        st.write(f"KDA: **{row['Avg_KDA']:.1f}**")
                    with col4:
                        st.write(f"WR: **{row['Win_Rate']:.1f}%**")
                    with col5:
                        games_count = int(row['Games'])
                        st.write(f"**{games_count}** games")
                    with col6:
                        if games_count == 1:
                            st.caption(":material/warning:    Small sample")
                        else:
                            st.caption(tier_data['badge'])
    st.markdown("---")
    
    st.markdown("### :material/analytics:    Detailed Statistics")
    
    # Keep numeric columns as numbers for proper sorting
    display_df = champ_insights[['Champion', 'Games', 'Win_Rate', 'Avg_KDA', 
                                    'Avg_Kills', 'Avg_Deaths', 'Avg_Assists', 'Tier']].copy()
    
    # Format numbers for display but keep them numeric
    display_df['Games'] = display_df['Games'].astype(int)
    display_df['Win_Rate'] = display_df['Win_Rate'].round(1)
    display_df['Avg_KDA'] = display_df['Avg_KDA'].round(1)
    display_df['Avg_Kills'] = display_df['Avg_Kills'].round(1)
    display_df['Avg_Deaths'] = display_df['Avg_Deaths'].round(1)
    display_df['Avg_Assists'] = display_df['Avg_Assists'].round(1)
    
    # Add numeric tier rank for proper sorting (S=1, A=2, B=3, C=4)
    tier_order = ['A-Tier', 'B-Tier', 'C-Tier', 'D-Tier']
    display_df['Tier'] = pd.Categorical(display_df['Tier'], categories=tier_order, ordered=True)
    
    # Reorder columns to put Tier_Rank before Tier (for sorting reference)
    display_df = display_df[['Champion', 'Games', 'Win_Rate', 'Avg_KDA', 
                                'Avg_Kills', 'Avg_Deaths', 'Avg_Assists', 'Tier']]
    
    # Sort by Tier_Rank by default
    display_df = display_df.sort_values('Tier')
    
    # Configure column display with proper formatting
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Champion": st.column_config.TextColumn("Champion", width="medium"),
            "Games": st.column_config.NumberColumn("Games", format="%d"),
            "Win_Rate": st.column_config.NumberColumn("Win Rate", format="%.1f%%"),
            "Avg_KDA": st.column_config.NumberColumn("Avg KDA", format="%.1f"),
            "Avg_Kills": st.column_config.NumberColumn("Avg Kills", format="%.1f"),
            "Avg_Deaths": st.column_config.NumberColumn("Avg Deaths", format="%.1f"),
            "Avg_Assists": st.column_config.NumberColumn("Avg Assists", format="%.1f"),
            "Tier": st.column_config.TextColumn("Tier", width="small"),
        }
    )
    
    best_champ = champ_insights.iloc[0]
    st.success(
        f" :material/award_star:    **Your Best Pick:** {best_champ['Champion']} - "
        f"{best_champ['Avg_KDA']:.1f} KDA, {best_champ['Win_Rate']:.1f}% WR "
        f"({int(best_champ['Games'])} games) - Performance Score: {best_champ['Performance_Score']:.1f}/10"
    )
    st.caption(" :material/lightbulb:    *Performance score considers games played, KDA, and win rate - not just raw stats.*")
    
    if metrics['champion_diversity_ratio'] > 0.5:
        st.info(f" :material/lightbulb:    **Champion Pool Tip:** You're playing {metrics['unique_champions']} different champions. "
                "Consider focusing on your top 3-5 performers to build consistency and climb faster!")
    # AI Summary Button
    st.markdown("---")
    display_ai_summary_button('champion_insights', "✨ Get AI Champion Pool Summary")