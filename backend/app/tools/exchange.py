"""Currency and Exchange Rate API tools.

Provides access to real-time currency exchange rates and purchasing
power comparisons for understanding global economic context.
"""

import os
from datetime import datetime
from typing import Optional

import httpx

# Exchange Rate API endpoints
EXCHANGE_RATE_BASE_URL = "https://api.exchangerate-api.com/v4/latest"
OPEN_EXCHANGE_RATES_URL = "https://openexchangerates.org/api"


def _get_api_key() -> str:
    """Get Exchange Rate API key from environment."""
    return os.getenv("EXCHANGE_RATE_API_KEY", "")


async def _fetch_exchange_rates(base_currency: str = "USD") -> dict:
    """Fetch current exchange rates.

    Args:
        base_currency: Base currency code (e.g., 'USD', 'EUR').

    Returns:
        Dict containing exchange rates or error message.
    """
    # Try the free API first (no key required)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{EXCHANGE_RATE_BASE_URL}/{base_currency}",
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"Failed to fetch exchange rates: {str(e)}"}


# Approximate purchasing power parity multipliers relative to USD
# Based on World Bank/IMF PPP data (simplified for demonstration)
PPP_MULTIPLIERS = {
    "USD": 1.0,
    "EUR": 0.85,  # Eurozone
    "GBP": 0.75,  # United Kingdom
    "JPY": 100.0,  # Japan (per dollar)
    "CAD": 1.25,  # Canada
    "AUD": 1.45,  # Australia
    "CHF": 0.90,  # Switzerland
    "CNY": 4.5,  # China (PPP adjusted)
    "INR": 25.0,  # India (PPP adjusted)
    "MXN": 10.0,  # Mexico (PPP adjusted)
    "BRL": 2.5,  # Brazil (PPP adjusted)
    "KRW": 850.0,  # South Korea
}

# Cost of living index relative to US average (100)
COST_OF_LIVING_INDEX = {
    "New York": 187,
    "San Francisco": 179,
    "Los Angeles": 166,
    "Chicago": 107,
    "Houston": 96,
    "Miami": 123,
    "Seattle": 149,
    "Denver": 128,
    "Atlanta": 107,
    "Boston": 152,
    "US Average": 100,
    # International
    "London": 145,
    "Paris": 119,
    "Tokyo": 102,
    "Sydney": 118,
    "Toronto": 98,
    "Singapore": 115,
    "Hong Kong": 114,
    "Zurich": 165,
    "Berlin": 86,
    "Amsterdam": 106,
}


def get_exchange_rate(
    from_currency: str = "USD",
    to_currency: str = "EUR",
    amount: float = 1.0,
) -> str:
    """Get current exchange rate between two currencies.

    Use this tool to understand currency conversion rates, which affect
    the real value of savings, cost of imports, and international
    purchasing power.

    Args:
        from_currency: Source currency code (e.g., 'USD', 'EUR', 'GBP').
            Defaults to 'USD'.
        to_currency: Target currency code. Defaults to 'EUR'.
        amount: Amount to convert. Defaults to 1.0.

    Returns:
        A formatted string showing the exchange rate, converted amount,
        and relevant context for financial decisions.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    result = loop.run_until_complete(_fetch_exchange_rates(from_currency))

    if "error" in result:
        return f"Error: {result['error']}"

    rates = result.get("rates", {})

    if to_currency not in rates:
        return f"Currency code '{to_currency}' not found. Common codes: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY"

    rate = rates[to_currency]
    converted = amount * rate

    lines = [f"Exchange Rate: {from_currency} to {to_currency}"]
    lines.append(f"Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("-" * 40)
    lines.append(f"Current rate: 1 {from_currency} = {rate:.4f} {to_currency}")
    lines.append(f"Conversion: {amount:,.2f} {from_currency} = {converted:,.2f} {to_currency}")

    # Show inverse rate too
    inverse_rate = 1 / rate if rate != 0 else 0
    lines.append(f"Inverse rate: 1 {to_currency} = {inverse_rate:.4f} {from_currency}")

    # Add some other major rates for context
    lines.append("")
    lines.append(f"Other rates from {from_currency}:")
    major_currencies = ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
    for curr in major_currencies:
        if curr in rates and curr != to_currency and curr != from_currency:
            lines.append(f"  {from_currency}/{curr}: {rates[curr]:.4f}")

    return "\n".join(lines)


def get_purchasing_power(
    income: float,
    location: str = "US Average",
    compare_to: Optional[str] = None,
) -> str:
    """Analyze purchasing power based on cost of living.

    Use this tool to understand how far money goes in different locations,
    helping users make informed decisions about relocation, remote work,
    or understanding their real financial position.

    Args:
        income: Annual income in USD.
        location: Current or primary location. Options include:
            US cities: 'New York', 'San Francisco', 'Los Angeles', 'Chicago',
                      'Houston', 'Miami', 'Seattle', 'Denver', 'Atlanta', 'Boston'
            International: 'London', 'Paris', 'Tokyo', 'Sydney', 'Toronto',
                          'Singapore', 'Hong Kong', 'Zurich', 'Berlin', 'Amsterdam'
            Default: 'US Average'
        compare_to: Optional second location to compare against.

    Returns:
        A formatted analysis of purchasing power with equivalent incomes
        in different locations and practical implications.
    """
    lines = ["Purchasing Power Analysis"]
    lines.append(f"Analysis date: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("=" * 50)

    # Get cost of living index for the location
    location_index = COST_OF_LIVING_INDEX.get(location, 100)

    lines.append(f"\nYour situation:")
    lines.append(f"  Income: ${income:,.0f}/year")
    lines.append(f"  Location: {location}")
    lines.append(f"  Cost of Living Index: {location_index} (US Average = 100)")

    # Calculate equivalent purchasing power
    us_equivalent = (income * 100) / location_index

    lines.append(f"\nPurchasing power analysis:")
    lines.append(f"  Your ${income:,.0f} in {location} has the same")
    lines.append(f"  purchasing power as ${us_equivalent:,.0f} in a")
    lines.append(f"  city with average US cost of living.")

    if location_index > 100:
        diff_pct = ((location_index - 100) / 100) * 100
        lines.append(f"\n  Note: {location} is {diff_pct:.0f}% more expensive")
        lines.append(f"  than the US average.")
    elif location_index < 100:
        diff_pct = ((100 - location_index) / 100) * 100
        lines.append(f"\n  Note: {location} is {diff_pct:.0f}% less expensive")
        lines.append(f"  than the US average.")

    # Compare to another location if specified
    if compare_to and compare_to in COST_OF_LIVING_INDEX:
        compare_index = COST_OF_LIVING_INDEX[compare_to]
        equivalent_in_compare = (income * compare_index) / location_index

        lines.append(f"\nComparison to {compare_to}:")
        lines.append(f"  Cost of Living Index: {compare_index}")
        lines.append(f"  To maintain your current lifestyle in {compare_to},")
        lines.append(f"  you would need: ${equivalent_in_compare:,.0f}/year")

        if equivalent_in_compare > income:
            lines.append(f"  That's ${equivalent_in_compare - income:,.0f} more than your current income.")
        else:
            lines.append(f"  That's ${income - equivalent_in_compare:,.0f} less than your current income.")

    # Show comparison table
    lines.append("\n" + "-" * 50)
    lines.append("Equivalent income needed in other locations:")
    lines.append(f"(to match ${income:,.0f} in {location})")
    lines.append("")

    sample_locations = ["New York", "San Francisco", "Chicago", "Houston", "Denver", "US Average"]
    for loc in sample_locations:
        if loc in COST_OF_LIVING_INDEX and loc != location:
            loc_index = COST_OF_LIVING_INDEX[loc]
            equivalent = (income * loc_index) / location_index
            lines.append(f"  {loc}: ${equivalent:,.0f}")

    lines.append("\n" + "-" * 50)
    lines.append("Note: Cost of living data is approximate and varies")
    lines.append("by lifestyle and specific neighborhood.")

    return "\n".join(lines)
