import sys
from pathlib import Path
import statsapi
import concurrent.futures

# Aseguramos el path para importar tu infraestructura actual
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_bvp(batter_id, batter_name, pitcher_id):
    """
    Realiza la consulta aislada a la API para un enfrentamiento BvP específico.
    Si no hay historial, retorna métricas en cero/vacías.
    """
    if not pitcher_id:
        return {'name': batter_name, 'pa': 0, 'avg': '---', 'obp': '---', 'slg': '---', 'ops': '---', 'hr': 0, 'k': 0, 'bb': 0}

    try:
        raw_data = statsapi.get('people', {
            'personIds': batter_id,
            'hydrate': f'stats(group=[hitting],type=[vsPlayer],opposingPlayerId={pitcher_id})'
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            # Buscamos el nodo 'vsPlayerTotal' que descubrimos en la Fase 0
            if stat_group.get('type', {}).get('displayName') == 'vsPlayerTotal':
                splits = stat_group.get('splits', [])
                if splits:
                    s = splits[0].get('stat', {})
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
        pass # Silenciamos errores individuales para no romper la tabla
    
    # Retorno por defecto si nunca se han enfrentado
    return {
        'name': batter_name, 'pa': 0, 'avg': '---', 'obp': '---', 'slg': '---', 
        'ops': '---', 'hr': 0, 'k': 0, 'bb': 0
    }

def print_matchup(team_name, batters, pitcher_name, pitcher_id):
    """
    Ejecuta las consultas en paralelo y renderiza una tabla ASCII.
    """
    print(f"\n{'='*75}")
    print(f"⚾ BATEADORES DE {team_name.upper()} vs {pitcher_name.upper()} (Pitcher)")
    print(f"{'='*75}")
    print(f"{'Bateador':<22} | {'PA':<3} | {'AVG':<5} | {'OBP':<5} | {'SLG':<5} | {'OPS':<5} | {'HR':<2} | {'K':<2} | {'BB':<2}")
    print("-" * 75)
    
    # Concurrencia: Ejecutamos las 9 consultas simultáneamente (Tarda ~1 segundo)
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for batter in batters:
            futures.append(executor.submit(fetch_bvp, batter['id'], batter['name'], pitcher_id))
            
        for future in futures:
            res = future.result()
            print(f"{res['name']:<22} | {res['pa']:<3} | {res['avg']:<5} | {res['obp']:<5} | {res['slg']:<5} | {res['ops']:<5} | {res['hr']:<2} | {res['k']:<2} | {res['bb']:<2}")

def main():
    client = MLBClient()
    game_id = 849839 # ID confirmado de SD vs MIL
    print(f"\n[INFO] Descargando rosters y probables para el juego {game_id}...")
    
    feed = client.get_live_feed(game_id)
    if not feed:
        print("❌ Error: No se pudo obtener el feed del juego.")
        return
        
    game_data = feed.get('gameData', {})
    live_data = feed.get('liveData', {})
    teams_box = live_data.get('boxscore', {}).get('teams', {})
    
    # 1. Identificar Pitchers Probables
    probables = game_data.get('probablePitchers', {})
    away_pitcher_id = probables.get('away', {}).get('id')
    home_pitcher_id = probables.get('home', {}).get('id')
    
    away_pitcher_name = game_data.get('players', {}).get(f"ID{away_pitcher_id}", {}).get('fullName', 'TBD')
    home_pitcher_name = game_data.get('players', {}).get(f"ID{home_pitcher_id}", {}).get('fullName', 'TBD')
    
    # 2. Extraer Lineups (Prioriza el battingOrder, si no hay, usa el roster activo)
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
    
    # 3. Imprimir Tablas
    print_matchup(away_team_name, away_batters, home_pitcher_name, home_pitcher_id)
    print_matchup(home_team_name, home_batters, away_pitcher_name, away_pitcher_id)

if __name__ == '__main__':
    main()