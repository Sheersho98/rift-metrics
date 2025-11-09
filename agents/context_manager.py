_player_context = {
    'rich_context': None,
    'champ_insights': None,
    'is_loaded': False
}

def set_context(rich_context, champ_insights):
    #Store player data for tools to access
    global _player_context
    _player_context = {
        'rich_context': rich_context,
        'champ_insights': champ_insights,
        'is_loaded': True
    }

def get_context():
    #Retrieve stored player data
    return _player_context

def clear_context():
    #clear set context
    global _player_context
    _player_context = {
        'rich_context': None,
        'champ_insights': None,
        'is_loaded': False
    }