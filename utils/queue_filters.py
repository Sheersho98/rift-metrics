import streamlit as st
import pandas as pd
from data.metrics import (
    calculate_advanced_metrics,
    get_champion_insights,
    calculate_early_late_game_stats,
    calculate_jungle_advanced_metrics,
    calculate_support_advanced_metrics,
    calculate_support_early_game_stats,
    calculate_support_early_dominance,
    calculate_jungle_early_game_stats,     
    calculate_jungle_early_dominance,
    calculate_playstyle_tags,
    calculate_objective_score,
    calculate_persistence_score,
    calculate_laner_additional_metrics,     
)
from data.context_builder import build_rich_player_context


def get_filtered_matches_and_counts(queue_type):
    #get filtered matches based on queue type and return match lists + counts for each queue type
    solo_matches = st.session_state.get('solo_matches', [])
    flex_matches = st.session_state.get('flex_matches', [])
    all_matches = st.session_state.get('raw_matches', [])
    
    solo_count = len(solo_matches)
    flex_count = len(flex_matches)
    total_count = len(all_matches)
    
    if queue_type == "solo":
        return solo_matches, solo_count, solo_count, flex_count, total_count
    elif queue_type == "flex":
        return flex_matches, flex_count, solo_count, flex_count, total_count
    else:  # "all"
        return all_matches, total_count, solo_count, flex_count, total_count


def prepare_match_dataframe(filtered_matches):  
    #convert raw match data into a clean DataFrame with calculated KDA
    matches = []
    for m in filtered_matches:
        matches.append({
            "Champion": m.get("championName", "Unknown"),
            "Result": "Win" if m.get("win", False) else "Loss",
            "Kills": m.get("kills", 0),
            "Deaths": max(m.get("deaths", 1), 1),  # Avoid division by zero
            "Assists": m.get("assists", 0),
        })
    
    df = pd.DataFrame(matches)
    df["Result"] = df["Result"].astype(str).str.lower()
    df["Win"] = df["Result"].apply(lambda x: 1 if "win" in x else 0)
    df["KDA"] = (df["Kills"] + df["Assists"]) / df["Deaths"]
    df = df.dropna(subset=["KDA"]).reset_index(drop=True)
    return df


def calculate_dominance_score(filtered_matches):
    #game dominance score (advantages over opponent)
    #CS diff@10, gold diff, and early kills
    
    if not filtered_matches:
        return 0.0
    
    wins = [m for m in filtered_matches if m.get('win')]
    if not wins:
        return 0.0
    
    cs_diff_at_10_total = 0
    for match in wins:
        #getting opp
        my_position = match.get('teamPosition', 'UNKNOWN')
        my_team_id = match.get('teamId')
        participants = match.get('participants', []) 
        opponent = None
        for p in participants:
            if p.get('teamPosition') == my_position and p.get('teamId') != my_team_id:
                opponent = p
                break
        if not opponent:
            continue
        
        #getting cs diff at 10
        cs_diff_at_10 = (
            match.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) -
            opponent.get('challenges', {}).get('laneMinionsFirst10Minutes', 0)
        )
        cs_diff_at_10_total += cs_diff_at_10
    
    avg_cs_advantage = cs_diff_at_10_total / len(wins)
    
    # gold differential (approximate from gold per minute)
    avg_gpm = sum(m.get('challenges', {}).get('goldPerMinute', 0) for m in wins) / len(wins)
    gold_advantage_estimate = (avg_gpm - 350) * 10  # 350 is baseline, difference * 10min
    
    avg_early_kills = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in wins) / len(wins)
    
    # Scoring based on ADVANTAGES
    # CS advantage: +20 = excellent, +10 = good, 0 = neutral, -10 = poor
    cs_score = min(10, max(0, (avg_cs_advantage + 10) / 3))
    
    # Gold advantage: +500g = excellent, +250g = good
    gold_score = min(10, max(0, (gold_advantage_estimate + 250) / 75))
    
    # Early kills: 2+ = excellent
    kill_score = min(10, avg_early_kills * 3)
    
    dominance_score = (cs_score + gold_score + kill_score) / 3
    return dominance_score


def build_filtered_context(filtered_matches, metrics, champ_insights, queue_type):
    #Build rich context for filtered data, with caching for 'all' games.
    
    # Check if we need to rebuild context
    current_user = st.session_state.get('current_user_id', '')
    last_context_user = st.session_state.get('last_context_user', '')
    
    # Force rebuild if user changed
    if current_user != last_context_user:
        st.session_state.current_filtered_context = None
        st.session_state.rich_context = None
        st.session_state.last_context_user = current_user
    
    should_rebuild = (
        queue_type != "all" or 
        'rich_context' not in st.session_state or 
        st.session_state.rich_context is None or
        'current_filtered_context' not in st.session_state or
        st.session_state.current_filtered_context is None
    )
    
    if should_rebuild and filtered_matches:
        filtered_rich_context = build_rich_player_context(
            filtered_matches,
            metrics,
            champ_insights
        )
        
        # Cache the "all games" context
        if queue_type == "all":
            st.session_state.rich_context = filtered_rich_context
            
            # Also update user cache
            if current_user in st.session_state.user_cache:
                st.session_state.user_cache[current_user]['rich_context'] = filtered_rich_context
        
        # Always store current filtered context for AI coach
        st.session_state.current_filtered_context = filtered_rich_context
        return filtered_rich_context
    else:
        # Use existing cached context
        return st.session_state.get('rich_context') or st.session_state.get('current_filtered_context')


def prepare_all_filtered_data(queue_type):
    #Main function: Get filtered matches and calculate all necessary metrics.
    
    # Get filtered matches and counts
    filtered_matches, filtered_count, solo_count, flex_count, total_count = \
        get_filtered_matches_and_counts(queue_type)
    
    # Check if we have data
    if filtered_count == 0:
        return {
            'has_data': False,
            'filtered_count': 0,
            'solo_count': solo_count,
            'flex_count': flex_count,
            'total_count': total_count,
        }
    
    # Prepare DataFrame
    df = prepare_match_dataframe(filtered_matches)
    
    # Calculate all metrics
    metrics = calculate_advanced_metrics(df)
    early_late_stats = calculate_early_late_game_stats(df, filtered_matches)
    support_early_stats = calculate_support_early_game_stats(filtered_matches)
    jungle_early_stats = calculate_jungle_early_game_stats(filtered_matches)
    jungle_advanced = calculate_jungle_advanced_metrics(filtered_matches)
    support_advanced = calculate_support_advanced_metrics(filtered_matches)
    champ_insights = get_champion_insights(df)
    dominance_score = calculate_dominance_score(filtered_matches)
    support_dominance_score = calculate_support_early_dominance(filtered_matches)
    jungle_dominance_score = calculate_jungle_early_dominance(filtered_matches)

    objective_score = calculate_objective_score(filtered_matches)
    persistence_score = calculate_persistence_score(filtered_matches)
    laner_advanced = calculate_laner_additional_metrics(filtered_matches)

    # Build rich context (with caching)
    rich_context = build_filtered_context(filtered_matches, metrics, champ_insights, queue_type)

    # Calculate role info for tags
    role_info = rich_context.get('role_consistency', {}) if rich_context else {}
    
    # Calculate playstyle tags
    playstyle_tags = calculate_playstyle_tags(
        metrics, 
        filtered_matches, 
        role_info,
        jungle_advanced,
        support_advanced
    )
    
    # Store champion insights in session state (needed for AI coach)
    st.session_state.champ_insights = champ_insights
    
    return {
        'has_data': True,
        'df': df,
        'metrics': metrics,
        'early_late_stats': early_late_stats,
        'champ_insights': champ_insights,
        'dominance_score': dominance_score,
        'filtered_matches': filtered_matches,
        'rich_context': rich_context,
        'filtered_count': filtered_count,
        'solo_count': solo_count,
        'flex_count': flex_count,
        'total_count': total_count,
        'jungle_advanced': jungle_advanced,
        'support_advanced': support_advanced,
        'support_early_stats': support_early_stats,
        'support_dominance_score': support_dominance_score,
        'jungle_early_stats': jungle_early_stats,
        'jungle_dominance_score': jungle_dominance_score,
        'playstyle_tags': playstyle_tags,
        'objective_score' : objective_score,
        'persistence_score': persistence_score,
        'laner_advanced' : laner_advanced,
    }   


def display_queue_filter_badge(queue_type, filtered_count, solo_count, flex_count):
    if queue_type == "all":
        st.sidebar.info(f" Showing **All Games** ({filtered_count} total: {solo_count} Solo/Duo, {flex_count} Flex)")
    elif queue_type == "solo":
        st.sidebar.info(f" Showing **Solo/Duo Only** ({filtered_count} games)")
    elif queue_type == "flex":
        st.sidebar.info(f" Showing **Flex 5v5 Only** ({filtered_count} games)")