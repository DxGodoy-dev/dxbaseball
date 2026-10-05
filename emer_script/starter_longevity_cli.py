import sys
from pathlib import Path
import statsapi

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def fetch_starter_longevity(pitcher_id, pitcher_name):
    """
    Calcula el promedio real de Innings y Pitcheos por Salida (Start).
    Maneja la conversión de tercios de inning (Base 3) a decimales reales.
    """
    try:
        raw_data = statsapi.get('people', {
            'personIds': pitcher_id,
            'hydrate': 'stats(group=[pitching],type=[season])'
        })
        stats = raw_data.get('people', [{}])[0].get('stats', [])
        
        for stat_group in stats:
            if stat_group.get('type', {}).get('displayName') == 'season':
                splits = stat_group.get('splits', [])
                if splits:
                    s = splits[0].get('stat', {})
                    
                    gs = s.get('gamesStarted', 0)
                    if gs == 0:
                        return f"{pitcher_name:<22} | NO HA INICIADO JUEGOS ESTA TEMPORADA"
                        
                    # Conversión de Inning a Outs totales para promedio exacto
                    ip_str = str(s.get('inningsPitched', '0.0'))
                    ip_parts = ip_str.split('.')
                    ip_full = int(ip_parts[0]) if ip_parts[0] else 0
                    ip_frac = int(ip_parts[1]) if len(ip_parts) > 1 else 0
                    
                    total_outs = (ip_full * 3) + ip_frac
                    outs_per_start = total_outs / gs
                    ip_per_start = outs_per_start / 3  # Convertido de vuelta a innings decimales
                    
                    pitches = s.get('numberOfPitches', 0)
                    pitches_per_start = pitches / gs
                    
                    era = s.get('era', '-.--')
                    
                    return f"{pitcher_name:<22} | {gs:<2} | {era:<5} | {ip_per_start:.1f}   | {pitches_per_start:.1f}"
                    
    except Exception as e:
        return f"{pitcher_name:<22} | ERROR: {e}"
        
    return f"{pitcher_name:<22} | SIN DATOS 2026"

def main():
    client = MLBClient()
    game_id = 849834 # ID confirmado SD vs MIL
    
    feed = client.get_live_feed(game_id)
    if not feed: 
        print("❌ Error: No se pudo obtener el feed del juego.")
        return
        
    game_data = feed.get('gameData', {})
    probables = game_data.get('probablePitchers', {})
    
    away_id = probables.get('away', {}).get('id')
    home_id = probables.get('home', {}).get('id')
    
    away_name = game_data.get('players', {}).get(f"ID{away_id}", {}).get('fullName', 'TBD') if away_id else 'TBD'
    home_name = game_data.get('players', {}).get(f"ID{home_id}", {}).get('fullName', 'TBD') if home_id else 'TBD'
    
    print(f"\n{'='*65}")
    print(f"⏱️  LONGEVIDAD DE ABRIDORES (TEMPORADA REGULAR 2026)")
    print(f"{'='*65}")
    print(f"{'Abridor':<22} | GS | ERA   | IP/GS | Pitches/GS")
    print("-" * 65)
    
    if away_id: print(fetch_starter_longevity(away_id, away_name))
    if home_id: print(fetch_starter_longevity(home_id, home_name))
    print("=" * 65)

if __name__ == '__main__':
    main()