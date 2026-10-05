import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_vs_team_stats(batter_id, batter_name, opposing_team_id):
    """
    Obtiene las estadísticas del bateador exclusivamente contra el equipo rival,
    limitado de manera estricta a la temporada 2026 para evitar ruido histórico.
    """
    try:
        raw_data = statsapi.get('people', {
            'personIds': batter_id,
            # Pedimos específicamente el split contra equipos y forzamos la temporada 2026
            'hydrate': 'stats(group=[hitting],type=[vsTeam],season=2026)',
        })
        
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            for split in stat_group.get('splits', []):
                # Filtramos por el ID del equipo rival y re-validamos el año
                if split.get('opponent', {}).get('id') == opposing_team_id and str(split.get('season')) == '2026':
                    s = split.get('stat', {})
                    return {
                        'name': batter_name,
                        'pa': s.get('plateAppearances', 0),
                        'avg': s.get('avg', '.000'),
                        'obp': s.get('obp', '.000'),
                        'slg': s.get('slg', '.000'),
                        'ops': s.get('ops', '.000'),
                        'hr': s.get('homeRuns', 0),
                        'k': s.get('strikeOuts', 0),
                        'bb': s.get('baseOnBalls', 0)
                    }
    except Exception:
        pass
        
    # Si no hay datos, devolvemos formato en ceros
    return {'name': batter_name, 'pa': 0, 'avg': '---', 'obp': '---', 'slg': '---', 'ops': '---', 'hr': 0, 'k': 0, 'bb': 0}

def print_vs_team(team_name, batters, opposing_team_name, opposing_team_id):
    if not batters:
        return
        
    print(f"\n{'='*75}")
    print(f"⚔️  STATS VS {opposing_team_name.upper()} (TEMPORADA 2026): {team_name.upper()}")
    print(f"{'='*75}")
    print(f"{'Bateador':<22} | {'PA':<4} | {'AVG':<5} | {'OBP':<5} | {'SLG':<5} | {'OPS':<5} | {'HR':<2} | {'K':<2} | {'BB':<2}")
    print("-" * 75)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_idx = {executor.submit(fetch_vs_team_stats, b['id'], b['name'], opposing_team_id): i for i, b in enumerate(batters)}
        
        results = [None] * len(batters)
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
            
        for res in results:
            if res:
                # Marcador visual para asesinos del equipo rival (OPS >= .900)
                killer = "💀" if res['ops'] != '---' and float(res['ops']) >= 0.900 else ""
                print(f"{res['name']:<22} | {res['pa']:<4} | {res['avg']:<5} | {res['obp']:<5} | {res['slg']:<5} | {res['ops']:<5} | {res['hr']:<2} | {res['k']:<2} | {res['bb']:<2} {killer}")

def main():
    game_id = 849839 
    print(f"\n🎯 Calculando splits vs Equipo Rival (Juego ID: {game_id})...")
    
    client = MLBClient()
    feed = client.get_live_feed(game_id)
    if not feed: return
        
    game_data = feed.get('gameData', {})
    teams_box = feed.get('liveData', {}).get('boxscore', {}).get('teams', {})
    
    # Extraer IDs oficiales de los equipos
    away_id = game_data.get('teams', {}).get('away', {}).get('id')
    home_id = game_data.get('teams', {}).get('home', {}).get('id')
    
    away_name = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
    home_name = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
    
    # Validación segura del lineup (Batting Order vs Roster completo)
    away_bids = teams_box.get('away', {}).get('battingOrder', []) or teams_box.get('away', {}).get('batters', [])
    home_bids = teams_box.get('home', {}).get('battingOrder', []) or teams_box.get('home', {}).get('batters', [])
        
    away_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} for bid in away_bids]
    home_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} for bid in home_bids]
    
    # Imprimimos cruzando a los bateadores contra el ID del equipo contrario
    print_vs_team(away_name, away_batters, home_name, home_id)
    print_vs_team(home_name, home_batters, away_name, away_id)

if __name__ == '__main__':
    main()