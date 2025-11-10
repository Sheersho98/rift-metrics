
import streamlit as st
from dotenv import load_dotenv
import os

from api.riot_api import fetch_all_match_data_direct
from ui.overview_component import (
    display_player_info_card,
    display_playstyle_tags,
    render_overview_tab,
)
from ui.match_history_component import render_match_history
from utils.helpers import filter_matches_by_queue
from utils.queue_filters import (
    prepare_all_filtered_data,
    display_queue_filter_badge,
)

from agents.playstyle_agent import generate_playstyle_description
from ui.styles import (
    apply_global_styles,
    apply_welcome_background_styles, 
    remove_welcome_background_styles,
    altair_chart_mobile_responsiveness,
)
from ui.welcome_component import render_welcome_page
from api.riot_api import(
    get_match_ids_by_puuid,
    get_match_details_by_matchId
)


altair_chart_mobile_responsiveness()


load_dotenv()

# Get configuration from environment
try:
    from utils.secrets import get_riot_api_key
    RIOT_API_KEY  = get_riot_api_key()
except Exception as e:
    #fallback
    RIOT_API_KEY = os.getenv("RIOT_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")

# Validate required environment variables
if not all([RIOT_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY]):
    st.error("Missing required environment variables. Please check your .env file.")
    st.stop()

# ============ SESSION STATE ============
MAX_CACHED_USERS = 5
if 'user_cache' not in st.session_state:
    st.session_state.user_cache = {}

if 'raw_matches' not in st.session_state:
    st.session_state.raw_matches = None
if 'rich_context' not in st.session_state:
    st.session_state.rich_context = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'context_provided' not in st.session_state:
    st.session_state.context_provided = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
    
# ============ Sidebar UI ============
st.sidebar.image("assets/RiftMetricsTransparent.png", width=200)
st.sidebar.markdown("### Enter Your Riot ID")
st.sidebar.caption("Example: If your Riot ID is 'Berserk#KNG0', enter 'Berserk' in Game Name and 'KNG0' in Tag Line")
#st.sidebar.caption("Format: GameName (without #) and TagLine separately")

riot_id = st.sidebar.text_input("Game Name", placeholder="e.g., HideOnBush (without #)")
tag_line = st.sidebar.text_input("Tag Line", placeholder="e.g., KNG0")
region = st.sidebar.selectbox("Region", ["NA","EUW","KR","OCE","EUNE","LAN","LAS","BR","JP","TR","RU","SG2","TW2","VN2"])

max_matches = 100
st.sidebar.markdown("---")
fetch_button = st.sidebar.button(" :material/search:    Fetch & Analyze Data", type="primary")
st.sidebar.info(" :material/lightbulb:    **Tip:** Enter your Game Name and Tag Line separately. Don't include the '#' symbol!")

# ============ DATA FETCHING ============

if fetch_button and riot_id and tag_line:

    user_key = f"{riot_id}#{tag_line}#{region}"

    # Reset tab to Overview
    st.session_state.selected_tab_index = 0
    st.session_state.selectbox_key = st.session_state.get('selectbox_key', 0) + 1

    # Reset queue filter to "All Games"
    st.session_state.queue_filter_index = 0
    st.session_state.queue_filter_key = st.session_state.get('queue_filter_key', 0) + 1
    
    should_fetch_new = True

    # Clear welcome page background styling
    remove_welcome_background_styles()

    if user_key in st.session_state.user_cache:
        try:
            with st.spinner("Checking for new matches..."):
                # Get account PUUID
                from api.riot_api import  get_match_ids_by_puuid, get_match_details_by_matchId
                
                temp_puuid = st.session_state.user_cache[user_key]['puuid']
                latest_match_ids = get_match_ids_by_puuid(region, temp_puuid, count=1)
                
                if 'error' not in latest_match_ids and len(latest_match_ids) > 0:

                    latest_match_id = latest_match_ids[0]
                    # Get the most recent match ID from cache
                    cached_matches = st.session_state.user_cache[user_key]['raw_matches']
                    if len(cached_matches) > 0:

                        cached_game_id = cached_matches[0].get('matchId', "")
                        latest_match_details = get_match_details_by_matchId(region, latest_match_id)
                        
                        if 'error' not in latest_match_details:
                            latest_game_id = latest_match_details['metadata'].get('matchId', 0)
                            # Match Ids match equals data is still fresh -> fetch from cache
                            if cached_game_id == latest_game_id:

                                should_fetch_new = False
                                
                                cached_data = st.session_state.user_cache[user_key]
                                st.session_state.raw_matches = cached_data['raw_matches']
                                st.session_state.solo_matches = cached_data['solo_matches']
                                st.session_state.flex_matches = cached_data['flex_matches']
                                st.session_state.rich_context = cached_data['rich_context']
                                st.session_state.puuid = cached_data['puuid']
                                st.session_state.riot_id = cached_data['riot_id']
                                st.session_state.tag_line = cached_data['tag_line']
                                st.session_state.iconId = cached_data['iconId']
                                st.session_state.rank_data = cached_data['rank_data']
                                st.session_state.total_games = cached_data['total_games']
                                st.session_state.current_user_id = user_key
                                
                                # restore playstyle cache
                                playstyle_cache = cached_data['playstyle_cache']
                                st.session_state.playstyle = playstyle_cache
                                print(st.session_state.playstyle)

                                # restore summary cache
                                summary_cache = cached_data.get('summary_cache', {})
                                for key, value in summary_cache.items():
                                    st.session_state[key] = value
                                
                                # Clear chat history for new session
                                st.session_state.chat_history = []
                                st.session_state.context_provided = False
                                st.session_state.current_filtered_context = None
                                
                                st.rerun()
        except Exception as e:
            st.warning(f"Cache check failed, fetching fresh data... ({str(e)})")
            should_fetch_new = True

    #stale cache data or fetching for non-cached user
    if should_fetch_new:
        with st.spinner("Fetching your account..."):
            try:
                # Get PUUID first
                from api.riot_api import get_account_puuid_by_riot_id
                account_data = get_account_puuid_by_riot_id(riot_id, tag_line)
                
                if 'error' in account_data:
                    st.error(f" :material/close:    Account not found: **{riot_id}#{tag_line}**")
                    st.info("Please check:\n- Game name is correct (without the # symbol)\n- Tag line is correct\n- You're searching in the right region")
                    st.stop()
                
                puuid = account_data['puuid']
                st.session_state.puuid = puuid
                st.session_state.riot_id = riot_id
                st.session_state.tag_line = tag_line

                from api.riot_api import get_summonerInfo_by_puuid
                summonerInfo = get_summonerInfo_by_puuid(region, puuid)
                if 'error' in summonerInfo:
                    st.error(f"Found account but couldn't fetch summoner info: {summonerInfo['error']}")
                    st.info("Please check:\n You're searching in the right region")
                    st.stop()

                iconId = summonerInfo['profileIconId']
                st.session_state.iconId = iconId

                
            except Exception as e:
                st.error(f"Error fetching account: {e}")
                st.stop()

        with st.spinner("Fetching your match data..."):
            try:
                # Fetch all match data
                all_matches, failed_matches = fetch_all_match_data_direct(
                    riot_id, tag_line, region, max_matches=max_matches
                )
                
                if len(all_matches) == 0:
                    st.warning(f" :material/check_circle:    Account **{riot_id}#{tag_line}** found, but you have no ranked match history!")
                    st.info("""
                    **Why is this happening?**
                    - You haven't played any ranked games yet (Solo/Duo or Flex)
                    - Your ranked matches are too old (we only fetch recent matches)
                    
                    **What to do:**
                    - Play some ranked games and come back!
                    - Make sure you're searching the correct region
                    """)
                    st.stop()
                else:
                    st.session_state.total_games = len(all_matches)
                    with st.spinner("Fetching rank information..."):
                        try:
                            from api.riot_api import get_league_entries_by_puuid
                            rank_data = get_league_entries_by_puuid(region, puuid)
                            st.session_state.rank_data = rank_data
                        except Exception as e:
                            st.warning(f"Could not fetch rank data: {e}")
                            st.session_state.rank_data = {'solo': None, 'flex': None}

                    with st.spinner(" :material/pending:    Analyzing your performance..."):

                        try:
                            st.session_state.raw_matches = all_matches

                            st.session_state.solo_matches = filter_matches_by_queue(all_matches, 'solo')
                            st.session_state.flex_matches = filter_matches_by_queue(all_matches, 'flex')

                            st.session_state.full_match_details = []
                            
                            #Before saving, check if max cache limit is not reached
                            if len(st.session_state.user_cache) >= MAX_CACHED_USERS and user_key not in st.session_state.user_cache:
                                oldest_key = next(iter(st.session_state.user_cache))
                                del st.session_state.user_cache[oldest_key]


                            #Saving to cache
                            st.session_state.current_user_id = user_key

                            # Collect AI summaries for this user
                            summary_cache = {}
                            summary_pages = ['champion_insights', 'advanced_stats', 'early_late', 'matchup_analysis', 'performance_trends']
                            for page in summary_pages:
                                summary_key = f"{user_key}_{page}_summary"
                                show_key = f"{user_key}_{page}_show_summary"
                                if summary_key in st.session_state:
                                    summary_cache[summary_key] = st.session_state[summary_key]
                                if show_key in st.session_state:
                                    summary_cache[show_key] = st.session_state[show_key]

                            st.session_state.user_cache[user_key] = {
                                'raw_matches': st.session_state.raw_matches,
                                'solo_matches': st.session_state.solo_matches,
                                'flex_matches': st.session_state.flex_matches,
                                'rich_context': None,
                                'puuid': st.session_state.puuid,
                                'riot_id': st.session_state.riot_id,
                                'tag_line': st.session_state.tag_line,
                                'iconId': st.session_state.iconId,
                                'rank_data': st.session_state.rank_data,
                                'total_games': st.session_state.total_games,
                                'playstyle_cache': None,
                                'summary_cache': summary_cache,
                            }

                        except Exception as e:
                            st.session_state.raw_matches = all_matches
                    
            except Exception as e:
                st.error(f"Error fetching data: {e}")
                import traceback
                st.code(traceback.format_exc())

# ============ MAIN APP INTEGRATION ============

if "raw_matches" in st.session_state and st.session_state.raw_matches:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### :material/videogame_asset:    Game Mode Filter")

    # Initialize queue filter
    if 'queue_filter_index' not in st.session_state:
        st.session_state.queue_filter_index = 0
    if 'queue_filter_key' not in st.session_state:
        st.session_state.queue_filter_key = 0

    queue_options = ["All Games", "Solo/Duo Only", "Flex 5v5 Only"]
    selected_queue_display = st.sidebar.radio(
        "Filter Analytics",
        options=queue_options,
        key=f'global_queue_filter_{st.session_state.queue_filter_key}',
        help="Filter all analytics by game mode",
        label_visibility='collapsed'
    )

    queue_map = {
        "All Games": "all",
        "Solo/Duo Only": "solo",
        "Flex 5v5 Only": "flex"
    }
    queue_type = queue_map[selected_queue_display]
    st.session_state.queue_filter_index = queue_options.index(selected_queue_display)

    # Get game counts for display
    solo_count = len(st.session_state.get('solo_matches', []))
    flex_count = len(st.session_state.get('flex_matches', []))
    total_count = len(st.session_state.get('raw_matches', []))

    # ===== FILTER MATCHES BASED ON QUEUE TYPE =====
    data_package = prepare_all_filtered_data(queue_type)
    
    if not data_package['has_data']:
        st.warning(f":material/warning:    No recent {selected_queue_display} games found in your match history!")
        st.info("Try selecting a different game mode filter or play some matches in this queue.")
        st.stop()
    
    # Unpack data package for easy access
    df = data_package['df']
    metrics = data_package['metrics']
    early_late_stats = data_package['early_late_stats']
    champ_insights = data_package['champ_insights']
    dominance_score = data_package['dominance_score']
    filtered_matches = data_package['filtered_matches']
    filtered_game_count = data_package['filtered_count']
    solo_count = data_package['solo_count']
    flex_count = data_package['flex_count']
    total_count = data_package['total_count']
    jungle_advanced = data_package['jungle_advanced']
    support_advanced = data_package['support_advanced']
    support_early_stats = data_package['support_early_stats']
    support_dominance_score = data_package['support_dominance_score']
    jungle_early_stats = data_package['jungle_early_stats']
    jungle_dominance_score = data_package['jungle_dominance_score']
    playstyle_tags = data_package['playstyle_tags']
    objective_score = data_package['objective_score']
    persistence_score = data_package['persistence_score']
    laner_advanced = data_package['laner_advanced']

    current_user_id = st.session_state.get('current_user_id', 'unknown')
    
    
    if fetch_button and user_key in st.session_state.user_cache and st.session_state.user_cache[user_key]['playstyle_cache'] == None:
        st.session_state.playstyle = None

        if st.session_state.current_filtered_context and champ_insights is not None:
            from agents.context_manager import set_context
            set_context(st.session_state.current_filtered_context, champ_insights)
            if st.session_state.playstyle is None:
                with st.spinner(" :material/pending:   Analyzing your performance"):
                    playstyle_tuple = generate_playstyle_description()
                    st.session_state.playstyle = playstyle_tuple
                    if user_key in st.session_state.user_cache:
                        st.session_state.user_cache[user_key]['playstyle_cache'] = playstyle_tuple

    # Get role consistency for conditional displays
    role_info = st.session_state.current_filtered_context.get('role_consistency', {}) if st.session_state.current_filtered_context else {}
    primary_role = role_info.get('primary_role', 'UNKNOWN')
    secondary_role = role_info.get('secondary_role', 'NONE')
    
    # Determine role categories for display logic
    is_laner = primary_role in ['TOP', 'MIDDLE', 'BOTTOM'] or secondary_role in ['TOP', 'MIDDLE', 'BOTTOM']
    is_jungler = primary_role == 'JUNGLE' or secondary_role == 'JUNGLE'
    is_support = primary_role == 'UTILITY' or secondary_role == 'UTILITY'

# ========== DISPLAY SECTIONS ========== 
    apply_global_styles()

    #Display summoner icon and name
    if 'riot_id' in st.session_state and 'tag_line' in st.session_state and 'iconId' in st.session_state:
        display_player_info_card(
            st.session_state.riot_id, 
            st.session_state.tag_line, 
            st.session_state.iconId
        )
        
        # Display playstyle tags
        if filtered_game_count >= 10:
            tags_html = display_playstyle_tags(playstyle_tags)
            if tags_html:
                st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown('---')

    # Display filter badge
    display_queue_filter_badge(queue_type, filtered_game_count, solo_count, flex_count)
    
    
    
    st.sidebar.markdown("### :material/assistant_navigation:    Navigation")
    tab_names = [
        "📊 Overview",            
        "📂 Match History",       
        "💎 Champion Insights",   
        "🧠 AI Coaching Session", 
        "📊 Advanced Stats",      
        "⏳ Early vs Late Game",   
        "⚔️ Matchup Analysis",    
        "📈 Performance Analysis" 
    ]

    # Initialize selected tab in session state
    if 'selected_tab_index' not in st.session_state:
        st.session_state.selected_tab_index = 0

    # Initialize selected selectbox in session state
    if 'selectbox_key' not in st.session_state:
        st.session_state.selectbox_key = 0

    selected_tab_name = st.sidebar.selectbox(
        "Select Section",
        options=tab_names,
        index=st.session_state.selected_tab_index,
        key=f'navigation_selector_{st.session_state.selectbox_key}',
        label_visibility='collapsed'
    )

    selected_tab = tab_names.index(selected_tab_name)
    st.session_state.selected_tab_index = selected_tab

    # ===== TAB 0: OVERVIEW =====
    if selected_tab == 0:
        render_overview_tab(data_package, queue_type)
    # ===== TAB 1: MATCH HISTORY =====
    elif selected_tab == 1:

        # Update session state temporarily for match history rendering
        original_matches = st.session_state.get('raw_matches')
        st.session_state.raw_matches = filtered_matches
        render_match_history()
        st.session_state.raw_matches = original_matches  # Restore

    # ===== TAB 2: CHAMPION INSIGHTS =====
    elif selected_tab == 2:
        from ui.champion_insights_component import render_champion_insights

        render_champion_insights(champ_insights, metrics) 
        

    # ===== TAB 3: AI COACHING =====
    elif selected_tab == 3:
        from ui.ai_coach_component import render_ai_coach

        render_ai_coach(filtered_game_count, selected_queue_display)
    
    # ===== TAB 4: ADVANCED STATS =====
    elif selected_tab == 4:
        from ui.advanced_stats_component import render_advanced_stats

        render_advanced_stats(
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
        )
        
    # ===== TAB 5: EARLY VS LATE GAME =====
    elif selected_tab == 5:
        from ui.early_vs_late_game_component import render_early_vs_late_game

        render_early_vs_late_game(
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
        )

    # ===== TAB 6: MATCHUP ANALYSIS =====
    elif selected_tab == 6:
        from ui.matchup_analysis_component import render_matchup_analysis

        render_matchup_analysis(selected_queue_display)

    # ===== TAB 7: PERFORMANCE ANALYSIS =====
    elif selected_tab == 7:
        from ui.performance_trends import render_performance_trends

        render_performance_trends(filtered_game_count, selected_queue_display, df, metrics)

#welcome page for when user first loads onto page
if 'raw_matches' not in st.session_state or st.session_state.raw_matches is None or len(st.session_state.raw_matches) == 0:
    render_welcome_page()
    st.stop()
