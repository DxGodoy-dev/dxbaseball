import sys
from pathlib import Path
import statsapi
import concurrent.futures

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_last_game_stats(batter_id, batter_name):
    """
    Descarga el Game Log del jugador y extrae EXCLUSIVAMENTE su último partido jugado.
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
            return f"{batter_name:<22} | SIN JUEGOS PREVIOS"
            
        # Ordenar por fecha (más reciente primero) y tomar solo el índice [0]
        game_logs.sort(key=lambda x: x.get('date', ''), reverse=True)
        last_game = game_logs[0]
        
        date = last_game.get('date', 'N/A')
        s = last_game.get('stat', {})
        
        ab = s.get('atBats', 0)
        hits = s.get('hits', 0)
        hr = s.get('homeRuns', 0)
        rbi = s.get('rbi', 0)
        bb = s.get('baseOnBalls', 0)
        k = s.get('strikeOuts', 0)
        
        # Marcador visual si dio hit en su último juego
        hit_marker = "🔥" if hits > 0 else "  "
        
        return f"{batter_name:<22} | {date:<10} | {hits}-{ab} {hit_marker} | HR: {hr} | RBI: {rbi} | BB: {bb} | K: {k}"
    except Exception as e:
        return f"{batter_name:<22} | ERROR INTERNO"

def print_last_game(team_name, batters):
    if not batters:
        print(f"\n⚠️ No se encontraron bateadores para {team_name}.")
        return
        
    print(f"\n{'='*75}")
    print(f"⚾ RENDIMIENTO EN SU ÚLTIMO PARTIDO JUGADO: {team_name.upper()}")
    print(f"{'='*75}")
    print(f"{'Bateador':<22} | {'Fecha':<10} | {'H-AB':<5} | {'Poder & Disciplina'}")
    print("-" * 75)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_idx = {executor.submit(fetch_last_game_stats, b['id'], b['name']): i for i, b in enumerate(batters)}
        
        results = [None] * len(batters)
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            results[idx] = future.result()
            
        for res in results:
            if res: print(res)

def main():
    game_id = 849839
    print(f"\n🎯 Analizando momentum para el Juego ID: {game_id}...")
    
    try:
        client = MLBClient()
        feed = client.get_live_feed(game_id)
        if not feed: 
            print("❌ Error: No se pudo obtener el feed del juego.")
            return
            
        game_data = feed.get('gameData', {})
        teams_box = feed.get('liveData', {}).get('boxscore', {}).get('teams', {})
        
        away_team = game_data.get('teams', {}).get('away', {}).get('name', 'Away Team')
        home_team = game_data.get('teams', {}).get('home', {}).get('name', 'Home Team')
        
        # Validación: Si no hay battingOrder oficial aún, usamos todos los bateadores activos (batters)
        away_bids = teams_box.get('away', {}).get('battingOrder', [])
        if not away_bids:
            away_bids = teams_box.get('away', {}).get('batters', [])
            
        home_bids = teams_box.get('home', {}).get('battingOrder', [])
        if not home_bids:
            home_bids = teams_box.get('home', {}).get('batters', [])
            
        away_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                        for bid in away_bids]
                        
        home_batters = [{'id': bid, 'name': game_data.get('players', {}).get(f"ID{bid}", {}).get('fullName', f"Unknown {bid}")} 
                        for bid in home_bids]
        
        print_last_game(away_team, away_batters)
        print_last_game(home_team, home_batters)
        
    except Exception as e:
        print(f"\n❌ Error fatal en la ejecución: {e}")

if __name__ == '__main__':
    main()