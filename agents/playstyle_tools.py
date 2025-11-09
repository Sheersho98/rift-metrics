from strands import tool
from agents.context_manager import get_context


@tool
def get_playstyle_fingerprint() -> dict:
    """
    Get the player's complete behavioral fingerprint - the patterns that define how they play.
    Returns aggression style, consistency patterns, decision-making tendencies, and win conditions.
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    # Use current_filtered_context to respect queue filters
    rich_ctx = ctx.get('current_filtered_context') or ctx.get('rich_context')
    
    # Core playstyle metrics
    overview = rich_ctx.get('overview', {})
    combat = rich_ctx.get('combat_stats', {})
    win_loss = rich_ctx.get('win_loss_comparison', {})
    
    # Calculate behavioral indicators
    avg_kills = combat.get('avg_kills', 0)
    avg_deaths = combat.get('avg_deaths', 0)
    avg_assists = combat.get('avg_assists', 0)
    avg_kda = combat.get('avg_kda', 0)
    
    # Aggression profile
    kill_participation = combat.get('avg_kill_participation', 0) * 100
    aggression_score = (avg_kills + avg_assists) / max(1, avg_deaths)
    
    # Consistency profile
    kda_std = combat.get('kda_std', 0)
    performance_volatility = rich_ctx.get('advanced_metrics', {}).get('performance_volatility', 5)
    
    # Win condition analysis
    win_avg_kda = win_loss.get('win_avg_kda', 0)
    loss_avg_kda = win_loss.get('loss_avg_kda', 0)
    kda_gap = win_avg_kda - loss_avg_kda
    
    deaths_per_win = win_loss.get('win_avg_deaths', 0)
    deaths_per_loss = win_loss.get('loss_avg_deaths', 0)
    death_discipline_gap = deaths_per_loss - deaths_per_win
    
    # Early vs late game identity
    early_game = rich_ctx.get('early_game_analysis', {})
    wins_early = early_game.get('wins', {})
    losses_early = early_game.get('losses', {})
    
    cs_at_10_wins = wins_early.get('avg_cs_at_10', 0)
    cs_at_10_losses = losses_early.get('avg_cs_at_10', 0)
    early_game_gap = cs_at_10_wins - cs_at_10_losses
    
    # Playstyle tags (for additional context)
    tags = rich_ctx.get('playstyle_tags', {})
    
    return {
        'aggression_profile': {
            'avg_kills': avg_kills,
            'avg_deaths': avg_deaths,
            'avg_assists': avg_assists,
            'kill_participation': kill_participation,
            'aggression_ratio': aggression_score,
            'style': 'aggressive' if avg_kills > 6 else 'passive' if avg_kills < 4 else 'balanced',
        },
        'consistency_profile': {
            'kda_standard_deviation': kda_std,
            'performance_volatility': performance_volatility,
            'style': 'consistent' if performance_volatility < 4 else 'volatile' if performance_volatility > 7 else 'moderate',
        },
        'win_conditions': {
            'kda_gap_between_wins_losses': kda_gap,
            'death_discipline_gap': death_discipline_gap,
            'wins_through': 'domination' if kda_gap > 2 else 'consistency' if death_discipline_gap < 2 else 'variance',
            'loses_through': 'deaths' if death_discipline_gap > 3 else 'impact' if kda_gap > 2 else 'coin_flip',
        },
        'early_game_identity': {
            'cs_at_10_wins': cs_at_10_wins,
            'cs_at_10_losses': cs_at_10_losses,
            'early_game_gap': early_game_gap,
            'identity': 'early_game_player' if early_game_gap > 10 else 'scaling_player' if early_game_gap < 5 else 'balanced',
        },
        'playstyle_tags_summary': {
            'strengths': [tag['label'] for tag in tags.get('strengths', [])],
            'weaknesses': [tag['label'] for tag in tags.get('weaknesses', [])],
        },
        'win_rate': overview.get('win_rate', 0),
    }


@tool
def get_behavioral_patterns() -> dict:
    """
    Get specific behavioral patterns that distinguish wins from losses.
    Shows what the player does differently when winning vs losing.
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    # Use current_filtered_context to respect queue filters
    rich_ctx = ctx.get('current_filtered_context') or ctx.get('rich_context')
    win_loss = rich_ctx.get('win_loss_comparison', {})
    
    # CS patterns
    win_cs = win_loss.get('win_avg_cs', 0)
    loss_cs = win_loss.get('loss_avg_cs', 0)
    cs_gap = win_cs - loss_cs
    
    # Damage patterns
    win_dmg = win_loss.get('win_avg_damage', 0)
    loss_dmg = win_loss.get('loss_avg_damage', 0)
    damage_gap = win_dmg - loss_dmg
    
    # Vision patterns
    win_vision = win_loss.get('win_avg_vision', 0)
    loss_vision = win_loss.get('loss_avg_vision', 0)
    vision_gap = win_vision - loss_vision
    
    # Gold efficiency
    win_gold = win_loss.get('win_avg_gold', 0)
    loss_gold = win_loss.get('loss_avg_gold', 0)
    gold_gap = win_gold - loss_gold
    
    # KDA breakdown
    win_kda = win_loss.get('win_avg_kda', 0)
    loss_kda = win_loss.get('loss_avg_kda', 0)
    
    win_kills = win_loss.get('win_avg_kills', 0)
    loss_kills = win_loss.get('loss_avg_kills', 0)
    
    win_deaths = win_loss.get('win_avg_deaths', 0)
    loss_deaths = win_loss.get('loss_avg_deaths', 0)
    
    win_assists = win_loss.get('win_avg_assists', 0)
    loss_assists = win_loss.get('loss_avg_assists', 0)
    
    # Objectives
    obj_by_outcome = rich_ctx.get('objective_control_by_outcome', {})
    
    return {
        'farming_behavior': {
            'cs_gap': cs_gap,
            'win_cs': win_cs,
            'loss_cs': loss_cs,
            'pattern': 'farms_better_when_winning' if cs_gap > 20 else 'farms_similarly' if abs(cs_gap) < 10 else 'farms_worse_when_ahead',
        },
        'combat_behavior': {
            'damage_gap': damage_gap,
            'kills_gap': win_kills - loss_kills,
            'deaths_gap': loss_deaths - win_deaths,  # Positive = dies more in losses
            'assists_gap': win_assists - loss_assists,
            'pattern': 'more_aggressive_wins' if (win_kills - loss_kills) > 1 else 'dies_more_losses' if (loss_deaths - win_deaths) > 3 else 'similar_combat',
        },
        'vision_behavior': {
            'vision_gap': vision_gap,
            'pattern': 'visions_better_wins' if vision_gap > 5 else 'similar_vision',
        },
        'gold_efficiency': {
            'gold_gap': gold_gap,
            'pattern': 'better_gold_conversion' if gold_gap > win_cs * 20 else 'similar_efficiency',
        },
        'objective_control': obj_by_outcome,
        'biggest_difference': (
            'deaths' if (loss_deaths - win_deaths) > max(abs(cs_gap/30), abs(damage_gap/5000), abs(vision_gap/5)) 
            else 'cs' if abs(cs_gap) > max(abs(damage_gap/100), abs(vision_gap) * 10) 
            else 'damage' if abs(damage_gap) > abs(vision_gap) * 1000 
            else 'vision'
        ),
    }


@tool
def get_role_playstyle() -> dict:
    """
    Get role-specific playstyle patterns. Different roles have different win conditions and patterns.
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    # Use current_filtered_context to respect queue filters
    rich_ctx = ctx.get('current_filtered_context') or ctx.get('rich_context')
    
    # Get role info
    role_consistency = rich_ctx.get('role_consistency', {})
    primary_role = role_consistency.get('primary_role', 'UNKNOWN')
    secondary_role = role_consistency.get('secondary_role', 'NONE')
    primary_pct = role_consistency.get('primary_role_percentage', 0)
    
    result = {
        'primary_role': primary_role,
        'secondary_role': secondary_role,
        'role_commitment': 'one_trick' if primary_pct > 80 else 'main_role' if primary_pct > 60 else 'flex_player',
        'primary_percentage': primary_pct,
    }
    
    # Role-specific metrics
    if primary_role == 'JUNGLE':
        jungle_perf = rich_ctx.get('jungle_performance', {})
        if jungle_perf.get('has_jungle_data'):
            result['jungle_style'] = {
                'objective_control': jungle_perf.get('jungle_objective_control', 0),
                'pressure_score': jungle_perf.get('jungle_pressure_score', 0),
                'counter_jungle': jungle_perf.get('counter_jungle_score', 0),
                'avg_epic_monsters': jungle_perf.get('avg_epic_monsters', 0),
                'style': (
                    'objective_focused' if jungle_perf.get('jungle_objective_control', 0) > 7 
                    else 'early_pressure' if jungle_perf.get('jungle_pressure_score', 0) > 7
                    else 'invader' if jungle_perf.get('counter_jungle_score', 0) > 7
                    else 'balanced'
                ),
            }
    
    elif primary_role == 'UTILITY':
        support_perf = rich_ctx.get('support_performance', {})
        if support_perf.get('has_support_data'):
            result['support_style'] = {
                'vision_dominance': support_perf.get('vision_dominance_score', 0),
                'utility_output': support_perf.get('utility_output_score', 0),
                'frontline_score': support_perf.get('frontline_score', 0),
                'avg_vision_per_min': support_perf.get('avg_vision_per_min', 0),
                'style': (
                    'vision_master' if support_perf.get('vision_dominance_score', 0) > 7
                    else 'enchanter' if support_perf.get('utility_output_score', 0) > 7
                    else 'tank' if support_perf.get('frontline_score', 0) > 7
                    else 'balanced'
                ),
            }
    
    elif primary_role in ['TOP', 'MIDDLE', 'BOTTOM']:
        # Laner-specific patterns
        early_game = rich_ctx.get('early_game_analysis', {})
        wins = early_game.get('wins', {})
        losses = early_game.get('losses', {})
        
        result['laner_style'] = {
            'avg_cs_at_10_wins': wins.get('avg_cs_at_10', 0),
            'avg_cs_at_10_losses': losses.get('avg_cs_at_10', 0),
            'laning_strength': (
                'lane_dominant' if wins.get('avg_cs_at_10', 0) > 70 and wins.get('avg_cs_at_10', 0) - losses.get('avg_cs_at_10', 0) > 15
                else 'scaling_focused' if losses.get('avg_cs_at_10', 0) > 60 and abs(wins.get('avg_cs_at_10', 0) - losses.get('avg_cs_at_10', 0)) < 10
                else 'inconsistent'
            ),
        }
    
    return result