# n8n Video Automation: Visual Diagrams

**Document**: System Architecture & Workflow Diagrams
**Created**: 2025-11-17
**Purpose**: Visual reference for workflow structure, system architecture, and data flow

---

## Table of Contents

1. [n8n Workflow Diagram](#1-n8n-workflow-diagram)
2. [System Architecture - Current (Monolithic)](#2-system-architecture---current-monolithic)
3. [System Architecture - Target (Microservices)](#3-system-architecture---target-microservices)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Deployment Architecture](#5-deployment-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Cost Optimization Flow](#7-cost-optimization-flow)
8. [Phase Evolution Diagram](#8-phase-evolution-diagram)

---

## 1. n8n Workflow Diagram

### 1.1 Complete 12-Phase Workflow

```mermaid
graph TB
    Start([CRON Trigger<br/>Every 6 hours]) --> Phase1[Phase 1: Fetch Trending Videos]

    Phase1 --> YT[YouTube API<br/>mostPopular]
    Phase1 --> TT[TikTok Scraper<br/>Apify ⚠️]
    Phase1 --> FB[Facebook Pages<br/>Optional]

    YT --> Merge[Merge Results]
    TT --> Merge
    FB --> Merge

    Merge --> Phase2[Phase 2: Calculate<br/>Trend Scores]
    Phase2 --> Score{Engagement Rate<br/>+ Velocity Scoring}

    Score --> Phase3[Phase 3: Extract Topics<br/>NLP Processing]
    Phase3 --> NLP[spaCy/Hugging Face<br/>Entity Extraction]

    NLP --> Phase4[Phase 4: Filter &<br/>Deduplicate]
    Phase4 --> DB1[(Database<br/>Lookup)]
    DB1 --> Top[Select Top 3-5 Trends]

    Top --> Phase5[Phase 5: Transform Topics<br/>3-Layer Framework]
    Phase5 --> L1[Layer 1: Topic Translation]
    L1 --> L2[Layer 2: Format Modification]
    L2 --> L3[Layer 3: Style Transformation]

    L3 --> Phase6[Phase 6: Generate<br/>AI Prompts]
    Phase6 --> Prompt[Build Veo 3.1 Prompt<br/>with Uniqueness Constraints]

    Prompt --> Phase7[Phase 7: Generate Videos<br/>Veo 3.1]
    Phase7 --> VeoInit[Initiate Generation<br/>POST to Vertex AI]
    VeoInit --> Wait[Wait 30s]
    Wait --> Poll[Check Status]
    Poll --> Done{Done?}
    Done -->|No| Wait
    Done -->|Yes| GCS[Extract GCS URI]

    GCS --> Phase8[Phase 8: Download Video<br/>from GCS]
    Phase8 --> Download[HTTP Download<br/>MP4 File]

    Download --> Phase9[Phase 9: Quality Control]
    Phase9 --> QC1[Check File Size]
    QC1 --> QC2[Check Format]
    QC2 --> QC3[Optional: Plagiarism Check]
    QC3 --> QC4[Manual Approval Gate]

    QC4 --> Approve{Approved?}
    Approve -->|No| Reject([Reject & Log])
    Approve -->|Yes| Phase10[Phase 10: Platform-Specific<br/>Formatting]

    Phase10 --> YTFormat[YouTube: Keep 16:9]
    Phase10 --> TTFormat[TikTok: Crop 9:16<br/>ffmpeg]
    Phase10 --> IGFormat[Instagram: Crop 9:16<br/>Max 90s]

    YTFormat --> Phase11[Phase 11: Publish to Platforms]
    TTFormat --> Phase11
    IGFormat --> Phase11

    Phase11 --> PubYT[YouTube<br/>videos.insert OAuth2]
    Phase11 --> PubTT[TikTok<br/>3-Phase Upload API]
    Phase11 --> PubIG[Instagram/Facebook<br/>Graph API]

    PubYT --> Phase12[Phase 12: Log Results]
    PubTT --> Phase12
    PubIG --> Phase12

    Phase12 --> DB2[(Store in Database<br/>Video ID, Platform, Timestamp)]
    DB2 --> Notify[Send Notification<br/>Slack/Email]
    Notify --> Update[Update Processed<br/>Topics List]
    Update --> End([End])

    style Phase1 fill:#e1f5ff
    style Phase2 fill:#e1f5ff
    style Phase3 fill:#e1f5ff
    style Phase4 fill:#fff3e0
    style Phase5 fill:#fff3e0
    style Phase6 fill:#fff3e0
    style Phase7 fill:#f3e5f5
    style Phase8 fill:#f3e5f5
    style Phase9 fill:#e8f5e9
    style Phase10 fill:#e8f5e9
    style Phase11 fill:#fce4ec
    style Phase12 fill:#fce4ec
    style TT fill:#ffcdd2
    style Start fill:#c8e6c9
    style End fill:#c8e6c9
    style Reject fill:#ffcdd2
```

### 1.2 Workflow Phases Legend

| Phase | Color | Purpose | Duration | Critical Path |
|-------|-------|---------|----------|---------------|
| **1-3** | 🔵 Blue | Trend Detection & Analysis | 2-5 min | ✅ Yes |
| **4-6** | 🟡 Orange | Content Transformation | 1-2 min | ✅ Yes |
| **7-8** | 🟣 Purple | AI Video Generation | 5-10 min | ✅ Yes |
| **9-10** | 🟢 Green | Quality Control & Formatting | 2-5 min | ⚠️ Blocking |
| **11-12** | 🔴 Pink | Publishing & Logging | 3-8 min | ✅ Yes |

**Total Pipeline Duration**: 13-30 minutes per video

---

## 2. System Architecture - Current (Monolithic)

### 2.1 Current State (As Documented in Guide)

```mermaid
graph TB
    subgraph "External APIs"
        YT[YouTube Data API<br/>v3]
        Apify[Apify TikTok<br/>Scraper ⚠️]
        Veo[Google Veo 3.1<br/>Vertex AI]
        YTUpload[YouTube Upload<br/>OAuth2]
        TTUpload[TikTok Content<br/>Posting API]
        FBUpload[Facebook/Instagram<br/>Graph API]
    end

    subgraph "n8n Monolith"
        Cron[Cron Trigger]
        HTTP1[HTTP Request Nodes]
        Func[Function Nodes<br/>Business Logic]
        Code[Code Nodes<br/>Python/spaCy]
        Wait[Wait Nodes]
        IF[IF Nodes]
        Execute[Execute Command<br/>ffmpeg ⚠️]
    end

    subgraph "Storage"
        GCS[(Google Cloud<br/>Storage)]
        DB[(Database<br/>Optional PostgreSQL)]
    end

    subgraph "Monitoring"
        Slack[Slack<br/>Notifications]
        Email[Email<br/>Alerts]
    end

    Cron --> HTTP1
    HTTP1 --> YT
    HTTP1 --> Apify

    YT --> Func
    Apify --> Func

    Func --> Code
    Code --> Func

    Func --> HTTP1
    HTTP1 --> Veo

    Veo --> Wait
    Wait --> HTTP1
    HTTP1 --> IF
    IF -->|Not Done| Wait
    IF -->|Done| GCS

    GCS --> Execute
    Execute --> HTTP1

    HTTP1 --> YTUpload
    HTTP1 --> TTUpload
    HTTP1 --> FBUpload

    YTUpload --> DB
    TTUpload --> DB
    FBUpload --> DB

    DB --> Slack
    DB --> Email

    style Cron fill:#90caf9
    style Func fill:#ffcc80
    style Code fill:#ffcc80
    style Execute fill:#ffcdd2
    style Apify fill:#ffcdd2
    style DB fill:#a5d6a7
    style GCS fill:#a5d6a7
```

### 2.2 Critical Issues in Current Architecture

```mermaid
graph LR
    subgraph "⚠️ CRITICAL ISSUES"
        I1[❌ SQL Injection<br/>String Interpolation]
        I2[❌ Command Injection<br/>Unsanitized ffmpeg]
        I3[❌ Single Point of Failure<br/>n8n Instance]
        I4[❌ No State Persistence<br/>Loss on Restart]
        I5[❌ Sequential Execution<br/>Max 12 videos/day]
        I6[❌ Synchronous Polling<br/>Blocks for 5-10 min]
        I7[❌ Hardcoded Credentials<br/>Environment Variables]
        I8[❌ TikTok ToS Violation<br/>Apify Scraping]
    end

    style I1 fill:#f44336,color:#fff
    style I2 fill:#f44336,color:#fff
    style I3 fill:#ff5722,color:#fff
    style I4 fill:#ff5722,color:#fff
    style I5 fill:#ff9800
    style I6 fill:#ff9800
    style I7 fill:#f44336,color:#fff
    style I8 fill:#f44336,color:#fff
```

---

## 3. System Architecture - Target (Microservices)

### 3.1 Phase 3-4 Target Architecture (Event-Driven)

```mermaid
graph TB
    subgraph "API Gateway Layer"
        Gateway[Cloud Load Balancer<br/>Global]
        CDN[Cloud CDN<br/>Video Delivery]
    end

    subgraph "Microservices (Cloud Run)"
        TrendSvc[Trend Service<br/>Detect & Score]
        TransformSvc[Transformation Service<br/>GPT-4 Powered]
        VideoSvc[Video Service<br/>Veo Orchestration]
        PublisherSvc[Publisher Service<br/>Multi-Platform]
        AnalyticsSvc[Analytics Service<br/>Performance Tracking]
        AdminSvc[Admin Service<br/>Dashboard API]
    end

    subgraph "Message Queue"
        PubSub1[Pub/Sub: trend-detected]
        PubSub2[Pub/Sub: content-transformed]
        PubSub3[Pub/Sub: video-ready]
        PubSub4[Pub/Sub: published]
    end

    subgraph "Data Layer"
        PostgreSQL[(Cloud SQL<br/>PostgreSQL)]
        Redis[(Memorystore<br/>Redis Cache)]
        BigQuery[(BigQuery<br/>Analytics Warehouse)]
        GCS[(Cloud Storage<br/>Videos)]
    end

    subgraph "External Services"
        Veo[Vertex AI<br/>Veo 3.1]
        OpenAI[OpenAI<br/>GPT-4]
        YouTube[YouTube API]
        TikTok[TikTok API]
        Facebook[Facebook Graph API]
    end

    subgraph "Monitoring & Security"
        Prometheus[Prometheus<br/>Metrics]
        Grafana[Grafana<br/>Dashboards]
        CloudLogging[Cloud Logging<br/>Structured Logs]
        SecretMgr[Secret Manager<br/>Credentials]
        IAM[Cloud IAM<br/>Access Control]
    end

    subgraph "Orchestration"
        CloudScheduler[Cloud Scheduler<br/>Cron Jobs]
        CloudTasks[Cloud Tasks<br/>Background Jobs]
    end

    Gateway --> TrendSvc
    Gateway --> AdminSvc

    CloudScheduler --> TrendSvc

    TrendSvc --> YouTube
    TrendSvc --> TikTok
    TrendSvc --> PostgreSQL
    TrendSvc --> Redis
    TrendSvc --> PubSub1

    PubSub1 --> TransformSvc
    TransformSvc --> OpenAI
    TransformSvc --> PostgreSQL
    TransformSvc --> PubSub2

    PubSub2 --> VideoSvc
    VideoSvc --> Veo
    VideoSvc --> GCS
    VideoSvc --> PostgreSQL
    VideoSvc --> CloudTasks
    VideoSvc --> PubSub3

    PubSub3 --> PublisherSvc
    PublisherSvc --> YouTube
    PublisherSvc --> TikTok
    PublisherSvc --> Facebook
    PublisherSvc --> PostgreSQL
    PublisherSvc --> PubSub4

    PubSub4 --> AnalyticsSvc
    AnalyticsSvc --> BigQuery

    AdminSvc --> PostgreSQL
    AdminSvc --> BigQuery

    CDN --> GCS

    TrendSvc -.-> Prometheus
    TransformSvc -.-> Prometheus
    VideoSvc -.-> Prometheus
    PublisherSvc -.-> Prometheus
    AnalyticsSvc -.-> Prometheus

    Prometheus --> Grafana

    TrendSvc -.-> CloudLogging
    TransformSvc -.-> CloudLogging
    VideoSvc -.-> CloudLogging
    PublisherSvc -.-> CloudLogging

    TrendSvc --> SecretMgr
    TransformSvc --> SecretMgr
    VideoSvc --> SecretMgr
    PublisherSvc --> SecretMgr

    SecretMgr --> IAM

    style TrendSvc fill:#81c784
    style TransformSvc fill:#64b5f6
    style VideoSvc fill:#ba68c8
    style PublisherSvc fill:#ff8a65
    style AnalyticsSvc fill:#ffd54f
    style AdminSvc fill:#90a4ae
    style Gateway fill:#4caf50
    style SecretMgr fill:#f44336,color:#fff
```

### 3.2 Service Responsibilities

| Service | Purpose | Technology | Scaling |
|---------|---------|-----------|---------|
| **Trend Service** | Poll APIs, score trends, deduplicate | FastAPI + Redis | 2-10 instances |
| **Transformation Service** | GPT-4 content transformation | FastAPI + OpenAI | 1-5 instances |
| **Video Service** | Veo orchestration, webhook handling | FastAPI + Cloud Tasks | 2-20 instances |
| **Publisher Service** | Multi-platform uploads, retry logic | FastAPI + Circuit Breaker | 2-15 instances |
| **Analytics Service** | Performance tracking, BigQuery ETL | FastAPI + BigQuery | 1-3 instances |
| **Admin Service** | Dashboard API, manual controls | FastAPI + WebSocket | 1-5 instances |

---

## 4. Data Flow Diagram

### 4.1 Complete Data Flow

```mermaid
sequenceDiagram
    participant Scheduler as Cloud Scheduler
    participant TrendSvc as Trend Service
    participant DB as PostgreSQL
    participant PubSub as Pub/Sub
    participant TransformSvc as Transform Service
    participant GPT4 as OpenAI GPT-4
    participant VideoSvc as Video Service
    participant Veo as Vertex AI Veo
    participant GCS as Cloud Storage
    participant QC as Quality Control
    participant PubSvc as Publisher Service
    participant Platforms as YouTube/TikTok/Instagram
    participant Analytics as Analytics Service
    participant BQ as BigQuery

    Scheduler->>TrendSvc: Trigger (every 6 hours)
    activate TrendSvc

    TrendSvc->>DB: Check last processed trends
    TrendSvc->>DB: Fetch trending videos (YouTube/TikTok)
    TrendSvc->>DB: Calculate trend scores
    TrendSvc->>DB: Deduplicate (fingerprint check)
    TrendSvc->>DB: Store top 3-5 trends

    TrendSvc->>PubSub: Publish "trend-detected" event
    deactivate TrendSvc

    PubSub->>TransformSvc: Consume "trend-detected"
    activate TransformSvc

    TransformSvc->>GPT4: Transform topic (3-layer framework)
    GPT4-->>TransformSvc: Transformed concept (JSON)
    TransformSvc->>GPT4: Generate Veo prompt
    GPT4-->>TransformSvc: Optimized prompt

    TransformSvc->>DB: Store transformation
    TransformSvc->>PubSub: Publish "content-transformed"
    deactivate TransformSvc

    PubSub->>VideoSvc: Consume "content-transformed"
    activate VideoSvc

    VideoSvc->>Veo: Initiate video generation
    Veo-->>VideoSvc: Operation ID
    VideoSvc->>DB: Store operation (status: generating)

    Note over VideoSvc,Veo: Webhook callback (3-5 minutes)

    Veo->>VideoSvc: Webhook: Generation complete
    VideoSvc->>GCS: Check video URI
    GCS-->>VideoSvc: Video metadata

    VideoSvc->>QC: Run quality control pipeline
    activate QC
    QC->>QC: Technical validation (resolution, duration)
    QC->>QC: CLIP similarity check (prompt fidelity)
    QC->>QC: Visual similarity (copyright check)
    QC->>QC: Brand safety (Video Intelligence API)
    QC-->>VideoSvc: Quality report
    deactivate QC

    alt Quality Check Passed
        VideoSvc->>DB: Update (status: ready)
        VideoSvc->>PubSub: Publish "video-ready"
    else Quality Check Failed
        VideoSvc->>DB: Update (status: failed)
        VideoSvc->>Analytics: Log failure
    end

    deactivate VideoSvc

    PubSub->>PubSvc: Consume "video-ready"
    activate PubSvc

    PubSvc->>GCS: Download video
    GCS-->>PubSvc: Video file

    par Publish to all platforms
        PubSvc->>Platforms: Upload to YouTube (16:9)
        PubSvc->>Platforms: Upload to TikTok (9:16)
        PubSvc->>Platforms: Upload to Instagram (9:16)
    end

    Platforms-->>PubSvc: Platform video IDs
    PubSvc->>DB: Store publications (with idempotency keys)
    PubSvc->>PubSub: Publish "published"
    deactivate PubSvc

    PubSub->>Analytics: Consume "published"
    activate Analytics
    Analytics->>DB: Fetch video metadata
    Analytics->>BQ: Load to BigQuery
    Analytics->>Platforms: Fetch initial analytics (24h later)
    Platforms-->>Analytics: Views, engagement
    Analytics->>BQ: Update with performance data
    deactivate Analytics
```

### 4.2 Error Handling Flow

```mermaid
graph TB
    Start[Service Execution] --> Try{Try Operation}

    Try -->|Success| Log[Log Success]
    Log --> Metric[Update Metrics]
    Metric --> Done([Continue Pipeline])

    Try -->|Error| Classify{Error Type?}

    Classify -->|Transient| Retry{Retry Count<br/>&lt; Max?}
    Classify -->|Permanent| DLQ[Send to Dead<br/>Letter Queue]

    Retry -->|Yes| Backoff[Exponential Backoff<br/>1s, 2s, 4s, 8s]
    Backoff --> Try

    Retry -->|No| Circuit{Circuit Breaker<br/>Triggered?}

    Circuit -->|Yes| Fallback[Execute Fallback<br/>Logic]
    Circuit -->|No| DLQ

    Fallback --> Alert[Send Alert<br/>Slack/PagerDuty]
    DLQ --> Alert

    Alert --> LogError[Log Error with<br/>Correlation ID]
    LogError --> Failed([Mark as Failed])

    style Try fill:#90caf9
    style Retry fill:#ffcc80
    style Circuit fill:#ff8a65
    style DLQ fill:#ffcdd2
    style Failed fill:#f44336,color:#fff
    style Done fill:#81c784
```

---

## 5. Deployment Architecture

### 5.1 Multi-Region Deployment (Phase 4)

```mermaid
graph TB
    subgraph "Global"
        GLB[Global Load Balancer<br/>Cloud Armor]
        CDN[Cloud CDN<br/>Multi-Region]
    end

    subgraph "US Region (us-central1)"
        subgraph "GKE Cluster US"
            K8S_US[Kubernetes<br/>3-50 nodes]
            Istio_US[Istio Service Mesh]
        end
        SQL_US[(Cloud SQL Primary<br/>PostgreSQL)]
        GCS_US[(Cloud Storage US)]
        Redis_US[(Memorystore US)]
    end

    subgraph "EU Region (europe-west1)"
        subgraph "GKE Cluster EU"
            K8S_EU[Kubernetes<br/>2-20 nodes]
            Istio_EU[Istio Service Mesh]
        end
        SQL_EU[(Cloud SQL Replica<br/>Read-Only)]
        GCS_EU[(Cloud Storage EU)]
        Redis_EU[(Memorystore EU)]
    end

    subgraph "APAC Region (asia-northeast1)"
        subgraph "GKE Cluster APAC"
            K8S_APAC[Kubernetes<br/>2-20 nodes]
            Istio_APAC[Istio Service Mesh]
        end
        SQL_APAC[(Cloud SQL Replica<br/>Read-Only)]
        GCS_APAC[(Cloud Storage APAC)]
        Redis_APAC[(Memorystore APAC)]
    end

    subgraph "Global Services"
        Veo[Vertex AI Veo<br/>us-central1 only]
        BQ[(BigQuery<br/>Multi-Region)]
        SecretMgr[Secret Manager<br/>Global]
    end

    GLB --> K8S_US
    GLB --> K8S_EU
    GLB --> K8S_APAC

    K8S_US --> SQL_US
    K8S_EU --> SQL_EU
    K8S_APAC --> SQL_APAC

    SQL_US -->|Replication| SQL_EU
    SQL_US -->|Replication| SQL_APAC

    K8S_US --> GCS_US
    K8S_EU --> GCS_EU
    K8S_APAC --> GCS_APAC

    CDN --> GCS_US
    CDN --> GCS_EU
    CDN --> GCS_APAC

    K8S_US --> Veo
    K8S_EU --> Veo
    K8S_APAC --> Veo

    K8S_US --> BQ
    K8S_EU --> BQ
    K8S_APAC --> BQ

    K8S_US --> SecretMgr
    K8S_EU --> SecretMgr
    K8S_APAC --> SecretMgr

    style GLB fill:#4caf50
    style SQL_US fill:#2196f3
    style SQL_EU fill:#64b5f6
    style SQL_APAC fill:#64b5f6
    style K8S_US fill:#ff9800
    style K8S_EU fill:#ffb74d
    style K8S_APAC fill:#ffb74d
```

### 5.2 Network Topology

```mermaid
graph TB
    subgraph "Public Internet"
        Users[Global Users]
        APIs[External APIs]
    end

    subgraph "GCP VPC (10.0.0.0/8)"
        subgraph "Public Subnet (10.1.0.0/16)"
            LB[Load Balancer<br/>10.1.1.10]
            NAT[Cloud NAT Gateway]
        end

        subgraph "Private Subnet - Services (10.2.0.0/16)"
            Pods[Kubernetes Pods<br/>10.2.x.x]
        end

        subgraph "Private Subnet - Data (10.3.0.0/16)"
            SQL[(Cloud SQL<br/>10.3.1.10)]
            Redis[(Redis<br/>10.3.2.10)]
        end

        subgraph "Managed Services (Private IP)"
            GCS[Cloud Storage<br/>Private Google Access]
            Veo[Vertex AI<br/>Private Google Access]
            BQ[BigQuery<br/>Private Google Access]
        end
    end

    Users -->|HTTPS| LB
    LB --> Pods

    Pods --> SQL
    Pods --> Redis
    Pods --> GCS
    Pods --> Veo
    Pods --> BQ

    Pods -->|Egress via NAT| NAT
    NAT --> APIs

    style Users fill:#90caf9
    style LB fill:#4caf50
    style Pods fill:#ff9800
    style SQL fill:#2196f3
    style Redis fill:#f44336
    style NAT fill:#9e9e9e
```

---

## 6. Security Architecture

### 6.1 Security Layers

```mermaid
graph TB
    subgraph "Layer 1: Network Security"
        CloudArmor[Cloud Armor<br/>DDoS Protection]
        VPC[VPC Firewall Rules]
        PrivateIP[Private IP Ranges]
    end

    subgraph "Layer 2: Identity & Access"
        IAM[Cloud IAM<br/>Least Privilege]
        ServiceAccounts[Service Accounts<br/>Per Microservice]
        Workload[Workload Identity<br/>Pod-to-GCP Auth]
    end

    subgraph "Layer 3: Data Protection"
        SecretMgr[Secret Manager<br/>Encrypted Credentials]
        CMEK[Customer-Managed<br/>Encryption Keys]
        TLS[TLS 1.3<br/>In-Transit Encryption]
    end

    subgraph "Layer 4: Application Security"
        InputVal[Input Validation<br/>Allowlists]
        Parameterized[Parameterized Queries<br/>No SQL Injection]
        CSP[Content Security Policy]
        RateLimit[Rate Limiting<br/>Per User/IP]
    end

    subgraph "Layer 5: Monitoring & Response"
        SIEM[Cloud Logging<br/>SIEM Integration]
        Alerts[Security Alerts<br/>PagerDuty]
        Audit[Audit Logs<br/>Immutable Storage]
    end

    CloudArmor --> VPC
    VPC --> PrivateIP

    IAM --> ServiceAccounts
    ServiceAccounts --> Workload

    SecretMgr --> CMEK
    CMEK --> TLS

    InputVal --> Parameterized
    Parameterized --> CSP
    CSP --> RateLimit

    SIEM --> Alerts
    Alerts --> Audit

    style CloudArmor fill:#4caf50
    style SecretMgr fill:#f44336,color:#fff
    style Parameterized fill:#81c784
    style Audit fill:#2196f3
```

### 6.2 Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant User as User/Client
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant IAM as Cloud IAM
    participant Service as Microservice
    participant Secret as Secret Manager
    participant DB as Database

    User->>Gateway: Request with JWT
    Gateway->>Auth: Validate JWT
    Auth->>IAM: Check permissions
    IAM-->>Auth: Permission granted
    Auth-->>Gateway: Token valid

    Gateway->>Service: Forward request (with correlation ID)

    Service->>IAM: Get service account token
    IAM-->>Service: Short-lived token

    Service->>Secret: Fetch API credentials
    Secret->>IAM: Verify service identity
    IAM-->>Secret: Identity verified
    Secret-->>Service: Encrypted credentials

    Service->>DB: Query with parameterized SQL
    DB-->>Service: Result

    Service-->>Gateway: Response
    Gateway-->>User: JSON response

    Note over Service,DB: All queries use<br/>prepared statements
```

---

## 7. Cost Optimization Flow

### 7.1 Budget Control Decision Tree

```mermaid
graph TB
    Start[Video Generation Request] --> Check{Check Monthly<br/>Budget}

    Check -->|Budget OK| ScoreCheck{Trend Score?}
    Check -->|Budget >90%| Priority{High Priority?}
    Check -->|Budget ≥100%| Pause[Pause All<br/>Workflows]

    Pause --> Alert1[Send Critical Alert]
    Alert1 --> End1([Request Rejected])

    Priority -->|Yes & Score >100K| Allow[Allow Generation]
    Priority -->|No| End2([Request Queued])

    ScoreCheck -->|Score >100K| ModelSelect{Select Model}
    ScoreCheck -->|Score 50-100K| Fast[Use Fast Model<br/>$1.20]
    ScoreCheck -->|Score <50K| Duration{Adjust Duration?}

    Duration -->|Yes| Short[5-second video<br/>$0.75]
    Duration -->|No| Fast

    ModelSelect -->|Budget High| Standard[Use Standard<br/>$3.20]
    ModelSelect -->|Budget Medium| Fast

    Allow --> Generate[Generate Video]
    Fast --> Generate
    Short --> Generate
    Standard --> Generate

    Generate --> QC{Quality<br/>Check?}

    QC -->|Pass| Publish[Publish]
    QC -->|Fail| Retry{Retry Count<br/>&lt; 2?}

    Retry -->|Yes| Regenerate[Regenerate with<br/>Simpler Prompt]
    Retry -->|No| Waste[Mark as Failed<br/>Cost: Sunk]

    Regenerate --> Generate

    Publish --> Track[Track Cost<br/>to Database]
    Track --> UpdateBudget[Update Budget<br/>Utilization]
    UpdateBudget --> End3([Success])

    Waste --> Alert2[Alert: Wasted Cost]
    Alert2 --> End4([Failed])

    style Start fill:#90caf9
    style Check fill:#ffcc80
    style Pause fill:#f44336,color:#fff
    style Fast fill:#81c784
    style Standard fill:#ff9800
    style QC fill:#64b5f6
    style Publish fill:#4caf50
    style Waste fill:#ffcdd2
```

### 7.2 Cost Attribution Tracking

```mermaid
graph LR
    subgraph "Cost Components"
        VeoCost[Veo Generation<br/>$0.75-3.20]
        EgressCost[GCS Egress<br/>$0.60-1.15]
        ComputeCost[Compute<br/>$0.10-0.30]
        StorageCost[Storage<br/>$0.02]
        APICost[API Calls<br/>$0.05]
    end

    subgraph "Tracking"
        PerVideo[Per-Video Cost<br/>$1.52-4.67]
        PerTrend[Per-Trend ROI]
        PerPlatform[Per-Platform<br/>Performance]
        Monthly[Monthly Total]
    end

    subgraph "Optimization"
        TopROI[Top ROI Topics<br/>Prioritize]
        BottomROI[Low ROI Topics<br/>Avoid]
        CostAlert[Budget Alerts<br/>50%, 75%, 90%]
        Forecast[Cost Forecast<br/>Next 30 Days]
    end

    VeoCost --> PerVideo
    EgressCost --> PerVideo
    ComputeCost --> PerVideo
    StorageCost --> PerVideo
    APICost --> PerVideo

    PerVideo --> PerTrend
    PerVideo --> PerPlatform
    PerVideo --> Monthly

    PerTrend --> TopROI
    PerTrend --> BottomROI
    Monthly --> CostAlert
    Monthly --> Forecast

    style VeoCost fill:#ba68c8
    style PerVideo fill:#ff8a65
    style TopROI fill:#81c784
    style BottomROI fill:#ffcdd2
    style CostAlert fill:#ffb74d
```

---

## 8. Phase Evolution Diagram

### 8.1 Architecture Evolution Roadmap

```mermaid
timeline
    title System Evolution Roadmap

    section Phase 0 (Week 1)
        Security Fixes : SQL/Command Injection
                      : Secrets Management
                      : Budget Controls
        Status: NOT DEPLOYABLE → SECURE

    section Phase 1 (Weeks 2-4)
        MVP Foundation : PostgreSQL Schema
                      : Basic APIs
                      : GPT-4 Transformation
                      : Human Approval
        Capacity: 10-20 videos/week
        Status: SECURE → MVP

    section Phase 2 (Weeks 5-10)
        Production Hardening : CLIP Quality Control
                            : Cloud Run Deployment
                            : Monitoring Stack
                            : Admin Dashboard
        Capacity: 50-100 videos/month
        Uptime: 95%
        Status: MVP → PRODUCTION

    section Phase 3 (Weeks 11-20)
        Scale Preparation : Microservices Refactor
                         : Pub/Sub Architecture
                         : BigQuery Analytics
                         : High Availability
        Capacity: 300-500 videos/month
        Uptime: 99%
        Status: PRODUCTION → SCALABLE

    section Phase 4 (Weeks 21-48)
        Enterprise Scale : Kubernetes (GKE)
                        : Multi-Region
                        : Multi-Tenancy
                        : Advanced AI Features
        Capacity: 1,000+ videos/month
        Uptime: 99.5%
        Status: SCALABLE → ENTERPRISE
```

### 8.2 Scaling Metrics Evolution

```mermaid
graph LR
    subgraph "Phase 1: MVP"
        P1V[10-20<br/>videos/week]
        P1C[$0<br/>testing only]
        P1U[N/A<br/>uptime]
    end

    subgraph "Phase 2: Production"
        P2V[50-100<br/>videos/month]
        P2C[$300-400<br/>monthly]
        P2U[95%<br/>uptime]
    end

    subgraph "Phase 3: Scale"
        P3V[300-500<br/>videos/month]
        P3C[$1,200-1,600<br/>monthly]
        P3U[99%<br/>uptime]
    end

    subgraph "Phase 4: Enterprise"
        P4V[1,000+<br/>videos/month]
        P4C[$3,000-6,000<br/>monthly]
        P4U[99.5%<br/>uptime]
    end

    P1V -->|3 weeks| P2V
    P2V -->|10 weeks| P3V
    P3V -->|28 weeks| P4V

    P1C --> P2C
    P2C --> P3C
    P3C --> P4C

    P1U --> P2U
    P2U --> P3U
    P3U --> P4U

    style P1V fill:#ffcdd2
    style P2V fill:#fff9c4
    style P3V fill:#c8e6c9
    style P4V fill:#81c784
```

---

## 9. Integration Diagram

### 9.1 External API Integration Map

```mermaid
graph TB
    subgraph "Video Automation System"
        Core[Core Services]
    end

    subgraph "Trend Detection APIs"
        YouTube[YouTube Data API v3<br/>10K units/day quota]
        TikTokResearch[TikTok Research API<br/>Academic approval required]
        SocialListening[Social Listening APIs<br/>Brandwatch/Phyllo]
    end

    subgraph "AI/ML APIs"
        Veo[Google Veo 3.1<br/>Vertex AI<br/>$0.15-0.40/sec]
        GPT4[OpenAI GPT-4<br/>Transformation<br/>$0.03/1K tokens]
        CLIP[OpenAI CLIP<br/>Quality Control<br/>Self-hosted]
        VideoIntel[Google Video Intelligence<br/>Safety Check<br/>$0.10/min]
    end

    subgraph "Publishing APIs"
        YTUpload[YouTube Data API<br/>OAuth2<br/>Resumable Upload]
        TTUpload[TikTok Content Posting<br/>4-Phase Upload<br/>Rate: 6 req/min]
        FBUpload[Facebook Graph API<br/>Chunked Upload<br/>v20.0]
    end

    subgraph "Infrastructure APIs"
        GCS[Cloud Storage<br/>Video Storage<br/>$0.023/GB/month]
        SecretMgr[Secret Manager<br/>Credentials<br/>$0.06/secret/month]
        PubSub[Pub/Sub<br/>Message Queue<br/>$40/TB]
    end

    subgraph "Monitoring APIs"
        Prometheus[Prometheus<br/>Metrics Collection]
        CloudLogging[Cloud Logging<br/>Structured Logs<br/>$0.50/GB]
        Slack[Slack Webhooks<br/>Notifications<br/>Free]
    end

    Core --> YouTube
    Core --> TikTokResearch
    Core --> SocialListening

    Core --> Veo
    Core --> GPT4
    Core --> CLIP
    Core --> VideoIntel

    Core --> YTUpload
    Core --> TTUpload
    Core --> FBUpload

    Core --> GCS
    Core --> SecretMgr
    Core --> PubSub

    Core --> Prometheus
    Core --> CloudLogging
    Core --> Slack

    style Core fill:#4caf50
    style YouTube fill:#ff0000
    style TikTokResearch fill:#000000,color:#fff
    style Veo fill:#4285f4
    style GPT4 fill:#74aa9c
    style YTUpload fill:#ff0000
    style TTUpload fill:#000000,color:#fff
    style FBUpload fill:#1877f2
    style GCS fill:#4285f4
    style Slack fill:#4a154b,color:#fff
```

---

## 10. Comparison: Before vs After

### 10.1 Architecture Comparison

```mermaid
graph TB
    subgraph "BEFORE: Monolithic n8n"
        B1[Single n8n Instance]
        B2[Sequential Execution]
        B3[Inline Business Logic]
        B4[No State Persistence]
        B5[Synchronous Polling]
        B6[No Resilience]

        B1 --> B2
        B2 --> B3
        B3 --> B4
        B4 --> B5
        B5 --> B6

        BMetrics[Metrics:<br/>12 videos/day max<br/>N/A uptime<br/>$4-6 per video<br/>20 min processing]

        style B1 fill:#ffcdd2
        style B2 fill:#ffcdd2
        style B3 fill:#ffcdd2
        style B4 fill:#ffcdd2
        style B5 fill:#ffcdd2
        style B6 fill:#ffcdd2
        style BMetrics fill:#f44336,color:#fff
    end

    subgraph "AFTER: Microservices"
        A1[Distributed Services]
        A2[Event-Driven Async]
        A3[Separate Business Logic]
        A4[PostgreSQL + Redis]
        A5[Webhook Callbacks]
        A6[Circuit Breakers + Retries]

        A1 --> A2
        A2 --> A3
        A3 --> A4
        A4 --> A5
        A5 --> A6

        AMetrics[Metrics:<br/>1,000+ videos/month<br/>99.5% uptime<br/>$2.50-3.50 per video<br/>5 min processing]

        style A1 fill:#c8e6c9
        style A2 fill:#c8e6c9
        style A3 fill:#c8e6c9
        style A4 fill:#c8e6c9
        style A5 fill:#c8e6c9
        style A6 fill:#c8e6c9
        style AMetrics fill:#4caf50,color:#fff
    end
```

---

## Summary

### Key Diagrams Purpose

| Diagram | Use Case | Phase |
|---------|----------|-------|
| **n8n Workflow** | Understand original sequential design | Reference |
| **Current Architecture** | Identify critical issues | Phase 0 |
| **Target Architecture** | Guide microservices refactor | Phase 3-4 |
| **Data Flow** | Debug and trace requests | All phases |
| **Deployment** | Infrastructure planning | Phase 2-4 |
| **Security** | Security review and audit | Phase 0-1 |
| **Cost Optimization** | Budget control implementation | All phases |
| **Phase Evolution** | Project planning and milestones | Management |

### Diagram Formats

All diagrams are in **Mermaid** format for easy rendering in:
- GitHub markdown
- GitLab markdown
- Notion
- Obsidian
- VS Code with Mermaid plugin
- Any markdown viewer with Mermaid support

### Next Steps

1. **Review diagrams** with stakeholders for alignment
2. **Update as needed** based on implementation feedback
3. **Use in documentation** for onboarding and training
4. **Include in PRs** to explain architectural changes
5. **Reference in runbooks** for operational procedures

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Format**: Mermaid Diagrams (Markdown Compatible)
**Maintained By**: Development Team
