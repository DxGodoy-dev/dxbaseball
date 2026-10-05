import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_overall_stats(batter_id, batter_name):
    """
    Realiza UNA sola consulta a la API pidiendo 'season' y 'career' simultáneamente.
    Respeta el principio DRY reduciendo peticiones de red.
    """
    result = {
        'name': batter_name,
        'season': {'pa': 0, 'avg': '---', 'obp': '---', 'slg': '---', 'ops': '---', 'hr': 0, 'k': 0, 'bb': 0},
        'career': {'pa': 0, 'avg': '---', 'obp': '---', 'slg': '---', 'ops': '---', 'hr': 0, 'k': 0, 'bb': 0}
    }
    
    try:
        raw_data = statsapi.get('people', {
            'personIds': batter_id,
            'hydrate': 'stats(group=[hitting],type=[season,career])' # Petición combinada
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            stat_type = stat_group.get('type', {}).get('displayName')
            splits = stat_group.get('splits', [])
            
            if splits:
                s = splits[0].get('stat', {})
                data_dict = {
                    'pa': s.get('plateAppearances', 0),
                    'avg': s.get('avg', '.000'),
                    'obp': s.get('obp', '.000'),
                    'slg': s.get('slg', '.000'),
                    'ops': s.get('ops', '.000'),
                    'hr': s.get('homeRuns', 0),
                    'k': s.get('strikeOuts', 0),
                    'bb': s.get('baseOnBalls', 0)
                }
                
                if stat_type == 'season':
                    result['season'] = data_dict
                elif stat_type == 'career':
                    result['career'] = data_dict
                    
    except Exception:
        pass 
        
    return result

def print_stat_block(team_name, batters, stat_key, title):
    """Renderiza la tabla para la métrica solicitada (season o career)."""
    print(f"\n{'='*75}")
    print(f"📊 {title}: {team_name.upper()}")
    print(f"{'='*75}")
    print(f"{'Bateador':<22} | {'PA':<3} | {'AVG':<5} | {'OBP':<5} | {'SLG':<5} | {'OPS':<5} | {'HR':<2} | {'K':<2} | {'BB':<2}")
    print("-" * 75)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_overall_stats, b['id'], b['name']): b for b in batters}
        
        # Recolectamos resultados manteniendo el orden del lineup
        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
        # Ordenamos los resultados por el orden original del lineup usando un pequeño hack de índice
        order = {b['name']: i for i, b in enumerate(batters)}
        results.sort(key=lambda x: order.get(x['name'], 99))
        
        for res in results:
            data = res[stat_key]
            print(f"{res['name']:<22} | {data['pa']:<3} | {data['avg']:<5} | {data['obp']:<5} | {data['slg']:<5} | {data['ops']:<5} | {data['hr']:<2} | {data['k']:<2} | {data['bb']:<2}")

def main():
    client = MLBClient()
    game_id = 849834 # SD vs MIL
    
    feed = client.get_live_feed(game_id)
    if not feed: return
        
    game_data = feed.get('gameData', {})
    teams_box = feed.get('liveData', {}).get('boxscore', {}).get('teams', {})
    
    away_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                    for bid in teams_box.get('away', {}).get('battingOrder', [])]
                    
    home_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                    for bid in teams_box.get('home', {}).get('battingOrder', [])]
        
    away_team = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
    home_team = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
    
    # Imprimimos Temporada Regular
    print_stat_block(away_team, away_batters, 'season', 'TEMPORADA REGULAR 2026')
    print_stat_block(home_team, home_batters, 'season', 'TEMPORADA REGULAR 2026')
    
    # Imprimimos De por Vida (Career)
    print_stat_block(away_team, away_batters, 'career', 'ESTADÍSTICAS DE POR VIDA (CAREER)')
    print_stat_block(home_team, home_batters, 'career', 'ESTADÍSTICAS DE POR VIDA (CAREER)')

if __name__ == '__main__':
    main()