import statsapi
import json

def rastreo_total_statcast(game_id):
    print(f"--- RASTREO TOTAL DE MÉTRICAS (Game: {game_id}) ---")
    raw = statsapi.get('game', {'gamePk': game_id})
    all_plays = raw.get('liveData', {}).get('plays', {}).get('allPlays', [])
    
    hallazgos_bateo = False
    hallazgos_pitcheo = False

    for i, play in enumerate(all_plays):
        desc = play.get('result', {}).get('description', 'Sin descripción')
        events = play.get('playEvents', [])
        
        for event in events:
            hit_data = event.get('hitData', {})
            pitch_data = event.get('pitchData', {})

            # 1. Verificar Bateo (El eslabón perdido)
            if hit_data and not hallazgos_bateo:
                print(f"\n[!!!] ¡HIT DATA ENCONTRADO! (Jugada {i})")
                print(f"Evento: {desc}")
                print(f"Ruta: allPlays[{i}].playEvents[x].hitData")
                print(f"Llaves detectadas: {list(hit_data.keys())}")
                print(f"Valores ejemplo: Speed: {hit_data.get('launchSpeed')}, Angle: {hit_data.get('launchAngle')}")
                hallazgos_bateo = True

            # 2. Verificar Pitcheo
            if pitch_data and not hallazgos_pitcheo:
                if 'startSpeed' in pitch_data:
                    print(f"\n[!] PITCH DATA ENCONTRADO (Jugada {i})")
                    print(f"Llaves detectadas: {list(pitch_data.keys())}")
                    hallazgos_pitcheo = True

        if hallazgos_bateo and hallazgos_pitcheo:
            print("\n--- INVESTIGACIÓN COMPLETADA: TODAS LAS RUTAS ASEGURADAS ---")
            return

    if not hallazgos_bateo:
        print("\n[ALERTA] Se recorrieron todas las jugadas y NO se encontró 'hitData'.")
        print("Es posible que este endpoint no incluya Statcast de bateo o necesitemos otro ID.")

if __name__ == "__main__":
    rastreo_total_statcast(745214)