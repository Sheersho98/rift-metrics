import json
import pandas as pd
from data.metrics import (
    calculate_jungle_early_game_stats,
    calculate_support_early_game_stats
)


def build_rich_player_context(raw_matches: list, metrics: dict, champ_insights: pd.DataFrame) -> dict:
    #rich context
    #structured context for raw data for the AI - returns dict (converted into json and injected into prompts)
    if not raw_matches or len(raw_matches) == 0:
        return {}
    
    # Extract detailed stats from raw matches
    detailed_matches = []
    
    for match in raw_matches:
        detailed_match = {
            # Basic info
            "champion": match.get('championName', 'Unknown'),
            "win": match.get('win', False),
            
            # KDA
            "kills": match.get('kills', 0),
            "deaths": match.get('deaths', 0),
            "assists": match.get('assists', 0),
            
            # Farm & Economy
            "totalMinionsKilled": match.get('totalMinionsKilled', 0),
            "neutralMinionsKilled": match.get('neutralMinionsKilled', 0),
            "goldEarned": match.get('goldEarned', 0),
            
            # Healing and Damage Dealt/Taken
            "totalDamageDealtToChampions": match.get('totalDamageDealtToChampions', 0),
            "totalDamageTaken": match.get('totalDamageTaken', 0),
            "damagePerMinute": match.get('challenges', {}).get('damagePerMinute', 0),
            "damageTakenOnTeamPercentage": match.get('challenges', {}).get('damageTakenOnTeamPercentage', 0),
            "totalDamageShieldedOnTeammates": match.get('challenges', {}).get('totalDamageShieldedOnTeammates', 0),
            "effectiveHealAndShielding" : match.get('challenges', {}).get('effectiveHealAndShielding', 0),
            
            # Vision
            "visionScore": match.get('visionScore', 0),
            "wardsPlaced": match.get('wardsPlaced', 0),
            "wardsKilled": match.get('wardTakedowns', 0),
            
            # Game details
            "gameDuration": match.get('challenges', {}).get('gameLength', 0),
            "position": match.get('teamPosition', 'UNKNOWN'),
            
            # Performance indicators (from challenges)
            "isLaner": match.get('teamPosition', 'UNKNOWN') in ['TOP', 'MID', 'BOTTOM'],
            "killParticipation": match.get('challenges', {}).get('killParticipation', 0),
            "laneMinionsFirst10Minutes": match.get('challenges', {}).get('laneMinionsFirst10Minutes', 0),
            "maxCsAdvantageOnLaneOpponent": match.get('challenges', {}).get('maxCsAdvantageOnLaneOpponent', 0),
            "soloKills": match.get('challenges', {}).get('soloKills', 0),
            "turretPlatesTaken": match.get('challenges', {}).get('turretPlatesTaken', 0),

            # Jungle-specific stats (only relevant if position is JUNGLE)
            "isJungler": match.get('teamPosition', 'UNKNOWN') == 'JUNGLE',
            "jungleCsBefore10Minutes": match.get('challenges', {}).get('jungleCsBefore10Minutes', 0),
            "scuttleCrabKills": match.get('challenges', {}).get('scuttleCrabKills', 0),
            "voidMonsterKill": match.get('challenges', {}).get('voidMonsterKill', 0),
            "dragonKills": match.get('challenges', {}).get('dragonKills', 0),
            "dragonTakedowns": match.get('challenges', {}).get('dragonTakedowns', 0),
            "teamRiftHeraldKills" : match.get('challenges', {}).get('teamRiftHeraldKills', 0),
            "teamElderDragonKills" : match.get('challenges', {}).get('teamElderDragonKills', 0),
            "teamBaronKills" : match.get('challenges', {}).get('teamBaronKills', 0),
            "moreEnemyJungleThanOpponent": match.get('challenges', {}).get('moreEnemyJungleThanOpponent', False),
            "enemyJungleMonsterKills": match.get('challenges', {}).get('enemyJungleMonsterKills', 0),
            "epicMonsterSteals": match.get('challenges', {}).get('epicMonsterSteals', 0),
            "buffsStolen": match.get('challenges', {}).get('buffsStolen', 0),

            #Support-specific stats (only relevant if position is UTILITY)
            "isSupport": match.get('teamPosition', 'UNKNOWN') == 'UTILITY',
            "controlWardsPlaced": match.get('challenges', {}).get('controlWardsPlaced', 0),
            "stealthWardsPlaced": match.get('challenges', {}).get('stealthWardsPlaced', 0),
            "visionScoreAdvantageLaneOpponent": match.get('challenges', {}).get('visionScoreAdvantageLaneOpponent', 0),
            "visionScorePerMinute": match.get('challenges', {}).get('visionScorePerMinute', 0),
            "fasterSupportQuestCompletion": match.get('challenges', {}).get('fasterSupportQuestCompletion', 0),
            "wardTakedownsBefore20M": match.get('challenges', {}).get('wardTakedownsBefore20M', 0),
            "wardsGuarded": match.get('challenges', {}).get('wardsGuarded', 0),
        }
        detailed_matches.append(detailed_match)
    
    # Aggregate statistics
    wins = [m for m in detailed_matches if m['win']]
    losses = [m for m in detailed_matches if not m['win']]
    
    # Calculate advanced metrics
    context = {
        "overview": {
            "total_games": len(detailed_matches),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": (len(wins) / len(detailed_matches)) * 100 if detailed_matches else 0,
        },
        
        "combat_stats": {
            "avg_kills": metrics['avg_kills'],
            "avg_deaths": metrics['avg_deaths'],
            "avg_assists": metrics['avg_assists'],
            "avg_kda": metrics['avg_kda'],
            "avg_damage_to_champs": sum(m['totalDamageDealtToChampions'] for m in detailed_matches) / len(detailed_matches),
            "avg_damage_taken": sum(m['totalDamageTaken'] for m in detailed_matches) / len(detailed_matches),
            "avg_damage_taken_percent": sum(m.get('challenges', {}).get('damageTakenOnTeamPercentage', 0) for m in detailed_matches) / len(detailed_matches) * 100,
            "avg_damage_shielded": sum(m.get('challenges', {}).get('totalDamageShieldedOnTeammates', 0) for m in detailed_matches) / len(detailed_matches),
            "avg_effective_heal_shield": sum(m.get('challenges', {}).get('effectiveHealAndShielding', 0) for m in detailed_matches) / len(detailed_matches),
        },

        "damage_efficiency": {
            "avg_damage_per_minute": sum(m['damagePerMinute'] for m in detailed_matches) / len(detailed_matches),
        },
        "laner_performance": analyze_laner_stats(detailed_matches),
        "jungle_performance": analyze_jungle_stats(detailed_matches),
        "support_performance": analyze_support_stats(detailed_matches),
        
        "farming_economy": {
            "avg_cs": sum(m['totalMinionsKilled'] for m in detailed_matches) / len(detailed_matches),
            "avg_jungle_cs": sum(m['neutralMinionsKilled'] for m in detailed_matches) / len(detailed_matches),
            "avg_gold": sum(m['goldEarned'] for m in detailed_matches) / len(detailed_matches),
            "avg_cs_at_10": sum(m['laneMinionsFirst10Minutes'] for m in detailed_matches) / len(detailed_matches) if detailed_matches else 0,
        },
        
        "vision_control": {
            "avg_vision_score": sum(m['visionScore'] for m in detailed_matches) / len(detailed_matches),
            "avg_wards_placed": sum(m['wardsPlaced'] for m in detailed_matches) / len(detailed_matches),
            "avg_wards_killed": sum(m['wardsKilled'] for m in detailed_matches) / len(detailed_matches),
        },
        
        "win_loss_comparison": {
            "win_avg_cs": sum(m['totalMinionsKilled'] for m in wins) / len(wins) if wins else 0,
            "loss_avg_cs": sum(m['totalMinionsKilled'] for m in losses) / len(losses) if losses else 0,
            "win_avg_damage": sum(m['totalDamageDealtToChampions'] for m in wins) / len(wins) if wins else 0,
            "loss_avg_damage": sum(m['totalDamageDealtToChampions'] for m in losses) / len(losses) if losses else 0,
            "win_avg_vision": sum(m['visionScore'] for m in wins) / len(wins) if wins else 0,
            "loss_avg_vision": sum(m['visionScore'] for m in losses) / len(losses) if losses else 0,
        },
        
        "champion_pool": {
            "unique_champions": metrics['unique_champions'],
            "most_played": champ_insights.iloc[0]['Champion'] if len(champ_insights) > 0 else "Unknown",
            "best_performer": {
                "champion": champ_insights.iloc[0]['Champion'] if len(champ_insights) > 0 else "Unknown",
                "kda": float(champ_insights.iloc[0]['Avg_KDA']) if len(champ_insights) > 0 else 0,
                "win_rate": float(champ_insights.iloc[0]['Win_Rate']) if len(champ_insights) > 0 else 0,
                "games": int(champ_insights.iloc[0]['Games']) if len(champ_insights) > 0 else 0,
            }
        },
        
        # Include last 5 matches with full detail for recency
        "recent_matches": detailed_matches[-5:] if len(detailed_matches) >= 5 else detailed_matches,
        
        # All matches in simplified form (for pattern recognition)
        "match_history": [{
            "champion": m['champion'],
            "win": m['win'],
            "kda": f"{m['kills']}/{m['deaths']}/{m['assists']}",
            "cs": m['totalMinionsKilled'],
            "damage": m['totalDamageDealtToChampions'],
            "vision": m['visionScore']
        } for m in detailed_matches]
    }

    context.update({
        'champion_details': build_champion_specific_context(raw_matches),
        'early_game_analysis': analyze_early_game_patterns(raw_matches),
        'early_game_jungle_analysis': calculate_jungle_early_game_stats(raw_matches),
        'early_game_support_analysis': calculate_support_early_game_stats(raw_matches),
        'damage_profile': analyze_damage_profile(raw_matches),
        
        'matchup_data': build_matchup_data(raw_matches),
        'opponent_stats': build_opponent_analysis(raw_matches),

        'role_analysis': analyze_role_distribution(raw_matches),

        'role_consistency': calculate_role_consistency(raw_matches),

        'objective_control_by_outcome': analyze_objective_control_by_outcome(raw_matches),

        # Objective control
        'objective_control': {
            'avg_dragon_participation': sum(m.get('challenges', {}).get('dragonTakedowns', 0) for m in raw_matches) / len(raw_matches),
            'avg_baron_participation': sum(m.get('challenges', {}).get('baronTakedowns', 0) for m in raw_matches) / len(raw_matches),
            'avg_herald_participation': sum(m.get('challenges', {}).get('riftHeraldTakedowns', 0) for m in raw_matches) / len(raw_matches),
            'avg_turret_plates': sum(m.get('challenges', {}).get('turretPlatesTaken', 0) for m in raw_matches) / len(raw_matches),
        },
        
        # Advanced combat metrics
        'combat_efficiency': {
            'avg_kill_participation': sum(m.get('challenges', {}).get('killParticipation', 0) for m in raw_matches) / len(raw_matches) * 100,
            'avg_solo_kills': sum(m.get('challenges', {}).get('soloKills', 0) for m in raw_matches) / len(raw_matches),
            'avg_damage_per_death': sum(m.get('totalDamageDealtToChampions', 0) / max(m.get('deaths', 1), 1) for m in raw_matches) / len(raw_matches),
            'multi_kill_rate': sum(m.get('doubleKills', 0) + m.get('tripleKills', 0) + m.get('quadraKills', 0) + m.get('pentaKills', 0) for m in raw_matches) / len(raw_matches),
        }
    })


    return context

def build_champion_specific_context(raw_matches: list) -> dict:
    champion_data = {}
    
    for match in raw_matches:
        champ = match.get('championName', 'Unknown')
        
        if champ not in champion_data:
            champion_data[champ] = {
                'games': 0,
                'wins': 0,
                'total_damage': 0,
                'total_damage_taken': 0,
                'total_cs': 0,
                'total_gold': 0,
                'total_vision_score': 0,
                'cs_at_10_list': [],
                'damage_to_objectives': 0,
                'epic_monster_kills': 0,
                'early_kills': 0,  # Kills before 10min
                'epic_monster_participation': 0,
            }
        
        cd = champion_data[champ]
        cd['games'] += 1
        cd['wins'] += 1 if match.get('win') else 0
        cd['total_damage'] += match.get('totalDamageDealtToChampions', 0)
        cd['total_damage_taken'] += match.get('totalDamageTaken', 0)
        cd['total_cs'] += match.get('totalMinionsKilled', 0)
        cd['total_gold'] += match.get('goldEarned', 0)
        cd['total_vision_score'] += match.get('visionScore', 0)
        cd['cs_at_10_list'].append(match.get('challenges', {}).get('laneMinionsFirst10Minutes', 0))
        cd['damage_to_objectives'] += match.get('damageDealtToObjectives', 0)
        cd['epic_monster_kills'] += (match.get('dragonKills', 0) + match.get('baronKills', 0))
        cd['epic_monster_participation'] += (match.get('dragonParticipation', 0) + match.get('dragonParticipation', 0))
        
        # Count early kills (approximate from takedownsFirstXMinutes)
        cd['early_kills'] += match.get('challenges', {}).get('takedownsFirstXMinutes', 0)
    
    # Calculate averages
    for champ, data in champion_data.items():
        games = data['games']
        data['avg_damage'] = data['total_damage'] / games
        data['avg_damage_taken'] = data['total_damage_taken'] / games
        data['avg_cs'] = data['total_cs'] / games
        data['avg_gold'] = data['total_gold'] / games
        data['avg_vision'] = data['total_vision_score'] / games
        data['avg_cs_at_10'] = sum(data['cs_at_10_list']) / len(data['cs_at_10_list']) if data['cs_at_10_list'] else 0
        data['avg_obj_damage'] = data['damage_to_objectives'] / games
        data['early_aggression'] = data['early_kills'] / games
        data['win_rate'] = (data['wins'] / games) * 100
    
    return champion_data

def analyze_early_game_patterns(raw_matches: list) -> dict:
    early_wins = [m for m in raw_matches if m.get('win')]
    early_losses = [m for m in raw_matches if not m.get('win')]
    
    def get_early_stats(matches):
        if not matches:
            return {}
        return {
            'avg_cs_at_10': sum(m.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) for m in matches) / len(matches),
            'avg_gold_at_10': sum(m.get('challenges', {}).get('goldPerMinute', 0) * 10 for m in matches) / len(matches),
            'first_blood_rate': sum(1 for m in matches if m.get('firstBloodKill') or m.get('firstBloodAssist')) / len(matches) * 100,
            'early_deaths': sum(m.get('challenges', {}).get('deathsByEnemyChamps', 0) for m in matches if m.get('challenges', {}).get('gameLength', 999) < 600) / len(matches),
        }
    
    return {
        'wins': get_early_stats(early_wins),
        'losses': get_early_stats(early_losses),
    }

def analyze_damage_profile(raw_matches: list) -> dict:
    total_physical = sum(m.get('physicalDamageDealtToChampions', 0) for m in raw_matches)
    total_magic = sum(m.get('magicDamageDealtToChampions', 0) for m in raw_matches)
    total_true = sum(m.get('trueDamageDealtToChampions', 0) for m in raw_matches)
    total_damage = total_physical + total_magic + total_true
    
    return {
        'physical_percent': (total_physical / total_damage * 100) if total_damage > 0 else 0,
        'magic_percent': (total_magic / total_damage * 100) if total_damage > 0 else 0,
        'true_percent': (total_true / total_damage * 100) if total_damage > 0 else 0,
        'avg_damage_per_gold': total_damage / sum(m.get('goldEarned', 1) for m in raw_matches),
        'avg_damage_share': sum(m.get('challenges', {}).get('teamDamagePercentage', 0) for m in raw_matches) / len(raw_matches) * 100,
    }

def build_matchup_data(raw_matches: list) -> dict:
    matchups = {}
    
    for match in raw_matches:
        my_champion = match.get('championName', 'Unknown')
        my_position = match.get('teamPosition', 'UNKNOWN')
        my_team_id = match.get('teamId')
        
        # Find lane opponent (same position, different team)
        participants = match.get('participants', [])  # You'll need to pass full match data
        
        opponent = None
        for p in participants:
            if p.get('teamPosition') == my_position and p.get('teamId') != my_team_id:
                opponent = p
                break
        
        if not opponent:
            continue
        
        matchup_key = f"{my_champion}_vs_{opponent.get('championName')}"
        
        if matchup_key not in matchups:
            matchups[matchup_key] = {
                'my_champion': my_champion,
                'opponent': opponent.get('championName'),
                'role': my_position,  
                'games': 0,
                'wins': 0,
                'total_kills': 0,
                'total_deaths': 0,
                'total_assists': 0,
                'total_cs': 0,
                'total_damage': 0,
                'total_dpm': 0,  
                'cs_diff_at_10': [],
                
                # Role-specific tracking
                'jungle_cs_at_10': [],  
                'vision_score_at_10': [],  
                'total_heal_shield': 0,  
                'total_epic_monsters': 0,  
                'total_scuttles': 0,  
            }
        
        m = matchups[matchup_key]
        m['games'] += 1
        m['wins'] += 1 if match.get('win') else 0
        m['total_kills'] += match.get('kills', 0)
        m['total_deaths'] += match.get('deaths', 0)
        m['total_assists'] += match.get('assists', 0)
        m['total_cs'] += match.get('totalMinionsKilled', 0)
        m['total_damage'] += match.get('totalDamageDealtToChampions', 0)
        m['total_dpm'] += match.get('challenges', {}).get('damagePerMinute', 0)  # NEW
        
        # Laner stats
        cs_adv_at_10 = (
            match.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) -
            opponent.get('challenges', {}).get('laneMinionsFirst10Minutes', 0)
        )
        m['cs_diff_at_10'].append(cs_adv_at_10)
        
        # Jungle-specific stats
        if my_position == 'JUNGLE':
            my_jungle_cs = match.get('challenges', {}).get('jungleCsBefore10Minutes', 0)
            opp_jungle_cs = opponent.get('challenges', {}).get('jungleCsBefore10Minutes', 0)
            m['jungle_cs_at_10'].append(my_jungle_cs - opp_jungle_cs)
            
            m['total_epic_monsters'] += (match.get('challenges', {}).get('dragonTakedowns', 0) + 
                                         match.get('challenges', {}).get('baronTakedowns', 0))
            m['total_scuttles'] += match.get('challenges', {}).get('scuttleCrabKills', 0)
        
        # Support-specific stats
        if my_position == 'UTILITY':
            my_vision = match.get('visionScore', 0)
            game_length_min = match.get('challenges', {}).get('gameLength', 1800) / 60
            vision_at_10 = (my_vision / game_length_min) * 10 if game_length_min > 0 else 0
            m['vision_score_at_10'].append(vision_at_10)
            
            m['total_heal_shield'] += match.get('challenges', {}).get('effectiveHealAndShielding', 0)
    
    # Calculate averages
    for key, data in matchups.items():
        games = data['games']
        role = data['role']
        
        # Common stats
        data['win_rate'] = (data['wins'] / games) * 100
        data['avg_kda'] = (data['total_kills'] + data['total_assists']) / max(data['total_deaths'], 1)
        data['avg_cs'] = data['total_cs'] / games
        data['avg_damage'] = data['total_damage'] / games
        data['avg_dpm'] = data['total_dpm'] / games 
        
        # Laner-specific averages
        if role in ['TOP', 'MIDDLE', 'BOTTOM']:
            data['avg_cs_diff'] = sum(data['cs_diff_at_10']) / len(data['cs_diff_at_10']) if data['cs_diff_at_10'] else 0
        
        # Jungle-specific averages
        if role == 'JUNGLE':
            data['avg_jungle_cs_diff'] = sum(data['jungle_cs_at_10']) / len(data['jungle_cs_at_10']) if data['jungle_cs_at_10'] else 0
            data['avg_epic_monsters'] = data['total_epic_monsters'] / games
            data['avg_scuttles'] = data['total_scuttles'] / games
        
        # Support-specific averages
        if role == 'UTILITY':
            data['avg_vision_at_10'] = sum(data['vision_score_at_10']) / len(data['vision_score_at_10']) if data['vision_score_at_10'] else 0
            data['avg_heal_shield'] = data['total_heal_shield'] / games
            # Vision score overall already tracked in general stats
    
    return matchups

def build_opponent_analysis(raw_matches: list) -> dict:
    opponent_stats = {}
    
    for match in raw_matches:
        my_position = match.get('teamPosition', 'UNKNOWN')
        my_team_id = match.get('teamId')
        
        participants = match.get('participants', [])
        
        opponent = None
        for p in participants:
            if p.get('teamPosition') == my_position and p.get('teamId') != my_team_id:
                opponent = p.get('championName')
                break
        
        if not opponent:
            continue
        
        if opponent not in opponent_stats:
            opponent_stats[opponent] = {
                'games': 0,
                'wins': 0,
                'total_kda': 0,
            }
        
        opp = opponent_stats[opponent]
        opp['games'] += 1
        opp['wins'] += 1 if match.get('win') else 0
        kda = (match.get('kills', 0) + match.get('assists', 0)) / max(match.get('deaths', 1), 1)
        opp['total_kda'] += kda
    
    # Calculate averages
    for opponent, data in opponent_stats.items():
        data['win_rate'] = (data['wins'] / data['games']) * 100
        data['avg_kda'] = data['total_kda'] / data['games']
    
    return opponent_stats

def analyze_role_distribution(raw_matches: list) -> dict:
    role_stats = {}
    
    for match in raw_matches:
        role = match.get('teamPosition', 'UNKNOWN')
        
        if role not in role_stats:
            role_stats[role] = {
                'games': 0,
                'wins': 0,
                'total_kda_sum': 0,
                'total_cs': 0,
                'total_damage': 0,
            }
        
        rs = role_stats[role]
        rs['games'] += 1
        rs['wins'] += 1 if match.get('win') else 0
        
        kda = (match.get('kills', 0) + match.get('assists', 0)) / max(match.get('deaths', 1), 1)
        rs['total_kda_sum'] += kda
        rs['total_cs'] += match.get('totalMinionsKilled', 0)
        rs['total_damage'] += match.get('totalDamageDealtToChampions', 0)
    
    # Calculate averages and determine primary role
    primary_role = None
    max_games = 0
    
    for role, data in role_stats.items():
        games = data['games']
        data['win_rate'] = (data['wins'] / games) * 100
        data['avg_kda'] = data['total_kda_sum'] / games
        data['avg_cs'] = data['total_cs'] / games
        data['avg_damage'] = data['total_damage'] / games
        data['play_rate'] = (games / len(raw_matches)) * 100
        
        if games > max_games:
            max_games = games
            primary_role = role
    
    return {
        'role_breakdown': role_stats,
        'primary_role': primary_role,
        'primary_role_games': max_games,
        'total_games': len(raw_matches),
    }

def calculate_role_consistency(raw_matches: list) -> dict:
    #Calculate player's most played roles and consistency in sticking to them.
    
    role_counts = {}
    
    for match in raw_matches:
        role = match.get('teamPosition', 'UNKNOWN')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    # Sort by frequency
    sorted_roles = sorted(role_counts.items(), key=lambda x: x[1], reverse=True)
    
    total_games = len(raw_matches)
    
    # Get top 2 roles
    primary_role = sorted_roles[0] if len(sorted_roles) > 0 else ('UNKNOWN', 0)
    secondary_role = sorted_roles[1] if len(sorted_roles) > 1 else ('NONE', 0)
    
    primary_role_name, primary_count = primary_role
    secondary_role_name, secondary_count = secondary_role
    
    # Calculate consistency percentages
    primary_consistency = (primary_count / total_games * 100) if total_games > 0 else 0
    secondary_consistency = (secondary_count / total_games * 100) if total_games > 0 else 0
    top_2_consistency = ((primary_count + secondary_count) / total_games * 100) if total_games > 0 else 0
    
    return {
        'primary_role': primary_role_name,
        'primary_role_games': primary_count,
        'primary_role_percentage': primary_consistency,
        'secondary_role': secondary_role_name,
        'secondary_role_games': secondary_count,
        'secondary_role_percentage': secondary_consistency,
        'top_2_roles_consistency': top_2_consistency,
        'all_roles_played': role_counts,
        'total_games': total_games,
        'role_diversity': len([r for r in role_counts.values() if r > 0]),
    }

def analyze_laner_stats(detailed_matches:list) -> dict:
    laner_matches = [m for m in detailed_matches if m.get('isLaner', False)]

    if not laner_matches:
        return {
            'total_laner_games': 0,
            'has_laner_data': False,
        }
    
    num_laner_games = len(laner_matches)

    # Calculate CS diff at 10 for each laner match
    cs_diffs_at_10 = []
    for match in laner_matches:
        # Getting opponent
        my_position = match.get('position')  # Using 'position' from detailed_matches
        my_team_id = match.get('teamId')
        participants = match.get('participants', [])
        
        opponent = None
        for p in participants:
            if p.get('teamPosition') == my_position and p.get('teamId') != my_team_id:
                opponent = p
                break
        
        if not opponent:
            continue
        
        # Getting CS diff at 10
        cs_diff_at_10 = (
            match.get('laneMinionsFirst10Minutes', 0) -
            opponent.get('challenges', {}).get('laneMinionsFirst10Minutes', 0)
        )
        cs_diffs_at_10.append(cs_diff_at_10)

    return {
        'total_laner_games': num_laner_games,
        'has_laner_data': True,
        
        # Early laning phase (first 10 minutes)
        'avg_cs_at_10': sum(m['laneMinionsFirst10Minutes'] for m in laner_matches) / num_laner_games,
        'avg_cs_diff_at_10': sum(cs_diffs_at_10) / len(cs_diffs_at_10) if cs_diffs_at_10 else 0,
        
        # Lane dominance
        'avg_max_cs_advantage': sum(m['maxCsAdvantageOnLaneOpponent'] for m in laner_matches) / num_laner_games,
        'avg_solo_kills': sum(m['soloKills'] for m in laner_matches) / num_laner_games,
        'avg_turret_plates': sum(m['turretPlatesTaken'] for m in laner_matches) / num_laner_games,
        
        # Overall farming efficiency
        'avg_total_cs': sum(m['totalMinionsKilled'] for m in laner_matches) / num_laner_games,
        'avg_cs_per_minute': sum(m['totalMinionsKilled'] / max(m['gameDuration'] / 60, 1) for m in laner_matches) / num_laner_games,
        
        # Combat effectiveness
        'avg_kill_participation': sum(m['killParticipation'] for m in laner_matches) / num_laner_games * 100,
        'avg_damage_per_minute': sum(m['damagePerMinute'] for m in laner_matches) / num_laner_games,
        'avg_damage_to_champions': sum(m['totalDamageDealtToChampions'] for m in laner_matches) / num_laner_games,
        
        # Tanking/Durability
        'avg_damage_taken': sum(m['totalDamageTaken'] for m in laner_matches) / num_laner_games,
        'avg_damage_taken_percent': sum(m['damageTakenOnTeamPercentage'] for m in laner_matches) / num_laner_games * 100,
        
        # Position breakdown
        'position_distribution': {
            'TOP': sum(1 for m in laner_matches if m['position'] == 'TOP'),
            'MIDDLE': sum(1 for m in laner_matches if m['position'] == 'MID'),
            'BOTTOM': sum(1 for m in laner_matches if m['position'] == 'BOTTOM'),
        },
    }

def analyze_jungle_stats(detailed_matches: list) -> dict:
    #Aggregate jungle-specific statistics across all jungle games.
    
    jungle_matches = [m for m in detailed_matches if m.get('isJungler', False)]
    
    if not jungle_matches:
        return {
            'total_jungle_games': 0,
            'has_jungle_data': False,
        }
    
    num_jungle_games = len(jungle_matches)
    
    return {
        'total_jungle_games': num_jungle_games,
        'has_jungle_data': True,
        
        # Early jungle performance
        'avg_jungle_cs_before_10': sum(m['jungleCsBefore10Minutes'] for m in jungle_matches) / num_jungle_games,
        'avg_scuttle_crabs': sum(m['scuttleCrabKills'] for m in jungle_matches) / num_jungle_games,
        
        # Epic monsters (personal participation)
        'avg_dragons_secured': sum(m['dragonKills'] for m in jungle_matches) / num_jungle_games,
        'avg_dragon_participation': sum(m['dragonTakedowns'] for m in jungle_matches) / num_jungle_games,
        'avg_void_grubs': sum(m['voidMonsterKill'] for m in jungle_matches) / num_jungle_games,
        
        # Team epic monsters
        'avg_team_heralds': sum(m['teamRiftHeraldKills'] for m in jungle_matches) / num_jungle_games,
        'avg_team_elder_dragons': sum(m['teamElderDragonKills'] for m in jungle_matches) / num_jungle_games,
        'avg_team_barons': sum(m['teamBaronKills'] for m in jungle_matches) / num_jungle_games,
        
        # Invade/Counter-jungle stats
        'avg_enemy_camps_taken': sum(m['enemyJungleMonsterKills'] for m in jungle_matches) / num_jungle_games,
        'avg_buffs_stolen': sum(m['buffsStolen'] for m in jungle_matches) / num_jungle_games,
        'avg_epic_monster_steals': sum(m['epicMonsterSteals'] for m in jungle_matches) / num_jungle_games,
        'invade_advantage_rate': sum(1 for m in jungle_matches if m['moreEnemyJungleThanOpponent']) / num_jungle_games * 100,
    }

def analyze_support_stats(detailed_matches: list) -> dict:
    support_matches = [m for m in detailed_matches if m.get('isSupport', False)]
    
    if not support_matches:
        return {
            'total_support_games': 0,
            'has_support_data': False,
        }
    
    num_support_games = len(support_matches)
    
    return {
        'total_support_games': num_support_games,
        'has_support_data': True,
        
        # Vision control (support-specific)
        'avg_control_wards': sum(m['controlWardsPlaced'] for m in support_matches) / num_support_games,
        'avg_stealth_wards': sum(m['stealthWardsPlaced'] for m in support_matches) / num_support_games,
        'avg_vision_score_per_min': sum(m['visionScorePerMinute'] for m in support_matches) / num_support_games,
        'avg_vision_advantage': sum(m['visionScoreAdvantageLaneOpponent'] for m in support_matches) / num_support_games,
        
        # General vision stats (from all support games)
        'avg_vision_score': sum(m['visionScore'] for m in support_matches) / num_support_games,
        'avg_wards_placed': sum(m['wardsPlaced'] for m in support_matches) / num_support_games,
        'avg_wards_killed': sum(m['wardsKilled'] for m in support_matches) / num_support_games,
        
        # Ward control
        'avg_wards_killed_before_20': sum(m['wardTakedownsBefore20M'] for m in support_matches) / num_support_games,
        'avg_wards_guarded': sum(m['wardsGuarded'] for m in support_matches) / num_support_games,
        
        # Support item efficiency
        'support_quest_speed': sum(1 for m in support_matches if m['fasterSupportQuestCompletion'] > 0) / num_support_games * 100,
        
        # Utility output
        'avg_heal_and_shielding': sum(m['effectiveHealAndShielding'] for m in support_matches) / num_support_games,
    }

def analyze_objective_control_by_outcome(raw_matches: list) -> dict:
    #objective control in wins vs losses
    wins = [m for m in raw_matches if m.get('win')]
    losses = [m for m in raw_matches if not m.get('win')]
    
    def get_objective_stats(matches):
        if not matches:
            return {}
        
        return {
            'avg_dragon_participation': sum(m.get('challenges', {}).get('dragonTakedowns', 0) for m in matches) / len(matches),
            'avg_baron_participation': sum(m.get('challenges', {}).get('baronTakedowns', 0) for m in matches) / len(matches),
            'avg_heralds': sum(m.get('challenges', {}).get('riftHeraldTakedowns', 0) for m in matches) / len(matches),
            'avg_turret_plates': sum(m.get('challenges', {}).get('turretPlatesTaken', 0) for m in matches) / len(matches),
            'avg_turret_kills': sum(m.get('turretKills', 0) for m in matches) / len(matches),
            'avg_turret_takedowns': sum(m.get('turretTakedowns', 0) for m in matches) / len(matches),
            'avg_damage_to_objectives': sum(m.get('damageDealtToObjectives', 0) for m in matches) / len(matches),
            'first_turret_rate': sum(1 for m in matches if m.get('firstTowerKill') or m.get('firstTowerAssist')) / len(matches) * 100,
        }
    
    win_stats = get_objective_stats(wins)
    loss_stats = get_objective_stats(losses)
    
    # Calculate differences
    differences = {}
    if win_stats and loss_stats:
        for key in win_stats:
            differences[f"{key}_difference"] = win_stats[key] - loss_stats[key]
    
    return {
        'wins': win_stats,
        'losses': loss_stats,
        'differences': differences,
        'win_games_count': len(wins),
        'loss_games_count': len(losses),
    }

def format_context_for_prompt(context: dict) -> str:
    #Converts the rich context dict into a clean, readable format for AI prompts
    return json.dumps(context, indent=2)