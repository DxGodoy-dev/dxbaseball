import subprocess
import sys
from pathlib import Path

def main():
    print("\n" + "="*80)
    print("🚀 INICIANDO ORQUESTADOR DE REPORTES (MOTOR COMPLETO DXBASEBALL) 🚀")
    print("="*80)
    
    # Lista de todos los scripts atómicos que construimos
    scripts = [
        ("1. MATCHUPS HISTÓRICOS (BvP)", "matchup_cli.py"),
        ("2. TENDENCIAS (ÚLTIMOS 5, 10, 15 JUEGOS)", "recent_trends_cli.py"),
        ("4. ESTADÍSTICAS GLOBALES (SEASON & CAREER)", "overall_stats_cli.py"),
        ("5. LONGEVIDAD DE ABRIDORES", "starter_longevity_cli.py"),
        ("6. DISCIPLINA DE BATEO (DESGASTE)", "batter_discipline_cli.py"),
        ("7. ESTADO DEL BULLPEN (RELEVISTAS)", "bullpen_stats_cli.py"),
        ("8. MOMENTUM (ÚLTIMO JUEGO)", "last_game_cli.py"),
        ("9. ENFRENTAMIENTOS DE SERIE H2H (EQUIPOS)", "series_h2h_cli.py")
    ]
    
    script_dir = Path(__file__).resolve().parent
    
    for title, script_name in scripts:
        print(f"\n{'*'*80}")
        print(f"---> EJECUTANDO: {title} <---")
        print(f"{'*'*80}")
        
        script_path = script_dir / script_name
        
        if not script_path.exists():
            print(f"⚠️  El archivo {script_name} no existe. Saltando...")
            continue
            
        try:
            subprocess.run(["uv", "run", str(script_path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error al ejecutar {script_name}: {e}")
            sys.exit(1)
            
    print("\n" + "="*80)
    print("✅ MOTOR FINALIZADO. INFORMACIÓN COMPLETA RECOPILADA.")
    print("="*80)

if __name__ == '__main__':
    main()