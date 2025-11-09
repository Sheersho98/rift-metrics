import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

from ui.summary_component import display_ai_summary_button

def render_performance_trends(filtered_game_count, selected_queue_display, df, metrics):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Performance Trends")
    
    st.markdown("---")
        
    if filtered_game_count < 10:
        st.info(f"Need **at least 10 games** in {selected_queue_display} to show reliable Performance Trends. You have only **{filtered_game_count}** game(s) recorded.")
        st.caption("Performance Trends from small sample sizes are not very reliable.")
    else:
        st.markdown("### :material/trending_up:    KDA Trend Over Time")
        # Prepare data for line chart
        kda_chart_data = pd.DataFrame({
            'Match Number': df.index + 1,
            'KDA': df['KDA'],
            'Average KDA': df['KDA'].mean()
        }).set_index('Match Number')
        
        st.line_chart(kda_chart_data, color=['#3498db', '#e74c3c'])
        st.caption(f"Average KDA: {df['KDA'].mean():.2f}")
        
        st.markdown("---")
        
        # Win/Loss and K/D/A side by side
        col1, col2 = st.columns([1.75, 1])
        
        with col1:
            st.markdown("### :material/bar_chart:    Average K/D/A")
            kda_data = {
                'Category': ['Kills', 'Deaths', 'Assists'],
                'Average per Game': [
                    df['Kills'].mean(),
                    df['Deaths'].mean(),
                    df['Assists'].mean()
                ],
                'Color': ['#e74c3c', '#95a5a6', '#3498db']
            }
            kda_df = pd.DataFrame(kda_data)
            chart = (
                alt.Chart(kda_df)
                .mark_bar(size=50)
                .encode(
                    x=alt.X('Category:N', title=None),
                    y=alt.Y('Average per Game:Q', title='Average per Game'),
                    color=alt.Color('Category:N', scale=alt.Scale(domain=kda_df['Category'], range=kda_df['Color']), legend=None),
                    tooltip=['Category', 'Average per Game']
                )
                .properties(
                    title='',
                    width=500,
                    height=400
                )
            )
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                fontSize=13,
                fontWeight='bold'
            ).encode(
                text=alt.Text('Average per Game:Q', format='.1f')
            )

            final_chart = (chart + text).configure_axis(
                labelFontSize=12,
                titleFontSize=13
            ).configure_title(
                fontSize=16,
                fontWeight='bold',
                anchor='start'
            )
            st.altair_chart(final_chart, use_container_width=True)

        with col2:
            st.markdown("### :material/rewarded_ads:    Win Rate Distribution")
            wins = df['Win'].sum()
            total_games = len(df)
            
            win_rate = (wins / len(df)) * 100

            st.metric(
                label=f"Win Rate over {total_games} games:",
                value=f"{win_rate:.1f}%",
                delta=f"{wins} games won vs {len(df) - wins} games lost"
            )

        st.markdown("---")
        
        # Win vs Loss comparison
        st.markdown("### :material/search_insights:    Win vs Loss Performance")
        
        win_games = df[df['Win'] == 1]
        loss_games = df[df['Win'] == 0]
        
        if len(win_games) > 0 and len(loss_games) > 0:
            categories = ['Kills', 'Deaths', 'Assists']
            win_stats = [
                win_games['Kills'].mean(),
                win_games['Deaths'].mean(),
                win_games['Assists'].mean()
            ]
            loss_stats = [
                loss_games['Kills'].mean(),
                loss_games['Deaths'].mean(),
                loss_games['Assists'].mean()
            ]

            data = pd.DataFrame({
                'Category': categories * 2,
                'Average': win_stats + loss_stats,
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
                    y=alt.Y('Average:Q', title='Average', axis=alt.Axis(titleFontSize=11, labelFontSize=10)),
                    color=alt.Color('Result:N', scale=color_scale, legend=alt.Legend(title=None, labelFontSize=10, orient='top')),
                    xOffset='Result:N'
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
                    y=alt.Y('Average:Q'),
                    text=alt.Text('Average:Q', format='.1f'),
                    xOffset='Result:N',
                    color=alt.Color('Result:N', scale=color_scale)
                )
            )

            final_chart = (
                (bars + text)
                .properties(
                    title='',
                    height=350
                )
                .configure_title(
                    fontSize=13,
                    fontWeight='bold',
                    anchor='start'
                )
                .configure_axis(
                    titleFontSize=11,
                    labelFontSize=10
                )
                .configure_legend(
                    labelFontSize=10,
                    orient='top'
                )
            )

            st.altair_chart(final_chart, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**When You Win:**")
                st.write(f"• Average KDA: {metrics.get('win_avg_kda', 0):.2f}")
                st.write(f"• Average Kills: {metrics.get('win_avg_kills', 0):.1f}")
                st.write(f"• Average Deaths: {metrics.get('win_avg_deaths', 0):.1f}")
            
            with col2:
                st.write("**When You Lose:**")
                st.write(f"• Average KDA: {metrics.get('loss_avg_kda', 0):.2f}")
                st.write(f"• Average Kills: {metrics.get('loss_avg_kills', 0):.1f}")
                st.write(f"• Average Deaths: {metrics.get('loss_avg_deaths', 0):.1f}")
            
            death_gap = metrics['deaths_per_loss'] - metrics['deaths_per_win']
            if death_gap > 3:
                st.warning(f" :material/warning:    You die {death_gap:.1f} more times per loss. Focus on staying alive when behind!")
        
        st.markdown("---")
        
        # Champion Performance - Weighted Score
        st.markdown("### :material/award_star:    Top 5 Performing Champions")
        
        # Calculate comprehensive performance score
        champ_performance = df.groupby('Champion').agg({
            'KDA': 'mean',
            'Win': ['mean', 'count'],
            'Kills': 'mean',
            'Assists': 'mean',
        }).reset_index()
        
        champ_performance.columns = ['Champion', 'Avg_KDA', 'Win_Rate', 'Games', 'Avg_Kills', 'Avg_Assists']
        champ_performance['Win_Rate'] = champ_performance['Win_Rate'] * 100
        
        # Calculate performance score (same formula as champion insights)
        def calc_perf_score(row):
            games = row['Games']
            kda = row['Avg_KDA']
            wr = row['Win_Rate']
            
            # Diminishing returns on games (log scale)
            games_weight = min(np.log1p(games) * 2, 10)
            kda_score = min(kda * 2, 10)
            wr_score = wr / 10
            
            # Weighted: 40% games, 35% KDA, 25% WR
            performance_score = (games_weight * 0.4) + (kda_score * 0.35) + (wr_score * 0.25)
            return performance_score
        
        champ_performance['Performance_Score'] = champ_performance.apply(calc_perf_score, axis=1)
        champ_top5 = champ_performance.sort_values('Performance_Score', ascending=False).head(5)
        
        # Display chart
        chart = (
            alt.Chart(champ_top5)
            .mark_bar(size=25)
            .encode(
                y=alt.Y('Champion:N', sort='-x', title=None, axis=alt.Axis(labelFontSize=13, labelFontWeight='bold')),
                x=alt.X('Performance_Score:Q', title='Performance Score'),
                color=alt.value("#DBC442"),
                tooltip=[
                    alt.Tooltip('Champion:N'),
                    alt.Tooltip('Performance_Score:Q', format='.2f', title='Performance Score'),
                    alt.Tooltip('Avg_KDA:Q', format='.2f', title='KDA'),
                    alt.Tooltip('Win_Rate:Q', format='.1f', title='Win Rate %'),
                    alt.Tooltip('Games:Q', format='d', title='Games'),
                ]
            )
        )

        text = (
            alt.Chart(champ_top5)
            .mark_text(
                align='left',
                baseline='middle',
                dx=5,
                fontSize=12,
                fontWeight='bold'
            )
            .encode(
                y=alt.Y('Champion:N', sort='-x'),
                x=alt.X('Performance_Score:Q'),
                text=alt.Text('Performance_Score:Q', format='.1f'),
                color=alt.value("#DBC442")
            )
        )

        final_chart = (
            (chart + text)
            .properties(
                title='Based on KDA, Win Rate, and Games Played',
                width=600,
                height=350
            )
            .configure_title(
                fontSize=14,
                fontWeight='bold',
                anchor='start'
            )
            .configure_axis(
                titleFontSize=13,
                labelFontSize=12
            )
        )

        st.altair_chart(final_chart, use_container_width=True)
        
        # Show detailed breakdown
        st.markdown("**Performance Breakdown:**")
        for idx, row in champ_top5.iterrows():
            st.write(
                f"**{row['Champion']}** - Score: {row['Performance_Score']:.1f}/10 "
                f"({row['Avg_KDA']:.1f} KDA, {row['Win_Rate']:.0f}% WR, {int(row['Games'])} games)"
            )
        
        st.caption(" :material/lightbulb: *Performance score weighs consistency (games played), efficiency (KDA), and success (win rate).*")
        
        st.markdown("---")
        
        # Recent form with better spacing
        st.markdown("### :material/browse_activity:    Performance Over Last 10 Games")
        recent_10 = df.tail(10).copy()
        recent_10['Result'] = recent_10['Win'].map({1: 'W', 0: 'L'})
        recent_10 = recent_10.reset_index(drop=True)
        recent_10['Match'] = [f'M{i+1}' for i in range(len(recent_10))]

        color_scale = alt.Scale(domain=['W', 'L'], range=['#2ecc71', '#e74c3c'])
        
        bars = (
            alt.Chart(recent_10)
            .mark_bar(size=30)
            .encode(
                x=alt.X('Match:N', title='Recent Matches (Oldest → Newest)', axis=alt.Axis(labelFontSize=10, labelAngle=-45)),
                y=alt.Y('KDA:Q', title='KDA', scale=alt.Scale(domain=[0, recent_10['KDA'].max() * 1.3]), axis=alt.Axis(titleFontSize=11, labelFontSize=10)),
                color=alt.Color('Result:N', scale=color_scale, legend=alt.Legend(title='Result', labelFontSize=10, orient='top')),
                tooltip=[
                    alt.Tooltip('Match:N', title='Match'),
                    alt.Tooltip('KDA:Q', format='.1f'),
                    alt.Tooltip('Result:N', title='Result')
                ]
            )
        )
        
        # Create combined text
        recent_10['label'] = recent_10.apply(lambda r: f"{r['Result']}\n{r['KDA']:.1f}", axis=1)
        
        labels = (
            alt.Chart(recent_10)
            .mark_text(
                align='center',
                baseline='bottom',
                dy=-3,
                fontSize=9,
                fontWeight='bold'
            )
            .encode(
                x=alt.X('Match:N'),
                y=alt.Y('KDA:Q'),
                text=alt.Text('label:N'),
                color=alt.Color('Result:N', scale=color_scale)
            )
        )

        # Baseline (KDA = 2.0)
        baseline = (
            alt.Chart(pd.DataFrame({'y': [2.0]}))
            .mark_rule(color='orange', strokeDash=[6, 4], size=2)
            .encode(y='y')
            .properties()
        )
        
        final_chart = (
            (bars + labels + baseline)
            .properties(
                title='(W = Win, L = Loss)',
                height=350
            )
            .configure_title(
                fontSize=13,
                fontWeight='bold',
                anchor='start'
            )
            .configure_axis(
                titleFontSize=11,
                labelFontSize=10
            )
            .configure_legend(
                labelFontSize=10,
                title=None,
                orient='top'
            )
            .configure_view(strokeOpacity=0)
        )

        st.altair_chart(final_chart, use_container_width=True)
        # AI Summary Button
        st.markdown("---")
            # Prepare page-specific metrics
        performance_metrics = {
            'win_avg_kda': metrics.get('win_avg_kda', 0),
            'loss_avg_kda': metrics.get('loss_avg_kda', 0),
            'win_avg_kills': metrics.get('win_avg_kills', 0),
            'loss_avg_kills': metrics.get('loss_avg_kills', 0),
            'win_avg_deaths': metrics.get('win_avg_deaths', 0),
            'loss_avg_deaths': metrics.get('loss_avg_deaths', 0),
            'deaths_per_loss': metrics.get('deaths_per_loss', 0),
            'deaths_per_win': metrics.get('deaths_per_win', 0),
            'death_gap': metrics.get('deaths_per_loss', 0) - metrics.get('deaths_per_win', 0),
        }
        
        display_ai_summary_button('performance_trends', "✨ Get AI Performance Summary", performance_metrics)