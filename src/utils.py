import os
import requests
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    """
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def ensure_directory_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist
    """
    os.makedirs(directory, exist_ok=True)


def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Generate list of dates between start_date and end_date (inclusive)
    Format: YYYY-MM-DD
    """
    if end_date.lower() == "latest":
        end_date = datetime.now().strftime("%Y-%m-%d")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


def get_all_trading_pairs() -> List[str]:
    """
    Get all available trading pairs from Binance Futures API
    Returns active USDT perpetual trading pairs only
    """
    try:
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        symbols = [
            symbol["symbol"]
            for symbol in data["symbols"]
            if symbol["status"] == "TRADING" and 
               symbol["contractType"] == "PERPETUAL" and
               symbol["quoteAsset"] == "USDT"  # Only USDT pairs for futures data
        ]
        return sorted(symbols)

    except Exception as e:
        raise Exception(f"Failed to fetch trading pairs from Binance Futures API: {e}")


def build_download_url(
    base_url: str, data_type: str, symbol: str, date: str, interval: str = None
) -> str:
    """
    Build download URL based on data type and parameters
    """
    if data_type in [
        "indexPriceKlines",
        "klines",
        "markPriceKlines",
        "premiumIndexKlines",
    ]:
        if interval is None:
            raise ValueError(f"Interval is required for {data_type}")
        return (
            f"{base_url}{data_type}/{symbol}/{interval}/{symbol}-{interval}-{date}.zip"
        )
    else:
        return f"{base_url}{data_type}/{symbol}/{symbol}-{data_type}-{date}.zip"


def get_output_filename(
    symbol: str, data_type: str, date: str, interval: str = None, extension: str = "csv"
) -> str:
    """
    Generate output filename for processed data
    """
    if interval:
        return f"{symbol}-{data_type}-{interval}-{date}.{extension}"
    else:
        return f"{symbol}-{data_type}-{date}.{extension}"


def is_file_exists(file_path: str) -> bool:
    """
    Check if file exists and has content
    """
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def is_download_needed(csv_path: str, overwrite_existing: bool = False) -> bool:
    """
    Check if download is needed based on existing file and overwrite setting
    """
    if overwrite_existing:
        return True
    
    if not os.path.exists(csv_path):
        return True
    
    # Check if file has content (more than just header)
    try:
        file_size = os.path.getsize(csv_path)
        if file_size < 100:  # Very small file, likely incomplete
            return True
        
        # Check if file has data beyond header
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return len(lines) <= 1  # Only header or empty
    except:
        return True  # If can't read file, need to download


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f}{size_names[i]}"


def validate_date_format(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD)
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_file_directory(
    data_type: str, symbol: str, interval: str = None, base_dir: str = "./data"
) -> str:
    """
    Get the directory path for storing files
    """
    if interval:
        return os.path.join(base_dir, data_type, symbol, interval)
    else:
        return os.path.join(base_dir, data_type, symbol)
