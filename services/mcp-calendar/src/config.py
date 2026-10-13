from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_oauth_credentials_path: str = "credentials.json"
    google_oauth_token_path: str = "token.json"
    calendar_timezone: str = "Asia/Kolkata"
    working_hours_start: str = "09:00"
    working_hours_end: str = "19:00"
    slot_granularity_minutes: int = 30
    # Central Government gazetted holidays, 2026 (source: DoPT-aligned public calendars).
    # Islamic-calendar dates (Eid, Bakrid, Muharram, Milad-un-Nabi) are moon-sighting dependent
    # and approximate until confirmed by the official DoPT circular each year — override via
    # INDIA_PUBLIC_HOLIDAYS env var (comma-separated ISO dates) once confirmed.
    india_public_holidays: list[str] = [
        "2026-01-26",  # Republic Day
        "2026-03-04",  # Holi
        "2026-03-21",  # Id-ul-Fitr
        "2026-03-26",  # Ram Navami
        "2026-03-31",  # Mahavir Jayanti
        "2026-04-03",  # Good Friday
        "2026-04-14",  # Dr. B.R. Ambedkar Jayanti
        "2026-05-01",  # Buddha Purnima
        "2026-05-28",  # Id-ul-Zuha (Bakrid)
        "2026-06-26",  # Muharram
        "2026-08-15",  # Independence Day
        "2026-08-26",  # Milad-un-Nabi
        "2026-09-04",  # Janmashtami
        "2026-10-02",  # Gandhi Jayanti
        "2026-10-20",  # Dussehra
        "2026-11-08",  # Diwali
        "2026-11-24",  # Guru Nanak's Birthday
        "2026-12-25",  # Christmas
    ]
    # Binds all interfaces so Container Apps' internal ingress can reach this service —
    # it is not internet-exposed (see infra topology, PROJECT_SPEC.md §12).
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8801


settings = Settings()
