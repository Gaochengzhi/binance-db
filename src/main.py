#!/usr/bin/env python3
"""
Binance Public Data Downloader - Main Entry Point
"""

import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger_setup import setup_logger, get_logger
from utils import (
    load_config,
    generate_date_range,
    get_all_trading_pairs,
    ensure_directory_exists,
)
from downloader import BinanceDataDownloader


def generate_download_tasks(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate all download tasks based on configuration
    """
    logger = get_logger()

    # Get time range
    time_range = config["time_range"]
    dates = generate_date_range(time_range["start_date"], time_range["end_date"])
    logger.info(f"Date range: {len(dates)} days from {dates[0]} to {dates[-1]}")

    # Get trading pairs
    trading_pairs = config.get("trading_pairs", [])
    if not trading_pairs:
        logger.info(
            "No specific trading pairs configured, fetching all from Binance API..."
        )
        try:
            trading_pairs = get_all_trading_pairs()
            logger.info(f"Found {len(trading_pairs)} trading pairs from API")
        except Exception as e:
            logger.error(f"Failed to fetch trading pairs: {e}")
            return []
    else:
        logger.info(f"Using configured trading pairs: {len(trading_pairs)} symbols")

    # Get data types and intervals
    data_types = config["data_types"]
    kline_intervals = config.get("kline_intervals", [])

    # Generate tasks
    tasks = []
    for date in dates:
        for symbol in trading_pairs:
            task = {
                "symbol": symbol,
                "date": date,
                "data_types": data_types,
                "kline_intervals": kline_intervals,
            }
            tasks.append(task)

    logger.info(f"Generated {len(tasks)} download tasks")
    return tasks


def download_task(
    downloader: BinanceDataDownloader, task: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a single download task
    """
    logger = get_logger()
    symbol = task["symbol"]
    date = task["date"]

    try:
        logger.info(f"Processing {symbol} for {date}")
        results = downloader.download_symbol_data(
            symbol=symbol,
            date=date,
            data_types=task["data_types"],
            kline_intervals=task["kline_intervals"],
        )

        # Count successes and failures
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        task_result = {
            "symbol": symbol,
            "date": date,
            "success_count": success_count,
            "total_count": total_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "details": results,
        }

        if success_count == total_count:
            logger.info(
                f"✓ Completed {symbol} {date}: {success_count}/{total_count} files"
            )
        else:
            logger.warning(
                f"⚠ Partial success {symbol} {date}: {success_count}/{total_count} files"
            )

        return task_result

    except Exception as e:
        logger.error(f"✗ Failed {symbol} {date}: {e}")
        return {
            "symbol": symbol,
            "date": date,
            "success_count": 0,
            "total_count": 0,
            "success_rate": 0,
            "error": str(e),
        }


def run_downloads(config: Dict[str, Any], tasks: List[Dict[str, Any]]):
    """
    Run downloads with concurrent execution
    """
    logger = get_logger()

    # Create output directories
    ensure_directory_exists(config["output_directory"])
    ensure_directory_exists(config["log_directory"])

    # Initialize downloader
    downloader = BinanceDataDownloader(config)

    # Get concurrency settings
    max_workers = config.get("download", {}).get("max_concurrent_downloads", 3)

    # Execute downloads
    logger.info(f"Starting downloads with {max_workers} concurrent workers")
    completed_tasks = 0
    successful_tasks = 0

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(download_task, downloader, task): task for task in tasks
            }

            # Process completed tasks
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    completed_tasks += 1

                    if result.get("success_rate", 0) == 1.0:
                        successful_tasks += 1

                    # Progress update
                    if completed_tasks % 10 == 0 or completed_tasks == len(tasks):
                        progress = (completed_tasks / len(tasks)) * 100
                        logger.info(
                            f"Progress: {completed_tasks}/{len(tasks)} ({progress:.1f}%) - Success: {successful_tasks}"
                        )

                except Exception as e:
                    logger.error(f"Task execution error: {e}")
                    completed_tasks += 1

    finally:
        downloader.close()

    # Final summary
    success_rate = (successful_tasks / len(tasks)) * 100 if tasks else 0
    logger.info(f"Download completed!")
    logger.info(f"Total tasks: {len(tasks)}")
    logger.info(f"Successful tasks: {successful_tasks}")
    logger.info(f"Success rate: {success_rate:.1f}%")


def main():
    """
    Main entry point
    """
    try:
        # Load configuration
        config = load_config()

        # Setup logging
        logger = setup_logger(config)
        logger.info("Binance Public Data Downloader started")
        logger.info(f"Configuration loaded from config.yaml")

        # Generate download tasks
        tasks = generate_download_tasks(config)

        if not tasks:
            logger.error(
                "No download tasks generated. Check configuration and network connection."
            )
            return 1

        # Run downloads
        run_downloads(config, tasks)

        logger.info("Binance Public Data Downloader finished")
        return 0

    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        return 1
    except Exception as e:
        if "logger" in locals():
            logger.error(f"Unexpected error: {e}")
        else:
            print(f"Critical error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
