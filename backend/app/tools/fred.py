"""FRED (Federal Reserve Economic Data) API tools.

Provides access to macroeconomic data including inflation rates,
interest rates, unemployment figures, and GDP growth.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import httpx

# Common FRED series IDs for economic indicators
FRED_SERIES = {
    # Inflation
    "cpi": "CPIAUCSL",  # Consumer Price Index for All Urban Consumers
    "cpi_yoy": "CPIAUCSL",  # CPI Year-over-Year (calculated)
    "pce": "PCEPI",  # Personal Consumption Expenditures Price Index
    "core_cpi": "CPILFESL",  # Core CPI (excluding food and energy)
    # Interest Rates
    "fed_funds": "FEDFUNDS",  # Federal Funds Effective Rate
    "prime_rate": "DPRIME",  # Bank Prime Loan Rate
    "treasury_10y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
    "treasury_2y": "DGS2",  # 2-Year Treasury Constant Maturity Rate
    "mortgage_30y": "MORTGAGE30US",  # 30-Year Fixed Rate Mortgage Average
    # Employment
    "unemployment": "UNRATE",  # Unemployment Rate
    "nonfarm_payrolls": "PAYEMS",  # All Employees, Total Nonfarm
    "initial_claims": "ICSA",  # Initial Claims
    # GDP and Growth
    "gdp": "GDP",  # Gross Domestic Product
    "real_gdp": "GDPC1",  # Real Gross Domestic Product
    "gdp_growth": "A191RL1Q225SBEA",  # Real GDP Growth Rate
    # Consumer
    "consumer_sentiment": "UMCSENT",  # University of Michigan Consumer Sentiment
    "retail_sales": "RSXFS",  # Advance Retail Sales
    "personal_income": "PI",  # Personal Income
    "savings_rate": "PSAVERT",  # Personal Saving Rate
}

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def _get_api_key() -> str:
    """Get FRED API key from environment."""
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        return "demo"  # FRED has a demo key for limited testing
    return api_key


def _format_date(date: datetime) -> str:
    """Format datetime for FRED API."""
    return date.strftime("%Y-%m-%d")


async def _fetch_fred_data(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """Fetch data from FRED API.

    Args:
        series_id: FRED series identifier.
        start_date: Start date (YYYY-MM-DD format).
        end_date: End date (YYYY-MM-DD format).
        limit: Maximum number of observations.

    Returns:
        Dict containing the data or error message.
    """
    api_key = _get_api_key()

    # Default to last year of data
    if not end_date:
        end_date = _format_date(datetime.now())
    if not start_date:
        start_date = _format_date(datetime.now() - timedelta(days=365))

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
        "sort_order": "desc",
        "limit": limit,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(FRED_BASE_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"Failed to fetch FRED data: {str(e)}"}


def get_fred_data(
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10,
) -> str:
    """Fetch economic data from the Federal Reserve Economic Database (FRED).

    Use this tool to get authoritative macroeconomic data including inflation rates,
    interest rates, unemployment figures, GDP, and other economic indicators.

    Common series IDs:
    - CPIAUCSL: Consumer Price Index (inflation)
    - FEDFUNDS: Federal Funds Rate
    - UNRATE: Unemployment Rate
    - GDP: Gross Domestic Product
    - MORTGAGE30US: 30-Year Mortgage Rate
    - DGS10: 10-Year Treasury Rate

    Args:
        series_id: The FRED series identifier (e.g., 'CPIAUCSL' for CPI).
        start_date: Optional start date in YYYY-MM-DD format. Defaults to 1 year ago.
        end_date: Optional end date in YYYY-MM-DD format. Defaults to today.
        limit: Maximum number of data points to return. Defaults to 10.

    Returns:
        A formatted string containing the economic data with dates and values,
        or an error message if the request fails.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(
        _fetch_fred_data(series_id, start_date, end_date, limit)
    )

    if "error" in result:
        return f"Error: {result['error']}"

    if "observations" not in result or not result["observations"]:
        return f"No data found for series {series_id}"

    # Format the response
    observations = result["observations"]
    lines = [f"FRED Data for {series_id}:"]
    lines.append(f"Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("-" * 40)

    for obs in observations:
        date = obs.get("date", "Unknown")
        value = obs.get("value", "N/A")
        if value != ".":  # FRED uses "." for missing values
            lines.append(f"  {date}: {value}")

    return "\n".join(lines)


def get_inflation_rate(months_back: int = 12) -> str:
    """Get current and historical inflation rates (CPI year-over-year change).

    This tool retrieves Consumer Price Index data and calculates the year-over-year
    inflation rate, which measures how much prices have increased compared to the
    same month in the previous year.

    Args:
        months_back: Number of months of historical data to retrieve. Defaults to 12.

    Returns:
        A formatted string showing inflation rates over the specified period,
        including the most recent rate and trend information.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Get enough data to calculate YoY changes
    end_date = _format_date(datetime.now())
    start_date = _format_date(datetime.now() - timedelta(days=(months_back + 13) * 31))

    result = loop.run_until_complete(
        _fetch_fred_data(FRED_SERIES["cpi"], start_date, end_date, limit=months_back + 13)
    )

    if "error" in result:
        return f"Error: {result['error']}"

    if "observations" not in result or len(result["observations"]) < 13:
        return "Insufficient data to calculate year-over-year inflation rates."

    observations = result["observations"]
    # Sort by date ascending for calculation
    observations = sorted(observations, key=lambda x: x["date"])

    lines = ["Inflation Rate (CPI Year-over-Year):"]
    lines.append(f"Data source: FRED (CPIAUCSL)")
    lines.append(f"Retrieved: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("-" * 40)

    # Calculate YoY changes
    yoy_rates = []
    for i in range(12, len(observations)):
        current = observations[i]
        year_ago = observations[i - 12]

        try:
            current_val = float(current["value"])
            year_ago_val = float(year_ago["value"])
            yoy_change = ((current_val - year_ago_val) / year_ago_val) * 100
            yoy_rates.append({
                "date": current["date"],
                "rate": yoy_change,
            })
        except (ValueError, ZeroDivisionError):
            continue

    # Show most recent rates
    for rate_data in reversed(yoy_rates[-min(months_back, len(yoy_rates)):]):
        lines.append(f"  {rate_data['date']}: {rate_data['rate']:.2f}%")

    if yoy_rates:
        latest = yoy_rates[-1]["rate"]
        lines.append("")
        lines.append(f"Current inflation rate: {latest:.2f}%")

        # Add context
        if latest > 4:
            lines.append("Assessment: Inflation is elevated above the Fed's 2% target.")
        elif latest > 2.5:
            lines.append("Assessment: Inflation is moderately above the Fed's 2% target.")
        elif latest > 1.5:
            lines.append("Assessment: Inflation is near the Fed's 2% target range.")
        else:
            lines.append("Assessment: Inflation is below the Fed's 2% target.")

    return "\n".join(lines)


def get_interest_rate(rate_type: str = "fed_funds") -> str:
    """Get current interest rates from the Federal Reserve.

    This tool retrieves various interest rate data that affects borrowing costs,
    savings returns, and overall economic conditions.

    Args:
        rate_type: Type of interest rate to retrieve. Options:
            - 'fed_funds': Federal Funds Rate (overnight lending rate)
            - 'prime': Bank Prime Loan Rate
            - 'treasury_10y': 10-Year Treasury Rate
            - 'treasury_2y': 2-Year Treasury Rate
            - 'mortgage_30y': 30-Year Fixed Mortgage Rate
            Defaults to 'fed_funds'.

    Returns:
        A formatted string showing the requested interest rate data with
        historical context and interpretation.
    """
    import asyncio

    rate_map = {
        "fed_funds": ("FEDFUNDS", "Federal Funds Effective Rate"),
        "prime": ("DPRIME", "Bank Prime Loan Rate"),
        "treasury_10y": ("DGS10", "10-Year Treasury Constant Maturity Rate"),
        "treasury_2y": ("DGS2", "2-Year Treasury Constant Maturity Rate"),
        "mortgage_30y": ("MORTGAGE30US", "30-Year Fixed Rate Mortgage Average"),
    }

    if rate_type not in rate_map:
        return f"Unknown rate type: {rate_type}. Available: {', '.join(rate_map.keys())}"

    series_id, rate_name = rate_map[rate_type]

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    end_date = _format_date(datetime.now())
    start_date = _format_date(datetime.now() - timedelta(days=365))

    result = loop.run_until_complete(
        _fetch_fred_data(series_id, start_date, end_date, limit=52)
    )

    if "error" in result:
        return f"Error: {result['error']}"

    if "observations" not in result or not result["observations"]:
        return f"No data found for {rate_name}"

    observations = [
        obs for obs in result["observations"]
        if obs.get("value") != "."
    ]

    if not observations:
        return f"No valid data found for {rate_name}"

    lines = [f"{rate_name}:"]
    lines.append(f"Data source: FRED ({series_id})")
    lines.append(f"Retrieved: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("-" * 40)

    # Show recent data points
    for obs in observations[:12]:
        lines.append(f"  {obs['date']}: {obs['value']}%")

    # Calculate change
    if len(observations) >= 2:
        try:
            current = float(observations[0]["value"])
            previous = float(observations[1]["value"])
            change = current - previous
            lines.append("")
            lines.append(f"Current rate: {current:.2f}%")
            lines.append(f"Change from previous: {change:+.2f}%")
        except ValueError:
            pass

    # Add context based on rate type
    if rate_type == "fed_funds" and observations:
        try:
            rate = float(observations[0]["value"])
            lines.append("")
            if rate > 5:
                lines.append("Context: The Fed Funds rate is relatively high, indicating tight monetary policy.")
            elif rate > 2:
                lines.append("Context: The Fed Funds rate is moderate.")
            else:
                lines.append("Context: The Fed Funds rate is low, indicating accommodative monetary policy.")
        except ValueError:
            pass

    return "\n".join(lines)


def get_unemployment_rate(months_back: int = 12) -> str:
    """Get current and historical unemployment rate data.

    This tool retrieves the U.S. unemployment rate, which measures the percentage
    of the labor force that is jobless and actively seeking employment.

    Args:
        months_back: Number of months of historical data to retrieve. Defaults to 12.

    Returns:
        A formatted string showing unemployment rates over the specified period
        with trend analysis and economic context.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    end_date = _format_date(datetime.now())
    start_date = _format_date(datetime.now() - timedelta(days=months_back * 31))

    result = loop.run_until_complete(
        _fetch_fred_data(FRED_SERIES["unemployment"], start_date, end_date, limit=months_back)
    )

    if "error" in result:
        return f"Error: {result['error']}"

    if "observations" not in result or not result["observations"]:
        return "No unemployment data found"

    observations = result["observations"]

    lines = ["U.S. Unemployment Rate:"]
    lines.append(f"Data source: FRED (UNRATE)")
    lines.append(f"Retrieved: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("-" * 40)

    for obs in observations:
        if obs.get("value") != ".":
            lines.append(f"  {obs['date']}: {obs['value']}%")

    # Analysis
    valid_obs = [obs for obs in observations if obs.get("value") != "."]
    if valid_obs:
        try:
            current = float(valid_obs[0]["value"])
            lines.append("")
            lines.append(f"Current unemployment rate: {current:.1f}%")

            # Historical context
            if current < 4:
                lines.append("Assessment: Labor market is very tight (low unemployment).")
                lines.append("Implication: Strong job security, potential wage growth pressure.")
            elif current < 5:
                lines.append("Assessment: Labor market is healthy.")
                lines.append("Implication: Good job market conditions for most workers.")
            elif current < 7:
                lines.append("Assessment: Unemployment is elevated.")
                lines.append("Implication: Job seekers may face more competition.")
            else:
                lines.append("Assessment: Unemployment is high.")
                lines.append("Implication: Challenging job market; consider building emergency savings.")
        except ValueError:
            pass

    return "\n".join(lines)
