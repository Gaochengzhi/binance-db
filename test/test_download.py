#!/usr/bin/env python3
"""
Test script for Binance Public Data Downloader
Downloads single day, single symbol data for testing
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logger_setup import setup_logger, get_logger
from utils import load_config, ensure_directory_exists
from downloader import BinanceDataDownloader

def test_single_download():
    """
    Test downloading data for a single symbol and date
    """
    try:
        # Load test configuration
        config = load_config('test_config.yaml')
        
        # Setup logging
        logger = setup_logger(config)
        logger.info("=== Binance Data Downloader Test Started ===")
        
        # Create test directories
        ensure_directory_exists(config['output_directory'])
        ensure_directory_exists(config['log_directory'])
        
        # Initialize downloader
        downloader = BinanceDataDownloader(config)
        
        # Test parameters
        symbol = "BTCUSDT"
        date = "2024-08-01"
        data_types = config['data_types']
        kline_intervals = config['kline_intervals']
        
        logger.info(f"Testing download for {symbol} on {date}")
        logger.info(f"Data types: {[k for k, v in data_types.items() if v]}")
        logger.info(f"Kline intervals: {kline_intervals}")
        
        # Execute download
        results = downloader.download_symbol_data(
            symbol=symbol,
            date=date,
            data_types=data_types,
            kline_intervals=kline_intervals
        )
        
        # Report results
        logger.info("=== Download Results ===")
        success_count = 0
        total_count = 0
        
        for data_key, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{data_key}: {status}")
            total_count += 1
            if success:
                success_count += 1
        
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info("=== Summary ===")
        logger.info(f"Total files: {total_count}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {total_count - success_count}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        # Close downloader
        downloader.close()
        
        if success_rate >= 80:
            logger.info("✓ Test PASSED - Success rate >= 80%")
            return 0
        else:
            logger.warning("⚠ Test INCOMPLETE - Success rate < 80%")
            return 1
            
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Test FAILED with error: {e}")
        else:
            print(f"Critical test error: {e}")
        return 1

def test_url_building():
    """
    Test URL building functionality
    """
    try:
        from utils import build_download_url
        
        base_url = "https://data.binance.vision/data/futures/um/daily/"
        
        # Test URLs
        test_cases = [
            ("aggTrades", "BTCUSDT", "2024-08-01", None),
            ("klines", "BTCUSDT", "2024-08-01", "1h"),
            ("indexPriceKlines", "BTCUSDT", "2024-08-01", "1d"),
        ]
        
        print("=== URL Building Test ===")
        for data_type, symbol, date, interval in test_cases:
            url = build_download_url(base_url, data_type, symbol, date, interval)
            print(f"{data_type} ({interval}): {url}")
        
        print("✓ URL building test passed")
        return True
        
    except Exception as e:
        print(f"✗ URL building test failed: {e}")
        return False

def main():
    """
    Main test function
    """
    print("Binance Public Data Downloader - Test Script")
    print("=" * 50)
    
    # Test URL building first
    if not test_url_building():
        return 1
    
    # Test actual download
    return test_single_download()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)