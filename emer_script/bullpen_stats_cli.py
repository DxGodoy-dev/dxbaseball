import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_pitcher_stats(pitcher_id, pitcher_name):
    """Obtiene las estadísticas de temporada regular (ERA, WHIP, K/9, K/BB) de un relevista."""
    try:
        raw_data = statsapi.get('people', {
            'personIds': pitcher_id,
            'hydrate': 'stats(group=[pitching],type=[season])'
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            splits = stat_group.get('splits', [])
            if splits:
                s = splits[0].get('stat', {})
                return {
                    'name': pitcher_name,
                    'era': s.get('era', '-.--'),
                    'whip': s.get('whip', '-.--'),
                    'ip': s.get('inningsPitched', '0.0'),
                    'k9': s.get('strikeoutsPer9Inn', '-.--'),
                    'k_bb': s.get('strikeoutWalkRatio', '-.--')
                }
    except Exception:
        pass
        
    return {'name': pitcher_name, 'era': '---', 'whip': '---', 'ip': '0.0', 'k9': '---', 'k_bb': '---'}

def print_bullpen(team_name, pitchers):
    print(f"\n{'='*75}")
    print(f"⚾ BULLPEN (TEMPORADA 2026): {team_name.upper()}")
    print(f"{'='*75}")
    print(f"{'Relevista':<22} | {'IP':<6} | {'ERA':<5} | {'WHIP':<5} | {'K/9':<5} | {'K/BB':<5}")
    print("-" * 75)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_pitcher_stats, p['id'], p['name']) for p in pitchers]
        
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
        # Ordenar de menor a mayor ERA para ver a los mejores primero
        results.sort(key=lambda x: float(x['era']) if x['era'] not in ('---', '-.--') else 999.0)
        
        for res in results:
            print(f"{res['name']:<22} | {res['ip']:<6} | {res['era']:<5} | {res['whip']:<5} | {res['k9']:<5} | {res['k_bb']:<5}")

def main():
    client = MLBClient()
    game_id = 849839 # SD vs MIL
    
    feed = client.get_live_feed(game_id)
    if not feed: return
        
    game_data = feed.get('gameData', {})
    live_data = feed.get('liveData', {})
    
    probables = game_data.get('probablePitchers', {})
    away_starter = probables.get('away', {}).get('id')
    home_starter = probables.get('home', {}).get('id')
    
    teams_box = live_data.get('boxscore', {}).get('teams', {})
    
    # CORRECCIÓN: Iteramos sobre todo el roster disponible del juego, no solo los pitchers activos
    away_players = teams_box.get('away', {}).get('players', {})
    away_pitchers = []
    for p_key, p_data in away_players.items():
        if p_data.get('position', {}).get('code') == '1': # Código 1 = Pitcher
            pid = p_data.get('person', {}).get('id')
            if pid and pid != away_starter:
                name = p_data.get('person', {}).get('fullName', f"Unknown {pid}")
                away_pitchers.append({'id': pid, 'name': name})
                
    home_players = teams_box.get('home', {}).get('players', {})
    home_pitchers = []
    for p_key, p_data in home_players.items():
        if p_data.get('position', {}).get('code') == '1':
            pid = p_data.get('person', {}).get('id')
            if pid and pid != home_starter:
                name = p_data.get('person', {}).get('fullName', f"Unknown {pid}")
                home_pitchers.append({'id': pid, 'name': name})
            
    away_team = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
    home_team = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
    
    print_bullpen(away_team, away_pitchers)
    print_bullpen(home_team, home_pitchers)

if __name__ == '__main__':
    main()