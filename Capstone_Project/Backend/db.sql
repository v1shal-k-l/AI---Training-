
CREATE DATABASE wealth_observability_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_India.1252'
    LC_CTYPE = 'English_India.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;



CREATE TABLE portfolios (
    portfolio_id SERIAL PRIMARY KEY,
    owner_code VARCHAR(50) NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    investment_style VARCHAR(50),
    base_currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 4. ASSETS
-- =====================================================

CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    asset_name VARCHAR(100) NOT NULL,
    asset_class VARCHAR(50) NOT NULL,
    sector VARCHAR(50),
    synthetic_reference_price NUMERIC(12,2) NOT NULL
        CHECK (synthetic_reference_price >= 0)
);


-- =====================================================
-- 5. HOLDINGS
-- =====================================================

CREATE TABLE holdings (
    holding_id SERIAL PRIMARY KEY,

    portfolio_id INTEGER NOT NULL
        REFERENCES portfolios(portfolio_id),

    asset_id INTEGER NOT NULL
        REFERENCES assets(asset_id),

    units NUMERIC(18,4) NOT NULL
        CHECK (units >= 0),

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(portfolio_id, asset_id)
);


-- =====================================================
-- 6. TRANSACTIONS
-- =====================================================

CREATE TABLE transactions (
    txn_id SERIAL PRIMARY KEY,

    portfolio_id INTEGER NOT NULL
        REFERENCES portfolios(portfolio_id),

    asset_id INTEGER NOT NULL
        REFERENCES assets(asset_id),

    txn_type VARCHAR(10) NOT NULL
        CHECK (txn_type IN ('BUY','SELL')),

    units NUMERIC(18,4) NOT NULL
        CHECK (units > 0),

    unit_price NUMERIC(12,2) NOT NULL
        CHECK (unit_price >= 0),

    transaction_value NUMERIC(20,2)
        GENERATED ALWAYS AS (units * unit_price) STORED,

    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 7. AI RUNS
-- =====================================================

CREATE TABLE ai_runs (
    run_id SERIAL PRIMARY KEY,

    portfolio_id INTEGER NOT NULL
        REFERENCES portfolios(portfolio_id),

    trace_id UUID NOT NULL UNIQUE,

    model_id VARCHAR(100) NOT NULL,

    prompt_version VARCHAR(20),

    status VARCHAR(20) NOT NULL
        CHECK (
            status IN ('SUCCESS','FAILED','PENDING')
        ),

    latency_ms INTEGER
        CHECK (latency_ms >= 0),

    token_usage INTEGER
        CHECK (token_usage >= 0),

    error_type VARCHAR(100),

    generated_summary TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 8. TRACE EVENTS
-- =====================================================

CREATE TABLE trace_events (
    event_id SERIAL PRIMARY KEY,

    run_id INTEGER NOT NULL
        REFERENCES ai_runs(run_id)
        ON DELETE CASCADE,

    span_name VARCHAR(100) NOT NULL,

    started_at TIMESTAMP NOT NULL,

    duration_ms INTEGER NOT NULL
        CHECK (duration_ms >= 0),

    status VARCHAR(20) NOT NULL
        CHECK (status IN ('SUCCESS','FAILED')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 9. AI FEEDBACK
-- =====================================================

CREATE TABLE ai_feedback (
    feedback_id SERIAL PRIMARY KEY,

    run_id INTEGER NOT NULL
        REFERENCES ai_runs(run_id)
        ON DELETE CASCADE,

    helpful BOOLEAN,

    reviewer_comment TEXT,

    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(run_id)
);


-- =====================================================
-- 10. AUDIT EVENTS
-- =====================================================

CREATE TABLE audit_events (
    audit_id SERIAL PRIMARY KEY,

    actor_code VARCHAR(50) NOT NULL,

    entity_type VARCHAR(50) NOT NULL,

    entity_id INTEGER NOT NULL,

    action VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 11. PORTFOLIO DUMMY DATA
-- =====================================================

INSERT INTO portfolios
(owner_code, portfolio_name, investment_style, base_currency)
VALUES
('USR001','Technology Growth Portfolio','Aggressive','USD'),
('USR002','Balanced Income Portfolio','Moderate','USD'),
('USR003','Diversified Wealth Portfolio','Balanced','USD');


-- =====================================================
-- 12. ASSET DUMMY DATA
-- =====================================================

INSERT INTO assets
(symbol, asset_name, asset_class, sector, synthetic_reference_price)
VALUES
('AAPL','Apple Inc','Equity','Technology',220),
('MSFT','Microsoft Corp','Equity','Technology',450),
('NVDA','NVIDIA Corp','Equity','Technology',750),
('GOOGL','Alphabet Inc','Equity','Technology',190),
('AMZN','Amazon Inc','Equity','Consumer',210),
('SPY','S&P 500 ETF','ETF','Index',600),
('QQQ','Nasdaq ETF','ETF','Index',500),
('BND','Bond ETF','Fixed Income','Bond',85),
('GLD','Gold ETF','Commodity','Gold',250),
('SHV','Cash ETF','Cash','Cash',110);


-- =====================================================
-- 13. HOLDINGS DUMMY DATA
-- =====================================================

INSERT INTO holdings
(portfolio_id, asset_id, units)
VALUES

-- Technology Growth Portfolio
(1,1,120),
(1,2,80),
(1,3,50),
(1,4,100),
(1,5,75),
(1,6,40),
(1,7,30),

-- Balanced Income Portfolio
(2,1,20),
(2,6,25),
(2,7,35),
(2,8,300),
(2,9,70),
(2,10,200),

-- Diversified Wealth Portfolio
(3,1,60),
(3,2,45),
(3,6,50),
(3,7,50),
(3,8,250),
(3,9,90),
(3,10,150);


-- =====================================================
-- 14. TRANSACTION DUMMY DATA
-- =====================================================

INSERT INTO transactions
(portfolio_id, asset_id, txn_type, units, unit_price)
VALUES

(1,1,'BUY',120,220),
(1,2,'BUY',80,450),
(1,3,'BUY',50,750),
(1,4,'BUY',100,190),
(1,5,'BUY',75,210),
(1,6,'BUY',40,600),
(1,7,'BUY',30,500),

(2,1,'BUY',20,220),
(2,6,'BUY',25,600),
(2,7,'BUY',35,500),
(2,8,'BUY',300,85),
(2,9,'BUY',70,250),
(2,10,'BUY',200,110),

(3,1,'BUY',60,220),
(3,2,'BUY',45,450),
(3,6,'BUY',50,600),
(3,7,'BUY',50,500),
(3,8,'BUY',250,85),
(3,9,'BUY',90,250),
(3,10,'BUY',150,110),

(1,1,'BUY',20,225),
(1,3,'SELL',10,740),
(2,8,'SELL',50,82),
(3,9,'BUY',20,252),
(3,7,'SELL',10,490);


-- =====================================================
-- 15. AI RUNS DUMMY DATA
-- =====================================================

INSERT INTO ai_runs
(
    portfolio_id,
    trace_id,
    model_id,
    prompt_version,
    status,
    latency_ms,
    token_usage,
    error_type,
    generated_summary
)
VALUES

(1,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',1200,510,NULL,'Technology holdings dominate allocation'),
(1,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',1400,540,NULL,'Portfolio heavily concentrated in technology'),
(1,gen_random_uuid(),'gemini-1.5-flash','v1','FAILED',6500,NULL,'TIMEOUT',NULL),
(1,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',1100,500,NULL,'Largest exposure identified'),
(1,gen_random_uuid(),'groq-llama3','v1','FAILED',5500,NULL,'RATE_LIMIT',NULL),

(2,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',900,420,NULL,'Balanced asset class allocation'),
(2,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',980,460,NULL,'Fixed income contributes stability'),
(2,gen_random_uuid(),'gemini-1.5-flash','v1','FAILED',6000,NULL,'TIMEOUT',NULL),
(2,gen_random_uuid(),'groq-llama3','v1','SUCCESS',800,390,NULL,'Diversified exposure observed'),
(2,gen_random_uuid(),'groq-llama3','v1','FAILED',600,NULL,'VALIDATION_ERROR',NULL),

(3,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',1000,480,NULL,'Portfolio broadly diversified'),
(3,gen_random_uuid(),'gemini-1.5-flash','v1','SUCCESS',920,430,NULL,'ETF and bond allocations balanced'),
(3,gen_random_uuid(),'groq-llama3','v1','SUCCESS',780,360,NULL,'Moderate concentration risk'),
(3,gen_random_uuid(),'groq-llama3','v1','FAILED',5100,NULL,'MODEL_UNAVAILABLE',NULL),
(3,gen_random_uuid(),'groq-llama3','v1','SUCCESS',850,370,NULL,'Largest holdings highlighted'),

(1,gen_random_uuid(),'gemini-1.5-flash','v2','SUCCESS',1300,530,NULL,'Technology remains primary allocation'),
(2,gen_random_uuid(),'gemini-1.5-flash','v2','SUCCESS',1050,450,NULL,'Income-oriented allocation observed'),
(3,gen_random_uuid(),'gemini-1.5-flash','v2','SUCCESS',890,410,NULL,'Diversification appears healthy'),
(1,gen_random_uuid(),'groq-llama3','v2','FAILED',4300,NULL,'QUOTA_EXCEEDED',NULL),
(2,gen_random_uuid(),'groq-llama3','v2','SUCCESS',770,380,NULL,'Balanced investment profile');


-- =====================================================
-- 16. TRACE EVENTS DUMMY DATA
-- =====================================================

INSERT INTO trace_events
(run_id, span_name, started_at, duration_ms, status)
VALUES

(1,'DATABASE_READ',NOW(),40,'SUCCESS'),
(1,'ALLOCATION_CALCULATION',NOW(),15,'SUCCESS'),
(1,'AI_INFERENCE',NOW(),1100,'SUCCESS'),
(1,'OUTPUT_VALIDATION',NOW(),25,'SUCCESS'),

(2,'DATABASE_READ',NOW(),35,'SUCCESS'),
(2,'ALLOCATION_CALCULATION',NOW(),20,'SUCCESS'),
(2,'AI_INFERENCE',NOW(),1300,'SUCCESS'),
(2,'OUTPUT_VALIDATION',NOW(),30,'SUCCESS'),

(3,'DATABASE_READ',NOW(),38,'SUCCESS'),
(3,'ALLOCATION_CALCULATION',NOW(),18,'SUCCESS'),
(3,'AI_INFERENCE',NOW(),6400,'FAILED'),

(4,'DATABASE_READ',NOW(),42,'SUCCESS'),
(4,'ALLOCATION_CALCULATION',NOW(),17,'SUCCESS'),
(4,'AI_INFERENCE',NOW(),1000,'SUCCESS'),
(4,'OUTPUT_VALIDATION',NOW(),28,'SUCCESS');


-- =====================================================
-- 17. FEEDBACK DUMMY DATA
-- =====================================================

INSERT INTO ai_feedback
(run_id, helpful, reviewer_comment)
VALUES

(1,TRUE,'Accurate explanation'),
(2,TRUE,'Good portfolio summary'),
(4,FALSE,'Concentration risk not clearly described'),
(6,TRUE,'Useful allocation breakdown'),
(7,TRUE,'Well structured response'),
(9,TRUE,'Helpful educational content'),
(11,FALSE,'Needs more detail on exposure'),
(13,TRUE,'Clear and concise'),
(15,TRUE,'Good diversification summary'),
(17,FALSE,'Could improve data limitations section');


-- =====================================================
-- 18. AUDIT EVENTS DUMMY DATA
-- =====================================================

INSERT INTO audit_events
(actor_code, entity_type, entity_id, action)
VALUES

('USR001','PORTFOLIO',1,'CREATE'),
('USR002','PORTFOLIO',2,'CREATE'),
('USR003','PORTFOLIO',3,'CREATE'),

('USR001','HOLDING',1,'UPDATE'),
('USR001','HOLDING',2,'UPDATE'),

('USR002','TRANSACTION',8,'BUY'),
('USR002','TRANSACTION',9,'SELL'),

('USR003','TRANSACTION',18,'BUY'),

('USR001','AI_RUN',1,'GENERATE_INSIGHT'),
('USR001','AI_RUN',2,'GENERATE_INSIGHT'),

('USR002','AI_RUN',6,'GENERATE_INSIGHT'),
('USR003','AI_RUN',11,'GENERATE_INSIGHT'),

('REVIEWER01','AI_FEEDBACK',1,'SUBMIT'),
('REVIEWER01','AI_FEEDBACK',2,'SUBMIT'),
('REVIEWER02','AI_FEEDBACK',4,'SUBMIT'),
('REVIEWER02','AI_FEEDBACK',6,'SUBMIT'),
('REVIEWER03','AI_FEEDBACK',11,'SUBMIT'),

('SYSTEM','TRACE_EVENT',3,'TIMEOUT_LOGGED'),
('SYSTEM','TRACE_EVENT',14,'MODEL_FAILURE_LOGGED'),
('SYSTEM','TRACE_EVENT',19,'QUOTA_FAILURE_LOGGED');


-- =====================================================
-- 19. VERIFICATION
-- =====================================================

SELECT 'portfolios' AS table_name, COUNT(*) AS total FROM portfolios
UNION ALL
SELECT 'assets', COUNT(*) FROM assets
UNION ALL
SELECT 'holdings', COUNT(*) FROM holdings
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'ai_runs', COUNT(*) FROM ai_runs
UNION ALL
SELECT 'trace_events', COUNT(*) FROM trace_events
UNION ALL
SELECT 'ai_feedback', COUNT(*) FROM ai_feedback
UNION ALL
SELECT 'audit_events', COUNT(*) FROM audit_events;

