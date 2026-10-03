from datetime import datetime
import pandas as pd
import statsapi

class consultas():
    def __init__(self):
        self.start_date, self.end_date, self.season_info = self.latest_season() 

    # BASIC
    def basic(self, *args):
        return(statsapi.get(*args))
    
    # ENDPOINTS
    def endpoints(self):
        return statsapi.ENDPOINTS.keys()

    # RECONOCEDOR
    def reconocer(self, dicc, nivel=0, ruta=""):
        indent = "  " * nivel
        
        # 1. Manejo de Nulos (Crucial para saber qué falta en la API)
        if dicc is None:
            print(f"{indent}└── [VALOR NULO] en {ruta}")
            return

        if isinstance(dicc, dict):
            # Si el diccionario está vacío, lo informamos
            if not dicc:
                print(f"{indent}├── {ruta} -> {{}} (Diccionario Vacío)")
                return

            for clave in sorted(dicc.keys()): # Ordenado para facilitar lectura
                nueva_ruta = f"{ruta}['{clave}']" if ruta else f"['{clave}']"
                print(f"{indent}├── {clave}  -> {nueva_ruta}")
                self.reconocer(dicc[clave], nivel + 1, nueva_ruta)

        elif isinstance(dicc, list):
            longitud = len(dicc)
            if longitud == 0:
                print(f"{indent}│   [LISTA VACÍA] -> {ruta}")
            else:
                # 2. Análisis de Consistencia de Lista
                tipos_en_lista = set(type(item).__name__ for item in dicc)
                print(f"{indent}│   [LISTA con {longitud} elementos | Tipos: {tipos_en_lista}]")
                
                # Solo exploramos el primero para el mapa, pero ya sabemos si hay tipos mezclados
                primer_elemento = dicc[0]
                if isinstance(primer_elemento, (dict, list)):
                    self.reconocer(primer_elemento, nivel + 1, f"{ruta}[0]")
                else:
                    print(f"{indent}│   └── Valor Ejemplo: {primer_elemento} ({type(primer_elemento).__name__})")

        # 3. Valores Atómicos (Strings, Ints, Floats)
        else:
            # Solo imprimimos el tipo si estamos en un nivel muy profundo o bajo demanda
            pass

    # LATEST_SEASON
    def latest_season(self, reference_date=None):
        season_info = statsapi.latest_season()
        start_date = season_info.get("regularSeasonStartDate")
        
        if reference_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = reference_date
            
        return start_date, end_date, season_info

    #SCHEDULE
    def schedule(self):
        data = statsapi.get("schedule", {"sportId": 1, "startDate": self.start_date, "endDate": self.end_date, "hydrate": "probablePitcher"})
        lista_df = []

        for dia in data['dates']:
            partidos = dia['games']
            
            if partidos:
                df_temporal = pd.json_normalize(partidos)
                lista_df.append(df_temporal)

        df = pd.concat(lista_df, ignore_index=True)

        mask_columns = [
            'gamePk', 'gameDate', 'status.abstractGameState', 
            'teams.away.team.id', 'teams.away.team.name', 'teams.away.probablePitcher.id', 
            'teams.home.team.id', 'teams.home.team.name', 'teams.home.probablePitcher.id', 
            'venue.id', 'dayNight', 'seriesGameNumber', 'gamesInSeries', 'doubleHeader'
        ]
        
        df = df[mask_columns]
        df['gameDate'] = pd.to_datetime(df['gameDate'])
        df['date'] = df['gameDate'].dt.strftime('%Y-%m-%d')

        return df

    # .META
    def meta(self, req: str) -> dict:
        return statsapi.meta(type= req, fields=None)


req = consultas()
consulta = req.meta("eventTypes")
print(consulta)
for i in consulta:
    print(f"CODE: {i.get('code', {})} | DESCRIPTION: {i.get('description', {})}")