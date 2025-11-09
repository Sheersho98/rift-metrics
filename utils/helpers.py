
import re

def extract_json_from_response(response_text: str) -> str:
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, response_text)
    if matches:
        return matches[-1]
    
    clean_response = response_text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[7:]
    if clean_response.startswith("```"):
        clean_response = clean_response[3:]
    if clean_response.endswith("```"):
        clean_response = clean_response[:-3]
    
    return clean_response.strip()

def get_champion_icon_url(champion_name: str) -> str:
    """Get champion icon URL from Data Dragon"""
    # Handle special cases with spaces/apostrophes
    clean_name = champion_name.replace(" ", "").replace("'", "")
    if clean_name == 'FiddleSticks':
        clean_name = clean_name.title()
    return f"https://ddragon.leagueoflegends.com/cdn/15.21.1/img/champion/{clean_name}.png"

def filter_matches_by_queue(matches: list, queue_type: str = 'all') -> list:
    """
    Filter matches by queue type
    queue_type: 'solo', 'flex', or 'all'
    """
    if queue_type == 'all':
        return matches
    elif queue_type == 'solo':
        return [m for m in matches if m.get('queueId') == 420]
    elif queue_type == 'flex':
        return [m for m in matches if m.get('queueId') == 440]
    return matches