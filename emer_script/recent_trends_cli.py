import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_last_n_games(batter_id, batter_name):
    """
    Descarga el registro de juegos, toma los últimos N juegos y calcula el AVG.
    """
    try:
        raw_data = statsapi.get('people', {
            'personIds': batter_id,
            'hydrate': 'stats(group=[hitting],type=[gameLog])'
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        game_logs = []
        for stat_group in stats:
            if stat_group.get('type', {}).get('displayName') == 'gameLog':
                game_logs = stat_group.get('splits', [])
                break
                
        if not game_logs:
            return {'name': batter_name, 'avg5': '---', 'avg10': '---', 'avg15': '---'}
            
        # Ordenar del más reciente al más antiguo por seguridad
        game_logs.sort(key=lambda x: x.get('date', ''), reverse=True)
            
        def calc_avg(logs, n):
            recent = logs[:n]
            hits = sum(game.get('stat', {}).get('hits', 0) for game in recent)
            at_bats = sum(game.get('stat', {}).get('atBats', 0) for game in recent)
            if at_bats == 0: 
                return ".000"
            return f".{int((hits / at_bats) * 1000):03d}"
            
        return {
            'name': batter_name,
            'avg5': calc_avg(game_logs, 5),
            'avg10': calc_avg(game_logs, 10),
            'avg15': calc_avg(game_logs, 15)
        }
    except Exception:
        pass 
        
    return {'name': batter_name, 'avg5': '---', 'avg10': '---', 'avg15': '---'}

def print_trends(team_name, batters):
    print(f"\n{'='*65}")
    print(f"🔥 AVG RECIENTE (5, 10 y 15 Juegos): {team_name.upper()}")
    print(f"{'='*65}")
    print(f"{'Bateador':<22} | {'AVG 5J':<8} | {'AVG 10J':<8} | {'AVG 15J':<8}")
    print("-" * 65)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for batter in batters:
            futures.append(executor.submit(fetch_last_n_games, batter['id'], batter['name']))
            
        for future in futures:
            res = future.result()
            
            # Indicador visual simple: Si en 5 juegos batea .300 o más
            hot_marker = "🔥 (Encendido)" if res['avg5'] != '---' and float(res['avg5']) >= 0.300 else ""
            
            print(f"{res['name']:<22} | {res['avg5']:<8} | {res['avg10']:<8} | {res['avg15']:<8} {hot_marker}")

def main():
    client = MLBClient()
    game_id = 849834 # SD vs MIL
    
    feed = client.get_live_feed(game_id)
    if not feed:
        print("❌ Error: No se pudo obtener el feed del juego.")
        return
        
    game_data = feed.get('gameData', {})
    live_data = feed.get('liveData', {})
    teams_box = live_data.get('boxscore', {}).get('teams', {})
    
    # Extraer Lineups
    away_batters = []
    away_order = teams_box.get('away', {}).get('battingOrder', teams_box.get('away', {}).get('batters', []))
    for bid in away_order:
        name = game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")
        away_batters.append({'id': bid, 'name': name})
        
    home_batters = []
    home_order = teams_box.get('home', {}).get('battingOrder', teams_box.get('home', {}).get('batters', []))
    for bid in home_order:
        name = game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")
        home_batters.append({'id': bid, 'name': name})
        
    away_team_name = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
    home_team_name = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
    
    print_trends(away_team_name, away_batters)
    print_trends(home_team_name, home_batters)

if __name__ == '__main__':
    main()