import streamlit as st
from utils.helpers import get_champion_icon_url
from ui.styles import match_history_styles

def get_summoner_spell_icon(spell_id):
    """Get summoner spell icon URL from spell ID"""
    spell_map = {
        1: "SummonerBoost",
        3: "SummonerExhaust",
        4: "SummonerFlash",
        6: "SummonerHaste",
        7: "SummonerHeal",
        11: "SummonerSmite",
        12: "SummonerTeleport",
        13: "SummonerMana",
        14: "SummonerDot",
        21: "SummonerBarrier",
        30: "SummonerPoroRecall",
        31: "SummonerPoroThrow",
        32: "SummonerSnowball",
        39: "SummonerSnowURFSnowball_Mark"
    }
    
    spell_name = spell_map.get(spell_id, "SummonerFlash")
    return f"https://ddragon.leagueoflegends.com/cdn/15.21.1/img/spell/{spell_name}.png"

def get_item_icon(item_id):
    """Get item icon URL from item ID"""
    if item_id == 0:
        return None
    return f"https://ddragon.leagueoflegends.com/cdn/15.21.1/img/item/{item_id}.png"

def render_match_history():
    
    #st.markdown("### :material/overview:   Match History")
    col1, col2, col3 = st.columns([0.5, 0.75, 0.5])
    with col2:
        st.markdown("## Match History")

    st.markdown("---")

    st.markdown("### :material/overview: ")
    match_history_styles()

    
    if 'raw_matches' not in st.session_state or not st.session_state.raw_matches:
        st.warning("No match data available. Please fetch your matches first!")
        return
    
    matches = st.session_state.raw_matches
    
    # Add expandable state to session
    if 'expanded_matches' not in st.session_state:
        st.session_state.expanded_matches = set()

    if 'matches_to_show' not in st.session_state:
        st.session_state.matches_to_show = 20

    matches_to_display = matches[:st.session_state.matches_to_show]
    for idx, match in enumerate(matches_to_display):
        is_win = match.get('win', False)
        
        champion_name = match.get('championName', 'Unknown')
        kills = match.get('kills', 0)
        deaths = match.get('deaths', 0)
        assists = match.get('assists', 0)
        kda = (kills + assists) / max(deaths, 1)
        
        queue_id = match.get('queueId', 0)
        queue_type = 'Solo/Duo' if queue_id == 420 else 'Flex 5v5' if queue_id == 440 else 'Unknown'
        
        # Get summoner spells
        spell1_id = match.get('summoner1Id', 4)
        spell2_id = match.get('summoner2Id', 4)
        
        # Get items
        items = [
            match.get('item0', 0),
            match.get('item1', 0),
            match.get('item2', 0),
            match.get('item3', 0),
            match.get('item4', 0),
            match.get('item5', 0),
        ]
        trinket = match.get('item6', 0)
        
        # Create expandable container
        is_expanded = idx in st.session_state.expanded_matches
        
        # Define colors
        bg_gradient = "linear-gradient(90deg, rgba(53, 92, 170, 0.3) 0%, rgba(53, 92, 170, 0.15) 50%, rgba(53, 92, 170, 0.05) 100%)" if is_win else "linear-gradient(90deg, rgba(170, 53, 53, 0.3) 0%, rgba(170, 53, 53, 0.15) 50%, rgba(170, 53, 53, 0.05) 100%)"
        border_color = "#5b8fd9" if is_win else "#d95b5b"
        result_text = "Victory" if is_win else "Defeat"
        result_color = "#5b8fd9" if is_win else "#d95b5b"
        queue_badge_color = "#9333ea" if queue_id == 420 else "#0891b2"
        
        # Build items HTML
        items_html = ""
        for item_id in items:
            item_url = get_item_icon(item_id)
            if item_url:
                items_html += f'<img src="{item_url}" style="width: 32px; height: 32px; border: 1px solid #333; border-radius: 4px; margin: 2px;"/>'
            else:
                items_html += '<div style="width: 32px; height: 32px; border: 1px solid #333; border-radius: 4px; margin: 2px; background: #1a1a1a; display: inline-block;"></div>'
        
        trinket_url = get_item_icon(trinket)
        trinket_html = f'<img src="{trinket_url}" style="width: 32px; height: 32px; border: 1px solid #d4af37; border-radius: 4px;"/>' if trinket_url else '<div style="width: 32px; height: 32px; border: 1px solid #d4af37; border-radius: 4px; background: #1a1a1a;"></div>'
        
        # Create the match card HTML
        expand_icon = "▼" if not is_expanded else "▲"
        
        # Build match card in parts to avoid f-string issues
        st.markdown(f"""
        <div style='background: {bg_gradient};
                    border-left: 5px solid {border_color};
                    padding: 15px;
                    margin-bottom: 5px;'>
            <div class='match-card' style='display: flex; align-items: center; gap: 20px; flex-wrap: wrap;'>
                <img src="{get_champion_icon_url(champion_name)}" class="champion-icon"/>
                <div class='meta'>
                    <div style='font-size: 15px; font-weight: bold; margin-bottom: 2px;'>{champion_name}</div>
                    <div style='color: {result_color}; font-size: 13px; font-weight: bold; background: rgba(91, 143, 217, 0.2); display: inline-block; padding: 2px 8px; border-radius: 4px;'>{result_text}</div>
                    <span style='background-color: {queue_badge_color}; color: white; display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; '>{queue_type}</span>
                </div>
                <div class='stats'>
                    <div>{kills} / {deaths} / {assists}</div>
                    <div style='color: #888; font-size: 13px;'>{kda:.2f} KDA</div>
                </div>
                <div style='display: flex; gap: 8px; align-items: center; flex: 2;' class='items'>
                    <div class='summoners'>
                        <img src="{get_summoner_spell_icon(spell1_id)}" style="width: 28px; height: 28px; border-radius: 4px;"/>
                        <img src="{get_summoner_spell_icon(spell2_id)}" style="width: 28px; height: 28px; border-radius: 4px;"/>
                    </div>
                    <div class='items'>
                        <div style='display: grid; grid-template-columns: repeat(3, 32px); gap: 2px;'>{items_html}</div>
                        <div style='margin-left: 4px;'>{trinket_html}</div>
                    </div>
                    <div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expand button
        if st.button(expand_icon, key=f"expand_{idx}", use_container_width=True):
            if is_expanded:
                st.session_state.expanded_matches.remove(idx)
            else:
                st.session_state.expanded_matches.add(idx)
            st.rerun()
        
        # Expanded details
        if is_expanded:

            #preloading some stats
            dmgShare = match.get('challenges', {}).get('teamDamagePercentage', 0) * 100
            dpm = match.get('challenges', {}).get('damagePerMinute', 0)
            total_cs = match.get('totalMinionsKilled', 0) + match.get('neutralMinionsKilled', 0)
            dmgTakenShare = match.get('challenges', {}).get('damageTakenOnTeamPercentage', 0) * 100
            healAndShield = match.get('challenges', {}).get('effectiveHealAndShielding', 0)
            kp = match.get('challenges', {}).get('killParticipation', 0) * 100
            dragons = match.get('challenges', {}).get('dragonTakedowns', 0)
            elder = match.get('challenges', {}).get('teamElderDragonKills', 0)
            total_dragons = dragons + elder
            barons = match.get('challenges', {}).get('baronTakedowns', 0)
            heralds = match.get('challenges', {}).get('riftHeraldTakedowns', 0)
            towers = match.get('challenges', {}).get('turretTakedowns', 0)
            plates = match.get('challenges', {}).get('turretPlatesTaken', 0)

            with st.container():
                detail_cols = st.columns(4)
                
                with detail_cols[0]:
                    st.metric(" :material/explosion:    Total Damage", f"{match.get('totalDamageDealtToChampions', 0):,}")
                    st.metric(" :material/groups_3:    DMG Share %", f"{dmgShare:.1f}%", help="% of damage done over entire team")
                    st.metric(" :material/hourglass_empty:    DMG/min (DPM)", f"{dpm:.0f}")
                
                with detail_cols[1]:
                    st.metric(" :material/target:    Kill Participation", f"{kp:.1f}%")
                    st.metric(" :material/grass:    CS", f"{total_cs}")
                    st.metric(" :material/money_bag:    Gold Earned", f"{match.get('goldEarned', 0):,}")
                    
                
                with detail_cols[2]:
                    st.metric(" :material/shield:    Damage Taken", f"{match.get('totalDamageTaken', 0):,}")
                    st.metric(" :material/security:    DMG Tanked %", f"{dmgTakenShare:.1f}%", help="% of damage tanked over entire team")
                    st.metric(
                        label=" :material/health_and_safety:  Shields & Heals",
                        value=f"{healAndShield:.0f}",
                        help="Effective healing and shielding on allies"
                    )
                    
                
                with detail_cols[3]:
                    st.metric(" :material/visibility:    Vision Score", match.get('visionScore', 0))
                    st.metric(" :material/mystery:    Wards Placed", match.get('wardsPlaced', 0))
                    st.metric(" :material/disabled_visible:    Wards Destroyed", match.get('wardsKilled', 0))
                
                st.markdown("##### :material/trophy:    Objectives")
                obj_cols = st.columns(5)
                
                with obj_cols[0]:
                    st.metric("Dragons", f"{total_dragons:.0f}")
                
                with obj_cols[1]:
                    st.metric("Barons", f"{barons:.0f}")
                
                with obj_cols[2]:
                    st.metric("Heralds", f"{heralds:.0f}")
                
                with obj_cols[3]:
                    st.metric("Turrets", f"{towers:.0f}")
                
                with obj_cols[4]:
                    st.metric("Plates", f"{plates:.0f}")

                st.markdown("---")

    if st.session_state.matches_to_show < len(matches):
        remaining = len(matches) - st.session_state.matches_to_show
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(f"Load More", use_container_width=True): #{min(20, remaining)}
                st.session_state.matches_to_show += 20
                st.rerun()