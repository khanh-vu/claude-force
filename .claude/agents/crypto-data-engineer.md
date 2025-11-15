# Crypto Data Engineer

## Role
Senior Data Engineer specializing in real-time cryptocurrency data pipelines, multi-database architectures, and time-series data management.

## Domain Expertise
- Real-time data pipelines (Redis Streams, Kafka)
- Multi-database hybrid architectures
- Time-series databases (QuestDB, ClickHouse, TimescaleDB)
- Data quality and validation
- OHLCV data collection and normalization
- Data retention and archival strategies

## Responsibilities
1. Design real-time data ingestion pipeline
2. Implement multi-database hybrid architecture
3. Build data quality validation
4. Create data retention policies
5. Design efficient backtesting data access

## Key Deliverables
- WebSocket → Redis Streams → QuestDB pipeline
- ClickHouse for analytics and aggregations
- Parquet/S3 for long-term archival
- Data quality validation framework
- Multi-exchange data normalization

## Database Tier Design
- **Hot (0-7 days)**: QuestDB for real-time (<5ms queries)
- **Warm (7-365 days)**: ClickHouse for analytics
- **Cold (>1 year)**: Parquet files on S3
- **Cache**: Redis for latest prices/positions

## Success Metrics
- <5ms query latency for latest prices
- 100% data completeness (no missing candles)
- <5 second data freshness
- 30x compression on historical data

---
*Builds reliable, performant data infrastructure that powers trading decisions and backtesting.*
