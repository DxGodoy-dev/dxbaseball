import statsapi

class APIInspector:
    """
    Herramientas de introspección para la API de MLB.
    Uso exclusivo para desarrollo y descubrimiento de esquemas.
    """
    
    @staticmethod
    def endpoints():
        """Lista todos los endpoints disponibles en el SDK."""
        return statsapi.ENDPOINTS.keys()

    @staticmethod
    def meta(tipo_dato: str):
        """
        Consulta metadatos de la API (ej: 'gameStatuses', 'hitTypes').
        """
        try:
            return statsapi.meta(type=tipo_dato)
        except Exception as e:
            return f"Error consultando meta '{tipo_dato}': {e}"

    def reconocer(self, dicc, nivel=0, ruta=""):
        """
        Explorador recursivo de JSON para mapear rutas de datos.
        """
        indent = "  " * nivel
        
        if dicc is None:
            print(f"{indent}└── [VALOR NULO] en {ruta}")
            return

        if isinstance(dicc, dict):
            if not dicc:
                print(f"{indent}├── {ruta} -> {{}} (Diccionario Vacío)")
                return
            for clave in sorted(dicc.keys()):
                nueva_ruta = f"{ruta}['{clave}']" if ruta else f"['{clave}']"
                print(f"{indent}├── {clave}  -> {nueva_ruta}")
                self.reconocer(dicc[clave], nivel + 1, nueva_ruta)

        elif isinstance(dicc, list):
            longitud = len(dicc)
            if longitud == 0:
                print(f"{indent}│   [LISTA VACÍA] -> {ruta}")
            else:
                tipos_en_lista = set(type(item).__name__ for item in dicc)
                print(f"{indent}│   [LISTA con {longitud} elementos | Tipos: {tipos_en_lista}]")
                primer_elemento = dicc[0]
                if isinstance(primer_elemento, (dict, list)):
                    self.reconocer(primer_elemento, nivel + 1, f"{ruta}[0]")
                else:
                    print(f"{indent}│   └── Valor Ejemplo: {primer_elemento} ({type(primer_elemento).__name__})")