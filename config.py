"""
VendorGuard - Application Configuration
Central configuration loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
load_dotenv()


class Config:
    """Application configuration from environment variables."""

    # --- API Keys ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
    NEWSCATCHER_API_KEY: str = os.getenv("NEWSCATCHER_API_KEY", "")
    GOOGLE_SERVICE_ACCOUNT_JSON: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")

    # --- Application Settings ---
    RISK_THRESHOLD: int = int(os.getenv("RISK_THRESHOLD", "65"))
    SCAN_TIMEOUT_SECONDS: int = int(os.getenv("SCAN_TIMEOUT_SECONDS", "120"))

    # --- Server Settings ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # --- Risk Scoring Weights (max points per category) ---
    WEATHER_RISK_MAX: int = 30
    NEWS_RISK_MAX: int = 30
    COMMODITY_RISK_MAX: int = 20
    HISTORICAL_RISK_MAX: int = 20

    # --- Risk Band Thresholds ---
    LOW_RISK_MAX: int = 40       # 0-40: LOW
    MEDIUM_RISK_MAX: int = 65    # 41-65: MEDIUM
    # 66-100: HIGH

    # --- Paths ---
    SYNTHETIC_DATA_PATH: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "vendors_synthetic.csv"
    )
    STATIC_FILES_PATH: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static"
    )

    # --- External API Endpoints ---
    OPENWEATHERMAP_BASE_URL: str = "https://api.openweathermap.org/data/2.5"
    NEWSCATCHER_BASE_URL: str = "https://v3-api.newscatcherapi.com/api"

    # --- Rate Limiting ---
    PYTRENDS_DELAY_SECONDS: float = 1.0    # Sleep between pytrends calls
    PPAC_MAX_REQUESTS_PER_SCAN: int = 1     # One PPAC request per scan

    # --- Fallback Values ---
    FALLBACK_DIESEL_PRICE_INR: float = 89.62  # Last known diesel price per litre

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration. Returns list of missing keys."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.OPENWEATHERMAP_API_KEY:
            missing.append("OPENWEATHERMAP_API_KEY")
        if not cls.NEWSCATCHER_API_KEY:
            missing.append("NEWSCATCHER_API_KEY")
        return missing


# Singleton config instance
config = Config()
