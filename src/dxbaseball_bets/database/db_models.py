from sqlalchemy import MetaData, Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import declarative_base

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

# --- MIXINS (Sincronizados con METRIC_SCALING) ---

class HitterBaseMixin:
    """Mix de estadísticas de bateo (Integers escalados)."""
    pa = Column(Integer, default=0)
    ab = Column(Integer, default=0)
    h = Column(Integer, default=0)
    d = Column(Integer, default=0)
    t = Column(Integer, default=0)
    hr = Column(Integer, default=0)
    bb = Column(Integer, default=0)
    k = Column(Integer, default=0)
    hbp = Column(Integer, default=0)
    sf = Column(Integer, default=0)
    sh = Column(Integer, default=0)
    avg = Column(Integer, default=0)  # x1000
    obp = Column(Integer, default=0)  # x1000
    slg = Column(Integer, default=0)  # x1000
    ops = Column(Integer, default=0)  # x1000
    babip = Column(Integer, default=0) # x1000

class PitcherBaseMixin:
    """Mix de estadísticas de pitcheo (Integers escalados)."""
    innings_pitched = Column(Integer, default=0)
    er = Column(Integer, default=0)
    h = Column(Integer, default=0)
    k = Column(Integer, default=0)
    bb = Column(Integer, default=0)
    hr = Column(Integer, default=0)
    era = Column(Integer, default=0)  # x1000
    whip = Column(Integer, default=0) # x1000
    fip = Column(Integer, default=0)  # x1000
    babip = Column(Integer, default=0) # x1000

# --- DIMENSIONES ---

class Venue(Base):
    __tablename__ = 'venues'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String)
    state = Column(String)
    turf_type = Column(String) # Corrección: Tipo de superficie
    latitude = Column(Integer)  # x1000
    longitude = Column(Integer) # x1000
    elevation = Column(Integer)
    left_line = Column(Integer)
    left = Column(Integer)
    left_center = Column(Integer)
    center_field = Column(Integer)
    right_center = Column(Integer)
    right = Column(Integer)
    right_line = Column(Integer)

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    bat_side = Column(String(1))
    pitch_hand = Column(String(1))
    primary_position = Column(String) # Corrección: Metadata de posición

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    abbreviation = Column(String(5))

class Umpire(Base):
    __tablename__ = 'umpires'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)

class GameContext(Base):
    __tablename__ = 'game_context'
    game_id = Column(Integer, primary_key=True)
    game_date = Column(String)
    venue_id = Column(Integer, ForeignKey('venues.id'))
    home_team_id = Column(Integer, ForeignKey('teams.id'))
    away_team_id = Column(Integer, ForeignKey('teams.id'))
    temperature = Column(Integer)
    condition = Column(String)
    wind = Column(String)

# --- HECHOS (Statcast Optimizado) ---

class AtBat(Base):
    __tablename__ = 'stc_at_bats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game_context.game_id'), index=True)
    at_bat_number = Column(Integer)
    pitcher_id = Column(Integer, ForeignKey('players.id'), index=True)
    batter_id = Column(Integer, ForeignKey('players.id'), index=True)
    inning = Column(Integer)
    event = Column(String) # Ej: Home Run, Strikeout[cite: 1]
    result = Column(String)

class Pitch(Base):
    __tablename__ = 'stc_pitches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game_context.game_id'), index=True)
    pitcher_id = Column(Integer, index=True)
    batter_id = Column(Integer, index=True)
    inning = Column(Integer)
    pitch_type = Column(String(5))
    velocity = Column(Integer)      # x10
    spin_rate = Column(Integer)     # x1
    px = Column(Integer)            # x1000
    pz = Column(Integer)            # x1000
    pfx_x = Column(Integer)         # x1000
    pfx_z = Column(Integer)         # x1000
    launch_speed = Column(Integer)  # x10
    launch_angle = Column(Integer)  # x10
    total_distance = Column(Integer) # x10
    is_swing = Column(Integer, default=0)
    is_miss = Column(Integer, default=0)
    is_strike_called = Column(Integer, default=0)

class InningMetric(Base):
    __tablename__ = 'inning_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('game_context.game_id'), index=True)
    pitcher_id = Column(Integer, ForeignKey('players.id'), index=True)
    inning = Column(Integer)
    velocity_loss_vs_start = Column(Integer) # x10
    csw_pct = Column(Integer)                # x1000

# --- PERFORMANCE Y CARRERA ---

class HitterPerformanceDaily(Base, HitterBaseMixin):
    __tablename__ = 'hitter_performance_daily'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True)
    woba = Column(Integer, default=0) # x1000
    iso = Column(Integer, default=0)  # x1000

class PitcherPerformanceDaily(Base, PitcherBaseMixin):
    __tablename__ = 'pitcher_performance_daily'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True)

class HitterCareerStats(Base, HitterBaseMixin):
    __tablename__ = 'hitter_career_stats'
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)

class PitcherCareerStats(Base, PitcherBaseMixin):
    __tablename__ = 'pitcher_career_stats'
    player_id = Column(Integer, ForeignKey('players.id'), primary_key=True)