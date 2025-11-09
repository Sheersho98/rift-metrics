import requests
import time
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")


def get_account_puuid_by_riot_id(game_name: str, tag_line: str) -> dict:
    base_url = "https://asia.api.riotgames.com"
    endpoint = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
def get_match_ids_by_puuid(region: str, puuid: str, count: int = 40) -> dict:
    routing_region = get_routing_region(region)
    base_url = f"https://{routing_region}.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={count}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_match_details_by_matchId(region: str, match_id: str) -> dict:
    routing_region = get_routing_region(region)
    base_url = f"https://{routing_region}.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_participant_details_by_puuid(match_details: dict, puuid: str) -> dict:
    for participant in match_details['info']['participants']:
        if participant['puuid'] == puuid:
            return participant
    return None

def get_routing_region(shard: str) -> str:
    shard = shard.upper()
    if shard in ["NA", "BR", "LAN", "LAS"]:
        return "americas"
    elif shard in ["KR", "JP"]:
        return "asia"
    elif shard in ["EUNE", "EUW", "ME1", "TR", "RU"]:
        return "europe"
    elif shard in ["OCE", "SG2", "TW2", "VN2"]:
        return "sea"
    else:
        return "americas"

def get_routing_region_summoner(shard: str) -> str:
    shard = shard.upper()
    if shard == "NA":
        return "NA1"
    elif shard == "EUW":
        return "EUW1"
    elif shard == "OCE":
        return "OC1"
    elif shard == "EUNE":
        return "EUN1"
    elif shard == "LAN":
        return "LA1"
    elif shard == "LAS":
        return "LA2"
    elif shard == "BR":
        return "BR1"
    elif shard == "TR":
        return "TR1"
    else:
        return shard

@st.cache_data(show_spinner=False, ttl=3600)
def fetch_all_match_data_direct(game_name: str, tag_line: str, region: str, max_matches: int = 40):
    """
    Directly fetch match data without going through the LLM agent.
    This bypasses token limits and caches the full dataset for 1 hour.
    
    Returns:
        tuple: (list of match data, list of failed match IDs)
    """
    # Step 1: Get PUUID
    account_data = get_account_puuid_by_riot_id(game_name, tag_line)
    if 'error' in account_data:
        raise Exception(f"Failed to get account: {account_data['error']}")
    puuid = account_data['puuid']
    
    # Step 2: Get match IDs
    match_ids = get_match_ids_by_puuid(region, puuid, count=max_matches)
    if 'error' in match_ids:
        raise Exception(f"Failed to get match IDs: {match_ids['error']}")
    
    # Limit to max_matches
    match_ids = match_ids[:max_matches]
    
    # Step 3: Fetch all match data with progress tracking
    all_matches = []
    full_match_details = []
    failed_matches = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, match_id in enumerate(match_ids):
        MAX_RETRIES = 3
        success = False
        
        for attempt in range(MAX_RETRIES):
            status_text.text(f"Fetching data to analyze. Hold on!")
            
            time.sleep(1.3)  # Rate limiting
            
            match_details = get_match_details_by_matchId(region, match_id.strip())
            
            if 'error' not in match_details:
                participant_details = get_participant_details_by_puuid(match_details, puuid)
                if participant_details:
                    queue_id = match_details['info'].get('queueId', 0)
                    participant_details['queueId'] = queue_id
                    participant_details['queue_type'] = 'Solo/Duo' if queue_id == 420 else 'Flex' if queue_id == 440 else 'Unknown'
                    
                    # Inject full participants list
                    participant_details['participants'] = match_details['info']['participants']
                    participant_details['matchId'] = match_details['metadata']['matchId']
                    all_matches.append(participant_details)
                    full_match_details.append(match_details)
                    success = True
                    break
            
            if attempt < MAX_RETRIES - 1:
                wait_for = 3 * (2 ** attempt)
                time.sleep(wait_for)
        
        if not success:
            failed_matches.append(match_id)
        
        # Update progress
        progress_bar.progress((i + 1) / len(match_ids))
    
    progress_bar.empty()
    status_text.empty()
    
    if failed_matches:
        st.warning(f" :material/warning:    Failed to fetch {len(failed_matches)} matches out of {len(match_ids)}")
    
    return all_matches, failed_matches

def get_summonerInfo_by_puuid(region: str, puuid: str) -> str:
    routing_region = get_routing_region_summoner(region)
    base_url = f"https://{routing_region}.api.riotgames.com"
    endpoint = f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        return response_data
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_profile_icon_url(profile_icon_id: int) -> str:
    """Get profile icon URL"""
    return f"https://ddragon.leagueoflegends.com/cdn/15.21.1/img/profileicon/{profile_icon_id}.png"

def get_league_entries_by_puuid(region: str, puuid: str) -> dict:
    """Get ranked information for a player"""
    routing_region = get_routing_region(region)
    
    # Need to get summonerId first from PUUID
    base_url = f"https://{region.lower()}.api.riotgames.com"
    summoner_endpoint = f"/lol/league/v4/entries/by-puuid/{puuid}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        # Get league entries
        league_endpoint = f"/lol/league/v4/entries/by-puuid/{puuid}"
        league_response = requests.get(base_url + league_endpoint, headers=headers)
        league_response.raise_for_status()
        
        league_data = league_response.json()
        
        # Parse solo/duo and flex ranks
        ranks = {
            'solo': None,
            'flex': None
        }
        
        for entry in league_data:
            queue_type = entry.get('queueType')
            if queue_type == 'RANKED_SOLO_5x5':
                ranks['solo'] = {
                    'tier': entry.get('tier'),
                    'rank': entry.get('rank'),
                    'lp': entry.get('leaguePoints'),
                    'wins': entry.get('wins'),
                    'losses': entry.get('losses'),
                }
            elif queue_type == 'RANKED_FLEX_SR':
                ranks['flex'] = {
                    'tier': entry.get('tier'),
                    'rank': entry.get('rank'),
                    'lp': entry.get('leaguePoints'),
                    'wins': entry.get('wins'),
                    'losses': entry.get('losses'),
                }
        return ranks
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}