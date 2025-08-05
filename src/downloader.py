import os
import time
import zipfile
import requests
from typing import Optional, Dict, Any
from logger_setup import get_logger
from utils import (
    ensure_directory_exists, 
    build_download_url, 
    get_output_filename, 
    is_file_exists, 
    is_download_needed,
    format_file_size,
    get_file_directory
)

class BinanceDataDownloader:
    """
    Core downloader class for Binance public data
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger()
        self.base_url = config['base_url']
        self.output_dir = config['output_directory']
        
        # Download settings
        download_config = config.get('download', {})
        self.retry_attempts = download_config.get('retry_attempts', 3)
        self.retry_delay = download_config.get('retry_delay', 5)
        self.rate_limit_delay = download_config.get('rate_limit_delay', 0.1)
        self.chunk_size = download_config.get('chunk_size', 8192)
        
        # File processing settings
        file_config = config.get('file_processing', {})
        self.auto_extract = file_config.get('auto_extract', True)
        self.delete_zip = file_config.get('delete_zip_after_extract', True)
        self.overwrite_existing = file_config.get('overwrite_existing', False)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Binance-Data-Downloader/1.0'
        })
    
    def download_file(self, symbol: str, data_type: str, date: str, interval: str = None) -> bool:
        """
        Download a single file with retry mechanism and rate limiting
        """
        try:
            # Build URL and file paths
            url = build_download_url(self.base_url, data_type, symbol, date, interval)
            
            # Determine output directory and filename
            file_dir = get_file_directory(data_type, symbol, interval, self.output_dir)
            ensure_directory_exists(file_dir)
            
            zip_filename = get_output_filename(symbol, data_type, date, interval, "zip")
            csv_filename = get_output_filename(symbol, data_type, date, interval, "csv")
            
            zip_path = os.path.join(file_dir, zip_filename)
            csv_path = os.path.join(file_dir, csv_filename)
            
            # Check if download is needed (resume functionality)
            if not is_download_needed(csv_path, self.overwrite_existing):
                self.logger.info(f"File already exists and complete, skipping: {os.path.basename(csv_path)}")
                return True
            
            # Download with retry mechanism
            for attempt in range(self.retry_attempts):
                try:
                    self.logger.info(f"Downloading [{attempt + 1}/{self.retry_attempts}]: {url}")
                    
                    # Apply rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                    response = self.session.get(url, stream=True, timeout=30)
                    
                    # Handle 404 errors (file doesn't exist for this date/symbol)
                    if response.status_code == 404:
                        self.logger.warning(f"Data not available (404): {url}")
                        return False  # Don't retry for 404
                    
                    response.raise_for_status()
                    
                    # Download file
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0
                    
                    with open(zip_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                    
                    self.logger.info(f"Downloaded {format_file_size(downloaded_size)}: {zip_filename}")
                    
                    # Extract if enabled
                    if self.auto_extract:
                        if self._extract_zip_file(zip_path, file_dir):
                            self.logger.info(f"Extracted: {csv_filename}")
                            
                            # Delete ZIP file if configured
                            if self.delete_zip:
                                os.remove(zip_path)
                                self.logger.debug(f"Deleted ZIP file: {zip_filename}")
                        else:
                            self.logger.error(f"Failed to extract: {zip_filename}")
                            return False
                    
                    return True
                    
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                    if attempt < self.retry_attempts - 1:
                        self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    else:
                        self.logger.error(f"All download attempts failed for: {url}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Unexpected error during download: {e}")
                    return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in download_file: {e}")
            return False
    
    def _extract_zip_file(self, zip_path: str, extract_dir: str) -> bool:
        """
        Extract ZIP file and handle potential errors
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except zipfile.BadZipFile:
            self.logger.error(f"Corrupted ZIP file: {zip_path}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to extract {zip_path}: {e}")
            return False
    
    def download_symbol_data(self, symbol: str, date: str, data_types: Dict[str, bool], 
                           kline_intervals: list = None) -> Dict[str, bool]:
        """
        Download all enabled data types for a specific symbol and date
        """
        results = {}
        
        for data_type, enabled in data_types.items():
            if not enabled:
                continue
            
            if data_type in ['indexPriceKlines', 'klines', 'markPriceKlines', 'premiumIndexKlines']:
                # These types require intervals
                if kline_intervals:
                    for interval in kline_intervals:
                        key = f"{data_type}_{interval}"
                        results[key] = self.download_file(symbol, data_type, date, interval)
                else:
                    self.logger.warning(f"No intervals specified for {data_type}, skipping")
            else:
                # Simple data types without intervals
                results[data_type] = self.download_file(symbol, data_type, date)
        
        return results
    
    def close(self):
        """
        Close the session
        """
        self.session.close()