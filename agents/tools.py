from strands import tool
from agents.context_manager import get_context

@tool
def get_player_overview() -> dict:
    """Get high-level player stats (win rate, KDA, games played)"""
    ctx = get_context()
    
    if not ctx['is_loaded'] or ctx['rich_context'] is None:
        return {"error": "No player data loaded"}
    
    return ctx['rich_context'].get("overview", {})

@tool
def get_detailed_stats(category: str) -> dict:
    """Get detailed stats for a category. Categories: 'combat', 'farming', 'vision', 'champion_pool'"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No player data loaded"}
    
    valid_categories = {
        'combat': 'combat_stats',
        'farming': 'farming_economy', 
        'vision': 'vision_control',
        'champion_pool': 'champion_pool'
    }
    
    key = valid_categories.get(category.lower())
    if not key:
        return {"error": f"Invalid category. Use: {', '.join(valid_categories.keys())}"}
    
    return ctx['rich_context'].get(key, {})

@tool
def compare_win_loss(stat_type: str) -> dict:
    """Compare stats between wins and losses. Types: 'cs', 'damage', 'vision'"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No player data loaded"}
    
    comparisons = ctx['rich_context'].get("win_loss_comparison", {})
    win_key = f"win_avg_{stat_type}"
    loss_key = f"loss_avg_{stat_type}"
    
    if win_key not in comparisons:
        return {"error": f"Invalid stat type. Use: cs, damage, vision"}
    
    return {
        "win_avg": comparisons[win_key],
        "loss_avg": comparisons[loss_key],
        "difference": comparisons[win_key] - comparisons[loss_key]
    }

@tool
def get_champion_stats(champion_name: str) -> dict:
    """Get performance stats for a specific champion"""
    ctx = get_context()
    
    if not ctx['is_loaded'] or ctx['champ_insights'] is None:
        return {"error": "No champion data loaded"}
    
    champ_insights = ctx['champ_insights']
    champ_row = champ_insights[champ_insights['Champion'].str.lower() == champion_name.lower()]
    
    if len(champ_row) == 0:
        available = ', '.join(champ_insights['Champion'].tolist()[:5])
        return {"error": f"Champion '{champion_name}' not found. Available: {available}..."}
    
    return champ_row.iloc[0].to_dict()

@tool
def get_champion_comparison(champion1: str, champion2: str) -> dict:
    """Compare detailed stats between two champions"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    champ_details = ctx['rich_context'].get('champion_details', {})
    
    c1 = champ_details.get(champion1)
    c2 = champ_details.get(champion2)
    
    if not c1:
        return {"error": f"No data for {champion1}"}
    if not c2:
        return {"error": f"No data for {champion2}"}
    
    return {
        "champion1": champion1,
        "champion2": champion2,
        "damage_comparison": {
            f"{champion1}_avg_damage": c1['avg_damage'],
            f"{champion2}_avg_damage": c2['avg_damage'],
            "difference": c1['avg_damage'] - c2['avg_damage']
        },
        "farming_comparison": {
            f"{champion1}_cs": c1['avg_cs'],
            f"{champion2}_cs": c2['avg_cs'],
            f"{champion1}_cs_at_10": c1['avg_cs_at_10'],
            f"{champion2}_cs_at_10": c2['avg_cs_at_10'],
        },
        "vision_comparison": {
            f"{champion1}_vision": c1['avg_vision'],
            f"{champion2}_vision": c2['avg_vision'],
        },
        "win_rates": {
            f"{champion1}_wr": c1['win_rate'],
            f"{champion2}_wr": c2['win_rate'],
        }
    }

@tool
def get_early_game_stats() -> dict:
    """Get detailed early game (0-10 minutes) performance"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    return ctx['rich_context'].get('early_game_analysis', {})

@tool
def get_damage_profile() -> dict:
    """Get player's damage composition and efficiency metrics"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    return ctx['rich_context'].get('damage_profile', {})

@tool
def get_objective_control_stats() -> dict:
    """Get overall statistics about objective control (dragons, barons, heralds, turrets)"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    # Return both overall and by-outcome stats
    return {
        'overall': ctx['rich_context'].get('objective_control', {}),
        'by_outcome': ctx['rich_context'].get('objective_control_by_outcome', {}),
    }

@tool
def list_champions() -> list:
    """Get list of all champions the player has played"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return []
    
    champ_details = ctx['rich_context'].get('champion_details', {})
    return list(champ_details.keys())

@tool
def get_matchup_stats(my_champion: str, opponent_champion: str) -> dict:
    """Get head-to-head stats for a specific champion matchup (e.g., Lucian vs Jinx)"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    matchup_key = f"{my_champion}_vs_{opponent_champion}"
    matchups = ctx['rich_context'].get('matchup_data', {})
    
    if matchup_key not in matchups:
        return {"error": f"No matchup data for {my_champion} vs {opponent_champion}"}
    
    return matchups[matchup_key]


@tool
def get_stats_vs_opponent(opponent_champion: str) -> dict:
    """Get overall stats against a specific opponent across all your champions"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    opponent_stats = ctx['rich_context'].get('opponent_stats', {})
    
    if opponent_champion not in opponent_stats:
        return {"error": f"No games found against {opponent_champion}"}
    
    return opponent_stats[opponent_champion]


@tool
def list_matchups_for_champion(champion: str) -> list:
    """List all matchups played with a specific champion"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return []
    
    matchups = ctx['rich_context'].get('matchup_data', {})
    
    return [
        {
            'opponent': data['opponent'],
            'games': data['games'],
            'win_rate': data['win_rate']
        }
        for key, data in matchups.items()
        if data['my_champion'] == champion
    ]

@tool
def get_role_analysis() -> dict:
    """Get player's role distribution and performance by role (TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY)"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    return ctx['rich_context'].get('role_analysis', {})


@tool
def get_objective_control_by_outcome() -> dict:
    """Compare objective control (dragons, barons, heralds, turrets) between wins and losses"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    return ctx['rich_context'].get('objective_control_by_outcome', {})

@tool
def get_role_consistency() -> dict:
    """Get player's primary and secondary roles with consistency metrics"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    return ctx['rich_context'].get('role_consistency', {})


@tool
def get_jungle_performance() -> dict:
    """Get jungle-specific performance metrics (only available if player plays jungle)"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    jungle_perf = ctx['rich_context'].get('jungle_performance', {})
    
    if not jungle_perf.get('has_jungle_data', False):
        return {"error": "Player has not played jungle in recent matches"}
    
    return jungle_perf


@tool
def get_support_performance() -> dict:
    """Get support-specific performance metrics (only available if player plays support)"""
    ctx = get_context()
    
    if not ctx['is_loaded']:
        return {"error": "No data loaded"}
    
    support_perf = ctx['rich_context'].get('support_performance', {})
    
    if not support_perf.get('has_support_data', False):
        return {"error": "Player has not played support in recent matches"}
    
    return support_perf