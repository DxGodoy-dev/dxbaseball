import sys
from pathlib import Path
from datetime import datetime, timedelta
import statsapi

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.api.mlb_client import MLBClient

def get_recent_series_games(client, current_game_id):
    """
    Rastrea hacia atrás los juegos finalizados entre ambos equipos hasta
    encontrar un rival distinto (límite de la serie actual).
    """
    feed = client.get_live_feed(current_game_id)
    if not feed:
        print("❌ Error al descargar el feed del juego actual.")
        return None, None, []

    game_data = feed.get('gameData', {})
    home_team = game_data.get('teams', {}).get('home', {})
    away_team = game_data.get('teams', {}).get('away', {})
    
    home_id = home_team.get('id')
    away_id = away_team.get('id')
    home_name = home_team.get('name', 'Home')
    away_name = away_team.get('name', 'Away')

    date_str = game_data.get('datetime', {}).get('originalDate', '2026-10-04')
    game_dt = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = (game_dt - timedelta(days=14)).strftime("%Y-%m-%d")
    end_date = (game_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    sched = statsapi.schedule(team=home_id, start_date=start_date, end_date=end_date)
    
    completed_games = [
        g for g in sched 
        if g.get('status') in ['Final', 'Game Over', 'Completed Early'] 
        and g.get('game_id') != current_game_id
    ]

    completed_games.sort(key=lambda x: x.get('game_date', ''))

    series_games = []
    for g in reversed(completed_games):
        opp_id = g['away_id'] if g['home_id'] == home_id else g['home_id']
        if opp_id == away_id:
            series_games.append(g)
        else:
            break

    series_games.reverse()
    return (home_id, home_name), (away_id, away_name), series_games

def compile_team_stats(client, series_games, team_a_id, team_b_id):
    """
    Descarga el boxscore de cada juego de la serie y agrega las estadísticas colectivas.
    """
    stats_acc = {
        team_a_id: {'w': 0, 'l': 0, 'r': 0, 'h': 0, 'ab': 0, 'hr': 0, 'bb': 0, 'k': 0, 'lob': 0, 'er': 0, 'outs': 0},
        team_b_id: {'w': 0, 'l': 0, 'r': 0, 'h': 0, 'ab': 0, 'hr': 0, 'bb': 0, 'k': 0, 'lob': 0, 'er': 0, 'outs': 0}
    }

    for g in series_games:
        gid = g['game_id']
        feed = client.get_live_feed(gid)
        if not feed:
            continue

        box = feed.get('liveData', {}).get('boxscore', {}).get('teams', {})
        
        for side in ['home', 'away']:
            team_info = box.get(side, {})
            tid = team_info.get('team', {}).get('id')
            if tid not in stats_acc:
                continue

            t_bat = team_info.get('teamStats', {}).get('batting', {})
            t_pit = team_info.get('teamStats', {}).get('pitching', {})

            stats_acc[tid]['r'] += t_bat.get('runs', 0)
            stats_acc[tid]['h'] += t_bat.get('hits', 0)
            stats_acc[tid]['ab'] += t_bat.get('atBats', 0)
            stats_acc[tid]['hr'] += t_bat.get('homeRuns', 0)
            stats_acc[tid]['bb'] += t_bat.get('baseOnBalls', 0)
            stats_acc[tid]['k'] += t_bat.get('strikeOuts', 0)
            stats_acc[tid]['lob'] += t_bat.get('leftOnBase', 0)

            stats_acc[tid]['er'] += t_pit.get('earnedRuns', 0)
            stats_acc[tid]['outs'] += t_pit.get('outs', 0)

        h_score = g.get('home_score', 0)
        a_score = g.get('away_score', 0)
        h_id = g.get('home_id')
        a_id = g.get('away_id')

        if h_score > a_score:
            if h_id in stats_acc: stats_acc[h_id]['w'] += 1
            if a_id in stats_acc: stats_acc[a_id]['l'] += 1
        elif a_score > h_score:
            if a_id in stats_acc: stats_acc[a_id]['w'] += 1
            if h_id in stats_acc: stats_acc[h_id]['l'] += 1

    return stats_acc

def main():
    game_id = 849834
    client = MLBClient()

    print(f"\n{'='*78}")
    print(f"🏟️  HISTORIAL RECIENTE H2H EN LA SERIE ACTUAL (Juego ID: {game_id})")
    print(f"{'='*78}")

    (home_id, home_name), (away_id, away_name), series_games = get_recent_series_games(client, game_id)
    if not series_games:
        print(f"\n⚠️  No hay enfrentamientos previos en esta serie (es el Juego 1 entre {away_name} y {home_name}).")
        return

    print(f"Partidos detectados en la serie actual: {len(series_games)}\n")
    for i, g in enumerate(series_games, 1):
        print(f"  • Juego {i} ({g['game_date']}): {g['away_name']} {g['away_score']} @ {g['home_name']} {g['home_score']} (Final)")

    totals = compile_team_stats(client, series_games, home_id, away_id)
    num_games = len(series_games)

    print(f"\n{'-'*78}")
    print(f"{'Métrica Colectiva':<28} | {away_name:<22} | {home_name:<22}")
    print(f"{'-'*78}")

    t_away = totals[away_id]
    t_home = totals[home_id]

    avg_away = f".{int(round((t_away['h'] / t_away['ab']), 3) * 1000):03d}" if t_away['ab'] > 0 else ".000"
    avg_home = f".{int(round((t_home['h'] / t_home['ab']), 3) * 1000):03d}" if t_home['ab'] > 0 else ".000"
    era_away = f"{(t_away['er'] * 27 / t_away['outs']):.2f}" if t_away['outs'] > 0 else "0.00"
    era_home = f"{(t_home['er'] * 27 / t_home['outs']):.2f}" if t_home['outs'] > 0 else "0.00"

    # Resolución: Variables independientes limpias para evitar SyntaxError por backslash en f-strings
    rec_away = f"{t_away['w']}-{t_away['l']}"
    rec_home = f"{t_home['w']}-{t_home['l']}"
    runs_away = f"{t_away['r']} ({t_away['r']/num_games:.1f})"
    runs_home = f"{t_home['r']} ({t_home['r']/num_games:.1f})"
    hits_away = f"{t_away['h']} ({t_away['h']/num_games:.1f})"
    hits_home = f"{t_home['h']} ({t_home['h']/num_games:.1f})"

    print(f"{'Récord en la Serie':<28} | {rec_away:<22} | {rec_home:<22}")
    print(f"{'Carreras Totales (R/J)':<28} | {runs_away:<22} | {runs_home:<22}")
    print(f"{'Hits Totales (H/J)':<28} | {hits_away:<22} | {hits_home:<22}")
    print(f"{'Promedio de Bateo (AVG)':<28} | {avg_away:<22} | {avg_home:<22}")
    print(f"{'Cuadrangulares (HR)':<28} | {t_away['hr']:<22} | {t_home['hr']:<22}")
    print(f"{'Bases por Bolas (BB)':<28} | {t_away['bb']:<22} | {t_home['bb']:<22}")
    print(f"{'Ponches Recibidos (K)':<28} | {t_away['k']:<22} | {t_home['k']:<22}")
    print(f"{'Dejados en Base (LOB)':<28} | {t_away['lob']:<22} | {t_home['lob']:<22}")
    print(f"{'Efectividad Colectiva (ERA)':<28} | {era_away:<22} | {era_home:<22}")
    print(f"{'='*78}\n")

if __name__ == '__main__':
    main()