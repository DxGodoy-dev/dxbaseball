import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_batter_discipline(batter_id, batter_name):
    """
    Calcula los Pitcheos por Aparición al Plato (P/PA) y trae BB/K 
    para medir el nivel de desgaste que generan al abridor rival.
    """
    try:
        raw_data = statsapi.get('people', {
            'personIds': batter_id,
            'hydrate': 'stats(group=[hitting],type=[season])'
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            if stat_group.get('type', {}).get('displayName') == 'season':
                splits = stat_group.get('splits', [])
                if splits:
                    s = splits[0].get('stat', {})
                    pa = s.get('plateAppearances', 0)
                    pitches = s.get('numberOfPitches', 0)
                    bb = s.get('baseOnBalls', 0)
                    k = s.get('strikeOuts', 0)
                    
                    if pa == 0:
                        return f"{batter_name:<22} | 0    | 0    | 0.00 | 0   | 0"
                        
                    p_pa = pitches / pa
                    
                    # Marcador para bateadores que ven muchos pitcheos (Desgastadores)
                    grinder = "⚠️" if p_pa >= 4.00 else "  "
                    
                    return f"{batter_name:<22} | {pa:<4} | {pitches:<4} | {p_pa:.2f} {grinder} | {bb:<3} | {k:<3}"
    except Exception:
        pass
    
    return f"{batter_name:<22} | SIN DATOS 2026"

def print_discipline(team_name, batters):
    print(f"\n{'='*65}")
    print(f"👀 DISCIPLINA Y DESGASTE (2026): {team_name.upper()}")
    print(f"{'='*65}")
    print(f"{'Bateador':<22} | PA   | Pts  | P/PA | BB  | K")
    print("-" * 65)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Usamos un diccionario para mantener el orden exacto del lineup
        future_to_index = {executor.submit(fetch_batter_discipline, b['id'], b['name']): i for i, b in enumerate(batters)}
        
        results = [None] * len(batters)
        for future in concurrent.futures.as_completed(future_to_index):
            idx = future_to_index[future]
            results[idx] = future.result()
            
        for res in results:
            if res:
                print(res)

def main():
    client = MLBClient()
    game_id = 849825
    
    feed = client.get_live_feed(game_id)
    if not feed: 
        print("❌ Error: No se pudo obtener el feed del juego.")
        return
        
    game_data = feed.get('gameData', {})
    teams_box = feed.get('liveData', {}).get('boxscore', {}).get('teams', {})
    
    away_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                    for bid in teams_box.get('away', {}).get('battingOrder', [])]
                    
    home_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                    for bid in teams_box.get('home', {}).get('battingOrder', [])]
                    
    away_team_name = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
    home_team_name = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
    
    print_discipline(away_team_name, away_batters)
    print_discipline(home_team_name, home_batters)

if __name__ == '__main__':
    main()