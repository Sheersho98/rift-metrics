import streamlit as st
import altair as alt
import pandas as pd

from ui.summary_component import display_ai_summary_button

def render_advanced_stats(
    filtered_game_count,
    selected_queue_display, 
    metrics,
    primary_role,
    dominance_score,
    jungle_advanced,
    support_advanced,
    is_laner,
    is_jungler,
    is_support,
    objective_score,
    persistence_score,
    laner_advanced,
):
    #st.markdown("## :material/table_chart_view: Advanced Statistics")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Advanced Statistics")
    
    st.markdown("---")

    if filtered_game_count < 10:
        st.info(f"Need **at least 10 games** in {selected_queue_display} to show reliable Advanced Statistics. You have only **{filtered_game_count}** game(s) recorded.")
        st.caption("Advanced stats are highly volatile with small sample sizes.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container():
                st.metric(
                    label=" :material/show_chart:    KDA Std Deviation",
                    value=f"{metrics['kda_consistency']:.2f}",
                    help="Raw KDA variation across games. Lower = more consistent performance. <1.5 = very consistent, 1.5-2.5 = good, >3.5 = volatile."
                )
                if metrics['kda_consistency'] < 1.5:
                    st.markdown(" :material/check_circle:    **Very consistent**")
                elif metrics['kda_consistency'] < 2.5:
                    st.markdown(" :material/check_circle:    **Good consistency**")
                elif metrics['kda_consistency'] < 3.5:
                    st.markdown(" :material/sentiment_neutral:   **Mediocre consistency**")
                else:
                    st.markdown(" :material/warning:    **High variance**")
                st.caption("Lower = more stable")

        with col2:
            with st.container():
                st.metric(
                    label=" :material/swords:    Aggression Score",
                    value=f"{metrics['aggression_score']:.1f}/game",
                    help="Average kills + assists per game. Measures fight participation and impact. 15+ = very aggressive, 10-15 = good, <10 = passive."
                )
                if metrics['aggression_score'] >= 15:
                    st.markdown(" :material/check_circle:    **Very aggressive**")
                elif metrics['aggression_score'] >= 10:
                    st.markdown(" :material/check_circle:    **Good participation**")
                else:
                    st.markdown(" :material/warning:    **Low participation**")
                st.caption("Kills + Assists per game")

        with col3:
            with st.container():
                st.metric(
                    label=" :material/chess_rook:    Objective Score",
                    value=f"{objective_score:.1f}/10",
                    help="Measures objective taking ability of player. Takes into consideration KP, turrets, dragon, herald and baron stats"
                )
                if objective_score >= 9.0:
                    st.markdown(" :material/trophy:    **Objective Master**")
                elif objective_score >= 8.0:
                    st.markdown(" :material/star:    **Elite Catalyst**")
                elif objective_score >= 6.5:
                    st.markdown(" :material/check_circle:    **Solid Objective Focus**")
                elif objective_score >= 5.0:
                    st.markdown(" :material/sentiment_neutral:    **Average Objective Player**")
                else:
                    st.markdown(" :material/warning:    **Lacks Objective Drive**")
                st.caption("7-9 great, lower = needs more objective focus")
        
        st.markdown("")  # Spacer
        
        # Row 2: Consistency Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.metric(
                    label=" :material/bar_chart:    Performance Volatility",
                    value=f"{metrics['performance_volatility']:.1f}/10",
                    help="0-2 = excellent, 2-5 = good, 5-7 = average, 7+ = inconsistent. Lower = more stable performance across games."
                )
                if metrics['performance_volatility'] <= 2:
                    st.markdown(" :material/check_circle:    **Excellent stability**")
                elif metrics['performance_volatility'] <= 5:
                    st.markdown(" :material/check_circle:    **Good stability**")
                elif metrics['performance_volatility'] <= 7:
                    st.markdown(" :material/sentiment_neutral:    **Average stability**")
                else:
                    st.markdown(" :material/warning:    **Work on consistency**")
                st.caption("0-2 excellent, 7+ inconsistent")
        
        with col2:
            with st.container():
                st.metric(
                    label=" :material/health_and_safety:    Safety Score",
                    value=f"{metrics['safety_score']:.1f}/10",
                    help="Inverse of death rate (10 - avg deaths). Measures survival and positioning. 7+ = excellent, 5-7 = good, <5 = dying too much."
                )
                if metrics['safety_score'] >= 7:
                    st.markdown(" :material/check_circle:    **Excellent survival**")
                elif metrics['safety_score'] >= 5:
                    st.markdown(" :material/check_circle:    **Good survival**")
                else:
                    st.markdown(" :material/warning:    **Dying too much**")
                st.caption("10 - avg deaths")

        with col3:
            with st.container():
                st.metric(
                    label=" :material/falling:    Persistence Score",
                    value=f"{persistence_score:.1f}/10",
                    help="Measures how much a player resists surrender and maintains performance during losing scenarios"
                )
                if persistence_score >= 9.0:
                    st.markdown(" :material/star_shine:    **The Unbreakable**")
                elif persistence_score >= 7.5:
                    st.markdown(" :material/check_circle:    **Resilient Competitor**")
                elif persistence_score >= 6.0:
                    st.markdown(" :material/sentiment_neutral:    **Steady Effort**")
                elif persistence_score >= 4.5:
                    st.markdown(" :material/warning:    **Tilts Easily**")
                else:
                    st.markdown(" :material/thumb_down:    **Gives Up Early**")
                st.caption("Higher = more untiltable")
        
        st.markdown("")  # Spacer
        
        # Row 3: Champion Pool Metrics
        col1, col2, col3 = st.columns(3)
            
        
        with col1:
            with st.container():
                st.metric(
                    label=" :material/shape_line:    Diversity Ratio",
                    value=f"{metrics['champion_diversity_ratio']:.1%}",
                    help=f"{metrics['unique_champions']} unique champions played over the last {metrics['total_games']} game(s). Optimal range: 20-40% (focused but flexible). <20% = one-trick, >50% = too scattered."
                )
                if metrics['champion_diversity_ratio'] <= 0.3:
                    st.markdown(" :material/check_circle:    **Focused pool**")
                elif metrics['champion_diversity_ratio'] <= 0.5:
                    st.markdown(" :material/check_circle:    **Balanced variety**")
                else:
                    st.markdown(" :material/warning:    **Too much variety**")
                st.caption("Optimal: 20-40%")
        
        with col2:
            with st.container():
                if 'win_avg_kda' in metrics and 'loss_avg_kda' in metrics:
                    kda_gap = abs(metrics['win_avg_kda'] - metrics['loss_avg_kda'])
                    st.metric(
                        label=" :material/space_bar:    Win/Loss KDA Gap",
                        value=f"{kda_gap:.1f}",
                        help="KDA difference between wins and losses. Lower = consistent regardless of outcome. <1.5 = very consistent, 1.5-3 = some variance, >3 = large gap."
                    )
                    if kda_gap <= 1.5:
                        st.markdown(" :material/check_circle:    **Consistent**")
                    elif kda_gap <= 3:
                        st.markdown(" :material/warning:    **Some variance**")
                    else:
                        st.markdown(" :material/warning:    **Large gap**")
                    st.caption("Win KDA - Loss KDA")
        
        # Column 3: Role-specific metric based on PRIMARY role
        with col3:
            with st.container():
                # Show metric based on PRIMARY role
                if primary_role in ['TOP', 'MIDDLE', 'BOTTOM']:
                    st.metric(
                        label=" :material/target:    Early Game Dominance",
                        value=f"{dominance_score:.1f}/10",
                        help="Composite score: CS advantage, gold differential, and early kills compared to lane opponent. Higher = stronger laning phase."
                    )
                    if dominance_score >= 7:
                        st.markdown(" :material/check_circle:    **Strong laning**")
                    elif dominance_score >= 5:
                        st.markdown(" :material/sentiment_neutral:    **Average laning**")
                    else:
                        st.markdown(" :material/warning:    **Needs improvement**")
                    st.caption("Advantage over lane opponent")
                
                elif primary_role == 'JUNGLE' and jungle_advanced['has_jungle_data']:
                    st.metric(
                        label=" :material/target:    Jungle Objective Control",
                        value=f"{jungle_advanced['jungle_objective_control']:.1f}/10",
                        help="Score based on dragon, baron, herald, and void grub participation. Higher = better objective priority."
                    )
                    if jungle_advanced['jungle_objective_control'] >= 7:
                        st.markdown(" :material/check_circle:    **Strong objectives**")
                    elif jungle_advanced['jungle_objective_control'] >= 5:
                        st.markdown(" :material/sentiment_neutral:    **Average objectives**")
                    else:
                        st.markdown(" :material/warning:    **Needs improvement**")
                    st.caption(f"{jungle_advanced['avg_dragons']:.1f} drags, {jungle_advanced['avg_barons']:.1f} barons")
                
                elif primary_role == 'UTILITY' and support_advanced['has_support_data']:
                    st.metric(
                        label=" :material/visibility:    Vision Dominance",
                        value=f"{support_advanced['vision_dominance_score']:.1f}/10",
                        help="Score based on vision score/min, control wards, wards cleared, and vision advantage. Higher = better vision control."
                    )
                    if support_advanced['vision_dominance_score'] >= 7:
                        st.markdown(" :material/check_circle:    **Excellent vision**")
                    elif support_advanced['vision_dominance_score'] >= 5:
                        st.markdown(" :material/sentiment_neutral:    **Good vision**")
                    else:
                        st.markdown(" :material/warning:    **Needs improvement**")
                    st.caption(f"{support_advanced['avg_vision_per_min']:.1f} vision/min")
                
                else:
                    st.metric(
                        label=" :material/chart_data:    Role Data",
                        value="N/A",
                        help="No role-specific data available for this queue."
                    )
                    st.caption("Play more games")
        
        # Row 4: Additional Role-Specific Metrics
        row_4_metrics = []
        
        # Laner specific metrics
        if is_laner and laner_advanced['has_lane_data']:
            row_4_metrics.append(('avg_cs_per_min', laner_advanced))
            row_4_metrics.append(('combat_efficiency_score', laner_advanced))

        # JUNGLE specific metrics 
        if is_jungler and jungle_advanced['has_jungle_data']:
            # If jungle is NOT primary, show objective control first
            if primary_role != 'JUNGLE':
                row_4_metrics.append(('jungle_objective', jungle_advanced))
            # Always show these two additional jungle metrics
            row_4_metrics.append(('jungle_pressure', jungle_advanced))
            row_4_metrics.append(('counter_jungle', jungle_advanced))
        
        # SUPPORT specific  metrics 
        if is_support and support_advanced['has_support_data']:
            # If support is NOT primary, show vision dominance first
            if primary_role != 'UTILITY':
                row_4_metrics.append(('vision_dominance', support_advanced))
            # Always show these two additional support metrics
            row_4_metrics.append(('utility_output', support_advanced))
            row_4_metrics.append(('frontline', support_advanced))
        
        # Display metrics in rows of up to 3 columns each
        if len(row_4_metrics) > 0:
            # Process metrics in chunks of 3
            for row_idx in range(0, len(row_4_metrics), 3):
                st.markdown("")  # Spacer
                
                chunk = row_4_metrics[row_idx:row_idx + 3]
                num_in_row = len(chunk)
                
                if num_in_row == 1:
                    col1, _, _ = st.columns([1, 1, 1])
                    cols = [col1]
                elif num_in_row == 2:
                    col1, col2, _ = st.columns([1, 1, 1])
                    cols = [col1, col2]
                else:  
                    col1, col2, col3 = st.columns(3)
                    cols = [col1, col2, col3]
                
                # helper function to display each metric 
                for idx, (metric_type, data) in enumerate(chunk):
                    with cols[idx]:
                        with st.container():
                            display_role_metric(metric_type, data)

        st.markdown("---")
        st.markdown("### :material/pie_chart:    Performance Profile")

        scores = {
            'Impact': min(10, metrics['carry_rate'] / 5),
            'Aggression': min(10, metrics['aggression_score'] / 2),
            'Consistency': metrics['consistency_score'], 
            'Safety': metrics['safety_score'],
        }

        score_explanations = {
            'Impact': 'Your ability to carry games with high kill participation',
            'Aggression': 'How actively you participate in fights and skirmishes',
            'Consistency': 'How stable your performance is across different games',
            'Safety': 'Your ability to stay alive and avoid unnecessary deaths',
        }

        scores_df = pd.DataFrame(
            list(scores.items()),
            columns=['Category', 'Score']
        )
        color_list = ["#e26751","#1abc5d", "#dfbf0d", "#4a1dc5"]
        scores_df['Color'] = color_list[:len(scores_df)]
        
        bars = (
            alt.Chart(scores_df)
            .mark_bar(size=35)
            .encode(
                y=alt.Y('Category:N', sort='-x', title=None, axis=alt.Axis(labelFontSize=13, labelFontWeight='bold')),
                x=alt.X('Score:Q', title='Score'),
                color=alt.Color('Category:N', scale=alt.Scale(domain=scores_df['Category'], range=scores_df['Color']), legend=None),
                tooltip=[alt.Tooltip('Category:N'), alt.Tooltip('Score:Q', format='.1f')]
            )
        )

        text = (
            alt.Chart(scores_df)
            .mark_text(
                align='left',
                baseline='middle',
                dx=5,
                fontSize=13,
                fontWeight='bold'
            )
            .encode(
                y=alt.Y('Category:N', sort='-x'),
                x=alt.X('Score:Q'),
                text=alt.Text('Score:Q', format='.1f'),
                color=alt.Color('Category:N', scale=alt.Scale(domain=scores_df['Category'], range=scores_df['Color']))
            )
        )

        final_chart = (
            (bars + text)
            .properties(
                title='Performance Scores',
                width=600,
                height=300
            )
            .configure_title(
                fontSize=16,
                fontWeight='bold',
                anchor='start'
            )
            .configure_axis(
                titleFontSize=13,
                labelFontSize=12
            )
        )

        st.altair_chart(final_chart, use_container_width=True)

        st.markdown("**Score Meanings:**")
        for score_name, explanation in score_explanations.items():
            st.write(f"**{score_name}:** {explanation}")
            st.caption(f"Your score: {scores[score_name]:.1f}/10")
            st.write("")

        st.markdown("---")
        # Prepare page-specific metrics for AI
        advanced_stats_metrics = {
            'kda_std_dev': metrics['kda_consistency'],
            'aggression_score': metrics['aggression_score'],
            'objective_score': objective_score,
            'performance_volatility': metrics['performance_volatility'],
            'safety_score': metrics['safety_score'],
            'persistence_score': persistence_score,
            'diversity_ratio': metrics['champion_diversity_ratio'],
            'win_loss_kda_gap': abs(metrics.get('win_avg_kda', 0) - metrics.get('loss_avg_kda', 0)),
            'early_game_dominance': dominance_score,
            'unique_champions': metrics['unique_champions'],
        }

        if primary_role in ['TOP', 'MIDDLE', 'BOTTOM'] and laner_advanced['has_lane_data']:
            print(laner_advanced)
            advanced_stats_metrics['avg_cs_per_min'] = laner_advanced['avg_cs_per_min']
            advanced_stats_metrics['gold_to_combat_efficiency_score'] = laner_advanced['combat_efficiency_score']
        elif primary_role == 'JUNGLE' and jungle_advanced['has_jungle_data']:
            advanced_stats_metrics['jungle_objective_control'] = jungle_advanced['jungle_objective_control']
            advanced_stats_metrics['jungle_pressure_score'] = jungle_advanced['jungle_pressure_score']
            advanced_stats_metrics['counter_jungle_score'] = jungle_advanced['counter_jungle_score']
        elif primary_role == 'UTILITY' and support_advanced['has_support_data']:
            advanced_stats_metrics['vision_dominance_score'] = support_advanced['vision_dominance_score']
            advanced_stats_metrics['utility_output_score'] = support_advanced['utility_output_score']
            advanced_stats_metrics['frontline_score'] = support_advanced['frontline_score']
        
        display_ai_summary_button('advanced_stats', "✨ Get AI Performance Summary", advanced_stats_metrics)


def display_role_metric(metric_type: str, data: dict):
    """Helper function to display role-specific metrics consistently"""
    if metric_type == 'jungle_objective':
        st.metric(
            label=" :material/target:    Jungle Objective Control",
            value=f"{data['jungle_objective_control']:.1f}/10",
            help="Score based on dragon, baron, herald, and void grub participation. Higher = better objective priority."
        )
        if data['jungle_objective_control'] >= 7:
            st.markdown(" :material/check_circle:    **Strong objectives**")
        elif data['jungle_objective_control'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Average objectives**")
        else:
            st.markdown(" :material/warning:    **Needs improvement**")
        st.caption(f"{data['avg_dragons']:.1f} drags, {data['avg_barons']:.1f} barons")
    
    elif metric_type == 'jungle_pressure':
        st.metric(
            label=" :material/bolt:    Jungle Pressure",
            value=f"{data['jungle_pressure_score']:.1f}/10",
            help="Early game jungle impact: scuttle control, early ganks, and farming efficiency. Higher = more early pressure."
        )
        if data['jungle_pressure_score'] >= 7:
            st.markdown(" :material/check_circle:    **High pressure**")
        elif data['jungle_pressure_score'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Moderate pressure**")
        else:
            st.markdown(" :material/warning:    **Low pressure**")
        st.caption(f"{data['avg_scuttles']:.1f} scuttles/game")
    
    elif metric_type == 'counter_jungle':
        st.metric(
            label=" :material/swords:    Counter-Jungle",
            value=f"{data['counter_jungle_score']:.1f}/10",
            help="Aggression in enemy jungle: camps stolen, buffs taken, epic steals. Higher = more invade success."
        )
        if data['counter_jungle_score'] >= 7:
            st.markdown(" :material/check_circle:    **Dominant invades**")
        elif data['counter_jungle_score'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Some invades**")
        else:
            st.markdown(" :material/warning:    **Passive**")
        st.caption(f"{data['avg_enemy_camps']:.1f} camps stolen")
    
    elif metric_type == 'vision_dominance':
        st.metric(
            label=" :material/undereye:    Vision Dominance",
            value=f"{data['vision_dominance_score']:.1f}/10",
            help="Score based on vision score/min, control wards, wards cleared, and vision advantage. Higher = better vision control."
        )
        if data['vision_dominance_score'] >= 7:
            st.markdown(" :material/check_circle:    **Excellent vision**")
        elif data['vision_dominance_score'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Good vision**")
        else:
            st.markdown(" :material/warning:    **Needs improvement**")
        st.caption(f"{data['avg_vision_per_min']:.1f} vision/min")
    
    elif metric_type == 'utility_output':
        st.metric(
            label=" :material/security:    Utility Output",
            value=f"{data['utility_output_score']:.1f}/10",
            help="Team support contribution: healing/shielding, assists, and kill participation. Higher = more team impact."
        )
        if data['utility_output_score'] >= 7:
            st.markdown(" :material/check_circle:    **High impact**")
        elif data['utility_output_score'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Good support**")
        else:
            st.markdown(" :material/warning:    **Low impact**")
        st.caption(f"{data['avg_assists']:.1f} assists/game")
    
    elif metric_type == 'frontline':
        st.metric(
            label=" :material/exercise:    Frontline Presence",
            value=f"{data['frontline_score']:.1f}/10",
            help="Tanking and protection: damage taken %, total damage absorbed, wards guarded. Higher = better frontline."
        )
        if data['frontline_score'] >= 7:
            st.markdown(" :material/check_circle:    **Strong frontline**")
        elif data['frontline_score'] >= 5:
            st.markdown(" :material/sentiment_neutral:    **Decent tanking**")
        else:
            st.markdown(" :material/warning:    **Squishy**")
        st.caption(f"{data['avg_dmg_taken_pct']:.1f}% team dmg")

    elif metric_type == 'avg_cs_per_min':
        st.metric(
            label=" :material/money_bag:    Average CS/Min",
            value=f"{data['avg_cs_per_min']:.1f} cs/min",
            help="CS per minute"
        )
        if data['avg_cs_per_min'] >= 9.0:
            st.markdown(" :material/crown:    **Farming King**")
        elif data['avg_cs_per_min'] >= 8.0:
            st.markdown(" :material/star:    **Elite Farmer**")
        elif data['avg_cs_per_min'] >= 7.0:
            st.markdown(" :material/check_circle:    **Optimal CS**")
        elif data['avg_cs_per_min'] >= 6.0:
            st.markdown(" :material/sentiment_neutral:    **Average Efficiency**")
        else:
            st.markdown(" :material/warning:    **Starvation**")
        st.caption("Optimal: 8-10+")

    elif metric_type == 'combat_efficiency_score':
        st.metric(
            label=" :material/balance:    Gold Combat Efficiency",
            value=f"{data['combat_efficiency_score']:.1f}/10",
            help="Damage and Tanking efficiency per 1k of gold earned"
        )
        if data['combat_efficiency_score'] >= 10.0:
            st.markdown(" :material/crown:    **Resource Dominator**")
        elif data['combat_efficiency_score'] >= 8.0:
            st.markdown(" :material/star:    **Highly Efficient Contributor**")
        elif data['combat_efficiency_score'] >= 6.0:
            st.markdown(" :material/check_circle:    **Solid Role Conversion**")
        elif data['combat_efficiency_score'] >= 4.0:
            st.markdown(" :material/sentiment_neutral:    **Average Efficiency**")
        else:
            st.markdown(" :material/warning:    **Inefficient Gold Use**")
        st.caption(f"{data['avg_damage_share']:.1f} % avg dmg and {data['avg_tank_share']:.1f}% avg dmg tanked")
