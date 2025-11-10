import pandas as pd
import numpy as np

def calculate_advanced_metrics(df):
    metrics = {}
    
    # Basic stats
    metrics['total_games'] = len(df)
    metrics['wins'] = df['Win'].sum()
    metrics['losses'] = metrics['total_games'] - metrics['wins']
    metrics['win_rate'] = df['Win'].mean() * 100
    
    # KDA metrics
    metrics['avg_kills'] = df['Kills'].mean()
    metrics['avg_deaths'] = df['Deaths'].mean()
    metrics['avg_assists'] = df['Assists'].mean()
    metrics['avg_kda'] = df['KDA'].mean()
    metrics['kda_consistency'] = df['KDA'].std()
    
    # Performance trends
    recent_5 = df.tail(5)
    metrics['recent_5_wr'] = recent_5['Win'].mean() * 100
    metrics['recent_5_kda'] = recent_5['KDA'].mean()
    
    # Win/Loss performance gap
    win_games = df[df['Win'] == 1]
    loss_games = df[df['Win'] == 0]
    
    if len(win_games) > 0:
        metrics['win_avg_kda'] = win_games['KDA'].mean()
        metrics['win_avg_kills'] = win_games['Kills'].mean()
        metrics['win_avg_deaths'] = win_games['Deaths'].mean()
    
    if len(loss_games) > 0:
        metrics['loss_avg_kda'] = loss_games['KDA'].mean()
        metrics['loss_avg_kills'] = loss_games['Kills'].mean()
        metrics['loss_avg_deaths'] = loss_games['Deaths'].mean()
    
    # Death patterns
    metrics['deaths_per_loss'] = loss_games['Deaths'].mean() if len(loss_games) > 0 else 0
    metrics['deaths_per_win'] = win_games['Deaths'].mean() if len(win_games) > 0 else 0
    
    # Aggression score
    metrics['aggression_score'] = (df['Kills'] + df['Assists']).mean()
    
    # Safety score
    metrics['safety_score'] = max(0, 10 - df['Deaths'].mean())
    
    # Champion diversity
    metrics['unique_champions'] = df['Champion'].nunique()
    metrics['champion_diversity_ratio'] = metrics['unique_champions'] / metrics['total_games']
    
    # IMPROVED: Performance volatility using normalized coefficient of variation
    # Use a sigmoid-like transformation to map CV to 0-10 scale
    # CV typically ranges from 0.3 (very consistent) to 2.0+ (very volatile)
    coefficient_of_variation = df['KDA'].std() / (df['KDA'].mean() + 0.01)
    # Map CV: 0.3->1, 0.6->3, 1.0->6, 1.5->8, 2.0+->10
    metrics['performance_volatility'] = min(10, max(0, (coefficient_of_variation - 0.2) * 6))
    
    # IMPROVED: Consistency score (inverse of volatility, better scaled)
    # High consistency = low volatility
    metrics['consistency_score'] = max(0, 10 - metrics['performance_volatility'])
    
    # Carry potential
    metrics['carry_games'] = ((df['Kills'] + df['Assists']) >= 10).sum()
    metrics['carry_rate'] = (metrics['carry_games'] / metrics['total_games']) * 100
    
    # High death games
    metrics['high_death_games'] = (df['Deaths'] >= 8).sum()
    metrics['feed_rate'] = (metrics['high_death_games'] / metrics['total_games']) * 100
    
    return metrics

def get_champion_insights(df):
    champ_stats = df.groupby('Champion').agg({
        'Kills': ['mean', 'sum'],
        'Deaths': ['mean', 'sum'],
        'Assists': ['mean', 'sum'],
        'KDA': 'mean',
        'Win': ['mean', 'count', 'sum']
    }).reset_index()
    
    champ_stats.columns = ['Champion', 'Avg_Kills', 'Total_Kills', 
                            'Avg_Deaths', 'Total_Deaths', 
                            'Avg_Assists', 'Total_Assists',
                            'Avg_KDA', 'Win_Rate', 'Games', 'Wins']
    
    champ_stats['Win_Rate'] = champ_stats['Win_Rate'] * 100
    champ_stats = champ_stats.sort_values('Avg_KDA', ascending=False)
    
    def get_tier(row):
        games = row['Games']
        kda = row['Avg_KDA']
        wr = row['Win_Rate']
        
        # Penalize small sample sizes
        # Champions with <3 games can't be A-tier, <5 games get downgraded
        if kda >= 4 and wr >= 60 and games >= 5:
            return 'A-Tier'
        elif kda >= 4 and wr >= 60 and games >= 3:
            return 'B-Tier'  # Downgrade potential A-tier with small sample
        elif kda >= 3 and wr >= 50 and games >= 3:
            return 'B-Tier'
        elif kda >= 3 and wr >= 50 and games < 3:
            return 'C-Tier'  # Downgrade B-tier with very small sample
        elif kda >= 2:
            return 'C-Tier'
        else:
            return 'D-Tier'
        
    champ_stats['Tier'] = champ_stats.apply(get_tier, axis=1)

    def calculate_performance_score(row):
        games = row['Games']
        kda = row['Avg_KDA']
        wr = row['Win_Rate']
        
        # Diminishing returns on games (log scale) to prevent one-trick domination
        # But still reward consistency
        games_weight = min(np.log1p(games) * 2, 10)  # Caps at ~10 for 100+ games
        
        # KDA component (normalized to 0-10)
        kda_score = min(kda * 2, 10)
        
        # Win rate component (normalized to 0-10)
        wr_score = wr / 10
        
        # Weighted average: 40% games, 35% KDA, 25% WR
        performance_score = (games_weight * 0.4) + (kda_score * 0.35) + (wr_score * 0.25)
        return performance_score
    
    champ_stats['Performance_Score'] = champ_stats.apply(calculate_performance_score, axis=1)
    
    # Sort by performance score (best pick consideration), but keep original KDA sort for display
    champ_stats = champ_stats.sort_values('Performance_Score', ascending=False)
    
    return champ_stats

def get_improvement_suggestions(metrics, df):
    suggestions = []
    
    if metrics['avg_deaths'] > 7:
        suggestions.append("🛡️ **Critical: Reduce deaths** - You're dying too frequently. Focus on:\n"
                          "   - Better ward coverage\n"
                          "   - Safer positioning in fights\n"
                          "   - Recognizing when fights are lost")
    elif metrics['avg_deaths'] > 5:
        suggestions.append("⚠️ **Work on survival** - Your death count is above average. Watch for:\n"
                          "   - Overextending when ahead\n"
                          "   - Missing enemy rotations\n"
                          "   - Greedy plays")
    
    if metrics['aggression_score'] < 8:
        suggestions.append("📈 **Increase impact** - Low kill participation detected. Try:\n"
                          "   - Roaming more frequently\n"
                          "   - Joining team fights earlier\n"
                          "   - Better communication with jungle")
    
    if metrics['win_rate'] < 45:
        suggestions.append("🎯 **Focus on fundamentals**:\n"
                          "   - Review your champion pool\n"
                          "   - Practice CSing/farming\n"
                          "   - Watch replays of losses")
    
    if metrics['performance_volatility'] > 5:
        suggestions.append("📊 **Improve consistency** - Your performance varies widely:\n"
                          "   - Stick to 2-3 comfort picks\n"
                          "   - Avoid tilt queuing\n"
                          "   - Develop a pre-game mental routine")
    
    if metrics['champion_diversity_ratio'] > 0.6:
        suggestions.append("🎮 **Narrow champion pool** - You're playing too many champions:\n"
                          "   - Focus on 3-5 champions max\n"
                          "   - Master mechanics before expanding\n"
                          "   - Higher mastery = better win rates")
    
    if 'loss_avg_deaths' in metrics and 'win_avg_deaths' in metrics:
        death_gap = metrics['loss_avg_deaths'] - metrics['win_avg_deaths']
        if death_gap > 4:
            suggestions.append("🔄 **Mental reset needed** - You die significantly more in losses:\n"
                              "   - Avoid revenge plays\n"
                              "   - Accept when behind\n"
                              "   - Play for late game scaling")
    
    if metrics['win_rate'] >= 55:
        suggestions.append("✨ **Keep it up!** - You're performing well. Focus on:\n"
                          "   - Maintaining current form\n"
                          "   - Learning win conditions\n"
                          "   - Shot-calling for team")
    
    if metrics['avg_kda'] >= 4:
        suggestions.append("🌟 **Excellent KDA** - Your risk/reward balance is strong!")
    
    if len(suggestions) == 0:
        suggestions.append("👍 **Solid fundamentals** - Keep refining your skills and climb!")
    
    return suggestions

def calculate_early_late_game_stats(df, raw_matches):
    #Calculate laner-specific early game performance (wins vs losses)
    
    # Filter for laner matches only
    laner_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') in ['TOP', 'MIDDLE', 'BOTTOM']]
    
    if not laner_matches:
        return {
            'has_laner_data': False,
            'wins': {},
            'losses': {},
            'cs_at_10_diff': 0,
            'gold_diff': 0,
            'early_kills_diff': 0,
        }
    
    wins = [m for m in laner_matches if m.get('win')]
    losses = [m for m in laner_matches if not m.get('win')]
    
    def get_early_late_stats(matches):
        if not matches:
            return {}
        
        # Early game stats
        cs_at_10 = [m.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) for m in matches]
        gold_per_min = [m.get('challenges', {}).get('goldPerMinute', 0) for m in matches]
        early_kills = [m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in matches]
        
        # Late game stats (approximate from total stats)
        avg_game_length = sum(m.get('challenges', {}).get('gameLength', 1200) for m in matches) / len(matches)
        total_damage = sum(m.get('totalDamageDealtToChampions', 0) for m in matches) / len(matches)
        
        return {
            'avg_cs_at_10': sum(cs_at_10) / len(cs_at_10) if cs_at_10 else 0,
            'avg_gold_per_min': sum(gold_per_min) / len(gold_per_min) if gold_per_min else 0,
            'avg_early_kills': sum(early_kills) / len(early_kills) if early_kills else 0,
            'avg_game_length_min': avg_game_length / 60,
            'avg_total_damage': total_damage,
            'early_death_rate': sum(1 for m in matches if m.get('deaths', 0) > 0 and m.get('challenges', {}).get('gameLength', 1200) < 900) / len(matches) * 100,
            'games_count': len(matches),
        }
    
    win_stats = get_early_late_stats(wins)
    loss_stats = get_early_late_stats(losses)
    
    return {
        'has_laner_data': True,
        'wins': win_stats,
        'losses': loss_stats,
        'cs_at_10_diff': win_stats.get('avg_cs_at_10', 0) - loss_stats.get('avg_cs_at_10', 0),
        'gold_diff': win_stats.get('avg_gold_per_min', 0) - loss_stats.get('avg_gold_per_min', 0),
        'early_kills_diff': win_stats.get('avg_early_kills', 0) - loss_stats.get('avg_early_kills', 0),
    }

def calculate_laner_additional_metrics(raw_matches):
   #laner-specific metrics
    
    lane_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') in ['TOP', 'MIDDLE', 'BOTTOM']]
    if not lane_matches:
        return {
            'has_lane_data': False,
            'avg_cs_per_min': 0,
            'combat_efficiency_score': 0,
        }
    
    num_games = len(lane_matches)

    total_cs_per_min = sum(((m.get('totalMinionsKilled', 0) + m.get('neutralMinionsKilled', 0)) / (m.get('challenges', {}).get('gameLength', 0)/60)) for m in lane_matches) if lane_matches else 0
    avg_cs_per_min = total_cs_per_min/num_games
    
    avg_damage_share = sum(m.get('challenges', {}).get('teamDamagePercentage', 0)*100 for m in lane_matches) / num_games
    avg_tank_share = sum(m.get('challenges',{}).get('damageTakenOnTeamPercentage', 0)*100 for m in lane_matches) / num_games
    combat_share = avg_damage_share + avg_tank_share
    
    avg_gold_gained = sum(m.get('goldEarned', 0) for m in lane_matches) / num_games
    gold_in_thousands = avg_gold_gained / 1000


    if gold_in_thousands > 0:
        combat_per_thousand = combat_share / gold_in_thousands
    else:
        combat_per_thousand = 0
    
    #scale to final score out of 10
    #benchmark of 5.0
    combat_efficiency_score = combat_per_thousand * 2

    return {
        'has_lane_data': True,
        'lane_games': num_games,
        'avg_cs_per_min': avg_cs_per_min,
        'combat_efficiency_score': combat_efficiency_score,

        'avg_damage_share': avg_damage_share,
        'avg_tank_share': avg_tank_share,
        'avg_gold_gained': avg_gold_gained,
    }


def calculate_jungle_advanced_metrics(raw_matches):
    #jungle-specific metrics
    
    jungle_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'JUNGLE']
    
    if not jungle_matches:
        return {
            'has_jungle_data': False,
            'jungle_objective_control': 0,
            'jungle_pressure_score': 0,
            'counter_jungle_score': 0,
        }
    
    num_games = len(jungle_matches)
    
    # Jungle Objective Control Score (0-10)
    # Based on: dragons, barons, heralds, void grubs
    avg_dragons = sum(m.get('challenges', {}).get('dragonTakedowns', 0) for m in jungle_matches) / num_games
    avg_barons = sum(m.get('challenges', {}).get('baronTakedowns', 0) for m in jungle_matches) / num_games
    avg_heralds = sum(m.get('challenges', {}).get('teamRiftHeraldKills', 0) for m in jungle_matches) / num_games
    avg_grubs = sum(m.get('challenges', {}).get('voidMonsterKill', 0) for m in jungle_matches) / num_games
    
    # Scoring: 2 dragons = 4pts, 1 baron = 3pts, 1 herald = 2pts, 3 grubs = 1pt (normalized to 10)
    objective_score = min(10, (avg_dragons * 2) + (avg_barons * 3) + (avg_heralds * 2) + (avg_grubs / 3))
    
    # Jungle Pressure Score (0-10)
    # Based on: scuttle control, early kills/assists, jungle CS
    avg_scuttles = sum(m.get('challenges', {}).get('scuttleCrabKills', 0) for m in jungle_matches) / num_games
    avg_early_takedowns = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in jungle_matches) / num_games
    avg_jungle_cs_10 = sum(m.get('challenges', {}).get('jungleCsBefore10Minutes', 0) for m in jungle_matches) / num_games
    
    # Scoring: 1.5 scuttles = 3pts, 2 early takedowns = 4pts, 40 cs@10 = 3pts
    pressure_score = min(10, (avg_scuttles / 1.5 * 3) + (avg_early_takedowns / 2 * 4) + (avg_jungle_cs_10 / 40 * 3))
    
    # Counter-Jungle Score (0-10)
    # Based on: enemy camps taken, buffs stolen, epic steals, invade advantage
    avg_enemy_camps = sum(m.get('challenges', {}).get('enemyJungleMonsterKills', 0) for m in jungle_matches) / num_games
    avg_buffs_stolen = sum(m.get('challenges', {}).get('buffsStolen', 0) for m in jungle_matches) / num_games
    avg_epic_steals = sum(m.get('challenges', {}).get('epicMonsterSteals', 0) for m in jungle_matches) / num_games
    invade_rate = sum(1 for m in jungle_matches if m.get('challenges', {}).get('moreEnemyJungleThanOpponent', False)) / num_games * 100
    
    # Scoring: 3 camps = 3pts, 0.5 buff = 2pts, 0.3 steal = 3pts, 50% invade = 2pts
    counter_score = min(10, (avg_enemy_camps / 3 * 3) + (avg_buffs_stolen / 0.5 * 2) + (avg_epic_steals / 0.3 * 3) + (invade_rate / 50 * 2))
    
    return {
        'has_jungle_data': True,
        'jungle_games': num_games,
        'jungle_objective_control': objective_score,
        'jungle_pressure_score': pressure_score,
        'counter_jungle_score': counter_score,
        
        # Raw stats for reference
        'avg_dragons': avg_dragons,
        'avg_barons': avg_barons,
        'avg_heralds': avg_heralds,
        'avg_scuttles': avg_scuttles,
        'avg_enemy_camps': avg_enemy_camps,
        'avg_epic_steals': avg_epic_steals,
    }

def calculate_support_advanced_metrics(raw_matches):
    #advanced support-specific metrics
    support_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'UTILITY']
    
    if not support_matches:
        return {
            'has_support_data': False,
            'vision_dominance_score': 0,
            'utility_output_score': 0,
            'frontline_score': 0,
        }
    
    num_games = len(support_matches)
    
    # Vision Dominance Score (0-10)
    # Based on: vision score per min, control wards, wards killed, vision advantage
    avg_vision_per_min = sum(m.get('challenges', {}).get('visionScorePerMinute', 0) for m in support_matches) / num_games
    avg_control_wards = sum(m.get('challenges', {}).get('controlWardsPlaced', 0) for m in support_matches) / num_games
    avg_wards_killed = sum(m.get('wardTakedowns', 0) for m in support_matches) / num_games
    avg_vision_advantage = sum(m.get('challenges', {}).get('visionScoreAdvantageLaneOpponent', 0) for m in support_matches) / num_games
    
    # Scoring: 2.0 vspm = 3pts, 8 pinks = 2pts, 15 wards killed = 3pts, +10 advantage = 2pts
    vision_score = min(10, (avg_vision_per_min / 2.0 * 3) + (avg_control_wards / 8 * 2) + (avg_wards_killed / 15 * 3) + (max(0, avg_vision_advantage) / 10 * 2))
    
    # Utility Output Score (0-10)
    # Based on: healing/shielding, assist rate, kill participation
    avg_heal_shield = sum(m.get('challenges', {}).get('effectiveHealAndShielding', 0) for m in support_matches) / num_games
    avg_assists = sum(m.get('assists', 0) for m in support_matches) / num_games
    avg_kp = sum(m.get('challenges', {}).get('killParticipation', 0) for m in support_matches) / num_games * 100
    
    # Scoring: 5000 heal/shield = 4pts, 15 assists = 3pts, 70% kp = 3pts
    utility_score = min(10, (avg_heal_shield / 5000 * 4) + (avg_assists / 15 * 3) + (avg_kp / 70 * 3))
    
    # Frontline/Tanking Score (0-10)
    # Based on: damage taken %, damage taken, wards guarded
    avg_dmg_taken_pct = sum(m.get('challenges', {}).get('damageTakenOnTeamPercentage', 0) for m in support_matches) / num_games * 100
    avg_dmg_taken = sum(m.get('totalDamageTaken', 0) for m in support_matches) / num_games
    avg_wards_guarded = sum(m.get('challenges', {}).get('wardsGuarded', 0) for m in support_matches) / num_games
    
    # Scoring: 25% team dmg = 4pts, 20k dmg = 3pts, 5 guarded = 3pts
    frontline_score = min(10, (avg_dmg_taken_pct / 25 * 4) + (avg_dmg_taken / 20000 * 3) + (avg_wards_guarded / 5 * 3))
    
    return {
        'has_support_data': True,
        'support_games': num_games,
        'vision_dominance_score': vision_score,
        'utility_output_score': utility_score,
        'frontline_score': frontline_score,
        
        # Raw stats for reference
        'avg_vision_per_min': avg_vision_per_min,
        'avg_control_wards': avg_control_wards,
        'avg_wards_killed': avg_wards_killed,
        'avg_heal_shield': avg_heal_shield,
        'avg_assists': avg_assists,
        'avg_dmg_taken_pct': avg_dmg_taken_pct,
    }

def calculate_support_early_game_stats(raw_matches):
    #Calculate support-specific early game performance (wins vs losses)

    support_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'UTILITY']
    
    if not support_matches:
        return {
            'has_support_data': False,
            'wins': {},
            'losses': {},
        }
    
    wins = [m for m in support_matches if m.get('win')]
    losses = [m for m in support_matches if not m.get('win')]
    
    def get_support_early_stats(matches):
        if not matches:
            return {}
        
        # Wards placed early (approximate from total / game length * 10 min)
        avg_wards_per_game = sum(m.get('wardsPlaced', 0) for m in matches) / len(matches)
        avg_game_length_min = sum(m.get('challenges', {}).get('gameLength', 1800) / 60 for m in matches) / len(matches)
        wards_at_10_estimate = (avg_wards_per_game / avg_game_length_min) * 10 if avg_game_length_min > 0 else 0
        
        # Support quest completion rate
        faster_quest = sum(1 for m in matches if m.get('challenges', {}).get('fasterSupportQuestCompletion', 0) > 0)
        quest_completion_rate = (faster_quest / len(matches)) * 100
        
        # Early assists/kill participation (first 10-15 min)
        avg_early_assists = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in matches) / len(matches)
        
        return {
            'avg_wards_at_10': wards_at_10_estimate,
            'quest_completion_rate': quest_completion_rate,
            'avg_early_assists': avg_early_assists,
            'games_count': len(matches),
        }
    
    win_stats = get_support_early_stats(wins)
    loss_stats = get_support_early_stats(losses)
    
    # Calculate differences
    wards_diff = win_stats.get('avg_wards_at_10', 0) - loss_stats.get('avg_wards_at_10', 0)
    quest_diff = win_stats.get('quest_completion_rate', 0) - loss_stats.get('quest_completion_rate', 0)
    assists_diff = win_stats.get('avg_early_assists', 0) - loss_stats.get('avg_early_assists', 0)
    
    return {
        'has_support_data': True,
        'wins': win_stats,
        'losses': loss_stats,
        'wards_at_10_diff': wards_diff,
        'quest_diff': quest_diff,
        'early_assists_diff': assists_diff,
    }

def calculate_jungle_early_game_stats(raw_matches):
    #Calculate jungle-specific early game performance (wins vs losses)
    jungle_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'JUNGLE']
    
    if not jungle_matches:
        return {
            'has_jungle_data': False,
            'wins': {},
            'losses': {},
        }
    
    wins = [m for m in jungle_matches if m.get('win')]
    losses = [m for m in jungle_matches if not m.get('win')]
    
    def get_jungle_early_stats(matches):
        if not matches:
            return {}
        
        # Jungle CS at 10 minutes
        avg_jungle_cs_10 = sum(m.get('challenges', {}).get('jungleCsBefore10Minutes', 0) for m in matches) / len(matches)
        
        # Gold per minute (first 10 min approximate)
        avg_gold_per_min = sum(m.get('challenges', {}).get('goldPerMinute', 0) for m in matches) / len(matches)
        
        # Early kills + assists (takedowns)
        avg_early_takedowns = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in matches) / len(matches)
        
        return {
            'avg_jungle_cs_10': avg_jungle_cs_10,
            'avg_gold_per_min': avg_gold_per_min,
            'avg_early_takedowns': avg_early_takedowns,
            'games_count': len(matches),
        }
    
    win_stats = get_jungle_early_stats(wins)
    loss_stats = get_jungle_early_stats(losses)
    
    # Calculate differences
    cs_diff = win_stats.get('avg_jungle_cs_10', 0) - loss_stats.get('avg_jungle_cs_10', 0)
    gold_diff = win_stats.get('avg_gold_per_min', 0) - loss_stats.get('avg_gold_per_min', 0)
    takedown_diff = win_stats.get('avg_early_takedowns', 0) - loss_stats.get('avg_early_takedowns', 0)
    
    return {
        'has_jungle_data': True,
        'wins': win_stats,
        'losses': loss_stats,
        'jungle_cs_10_diff': cs_diff,
        'gold_diff': gold_diff,
        'early_takedown_diff': takedown_diff,
    }

def calculate_support_early_dominance(raw_matches):
    #Calculate early game dominance score based on: support quest completion, vision advantage, and early assists.
    
    support_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'UTILITY']
    
    if not support_matches:
        return 0.0
    
    wins = [m for m in support_matches if m.get('win')]
    
    if not wins:
        return 0.0
    
    # Support Quest Completion Time (faster = better)
    faster_quest_count = sum(1 for m in wins if m.get('challenges', {}).get('fasterSupportQuestCompletion', 0) > 0)
    quest_score = (faster_quest_count / len(wins) * 100) / 10  # 100% completion = 10 pts
    
    # Vision Advantage over lane opponent
    avg_vision_advantage = sum(m.get('challenges', {}).get('visionScoreAdvantageLaneOpponent', 0) for m in wins) / len(wins)
    vision_score = min(10, max(0, (avg_vision_advantage + 5) / 1.5))  # +10 advantage = 10pts, -5 = 0pts
    
    # Early assists/kill participation
    avg_early_assists = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in wins) / len(wins)
    assist_score = min(10, avg_early_assists * 2)  # 5 early assists = 10pts
    
    # Weighted average: 40% quest, 30% vision, 30% assists
    dominance_score = (quest_score * 0.4) + (vision_score * 0.3) + (assist_score * 0.3)
    
    return dominance_score

def calculate_jungle_early_dominance(raw_matches):
    #Calculate early game jungle dominance score based on: jungle CS advantage, gold differential, and early kills+assists.
    
    jungle_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') == 'JUNGLE']
    
    if not jungle_matches:
        return 0.0
    
    wins = [m for m in jungle_matches if m.get('win')]
    
    if not wins:
        return 0.0
    
    # Jungle CS at 10 (higher = better clear speed)
    avg_jungle_cs_10 = sum(m.get('challenges', {}).get('jungleCsBefore10Minutes', 0) for m in wins) / len(wins)
    cs_score = (avg_jungle_cs_10 / 40) * 10  # 40 CS@10 = max score
    
    # Gold per minute advantage (compare to baseline 350 gpm)
    avg_gpm = sum(m.get('challenges', {}).get('goldPerMinute', 0) for m in wins) / len(wins)
    gold_advantage = (avg_gpm - 350) * 10  # Difference from baseline
    gold_score = min(10, max(0, (gold_advantage + 250) / 50))  # +250g = 5pts, +500g = 10pts
    
    # Early kills + assists (takedowns)
    avg_early_takedowns = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in wins) / len(wins)
    takedown_score = min(10, avg_early_takedowns * 2)  # 5 early takedowns = 10pts
    
    # Weighted average: 30% CS, 30% gold, 40% takedowns (ganks matter more for junglers)
    dominance_score = (cs_score * 0.3) + (gold_score * 0.3) + (takedown_score * 0.4)
    
    return dominance_score

def _calculate_role_specific_tags(primary_role: str, secondary_role: str, raw_matches: list, 
                                   jungle_advanced: dict = None, support_advanced: dict = None,
                                   metrics: dict = None):
    #Helper function to calculate role-specific tags.
    
    tags = {'strengths': [], 'weaknesses': []}
    
    # === LANER TAGS ===
    if primary_role in ['TOP', 'MIDDLE', 'BOTTOM'] or secondary_role in ['TOP', 'MIDDLE', 'BOTTOM']:
        laner_matches = [m for m in raw_matches if m.get('teamPosition', 'UNKNOWN') in ['TOP', 'MIDDLE', 'BOTTOM']]
        
        if laner_matches:
            # Calculate laner stats
            avg_cs_10 = sum(m.get('challenges', {}).get('laneMinionsFirst10Minutes', 0) for m in laner_matches) / len(laner_matches)
            avg_plates = sum(m.get('challenges', {}).get('turretPlatesTaken', 0) for m in laner_matches) / len(laner_matches)
            avg_early_kills = sum(m.get('challenges', {}).get('takedownsFirstXMinutes', 0) for m in laner_matches) / len(laner_matches)
            
            # Lane Kingdom (strong laning)
            if avg_cs_10 >= 65 and (avg_plates >= 1.5 or avg_early_kills >= 1.5):
                score = ((avg_cs_10 / 80) * 40) + ((avg_plates / 3) * 30) + ((avg_early_kills / 3) * 30)
                tags['strengths'].append({
                    'label': 'Lane Kingdom',
                    'score': score,
                    'tooltip': f"{avg_cs_10:.0f} CS@10, {avg_plates:.1f} plates, {avg_early_kills:.1f} early kills"
                })
            
            # Weak Laning
            elif avg_cs_10 < 50:
                score = 100 - ((avg_cs_10 / 50) * 100)
                tags['weaknesses'].append({
                    'label': 'Weak Laning',
                    'score': score,
                    'tooltip': f"{avg_cs_10:.0f} CS@10 - below 50 benchmark"
                })
    
    # === JUNGLE TAGS ===
    if (primary_role == 'JUNGLE' or secondary_role == 'JUNGLE') and jungle_advanced and jungle_advanced.get('has_jungle_data'):
        
        # Dragonslayer (high objective control)
        obj_score = jungle_advanced.get('jungle_objective_control', 0)
        if obj_score >= 7:
            tags['strengths'].append({
                'label': 'Dragonslayer',
                'score': obj_score * 10,
                'tooltip': f"{jungle_advanced.get('avg_dragons', 0):.1f} drags, {jungle_advanced.get('avg_barons', 0):.1f} barons"
            })
        
        # Counter Jungle King
        counter_score = jungle_advanced.get('counter_jungle_score', 0)
        if counter_score >= 6:
            tags['strengths'].append({
                'label': 'Counter Jungle King',
                'score': counter_score * 10,
                'tooltip': f"{jungle_advanced.get('avg_enemy_camps', 0):.1f} enemy camps, {jungle_advanced.get('avg_epic_steals', 0):.1f} steals"
            })
        
        # Objective Neglect
        if obj_score < 4:
            score = 100 - (obj_score * 20)
            tags['weaknesses'].append({
                'label': 'Objective Neglect',
                'score': score,
                'tooltip': f"Low objective control ({obj_score:.1f}/10)"
            })
        
        # Passive Jungler
        pressure_score = jungle_advanced.get('jungle_pressure_score', 0)
        if pressure_score < 4:
            score = 100 - (pressure_score * 20)
            tags['weaknesses'].append({
                'label': 'Passive Jungler',
                'score': score,
                'tooltip': f"Low early pressure ({pressure_score:.1f}/10)"
            })
    
    # === SUPPORT TAGS ===
    if (primary_role == 'UTILITY' or secondary_role == 'UTILITY') and support_advanced and support_advanced.get('has_support_data'):
        
        # The All Seeing (high vision)
        vision_score = support_advanced.get('vision_dominance_score', 0)
        if vision_score >= 7:
            tags['strengths'].append({
                'label': 'The All Seeing',
                'score': vision_score * 10,
                'tooltip': f"{support_advanced.get('avg_vision_per_min', 0):.1f} vision/min"
            })
        
        # Guardian Angel (high utility)
        utility_score = support_advanced.get('utility_output_score', 0)
        if utility_score >= 7:
            tags['strengths'].append({
                'label': 'Guardian Angel',
                'score': utility_score * 10,
                'tooltip': f"{support_advanced.get('avg_heal_shield', 0):,.0f} healing/shielding"
            })
        
        # Nearsighted (low vision)
        if vision_score < 4:
            score = 100 - (vision_score * 20)
            tags['weaknesses'].append({
                'label': 'Nearsighted',
                'score': score,
                'tooltip': f"Low vision control ({vision_score:.1f}/10)"
            })
        
        # Low Impact
        if utility_score < 4:
            score = 100 - (utility_score * 20)
            tags['weaknesses'].append({
                'label': 'Low Impact',
                'score': score,
                'tooltip': f"Low utility output ({utility_score:.1f}/10)"
            })
    
    return tags

def calculate_playstyle_tags(metrics: dict, raw_matches: list, role_info: dict, jungle_advanced: dict = None, support_advanced: dict = None):
    
    #Calculate playstyle tags (strengths and weaknesses) based on player metrics.
    #Returns lists of tags with their scores for dynamic selection.
    
    if metrics['total_games'] < 10:
        return {'strengths': [], 'weaknesses': [], 'neutral': []}
    
    tags = {
        'strengths': [],
        'weaknesses': [],
        'neutral': []
    }
    
    primary_role = role_info.get('primary_role', 'UNKNOWN')
    secondary_role = role_info.get('secondary_role', 'NONE')
    
    # Calculate scores for each potential tag (0-100 scale)
    # Higher score = more applicable
    
    # === GENERIC STRENGTHS ===
    
    # Consistent Performer (low volatility)
    if metrics.get('performance_volatility', 10) <= 3:
        score = 100 - (metrics['performance_volatility'] * 10)
        tags['strengths'].append({
            'label': 'Consistent Performer',
            'score': score,
            'tooltip': f"Low performance variance ({metrics['performance_volatility']:.1f}/10)"
        })
    
    # Team Player (high assists and KP)
    avg_assists = metrics.get('avg_assists', 0)
    if avg_assists >= 8:
        # Get kill participation from raw matches
        avg_kp = sum(m.get('challenges', {}).get('killParticipation', 0) for m in raw_matches) / len(raw_matches) * 100 if raw_matches else 0
        if avg_kp >= 60:
            score = min(100, (avg_assists / 15 * 50) + (avg_kp / 80 * 50))
            tags['strengths'].append({
                'label': 'Team Player',
                'score': score,
                'tooltip': f"{avg_assists:.1f} avg assists, {avg_kp:.0f}% kill participation"
            })
    
    # Safe Player (low deaths)
    if metrics.get('safety_score', 0) >= 7:
        score = metrics['safety_score'] * 10
        tags['strengths'].append({
            'label': 'Safe Player',
            'score': score,
            'tooltip': f"{metrics['avg_deaths']:.1f} avg deaths - excellent survival"
        })
    
    # Damage Dealer (high DPM)
    avg_dpm = sum(m.get('challenges', {}).get('damagePerMinute', 0) for m in raw_matches) / len(raw_matches) if raw_matches else 0
    if avg_dpm >= 500:
        score = min(100, (avg_dpm / 800) * 100)
        tags['strengths'].append({
            'label': 'Damage Dealer',
            'score': score,
            'tooltip': f"{avg_dpm:.0f} damage per minute"
        })
    
    # One Man Army (high damage share or tank)
    avg_dmg_share = sum(m.get('challenges', {}).get('teamDamagePercentage', 0) for m in raw_matches) / len(raw_matches) * 100 if raw_matches else 0
    avg_tank_share = sum(m.get('challenges', {}).get('damageTakenOnTeamPercentage', 0) for m in raw_matches) / len(raw_matches) * 100 if raw_matches else 0
    
    if avg_dmg_share >= 25 or avg_tank_share >= 25:
        score = max(avg_dmg_share, avg_tank_share) * 3
        label = "One Man Army" if avg_dmg_share >= avg_tank_share else "Team's Shield"
        tags['strengths'].append({
            'label': label,
            'score': score,
            'tooltip': f"{max(avg_dmg_share, avg_tank_share):.0f}% of team's burden"
        })
    
    # === GENERIC WEAKNESSES ===
    
    # Coin Flip (high volatility)
    if metrics.get('performance_volatility', 0) >= 7:
        score = metrics['performance_volatility'] * 10
        tags['weaknesses'].append({
            'label': 'Coin Flip',
            'score': score,
            'tooltip': f"High performance variance ({metrics['performance_volatility']:.1f}/10)"
        })
    
    # Weak Vision (low vision score)
    avg_vision = sum(m.get('visionScore', 0) for m in raw_matches) / len(raw_matches) if raw_matches else 0
    if avg_vision < 20 and primary_role != 'UTILITY':  # Don't penalize non-supports as harshly
        score = 100 - (avg_vision / 20 * 100)
        tags['weaknesses'].append({
            'label': 'Weak Vision',
            'score': score,
            'tooltip': f"{avg_vision:.1f} avg vision score"
        })
    
    # Spectator (low KP)
    avg_kp = sum(m.get('challenges', {}).get('killParticipation', 0) for m in raw_matches * 100)/ len(raw_matches)  if raw_matches else 0
    if avg_kp < 30:
        score = 100 - (avg_kp / 30 * 100)
        tags['weaknesses'].append({
            'label': 'Spectator',
            'score': score,
            'tooltip': f"{avg_kp:.0f}% kill participation"
        })
    
    # Careless (high death rate)
    if metrics.get('avg_deaths', 0) >= 7:
        score = min(100, (metrics['avg_deaths'] / 10) * 100)
        tags['weaknesses'].append({
            'label': 'Careless',
            'score': score,
            'tooltip': f"{metrics['avg_deaths']:.1f} avg deaths per game"
        })
    
    # === NEUTRAL TAG ===
    
    # Glass Cannon (high DPM but also high deaths)
    if avg_dpm >= 500 and metrics.get('avg_deaths', 0) >= 6:
        score = ((avg_dpm / 800) * 50) + ((metrics['avg_deaths'] / 10) * 50)
        tags['neutral'].append({
            'label': 'Glass Cannon',
            'score': score,
            'tooltip': f"{avg_dpm:.0f} DPM but {metrics['avg_deaths']:.1f} deaths"
        })
    
    # === ADD ROLE-SPECIFIC TAGS ===
    role_tags = _calculate_role_specific_tags(
        primary_role, 
        secondary_role, 
        raw_matches, 
        jungle_advanced, 
        support_advanced,
        metrics
    )
    
    # Merge role-specific tags
    tags['strengths'].extend(role_tags['strengths'])
    tags['weaknesses'].extend(role_tags['weaknesses'])
    
    # Sort by score (highest first) and limit
    tags['strengths'] = sorted(tags['strengths'], key=lambda x: x['score'], reverse=True)[:8]
    tags['weaknesses'] = sorted(tags['weaknesses'], key=lambda x: x['score'], reverse=True)[:5]
    
    return tags

def calculate_damage_efficiency(raw_matches: list):
    #Measures how efficiently a player converts gold earned into damage
    
    avg_dpg = sum((m.get('totalDamageDealtToChampions', 0)/m.get('goldEarned')) for m in raw_matches)/len(raw_matches) if raw_matches else 0
    for match in raw_matches:
        totalDamageToChampions = match.get('totalDamageDealtToChampions')
        goldEarned = match.get('goldEarned')

        dpg = totalDamageToChampions / goldEarned
        print(dpg)
    return avg_dpg

def calculate_objective_score(raw_matches: list):
    #Measures how actively a player participates in objectives (kills, dragons, barons, heralds and turrets)
    
    if not raw_matches:
        return 0.0
    
    num_games = len(raw_matches)

    avg_kp = sum(m.get('challenges', {}).get('killParticipation', 0) for m in raw_matches)/ num_games if raw_matches else 0
    avg_dragons = sum(m.get('challenges', {}).get('dragonTakedowns', 0) for m in raw_matches) / num_games if raw_matches else 0
    avg_barons = sum(m.get('challenges', {}).get('baronTakedowns', 0) for m in raw_matches) / num_games if raw_matches else 0
    avg_heralds = sum(m.get('challenges', {}).get('teamRiftHeraldKills', 0) for m in raw_matches) / num_games if raw_matches else 0
    avg_turrets = sum(m.get('challenges', {}).get('turretTakedowns', 0) for m in raw_matches) / num_games
    
    #defining weights
    W_KP, W_D, W_B, W_H, W_T = 3.0, 1.5, 2.5, 1.0, 2.0
    max_weighted_score = 12.55

    weighted_performance = (avg_kp * W_KP) + (avg_dragons * W_D) + \
                       (avg_barons * W_B) + (avg_heralds * W_H) + (avg_turrets * W_T)
    objective_score = (weighted_performance / max_weighted_score) * 10
    return objective_score

def calculate_persistence_score(raw_matches: list):
    #Measures how much a player never gives up even in losing games (by calculating objective score, combat share and kill participation in losing games)
    
    if not raw_matches:
        return 0.0
    
    losses = [m for m in raw_matches if not m.get('win')]
    if not losses:
        return 0.0

    num_games = len(losses)

    loss_objective_score  = calculate_objective_score(losses)
    loss_avg_damage_share = sum(m.get('challenges', {}).get('teamDamagePercentage', 0) for m in losses)/ num_games if losses else 0
    loss_avg_tanking_share = sum(m.get('challenges', {}).get('damageTakenOnTeamPercentage', 0) for m in losses)/ num_games if losses else 0
    lost_combat_share = loss_avg_damage_share + loss_avg_tanking_share
    loss_avg_kill_participation = sum(m.get('challenges', {}).get('killParticipation', 0) for m in losses)/ num_games if losses else 0

    #defining weights
    W_LKP = 3.5  # Loss Kill Participation
    W_LOV = 3.0  # Loss Objective Score
    W_LCS = 3.5  # Loss Combat Share Sum (Damage + Tanking)
    max_weighted_score = 18.5

    weighted_performance = (loss_avg_kill_participation * W_LKP) + (loss_objective_score * W_LOV) + \
                       (lost_combat_share * W_LCS)
    objective_score = (weighted_performance / max_weighted_score) * 10
    return objective_score