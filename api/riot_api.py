import requests
import time
import streamlit as st
import os
import httpx, asyncio
from dotenv import load_dotenv

try:
    from utils.secrets import get_riot_api_key
    RIOT_API_KEY  = get_riot_api_key()
except Exception as e:
    #fallback
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
# In your API module

def fetch_all_match_data_direct(game_name: str, tag_line: str, region: str, max_matches: int):
    #handles partial fetches and visual rate-limit retries
    RIOT_BURST_LIMIT = 20
    match_fetching_semaphore = asyncio.Semaphore(RIOT_BURST_LIMIT)
    
    with st.spinner("Fetching player account data..."):
        #fetch puuid (Sequential)
        account_data = asyncio.run(get_account_puuid_by_riot_id_async(game_name, tag_line, httpx.AsyncClient(timeout=30.0)))
        if 'error' in account_data:
            raise Exception(f"Failed to get account: {account_data['error']}")
        puuid = account_data['puuid']

        #fetch all match ids (Sequential)
        match_ids_full_list = asyncio.run(get_match_ids_by_puuid_async(region, puuid, max_matches, httpx.AsyncClient(timeout=30.0)))
        if 'error' in match_ids_full_list:
            raise Exception(f"Failed to get match IDs: {match_ids_full_list['error']}")
            
        match_ids_to_process = match_ids_full_list[:max_matches:]

    # lists to store final results
    final_all_matches = []
    fetch_status_placeholder = st.empty()
    # loop as long as there are matches left to process
    while match_ids_to_process: 
        
        with st.spinner(f"Fetching match details..."):
            
            #run async function with ONLY the matches that still need fetching
            all_matches_successful, matches_to_retry, long_wait_signal = asyncio.run(
                fetch_all_match_data_async(
                    game_name, 
                    tag_line, 
                    region, 
                    match_ids_to_process,
                    puuid,
                    match_fetching_semaphore,
                    max_matches
                )
            )

        #process Successful Fetches
        final_all_matches.extend(all_matches_successful)
        
        #check for long wait
        if long_wait_signal:
            required_wait = long_wait_signal
            fetch_status_placeholder.empty()

            # --- ui Wait/Countdown ---
            with fetch_status_placeholder.status(f"Riot API Rate Limit Hit. Waiting for counter reset...", expanded=True) as status:
                wait_bar = status.progress(0, text=f"Waiting {required_wait:.0f}s...")
                
                for remaining_time in range(int(required_wait), 0, -1):
                    
                    percent_complete = 1 - (remaining_time / required_wait)
                    wait_bar.progress(percent_complete, text=f"Waiting {remaining_time:.0f}s for Riot API window reset...")
                    time.sleep(1)
                        
                status.update(label="Rate Limit Reset Complete!", state="complete", expanded=False)
                time.sleep(1) # 1 second to let user see 'Complete' state
            
            fetch_status_placeholder.empty()
            st.toast("Rate limit window reset. Retrying fetch!")

            # After waiting, set the remaining matches for the next iteration
            match_ids_to_process = matches_to_retry 
            continue # Start the while loop again to retry the failed segment
            
        elif not matches_to_retry:
            # All matches fetched successfully
            break 
        
        else:
            # non-rate limit errors occurred, retry failed ones
            match_ids_to_process = matches_to_retry

    fetch_status_placeholder.empty()
    return final_all_matches, [] # returning empty list for failed matches, as they were retried successfully

async def fetch_all_match_data_async(
    game_name: str, 
    tag_line: str, 
    region: str, 
    match_ids_to_process: list,
    puuid: str,                  
    semaphore: asyncio.Semaphore,
    max_matches: int = 100
):
    all_matches_successful = []
    matches_to_retry = []
    long_wait_signal = None
    
    # using httpx.AsyncClient for connection pooling
    async with httpx.AsyncClient(timeout=30.0) as client:

        #fetch match data CONCURRENTLY ---
        tasks = [
            fetch_match_details_async(region, match_id.strip(), client, semaphore)
            for match_id in match_ids_to_process
        ]
        
        match_details_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, match_details in enumerate(match_details_results):
            match_id = match_ids_to_process[i]
            
            # check for long wait
            if isinstance(match_details, dict) and 'long_wait_signal' in match_details:
                #entire loop stops and signals the wait.
                long_wait_signal = match_details['long_wait_signal']
                matches_to_retry.extend(match_ids_to_process[i:])
                break # stop and signal the retry
            
            # check for Success
            elif isinstance(match_details, dict) and 'error' not in match_details:
                participant_details = get_participant_details_by_puuid(match_details, puuid)
                if participant_details:
                    queue_id = match_details['info'].get('queueId', 0)
                    participant_details['queueId'] = queue_id
                    participant_details['queue_type'] = 'Solo/Duo' if queue_id == 420 else 'Flex' if queue_id == 440 else 'Unknown'
                    participant_details['participants'] = match_details['info']['participants']
                    participant_details['matchId'] = match_details['metadata']['matchId']
                    all_matches_successful.append(participant_details)
            else:
                matches_to_retry.append(match_id)
                
    # Return the results, the list of matches that still need fetching, and the wait signal
    return all_matches_successful, matches_to_retry, long_wait_signal

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
    return f"https://ddragon.leagueoflegends.com/cdn/15.21.1/img/profileicon/{profile_icon_id}.png"

def get_league_entries_by_puuid(region: str, puuid: str) -> dict:
    #ranked info
    routing_region = get_routing_region_summoner(region)
    base_url = f"https://{routing_region.lower()}.api.riotgames.com"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    
    try:
        league_endpoint = f"/lol/league/v4/entries/by-puuid/{puuid}"
        league_response = requests.get(base_url + league_endpoint, headers=headers)
        league_response.raise_for_status()
        
        league_data = league_response.json()
        
        #Parse solo/duo and flex ranks
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
    

async def fetch_url_quick(url: str, client: httpx.AsyncClient):
    headers = {"X-Riot-Token": RIOT_API_KEY}
    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status() 
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            #getting'Retry-After' header from riot api response
            retry_after = int(e.response.headers.get('Retry-After', 5)) 
            return {'retry_after': retry_after} # Signal that a retry is required
        
        # non-429 HTTP error handling
        return {'error': f"HTTP Error {e.response.status_code}"}
    except Exception as e:
        return {'error': f"An error occurred: {e}"}
    
LONG_WAIT_REQUIRED = 125.0 

async def fetch_match_details_async(region: str, match_id: str, client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
    #Async fetch with burst control (Semaphore) and retry loop for 429 errors.

    MAX_RETRIES = 5
    DELAY_PER_REQUEST = 1.5
    
    #Burst Control: limitting concurrent tasks
    async with semaphore: 
        
        routing_region = get_routing_region(region)
        base_url = f"https://{routing_region}.api.riotgames.com"
        url = f"{base_url}/lol/match/v5/matches/{match_id}"
        
        for attempt in range(MAX_RETRIES):
            
            #minimal non-blocking delay on every attempt to protect from internal bursts
            await asyncio.sleep(DELAY_PER_REQUEST) 

            result = await fetch_url_quick(url, client)
            
            # success
            if 'error' not in result and 'retry_after' not in result:
                return result
            
            # rate limit handler
            if 'retry_after' in result:
                wait_time = result['retry_after']
                if wait_time > 5:
                    return {'long_wait_signal': wait_time}

                if attempt < MAX_RETRIES - 1:
                    wait_time += 0.5 
                    print(f"Rate limit hit for {match_id}. Retrying in {wait_time}s. (Attempt {attempt+1})")
                    await asyncio.sleep(wait_time)
                else:
                    return {'error': f"Failed after {MAX_RETRIES} retries due to rate limits."}

            # other Error
            else:
                return result

    return {'error': f"Failed to fetch {match_id} after {MAX_RETRIES} attempts."}

# async version using quick url helper func
async def get_account_puuid_by_riot_id_async(game_name: str, tag_line: str, client: httpx.AsyncClient):
    base_url = "https://asia.api.riotgames.com"
    url = f"{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    return await fetch_url_quick(url, client)

async def get_match_ids_by_puuid_async(region: str, puuid: str, count: int, client: httpx.AsyncClient):
    routing_region = get_routing_region(region)
    base_url = f"https://{routing_region}.api.riotgames.com"
    url = f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count={count}"
    return await fetch_url_quick(url, client)