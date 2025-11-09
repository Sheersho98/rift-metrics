import streamlit as st
import pandas as pd
import altair as alt

from ui.summary_component import display_ai_summary_button

def render_early_vs_late_game(
    filtered_game_count,
    selected_queue_display,
    is_laner,
    early_late_stats,
    is_jungler,
    is_support,
    jungle_early_stats,
    support_early_stats,
    dominance_score,
    jungle_dominance_score,
    support_dominance_score,
):
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        st.markdown("## Early vs Late Game Analysis")
    
    st.markdown("---")
        
    if filtered_game_count < 10:
        st.info(f"Need **at least 10 games** in {selected_queue_display} to show reliable Early vs Late Game analysis. You have only **{filtered_game_count}** game(s) recorded.")
        st.caption("Early vs Late Game analysis is highly skewed with small sample sizes.")
    else:
        # LANER SECTION - Show if player plays laner roles
        if is_laner and early_late_stats.get('has_laner_data', False):
            st.markdown("### :material/target:    Laner Early Game Performance (First 10-15 Minutes)")
            if not is_jungler and not is_support:
                st.caption("Your early game performance in lane")
            else:
                st.caption("Your early game performance when playing TOP/MID/BOT")
            
            win_early = early_late_stats['wins']
            loss_early = early_late_stats['losses']

            win_avg_cs_at_10 = win_early.get('avg_cs_at_10', 0.0)
            win_avg_gold_per_min = win_early.get('avg_gold_per_min', 0.0)
            win_avg_early_kills = win_early.get('avg_early_kills', 0.0)

            loss_avg_cs_at_10 = loss_early.get('avg_cs_at_10', 0.0)
            loss_avg_gold_per_min = loss_early.get('avg_gold_per_min', 0.0)
            loss_avg_early_kills = loss_early.get('avg_early_kills', 0.0)

            cs_at_10_diff = early_late_stats.get('cs_at_10_diff', 0.0)
            gold_diff = early_late_stats.get('gold_diff', 0.0)
            early_kills_diff = early_late_stats.get('early_kills_diff', 0.0)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "CS @ 10min (Wins)", 
                    f"{win_avg_cs_at_10:.1f}",
                    delta=f"+{cs_at_10_diff:.1f} vs Losses"
                )
            
            with col2:
                st.metric(
                    "Gold/Min (Wins)",
                    f"{win_avg_gold_per_min:.0f}",
                    delta=f"+{gold_diff:.0f} vs Losses"
                )
            
            with col3:
                st.metric(
                    "Early Kills (Wins)",
                    f"{win_avg_early_kills:.1f}",
                    delta=f"+{early_kills_diff:.1f} vs Losses"
                )
            
            st.markdown("---")

            # Comparison chart for laners
            st.markdown("### :material/scoreboard:    Wins vs Losses Breakdown")

            categories = ['CS@10', 'Gold/Min', 'Early Kills']
            win_values = [
                win_avg_cs_at_10,
                win_avg_gold_per_min / 10,  # Scale down for visibility
                win_avg_early_kills
            ]
            loss_values = [
                loss_avg_cs_at_10,
                loss_avg_gold_per_min / 10,
                loss_avg_early_kills
            ]
            
            data = pd.DataFrame({
                'Category': categories * 2,
                'Value': win_values + loss_values,
                'Result': ['Wins'] * 3 + ['Losses'] * 3
            })
            color_scale = alt.Scale(
                domain=['Wins', 'Losses'],
                range=['#2ecc71', '#e74c3c']
            )
            bars = (
                alt.Chart(data)
                .mark_bar(size=30)
                .encode(
                    x=alt.X('Category:N', title=None, axis=alt.Axis(labelFontSize=11, labelFontWeight='bold', labelAngle=0)),
                    y=alt.Y('Value:Q', title='Value', axis=alt.Axis(titleFontSize=11, labelFontSize=10)),
                    color=alt.Color('Result:N', scale=color_scale, legend=alt.Legend(title=None, labelFontSize=10, orient='top')),
                    xOffset='Result:N',
                    tooltip=[
                        alt.Tooltip('Category:N'),
                        alt.Tooltip('Result:N'),
                        alt.Tooltip('Value:Q', format='.2f')
                    ]
                )
            )
            
            text = (
                alt.Chart(data)
                .mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-3,
                    fontSize=10,
                    fontWeight='bold'
                )
                .encode(
                    x=alt.X('Category:N'),
                    y=alt.Y('Value:Q'),
                    text=alt.Text('Value:Q', format='.1f'),
                    xOffset='Result:N',
                    color=alt.Color('Result:N', scale=color_scale)
                )
            )
            
            final_chart = (
                (bars + text)
                .properties(
                    title='Early Game Stats: Wins vs Losses',
                    height=350
                )
                .configure_title(
                    fontSize=13,
                    fontWeight='bold',
                    anchor='start'
                )
                .configure_axis(
                    labelFontSize=11,
                    titleFontSize=11
                )
                .configure_legend(
                    labelFontSize=10,
                    title=None,
                    orient='top'
                )
                .configure_view(strokeOpacity=0)
            )
            st.altair_chart(final_chart, use_container_width=True)

            st.markdown("---")
            
            # Laner Early Game Dominance Score
            st.markdown("### :material/my_location:    Laner Early Game Dominance")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Dominance Score", f"{dominance_score:.1f}/10")
                
                if dominance_score >= 7:
                    st.success(" :material/check_circle:    **Strong early game!** You consistently build leads.")
                elif dominance_score >= 5:
                    st.info(" :material/trending_up:    **Solid early game.** Room for optimization.")
                else:
                    st.warning(" :material/warning:    **Weak early game.** Focus on laning fundamentals.")
            
            with col2:
                st.markdown("**What this measures:**")
                st.write("• CS efficiency in first 10 minutes")
                st.write("• Gold generation rate")
                st.write("• Early kill participation")
                st.write("")
                st.caption(f"**In wins:** {win_avg_cs_at_10:.0f} CS@10, {win_avg_early_kills:.1f} early kills")
                st.caption(f"**In losses:** {loss_avg_cs_at_10:.0f} CS@10, {loss_avg_early_kills:.1f} early kills")
            
            st.markdown("---")
        
        # JUNGLE SECTION - Show if player plays jungle
        if is_jungler and jungle_early_stats.get('has_jungle_data', False):
            st.markdown("### :material/forest:    Jungle Early Game Performance (First 10-15 Minutes)")
            st.caption("Your early game performance when playing JUNGLE")
            
            win_jungle = jungle_early_stats['wins']
            loss_jungle = jungle_early_stats['losses']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Jungle CS @ 10min (Wins)",
                    f"{win_jungle.get('avg_jungle_cs_10', 0):.1f}",
                    delta=f"+{jungle_early_stats['jungle_cs_10_diff']:.1f} vs Losses"
                )
            
            with col2:
                st.metric(
                    "Gold/Min (Wins)",
                    f"{win_jungle.get('avg_gold_per_min', 0):.0f}",
                    delta=f"+{jungle_early_stats['gold_diff']:.0f} vs Losses"
                )
            
            with col3:
                st.metric(
                    "Early Takedowns (Wins)",
                    f"{win_jungle.get('avg_early_takedowns', 0):.1f}",
                    delta=f"+{jungle_early_stats['early_takedown_diff']:.1f} vs Losses",
                    help="Kills + Assists in first 10-15 minutes"
                )
            
            st.markdown("---")
            
            # Jungle Early Game Dominance Score
            st.markdown("### :material/forest:    Jungle Early Game Dominance")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Dominance Score", f"{jungle_dominance_score:.1f}/10")
                
                if jungle_dominance_score >= 7:
                    st.success(" :material/check_circle:    **Strong jungle pressure!** You control the early game.")
                elif jungle_dominance_score >= 5:
                    st.info(" :material/trending_up:    **Solid jungle performance.** Room for optimization.")
                else:
                    st.warning(" :material/warning:    **Weak early jungle.** Focus on pathing and ganking.")
            
            with col2:
                st.markdown("**What this measures:**")
                st.write("• Jungle clear efficiency")
                st.write("• Gold generation rate")
                st.write("• Early gank success (kills + assists)")
                st.write("")
                st.caption(f"**In wins:** {win_jungle.get('avg_jungle_cs_10', 0):.0f} jungle CS@10, {win_jungle.get('avg_early_takedowns', 0):.1f} early takedowns")
                st.caption(f"**In losses:** {loss_jungle.get('avg_jungle_cs_10', 0):.0f} jungle CS@10, {loss_jungle.get('avg_early_takedowns', 0):.1f} early takedowns")
            
            st.markdown("---")

            # Comparison chart for jungle
            st.markdown("### :material/scoreboard:    Wins vs Losses Breakdown")

            categories = ['Jungle CS@10', 'Gold/Min', 'Early Takedowns']
            win_values = [
                win_jungle.get('avg_jungle_cs_10', 0),
                win_jungle.get('avg_gold_per_min', 0) / 10,  # Scale down for visibility
                win_jungle.get('avg_early_takedowns', 0)
            ]
            loss_values = [
                loss_jungle.get('avg_jungle_cs_10', 0),
                loss_jungle.get('avg_gold_per_min', 0) / 10,
                loss_jungle.get('avg_early_takedowns', 0)
            ]
            
            data = pd.DataFrame({
                'Category': categories * 2,
                'Value': win_values + loss_values,
                'Result': ['Wins'] * 3 + ['Losses'] * 3
            })
            color_scale = alt.Scale(
                domain=['Wins', 'Losses'],
                range=['#2ecc71', '#e74c3c']
            )
            bars = (
                alt.Chart(data)
                .mark_bar(size=30)
                .encode(
                    x=alt.X('Category:N', title=None, axis=alt.Axis(labelFontSize=11, labelFontWeight='bold', labelAngle=0)),
                    y=alt.Y('Value:Q', title='Value', axis=alt.Axis(titleFontSize=11, labelFontSize=10)),
                    color=alt.Color('Result:N', scale=color_scale, legend=alt.Legend(title=None, labelFontSize=10, orient='top')),
                    xOffset='Result:N',
                    tooltip=[
                        alt.Tooltip('Category:N'),
                        alt.Tooltip('Result:N'),
                        alt.Tooltip('Value:Q', format='.2f')
                    ]
                )
            )
            
            text = (
                alt.Chart(data)
                .mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-3,
                    fontSize=10,
                    fontWeight='bold'
                )
                .encode(
                    x=alt.X('Category:N'),
                    y=alt.Y('Value:Q'),
                    text=alt.Text('Value:Q', format='.1f'),
                    xOffset='Result:N',
                    color=alt.Color('Result:N', scale=color_scale)
                )
            )
            
            final_chart = (
                (bars + text)
                .properties(
                    title='Early Game Stats: Wins vs Losses (Jungle)',
                    height=350
                )
                .configure_title(
                    fontSize=13,
                    fontWeight='bold',
                    anchor='start'
                )
                .configure_axis(
                    labelFontSize=11,
                    titleFontSize=11
                )
                .configure_legend(
                    labelFontSize=10,
                    title=None,
                    orient='top'
                )
                .configure_view(strokeOpacity=0)
            )
            st.altair_chart(final_chart, use_container_width=True)

            st.markdown("---")
        
        # SUPPORT SECTION - Show if player plays support
        if is_support and support_early_stats.get('has_support_data', False):
            st.markdown("### :material/handshake:    Support Early Game Performance (First 10-15 Minutes)")
            st.caption("Your early game performance when playing SUPPORT")
            
            win_support = support_early_stats['wins']
            loss_support = support_early_stats['losses']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Wards @ 10min (Wins)",
                    f"{win_support.get('avg_wards_at_10', 0):.1f}",
                    delta=f"+{support_early_stats['wards_at_10_diff']:.1f} vs Losses"
                )
            
            with col2:
                st.metric(
                    "Quest Completion (Wins)",
                    f"{win_support.get('quest_completion_rate', 0):.0f}%",
                    delta=f"+{support_early_stats['quest_diff']:.0f}% vs Losses",
                    help="% of games where you completed support quest faster than opponent"
                )
            
            with col3:
                st.metric(
                    "Early Assists (Wins)",
                    f"{win_support.get('avg_early_assists', 0):.1f}",
                    delta=f"+{support_early_stats['early_assists_diff']:.1f} vs Losses"
                )
            
            st.markdown("---")

            # Comparison chart for support
            st.markdown("### :material/scoreboard:    Wins vs Losses Breakdown")

            categories = ['Wards@10', 'Quest %', 'Early Assists']
            win_values = [
                win_support.get('avg_wards_at_10', 0),
                win_support.get('quest_completion_rate', 0) / 10,  # Scale down for visibility
                win_support.get('avg_early_assists', 0)
            ]
            loss_values = [
                loss_support.get('avg_wards_at_10', 0),
                loss_support.get('quest_completion_rate', 0) / 10,
                loss_support.get('avg_early_assists', 0)
            ]
            
            data = pd.DataFrame({
                'Category': categories * 2,
                'Value': win_values + loss_values,
                'Result': ['Wins'] * 3 + ['Losses'] * 3
            })
            color_scale = alt.Scale(
                domain=['Wins', 'Losses'],
                range=['#2ecc71', '#e74c3c']
            )
            bars = (
                alt.Chart(data)
                .mark_bar(size=30)
                .encode(
                    x=alt.X('Category:N', title=None, axis=alt.Axis(labelFontSize=11, labelFontWeight='bold', labelAngle=0)),
                    y=alt.Y('Value:Q', title='Value', axis=alt.Axis(titleFontSize=11, labelFontSize=10)),
                    color=alt.Color('Result:N', scale=color_scale, legend=alt.Legend(title=None, labelFontSize=10, orient='top')),
                    xOffset='Result:N',
                    tooltip=[
                        alt.Tooltip('Category:N'),
                        alt.Tooltip('Result:N'),
                        alt.Tooltip('Value:Q', format='.2f')
                    ]
                )
            )
            
            text = (
                alt.Chart(data)
                .mark_text(
                    align='center',
                    baseline='bottom',
                    dy=-3,
                    fontSize=10,
                    fontWeight='bold'
                )
                .encode(
                    x=alt.X('Category:N'),
                    y=alt.Y('Value:Q'),
                    text=alt.Text('Value:Q', format='.1f'),
                    xOffset='Result:N',
                    color=alt.Color('Result:N', scale=color_scale)
                )
            )
            
            final_chart = (
                (bars + text)
                .properties(
                    title='Early Game Stats: Wins vs Losses (Support)',
                    height=350
                )
                .configure_title(
                    fontSize=13,
                    fontWeight='bold',
                    anchor='start'
                )
                .configure_axis(
                    labelFontSize=11,
                    titleFontSize=11
                )
                .configure_legend(
                    labelFontSize=10,
                    title=None,
                    orient='top'
                )
                .configure_view(strokeOpacity=0)
            )
            st.altair_chart(final_chart, use_container_width=True)

            st.markdown("---")
            
            # Support Early Game Dominance Score
            st.markdown("### :material/star_shine:    Support Early Game Dominance")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Dominance Score", f"{support_dominance_score:.1f}/10")
                
                if support_dominance_score >= 7:
                    st.success(" :material/check_circle:    **Strong early support!** You enable your team well.")
                elif support_dominance_score >= 5:
                    st.info(" :material/trending_up:    **Solid early support.** Room for optimization.")
                else:
                    st.warning(" :material/warning:    **Weak early support.** Focus on vision and roaming.")
            
            with col2:
                st.markdown("**What this measures:**")
                st.write("• Support item completion speed")
                st.write("• Vision control advantage")
                st.write("• Early kill participation")
                st.write("")
                st.caption(f"**In wins:** {win_support.get('avg_wards_at_10', 0):.1f} wards@10, {win_support.get('avg_early_assists', 0):.1f} early assists")
                st.caption(f"**In losses:** {loss_support.get('avg_wards_at_10', 0):.1f} wards@10, {loss_support.get('avg_early_assists', 0):.1f} early assists")
            
            st.markdown("---")
        
        # If no role data available
        if not (is_laner and early_late_stats.get('has_laner_data', False)) and \
            not (is_jungler and jungle_early_stats.get('has_jungle_data', False)) and \
            not (is_support and support_early_stats.get('has_support_data', False)):
            st.warning("No early game data available for your roles in this queue. Play more games!")
        
        display_ai_summary_button('early_late', "✨ Get AI Early Game Analysis")