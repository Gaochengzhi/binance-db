#!/usr/bin/env python3
"""
Test script for resume functionality
Downloads data, then runs again to test resume
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from logger_setup import setup_logger, get_logger
from utils import load_config, ensure_directory_exists
from downloader import BinanceDataDownloader

def test_resume_functionality():
    """
    Test resume functionality by running download twice
    """
    try:
        # Load test configuration
        config = load_config('test_config.yaml')
        
        # Setup logging
        logger = setup_logger(config)
        logger.info("=== Resume Functionality Test Started ===")
        
        # Create test directories
        ensure_directory_exists(config['output_directory'])
        ensure_directory_exists(config['log_directory'])
        
        # Test parameters
        symbol = "BTCUSDT"
        date = "2024-08-01"
        data_types = {'aggTrades': True, 'klines': True}  # Smaller test
        kline_intervals = ['1d']
        
        logger.info("=== First Download Run ===")
        
        # First download
        downloader1 = BinanceDataDownloader(config)
        results1 = downloader1.download_symbol_data(
            symbol=symbol,
            date=date,
            data_types=data_types,
            kline_intervals=kline_intervals
        )
        downloader1.close()
        
        # Report first run results
        success_count1 = sum(1 for success in results1.values() if success)
        logger.info(f"First run: {success_count1}/{len(results1)} files downloaded")
        
        logger.info("=== Second Download Run (Resume Test) ===")
        
        # Set overwrite to False for resume test
        config['file_processing']['overwrite_existing'] = False
        
        # Second download (should skip existing files)
        downloader2 = BinanceDataDownloader(config)
        results2 = downloader2.download_symbol_data(
            symbol=symbol,
            date=date,
            data_types=data_types,
            kline_intervals=kline_intervals
        )
        downloader2.close()
        
        # Report second run results
        success_count2 = sum(1 for success in results2.values() if success)
        logger.info(f"Second run: {success_count2}/{len(results2)} files processed")
        
        logger.info("=== Resume Test Summary ===")
        logger.info(f"First run downloaded: {success_count1} files")
        logger.info(f"Second run processed: {success_count2} files")
        
        if success_count1 > 0 and success_count2 > 0:
            logger.info("✓ Resume functionality test PASSED")
            return 0
        else:
            logger.error("✗ Resume functionality test FAILED")
            return 1
            
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"Resume test FAILED with error: {e}")
        else:
            print(f"Critical resume test error: {e}")
        return 1

def test_coin_fetching():
    """
    Test trading pairs fetching from Binance API
    """
    try:
        from utils import get_all_trading_pairs
        
        print("=== Trading Pairs Fetching Test ===")
        pairs = get_all_trading_pairs()
        
        print(f"Fetched {len(pairs)} trading pairs from Binance Futures API")
        print("First 10 pairs:", pairs[:10])
        print("Common pairs check:")
        
        common_pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT']
        for pair in common_pairs:
            if pair in pairs:
                print(f"  ✓ {pair} found")
            else:
                print(f"  ✗ {pair} not found")
        
        print("✓ Trading pairs fetching test completed")
        return True
        
    except Exception as e:
        print(f"✗ Trading pairs fetching test failed: {e}")
        return False

def main():
    """
    Main test function
    """
    print("Binance Public Data Downloader - Resume & API Test Script")
    print("=" * 60)
    
    # Test trading pairs fetching first
    if not test_coin_fetching():
        return 1
    
    print("\n" + "=" * 60)
    
    # Test resume functionality
    return test_resume_functionality()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)