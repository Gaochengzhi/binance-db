# Binance 数据 ETL 管道

高性能的币安期货数据下载、处理和分析管道，集成优化的 DuckDB 存储系统。

## 功能特点

支持多种数据类型的批量下载（aggTrades、klines、indexPriceKlines 等），具备断点续传、自动解压、并发下载等功能。内置高性能 CSV 到 Parquet 转换工具，通过分区裁剪和内存优化实现快速查询，提供交互式菜单和性能测试套件，确保数据完整性和查询效率。

## 安装

```bash
uv sync
```


## 配置

### 数据下载配置

编辑 `config.yaml` 配置下载参数：

```yaml
# 时间范围设置
time_range:
  start_date: "2025-01-01"
  end_date: "2025-01-02"

# 要下载的数据类型
data_types:
  aggTrades: true
  klines: true
  indexPriceKlines: true
  markPriceKlines: true
  bookDepth: true
  bookTicker: true
  metrics: true
  trades: true
  premiumIndexKlines: true

# K线时间间隔
kline_intervals:
  - "1d"
  - "4h"  
  - "1h"
  - "15m"
  - "5m"
  - "1m"

# 交易对
trading_pairs:
  - "BTCUSDT"
  - "ETHUSDT"
  - "BNBUSDT"

# 下载设置
download_settings:
  max_concurrent_downloads: 5    # 并发下载数量
  retry_attempts: 3              # 失败重试次数  
  retry_delay: 2                 # 重试间隔（秒）
  rate_limit_delay: 0.1          # 请求限速间隔
  auto_extract: true             # 自动解压 ZIP 文件
  delete_zip_after_extract: true # 解压后删除 ZIP 文件
  overwrite_existing: false      # 跳过已存在文件（断点续传）
```

### ETL 工具配置

编辑 `csv2duckdb.py` 中的配置段：

```python
# ============================================================================
# 📋 用户配置区域 - 请根据你的环境修改以下路径
# ============================================================================
DATA_PATH = "/data/binance_data/binance_parquet"         # Parquet输出目录
SRC_DIR   = pathlib.Path("/data/binance_data")           # CSV源数据目录
DUCK_DB   = "/data/binance_data/binance.duckdb"          # DuckDB数据库文件
LOG_DIR   = "logs"                                       # 日志文件目录
CPU       = os.cpu_count()                               # CPU核心数

# ============================================================================
# 🧪 测试配置区域 - 性能测试参数
# ============================================================================
# 短时间范围测试 (用于全盘扫描，数据密集型)
TEST_SHORT_START = datetime(2025, 8, 1, 0, 0, tzinfo=timezone.utc)
TEST_SHORT_END = datetime(2025, 8, 2, 4, 0, tzinfo=timezone.utc)

# 长时间范围测试 (用于单符号时序分析，时间跨度大)
TEST_LONG_START = datetime(2024, 7, 29, 0, 0, tzinfo=timezone.utc) 
TEST_LONG_END = datetime(2025, 8, 1, 23, 59, tzinfo=timezone.utc)
```

## 使用方法

### 数据下载
```bash
python run.py
```

### CSV 转 DuckDB ETL 工具
```bash
# 交互式菜单
python csv2duckdb.py

# 直接命令
python csv2duckdb.py etl            # 转换 CSV 为 Parquet
python csv2duckdb.py init           # 初始化 DuckDB 视图
python csv2duckdb.py test           # 运行性能测试
python csv2duckdb.py cleanup        # 清理损坏文件
python csv2duckdb.py status         # 显示数据状态
```

## 数据结构

### 原始 CSV 数据
下载的数据存储在 `data/` 目录中：

```
data/
├── aggTrades/
│   ├── BTCUSDT/
│   │   ├── BTCUSDT-aggTrades-2025-01-01.csv
│   │   ├── BTCUSDT-aggTrades-2025-01-02.csv
│   │   └── ...
│   ├── ETHUSDT/
│   └── BNBUSDT/
├── klines/
│   ├── BTCUSDT/
│   │   ├── 1d/
│   │   │   ├── BTCUSDT-1d-2025-01-01.csv
│   │   │   └── BTCUSDT-1d-2025-01-02.csv
│   │   ├── 4h/
│   │   │   ├── BTCUSDT-4h-2025-01-01.csv
│   │   │   └── BTCUSDT-4h-2025-01-02.csv
│   │   ├── 1h/
│   │   │   ├── BTCUSDT-1h-2025-01-01.csv
│   │   │   └── BTCUSDT-1h-2025-01-02.csv
│   │   ├── 15m/
│   │   ├── 5m/
│   │   └── 1m/
│   ├── ETHUSDT/
│   └── BNBUSDT/
├── indexPriceKlines/
│   ├── BTCUSDT/
│   │   ├── 1d/
│   │   ├── 4h/
│   │   └── 1h/
│   ├── ETHUSDT/
│   └── BNBUSDT/
├── markPriceKlines/
├── premiumIndexKlines/
├── bookDepth/
├── bookTicker/
├── metrics/
└── trades/
```

### 优化后的 Parquet 数据结构
ETL 处理后，数据以分区结构组织以实现高效查询：

```
binance_parquet/
├── klines/
│   ├── interval=1d/
│   │   ├── date=2025-08-01/
│   │   │   ├── symbol=BTCUSDT.parquet
│   │   │   ├── symbol=ETHUSDT.parquet
│   │   │   └── symbol=BNBUSDT.parquet
│   │   └── date=2025-08-02/
│   ├── interval=4h/
│   │   ├── date=2025-08-01/
│   │   └── date=2025-08-02/
│   ├── interval=1h/
│   ├── interval=15m/
│   ├── interval=5m/
│   └── interval=1m/
├── indexPriceKlines/
│   ├── interval=1d/
│   │   └── date=2025-08-01/
│   ├── interval=4h/
│   └── interval=1h/
├── markPriceKlines/
├── premiumIndexKlines/
├── bookDepth/
│   └── date=2025-08-01/
│       ├── symbol=BTCUSDT.parquet
│       ├── symbol=ETHUSDT.parquet
│       └── symbol=BNBUSDT.parquet
├── bookTicker/
├── aggTrades/
├── trades/
├── metrics/
└── binance.duckdb                    # 带有优化视图的 DuckDB 数据库
```

**分区策略：**
- **按日期分区** 实现高效的时间范围查询
- **按符号组织文件** 优化单个资产分析  
- **按间隔分目录** 适用于 K线数据类型
- **ZSTD 压缩的 Parquet 格式** 实现最佳存储和查询性能

## 数据类型

- **aggTrades**: 聚合交易数据
- **klines**: 蜡烛图/K线数据  
- **indexPriceKlines**: 指数价格K线数据
- **markPriceKlines**: 标记价格K线数据
- **bookDepth**: 订单簿深度快照
- **bookTicker**: 最优买卖价格和数量
- **metrics**: 交易指标和统计数据
- **trades**: 单笔交易数据
- **premiumIndexKlines**: 溢价指数K线数据

## CSV 文件格式

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

## ETL 性能特性

### 查询优化
- **分区裁剪**: 只读取相关的日期/时间间隔分区
- **内存优化**: 8GB 内存限制和多线程处理
- **对象缓存**: 启用 DuckDB 内置查询结果缓存
- **直接文件访问**: 绕过视图以获得最大性能

### 性能测试模式
ETL 工具包含 4 种查询模式的综合性能测试：

| 查询类型           | 描述                     | 使用场景       |
| ------------------ | ------------------------ | -------------- |
| **全盘短时间扫描** | 短时间窗口内扫描所有符号 | 数据密集型分析 |
| **单符号长时序**   | 单个符号的长时间序列     | 时间序列分析   |
| **热门符号扫描**   | 短时间内的多个热门符号   | 重点市场分析   |
| **交易量统计**     | 聚合交易量排名           | 市场概览       |

### DuckDB 查询 API
```python
from csv2duckdb import BinanceDuck

db = BinanceDuck()

# 带分区裁剪的时间范围扫描
data = db.scan_15m_optimized(start_ts, end_ts, symbols=['BTCUSDT', 'ETHUSDT'])

# 单符号时间序列  
series = db.scan_single_symbol('BTCUSDT', start_ts, end_ts)

# 聚合统计
stats = db.scan_aggregated(start_ts, end_ts, symbols=['BTCUSDT'])

# 交易量排名
top_vol = db.scan_top_volume(start_ts, end_ts, limit=10)
```

