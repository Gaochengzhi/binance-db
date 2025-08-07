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

# 可选K线时间间隔
kline_intervals:
  - "1d"
  - "4h"  
  - "1h"
  - "15m"
  - "5m"
  - "1m"

# 交易对
trading_pairs:
# 留空就是下载所有
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
├── bookDepth/
│   ├── BTCUSDT/
│   │   ├── BTCUSDT-bookDepth-2025-01-01.csv
│   │   ├── BTCUSDT-bookDepth-2025-01-02.csv
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
│   │   │   └── ...
│   ├── ETHUSDT/
│   └── BNBUSDT/
├── indexPriceKlines/
│   ├── BTCUSDT/
│   │   ├── 1d/
│   │   ├── 4h/
│   │   └── 1h/
│   │   └── 15m/
│   ├── ETHUSDT/
│   └── BNBUSDT/
├── markPriceKlines/
├── premiumIndexKlines/
├── metrics/
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

所有CSV文件采用横向表格格式，每行为一条记录。以下是各数据类型的详细字段说明：

### K线数据 (klines/indexPriceKlines/markPriceKlines/premiumIndexKlines)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| open_time | long | 开盘时间戳（毫秒） |
| open | decimal | 开盘价格 |
| high | decimal | 最高价格 |
| low | decimal | 最低价格 |
| close | decimal | 收盘价格 |
| volume | decimal | 成交量 |
| close_time | long | 收盘时间戳（毫秒） |
| quote_volume | decimal | 成交额（报价资产） |
| count | int | 成交笔数 |
| taker_buy_volume | decimal | 主动买入成交量（基础资产） |
| taker_buy_quote_volume | decimal | 主动买入成交额（报价资产） |
| ignore | int | 忽略字段（通常为0） |

### 聚合交易数据 (aggTrades)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| agg_trade_id | long | 聚合交易ID |
| price | decimal | 成交价格 |
| quantity | decimal | 成交数量 |
| first_trade_id | long | 首个交易ID |
| last_trade_id | long | 末个交易ID |
| transact_time | long | 成交时间戳（毫秒） |
| is_buyer_maker | boolean | 买方是否为挂单方 |

### 单笔交易数据 (trades)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| id | long | 交易ID |
| price | decimal | 成交价格 |
| qty | decimal | 成交数量 |
| quote_qty | decimal | 成交金额 |
| time | long | 成交时间戳（毫秒） |
| is_buyer_maker | boolean | 买方是否为挂单方 |

### 最优挂单 (bookTicker)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| update_id | long | 更新ID |
| best_bid_price | decimal | 最优买价 |
| best_bid_qty | decimal | 最优买量 |
| best_ask_price | decimal | 最优卖价 |
| best_ask_qty | decimal | 最优卖量 |
| transaction_time | long | 交易时间戳（毫秒） |
| event_time | long | 事件时间戳（毫秒） |

### 订单簿深度 (bookDepth)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| timestamp | datetime | 时间戳 |
| percentage | float | 价格偏离百分比 |
| depth | decimal | 累计挂单数量 |
| notional | decimal | 累计挂单金额 |

### 交易指标 (metrics)

| 字段名 | 数据类型 | 说明 |
|--------|----------|------|
| create_time | datetime | 创建时间 |
| symbol | string | 交易对符号 |
| sum_open_interest | decimal | 总持仓量 |
| sum_open_interest_value | decimal | 总持仓价值 |
| count_toptrader_long_short_ratio | decimal | 大户多空比例计数 |
| sum_toptrader_long_short_ratio | decimal | 大户多空比例总和 |
| count_long_short_ratio | decimal | 账户多空比例计数 |
| sum_taker_long_short_vol_ratio | decimal | 主动成交多空比例总和 |

## ETL 性能特性

### 查询优化
- **分区裁剪**: 只读取相关的日期/时间间隔分区
- **内存优化**: 8GB 内存限制和多线程处理
- **对象缓存**: 启用 DuckDB 内置查询结果缓存
- **直接文件访问**: 绕过视图以获得最大性能



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

## 数据更新策略

### 增量数据更新

当新的CSV数据到达时，ETL工具支持多种数据更新方式：

#### 1. 自动增量更新（推荐）
```bash
# 运行ETL转换，自动跳过已存在的文件
python csv2duckdb.py etl
```

#### 2. 强制覆盖更新
如需重新处理某些文件，手动删除对应的Parquet文件后重新运行ETL：
```bash
# 删除特定日期的数据
rm -rf /data/binance_data/binance_parquet/klines/interval=15m/date=2025-08-01/

# 重新转换
python csv2duckdb.py etl
```

#### 3. 清理损坏文件
定期运行清理命令确保数据完整性：
```bash
python csv2duckdb.py cleanup
```

#### 4. 更新DuckDB视图
当添加新的数据类型或修改分区结构后，需要重新初始化DuckDB视图：
```bash
python csv2duckdb.py init
```

### 数据一致性保证

- **原子性写入**: 使用临时文件确保写入过程的原子性
- **完整性检查**: 自动验证Parquet文件完整性，删除损坏文件
- **断点续传**: 跳过已存在且有效的文件，支持中断后继续处理
- **分区管理**: 按日期和符号分区，便于增量更新和查询优化

### 性能基准
- **查询优化**: 比原始基于视图的查询快 10-50 倍
- **分区裁剪**: 只扫描相关文件而非完整数据集
- **内存效率**: 通过受控内存使用处理大型数据集
- **并行处理**: 多线程 ETL 转换和并发查询

## 许可证

本项目采用 **MIT License with Commercial Use Restriction** 许可证：

- ✅ **个人使用**: 完全免费，包括学习、研究、个人项目
- ✅ **学术研究**: 支持教育机构和非营利研究
- ✅ **开源贡献**: 欢迎社区参与和改进
- ❌ **商业使用**: 组织和公司需要获得明确授权

详细条款请参阅 [LICENSE](LICENSE) 文件。如需商业使用，请联系作者获取授权。

