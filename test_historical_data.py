from datetime import datetime, timedelta

from providers.angel.session_manager import SessionManager
from providers.angel.smartapi_client import SmartApiClient
from providers.angel.angel_datasource import AngelDataSource


session = SessionManager()

api = session.connect()

client = SmartApiClient(api)

datasource = AngelDataSource(client)

response = datasource.get_historical_data(
    exchange="NSE",
    token="2885",                  # RELIANCE-EQ
    interval="ONE_DAY",
    from_datetime=datetime.now() - timedelta(days=30),
    to_datetime=datetime.now(),
)

print("\n\nFINAL RESPONSE")
print(response)
