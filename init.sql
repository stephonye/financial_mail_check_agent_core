-- Financial Email Processor 数据库初始化脚本
-- 创建于: 2025-08-29

-- 切换到postgres数据库
\c postgres;

-- 创建应用数据库
CREATE DATABASE financial_emails;

-- 创建专用用户
CREATE USER financial_user WITH PASSWORD 'financial_password';

-- 授予用户权限
GRANT ALL PRIVILEGES ON DATABASE financial_emails TO financial_user;

-- 切换到应用数据库
\c financial_emails;

-- 创建财务邮件表
CREATE TABLE IF NOT EXISTS financial_emails (
    id SERIAL PRIMARY KEY,
    
    -- 邮件元数据
    email_id VARCHAR(255) UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    from_email TEXT NOT NULL,
    email_date TIMESTAMP,
    body_preview TEXT,
    
    -- 财务信息
    document_type VARCHAR(50),
    status VARCHAR(50),
    counterparty TEXT,
    
    -- 金额信息
    original_amount DECIMAL(15, 2),
    original_currency VARCHAR(10),
    usd_amount DECIMAL(15, 2),
    exchange_rate DECIMAL(10, 6),
    
    -- 日期信息
    due_date TIMESTAMP,
    issue_date TIMESTAMP,
    start_date TIMESTAMP,
    
    -- 元数据
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 原始数据
    raw_data JSONB,
    
    -- 确认状态
    confirmed BOOLEAN DEFAULT FALSE,
    confirmed_at TIMESTAMP,
    
    -- 修改记录
    modifications JSONB DEFAULT '[]'::JSONB
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_financial_emails_email_id ON financial_emails(email_id);
CREATE INDEX IF NOT EXISTS idx_financial_emails_status ON financial_emails(status);
CREATE INDEX IF NOT EXISTS idx_financial_emails_document_type ON financial_emails(document_type);
CREATE INDEX IF NOT EXISTS idx_financial_emails_processed_at ON financial_emails(processed_at);
CREATE INDEX IF NOT EXISTS idx_financial_emails_confirmed ON financial_emails(confirmed);
CREATE INDEX IF NOT EXISTS idx_financial_emails_from_email ON financial_emails(from_email);
CREATE INDEX IF NOT EXISTS idx_financial_emails_date_range ON financial_emails(email_date);

-- 创建GIN索引用于JSONB查询
CREATE INDEX IF NOT EXISTS idx_financial_emails_raw_data ON financial_emails USING GIN (raw_data);
CREATE INDEX IF NOT EXISTS idx_financial_emails_modifications ON financial_emails USING GIN (modifications);

-- 创建会话管理表
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(100),
    email_account VARCHAR(255),
    current_state VARCHAR(50) DEFAULT 'idle',
    
    -- 统计信息
    processed_count INTEGER DEFAULT 0,
    confirmed_count INTEGER DEFAULT 0,
    modified_count INTEGER DEFAULT 0,
    
    -- 时间信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- 会话数据
    session_data JSONB DEFAULT '{}'::JSONB,
    modification_history JSONB DEFAULT '[]'::JSONB
);

-- 会话表索引
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_email_account ON user_sessions(email_account);
CREATE INDEX IF NOT EXISTS idx_user_sessions_state ON user_sessions(current_state);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity);

-- 创建汇率缓存表
CREATE TABLE IF NOT EXISTS exchange_rates (
    base_currency VARCHAR(10) NOT NULL,
    target_currency VARCHAR(10) NOT NULL,
    rate DECIMAL(10, 6) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    
    PRIMARY KEY (base_currency, target_currency)
);

-- 汇率表索引
CREATE INDEX IF NOT EXISTS idx_exchange_rates_base ON exchange_rates(base_currency);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_target ON exchange_rates(target_currency);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_updated ON exchange_rates(last_updated);

-- 授予用户权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO financial_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO financial_user;
GRANT USAGE ON SCHEMA public TO financial_user;

-- 插入示例数据（可选）
INSERT INTO exchange_rates (base_currency, target_currency, rate, source) VALUES
('USD', 'USD', 1.000000, 'fixed'),
('EUR', 'USD', 1.100000, 'fixed'),
('GBP', 'USD', 1.270000, 'fixed'),
('JPY', 'USD', 0.006800, 'fixed'),
('CNY', 'USD', 0.140000, 'fixed'),
('CAD', 'USD', 0.740000, 'fixed'),
('AUD', 'USD', 0.670000, 'fixed')
ON CONFLICT (base_currency, target_currency) DO UPDATE
SET rate = EXCLUDED.rate, last_updated = CURRENT_TIMESTAMP;

-- 创建更新修改时间的触发器
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_financial_emails_modtime 
    BEFORE UPDATE ON financial_emails 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_user_sessions_activity 
    BEFORE UPDATE ON user_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- 输出完成信息
\echo '✅ 数据库初始化完成！'
\echo '📊 数据库: financial_emails'
\echo '👤 用户: financial_user'
\echo '🔑 密码: financial_password'
\echo '🌐 连接: postgresql://financial_user:financial_password@localhost:5432/financial_emails'