# Binance Public Data Downloader

A Python script system for batch downloading Binance public futures data with automatic extraction and resume functionality.

## Features

- Multiple data types: aggTrades, klines, indexPriceKlines, markPriceKlines, etc.
- Resume from breakpoint
- Automatic ZIP file extraction
- Concurrent downloads for efficiency
- Flexible configuration management
- Comprehensive error logging and rate limiting

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure download parameters:

```yaml
# Time range settings
time_range:
  start_date: "2025-01-01"
  end_date: "2025-01-02"

# Data types to download
data_types:
  aggTrades: true
  klines: true
  indexPriceKlines: true

# Klines intervals
kline_intervals:
  - "1d"
  - "4h"
  - "1h"
  - "15m"

# Trading pairs
trading_pairs:
  - "BTCUSDT"
```

## Usage

```bash
python run.py
```

## Data Structure

Downloaded data is stored in the `data/` directory:

```
data/
├── aggTrades/
│   └── BTCUSDT/
│       └── BTCUSDT-aggTrades-2025-01-01.csv
├── klines/
│   └── BTCUSDT/
│       ├── 1d/
│       ├── 4h/
│       └── 1h/
└── indexPriceKlines/
    └── BTCUSDT/
        ├── 1d/
        └── 4h/
```

## Data Types

- **aggTrades**: Aggregate trade data
- **klines**: Candlestick/Kline data  
- **indexPriceKlines**: Index price kline data
- **markPriceKlines**: Mark price kline data
- **bookDepth**: Order book depth snapshots
- **bookTicker**: Best bid/ask price and quantity
- **metrics**: Trading metrics and statistics
- **trades**: Individual trade data
- **premiumIndexKlines**: Premium index kline data

## CSV Headers

### aggTrades
```
agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker
```

### klines/indexPriceKlines/markPriceKlines/premiumIndexKlines
```
open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore
```

### trades
```
id,price,qty,quote_qty,time,is_buyer_maker
```

### bookTicker
```
update_id,best_bid_price,best_bid_qty,best_ask_price,best_ask_qty,transaction_time,event_time
```

### bookDepth
```
timestamp,percentage,depth,notional
```

### metrics
```
create_time,symbol,sum_open_interest,sum_open_interest_value,count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,count_long_short_ratio,sum_taker_long_short_vol_ratio
```

## Download Settings

- **max_concurrent_downloads**: Control parallel downloads
- **retry_attempts**: Number of retry attempts on failure
- **retry_delay**: Delay between retries (seconds)
- **rate_limit_delay**: Delay between requests to respect API limits
- **auto_extract**: Automatically extract ZIP files
- **delete_zip_after_extract**: Clean up ZIP files after extraction
- **overwrite_existing**: Skip existing files for resume functionality