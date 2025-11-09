from strands import tool
from agents.context_manager import get_context


@tool
def get_champion_insights_summary() -> dict:
    """
    Get comprehensive champion pool data matching what's displayed on the page.
    Returns tier distribution, detailed champion stats, and pool diversity metrics.
    """
    ctx = get_context()
    
    if not ctx['is_loaded'] or ctx['champ_insights'] is None:
        return {"error": "No champion data loaded"}
    
    champ_insights = ctx['champ_insights']
    
    # Tier distribution - exactly as shown on page
    tier_counts = champ_insights['Tier'].value_counts().to_dict()
    
    # Get ALL champions by tier (not just top 3)
    champions_by_tier = {}
    for tier in ['A-Tier', 'B-Tier', 'C-Tier', 'D-Tier']:
        tier_champs = champ_insights[champ_insights['Tier'] == tier]
        if len(tier_champs) > 0:
            champions_by_tier[tier] = tier_champs[
                ['Champion', 'Avg_KDA', 'Win_Rate', 'Games']
            ].to_dict('records')
    
    # Champion pool diversity - as calculated on page
    total_champs = len(champ_insights)
    total_games = int(champ_insights['Games'].sum())
    diversity_ratio = total_champs / total_games if total_games > 0 else 0
    
    # Best performer (top of the list)
    best_champ = champ_insights.iloc[0]
    best_performer = {
        'champion': best_champ['Champion'],
        'kda': float(best_champ['Avg_KDA']),
        'win_rate': float(best_champ['Win_Rate']),
        'games': int(best_champ['Games'])
    }
    
    # Games distribution - how concentrated is the pool?
    top_3_games = champ_insights.head(3)['Games'].sum()
    top_3_percentage = (top_3_games / total_games * 100) if total_games > 0 else 0
    
    return {
        'tier_distribution': tier_counts,
        'champions_by_tier': champions_by_tier,
        'total_champions': total_champs,
        'total_games': total_games,
        'diversity_ratio': diversity_ratio,
        'best_performer': best_performer,
        'top_3_games_percentage': top_3_percentage,
        'diversity_assessment': 'high' if diversity_ratio > 0.5 else 'focused' if diversity_ratio < 0.3 else 'balanced',
    }


@tool
def get_advanced_stats_summary() -> dict:
    """
    Get ALL advanced statistics exactly as displayed on the Advanced Stats page.
    Returns performance metrics, consistency metrics, champion pool stats, performance scores,
    and role-specific metrics (jungle/support if applicable).
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    rich_ctx = ctx['rich_context']
    
    # Get role information
    role_consistency = rich_ctx.get('role_consistency', {})
    primary_role = role_consistency.get('primary_role', 'UNKNOWN')
    secondary_role = role_consistency.get('secondary_role', 'NONE')
    
    # Get role-specific performance data
    laner_perf = rich_ctx.get('laner_performance', {})
    jungle_perf = rich_ctx.get('jungle_performance', {})
    support_perf = rich_ctx.get('support_performance', {})
    
    return {
        'role_info': {
            'primary_role': primary_role,
            'secondary_role': secondary_role,
            'primary_percentage': role_consistency.get('primary_role_percentage', 0),
            'secondary_percentage': role_consistency.get('secondary_role_percentage', 0),
        },
        'laner_metrics': laner_perf if laner_perf.get('has_laner_data', False) else None,
        'jungle_metrics': jungle_perf if jungle_perf.get('has_jungle_data', False) else None,
        'support_metrics': support_perf if support_perf.get('has_support_data', False) else None,
        'note': 'Role-specific metrics available. Use role_info to understand player context.'
    }


@tool
def get_page_specific_metrics(page_data: dict) -> dict:
    """
    Generic tool to receive page-specific metrics that are calculated in main.py.
    This allows passing exact metrics shown on each page.
    """
    return page_data


@tool
def get_early_late_game_summary() -> dict:
    """
    Get comprehensive early vs late game data for ALL roles the player plays.
    Returns role-specific early game stats (laner, jungle, support).
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    rich_ctx = ctx['rich_context']
    
    # Get role information
    role_consistency = rich_ctx.get('role_consistency', {})
    primary_role = role_consistency.get('primary_role', 'UNKNOWN')
    secondary_role = role_consistency.get('secondary_role', 'NONE')
    
    # Get early game data for each role type
    
    
    result = {
        'role_info': {
            'primary_role': primary_role,
            'secondary_role': secondary_role,
        }
    }
    
    # Add laner stats if applicable
    if primary_role in ['TOP', 'MIDDLE', 'BOTTOM'] or secondary_role in ['TOP', 'MIDDLE', 'BOTTOM']:
        laner_early = rich_ctx.get('early_game_analysis', {})
        wins = laner_early.get('wins', {})
        losses = laner_early.get('losses', {})
        
        result['laner_early_game'] = {
            'wins': {
                'cs_at_10': wins.get('avg_cs_at_10', 0),
                'gold_per_min': wins.get('avg_gold_at_10', 0) / 10 if wins.get('avg_gold_at_10', 0) > 0 else 0,
                'early_kills': wins.get('first_blood_rate', 0),
            },
            'losses': {
                'cs_at_10': losses.get('avg_cs_at_10', 0),
                'gold_per_min': losses.get('avg_gold_at_10', 0) / 10 if losses.get('avg_gold_at_10', 0) > 0 else 0,
                'early_kills': losses.get('first_blood_rate', 0),
            },
            'cs_diff': wins.get('avg_cs_at_10', 0) - losses.get('avg_cs_at_10', 0),
        }
    elif primary_role == 'JUNGLE' or secondary_role == 'JUNGLE':
        jungle_early = rich_ctx.get('early_game_jungle_analysis', {})
        wins = jungle_early.get('wins', {})
        losses = jungle_early.get('losses', {})
        
        result['jungle_early_game'] = {
            'wins': {
                'jungle_cs_10': wins.get('avg_jungle_cs_10', 0),
                'gold_per_min': wins.get('avg_gold_per_min', 0) / 10 if wins.get('avg_gold_at_10', 0) > 0 else 0,
                'early_kills': wins.get('avg_early_takedowns', 0),
            },
            'losses': {
                'jungle_cs_10': losses.get('avg_jungle_cs_10', 0),
                'gold_per_min': losses.get('avg_gold_per_min', 0) / 10 if losses.get('avg_gold_at_10', 0) > 0 else 0,
                'early_kills': losses.get('avg_early_takedowns', 0),
            },
            'cs_diff': wins.get('avg_cs_at_10', 0) - losses.get('avg_cs_at_10', 0),
        }
    elif primary_role == 'UTILITY' or secondary_role == 'UTILITY':
        support_early = rich_ctx.get('early_game_support_analysis', {})
        wins = support_early.get('wins', {})
        losses = support_early.get('losses', {})
        
        result['support_early_game'] = {
            'wins': {
                'wards_at_10': wins.get('avg_wards_at_10', 0),
                'quest_completion_rate': wins.get('quest_completion_rate', 0) / 10 if wins.get('avg_gold_at_10', 0) > 0 else 0,
                'early_assists': wins.get('avg_early_assists', 0),
            },
            'losses': {
                'wards_at_10': losses.get('avg_wards_at_10', 0),
                'quest_completion_rate': losses.get('quest_completion_rate', 0) / 10 if losses.get('avg_gold_at_10', 0) > 0 else 0,
                'early_assists': losses.get('avg_early_assists', 0),
            },
            'ward_diff': wins.get('avg_wards_at_10', 0) - losses.get('avg_wards_at_10', 0),
        }
    result['note'] = 'Early game stats shown per role. Laners judged on CS@10, junglers on clear speed, supports on vision.'
    
    return result

@tool
def get_matchup_analysis_summary() -> dict:
    """
    Get complete matchup analysis exactly as displayed on page.
    Returns best matchups (60%+ WR), worst matchups (<40% WR), and all matchup details including CS diff@10.
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    # Get role information
    rich_ctx = ctx['rich_context']
    role_consistency = rich_ctx.get('role_consistency', {})
    primary_role = role_consistency.get('primary_role', 'UNKNOWN')
    secondary_role = role_consistency.get('secondary_role', 'NONE')
    
    matchups = rich_ctx.get('matchup_data', {})
    
    if not matchups:
        return {"error": "No matchup data available"}
    
    # Filter matchups with 2+ games (same threshold as page display)
    valid_matchups = {k: v for k, v in matchups.items() if v['games'] >= 2}
    
    if not valid_matchups:
        return {"error": "Not enough matchup data (need 2+ games per matchup)"}
    
    # Sort by win rate (same as page)
    sorted_matchups = sorted(valid_matchups.items(), key=lambda x: x[1]['win_rate'], reverse=True)
    
    # Best matchups - 60%+ WR with ALL available stats
    best_matchups = [
        {
            'my_champion': v['my_champion'],
            'opponent': v['opponent'],
            'role': v.get('role', 'UNKNOWN'),
            'win_rate': round(v['win_rate'], 1),
            'games': v['games'],
            'avg_kda': round(v['avg_kda'], 2),
            'avg_dpm': round(v.get('avg_dpm', 0), 0),
            
            # Laner stats (will be present for all, but most relevant for TOP/MID/BOT)
            'avg_cs': round(v['avg_cs'], 1),
            'avg_cs_diff_at_10': round(v.get('avg_cs_diff', 0), 1),
            'avg_damage': round(v['avg_damage'], 0),
            
            # Jungle stats (only populated if role == JUNGLE)
            'avg_jungle_cs_diff': round(v.get('avg_jungle_cs_diff', 0), 1),
            'avg_epic_monsters': round(v.get('avg_epic_monsters', 0), 1),
            'avg_scuttles': round(v.get('avg_scuttles', 0), 1),
            
            # Support stats (only populated if role == UTILITY)
            'avg_vision_at_10': round(v.get('avg_vision_at_10', 0), 1),
            'avg_heal_shield': round(v.get('avg_heal_shield', 0), 0),
        }
        for k, v in sorted_matchups if v['win_rate'] >= 60
    ]

    # Worst matchups - <40% WR with ALL available stats
    worst_matchups = [
        {
            'my_champion': v['my_champion'],
            'opponent': v['opponent'],
            'role': v.get('role', 'UNKNOWN'),
            'win_rate': round(v['win_rate'], 1),
            'games': v['games'],
            'avg_kda': round(v['avg_kda'], 2),
            'avg_dpm': round(v.get('avg_dpm', 0), 0),
            
            # Laner stats
            'avg_cs': round(v['avg_cs'], 1),
            'avg_cs_diff_at_10': round(v.get('avg_cs_diff', 0), 1),
            'avg_damage': round(v['avg_damage'], 0),
            
            # Jungle stats
            'avg_jungle_cs_diff': round(v.get('avg_jungle_cs_diff', 0), 1),
            'avg_epic_monsters': round(v.get('avg_epic_monsters', 0), 1),
            'avg_scuttles': round(v.get('avg_scuttles', 0), 1),
            
            # Support stats
            'avg_vision_at_10': round(v.get('avg_vision_at_10', 0), 1),
            'avg_heal_shield': round(v.get('avg_heal_shield', 0), 0),
        }
        for k, v in sorted_matchups if v['win_rate'] < 40
    ]
    
    # Overall stats
    total_matchups = len(valid_matchups)
    avg_win_rate = sum(v['win_rate'] for v in valid_matchups.values()) / len(valid_matchups)

    # Determine role-specific interpretation
    interpretation = {
        'best_threshold': '60%+ win rate',
        'worst_threshold': 'Below 40% win rate',
        'recommendation': 'Consider banning worst matchups or dodging them in ranked',
    }

    # Add role-specific guidance
    if primary_role in ['TOP', 'MIDDLE', 'BOTTOM']:
        interpretation.update({
            'primary_role': f'Laner ({primary_role})',
            'key_metrics': 'CS diff@10, KDA, and damage output',
            'cs_diff_meaning': 'Positive CS diff@10 means you are ahead in lane, negative means behind',
            'success_indicator': 'CS advantage >10 and KDA >3 indicates dominant matchup',
        })
    elif primary_role == 'JUNGLE':
        interpretation.update({
            'primary_role': 'Jungler',
            'key_metrics': 'Jungle CS diff@10, epic monster control, and scuttle control',
            'jungle_cs_meaning': 'Positive jungle CS diff means better jungle clear/pathing than opponent',
            'success_indicator': 'Jungle CS diff >5 and epic monsters >1.5 indicates dominant matchup',
        })
    elif primary_role == 'UTILITY':
        interpretation.update({
            'primary_role': 'Support',
            'key_metrics': 'Vision score@10, healing/shielding output, and KDA',
            'vision_meaning': 'Vision @10 >8 indicates strong early vision control',
            'success_indicator': 'Vision @10 >8 and KDA >3 indicates dominant matchup',
        })
    else:
        interpretation.update({
            'primary_role': 'Multi-role player',
            'key_metrics': 'KDA and damage per minute (role-agnostic)',
            'note': 'Stats vary by matchup role - check individual matchup details',
        })

    # Add secondary role note if exists
    if secondary_role != 'NONE':
        interpretation['secondary_role'] = secondary_role
        interpretation['role_note'] = f'You also play {secondary_role} - matchups include both roles'

    return {
        'total_matchups_tracked': total_matchups,
        'primary_role': primary_role,
        'secondary_role': secondary_role if secondary_role != 'NONE' else None,
        'best_matchups_count': len(best_matchups),
        'worst_matchups_count': len(worst_matchups),
        'best_matchups': best_matchups,
        'worst_matchups': worst_matchups,
        'avg_win_rate_across_all_matchups': round(avg_win_rate, 1),
        'interpretation': interpretation,
    }


@tool
def get_performance_trends_summary() -> dict:
    """
    Get comprehensive performance trends exactly as shown on Performance Analysis page.
    Returns KDA trends, win rate, K/D/A averages, wins vs losses comparison, recent form,
    and top performing champions.
    """
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    rich_ctx = ctx['rich_context']
    champ_details = rich_ctx.get('champion_details', {})
    
    overview = rich_ctx.get('overview', {})
    win_loss = rich_ctx.get('win_loss_comparison', {})
    combat = rich_ctx.get('combat_stats', {})
    
    # Overall stats
    total_games = overview.get('total_games', 0)
    wins = overview.get('wins', 0)
    losses = overview.get('losses', 0)
    win_rate = overview.get('win_rate', 0)
    
    # K/D/A averages (shown in bar chart)
    avg_kills = combat.get('avg_kills', 0)
    avg_deaths = combat.get('avg_deaths', 0)
    avg_assists = combat.get('avg_assists', 0)
    avg_kda = combat.get('avg_kda', 0)
    
    # Recent matches (last 5 shown in match history)
    recent_matches = rich_ctx.get('recent_matches', [])
    recent_wins = sum(1 for m in recent_matches if m.get('win'))
    recent_losses = len(recent_matches) - recent_wins
    
    # CS comparison (from win_loss_comparison)
    win_avg_cs = win_loss.get('win_avg_cs', 0)
    loss_avg_cs = win_loss.get('loss_avg_cs', 0)
    cs_difference = win_avg_cs - loss_avg_cs
    
    # Damage comparison
    win_avg_damage = win_loss.get('win_avg_damage', 0)
    loss_avg_damage = win_loss.get('loss_avg_damage', 0)
    damage_difference = win_avg_damage - loss_avg_damage
    
    # Vision comparison
    win_avg_vision = win_loss.get('win_avg_vision', 0)
    loss_avg_vision = win_loss.get('loss_avg_vision', 0)
    
    # Top performing champions (by performance score: games, KDA, win rate weighted)
    top_champions = []
    for champ_name, champ_data in champ_details.items():
        games = champ_data.get('games', 0)
        if games < 2:  # Skip champions with too few games
            continue
        
        # Calculate performance score (same formula as in main.py)
        wins_champ = champ_data.get('wins', 0)
        wr = (wins_champ / games * 100) if games > 0 else 0
        
        avg_dmg = champ_data.get('avg_damage', 0)
        avg_cs_champ = champ_data.get('avg_cs', 0)
        
        # Approximate KDA from champion data
        # We have total damage, cs, etc. but not direct KDA
        # Use win rate and games as proxy
        import math
        games_weight = min(math.log1p(games) * 2, 10)
        wr_score = wr / 10
        
        # Simple performance score
        performance_score = (games_weight * 0.5) + (wr_score * 0.5)
        
        top_champions.append({
            'champion': champ_name,
            'games': games,
            'win_rate': wr,
            'avg_damage': avg_dmg,
            'avg_cs': avg_cs_champ,
            'performance_score': performance_score,
        })
    
    # Sort by performance score and take top 5
    top_champions = sorted(top_champions, key=lambda x: x['performance_score'], reverse=True)[:5]
    
    return {
        'overall_performance': {
            'win_rate': win_rate,
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'avg_kda': avg_kda,
        },
        'kda_breakdown': {
            'avg_kills': avg_kills,
            'avg_deaths': avg_deaths,
            'avg_assists': avg_assists,
        },
        'win_vs_loss_comparison': {
            'cs_difference': cs_difference,
            'damage_difference': damage_difference,
            'win_avg_cs': win_avg_cs,
            'loss_avg_cs': loss_avg_cs,
            'win_avg_damage': win_avg_damage,
            'loss_avg_damage': loss_avg_damage,
            'win_avg_vision': win_avg_vision,
            'loss_avg_vision': loss_avg_vision,
        },
        'recent_form': {
            'last_5_games': len(recent_matches),
            'recent_wins': recent_wins,
            'recent_losses': recent_losses,
            'recent_win_rate': (recent_wins / len(recent_matches) * 100) if recent_matches else 0,
        },
        'top_performing_champions': top_champions,
        'key_patterns': {
            'biggest_stat_difference': 'CS' if abs(cs_difference) > abs(damage_difference/1000) else 'Damage',
            'cs_gap_severity': 'large' if abs(cs_difference) > 30 else 'moderate' if abs(cs_difference) > 15 else 'small',
        }
    }