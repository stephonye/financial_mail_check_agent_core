"""
PostgreSQL数据库服务 - 财务邮件数据存储
支持直接连接和MCP (Model Context Protocol) 连接
"""
import os
import json
import psycopg2
from psycopg2 import sql, pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from decimal import Decimal
from permission_controller import permission_controller

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """PostgreSQL数据库服务类 - 支持直接连接和MCP连接"""
    
    # 连接池实例（类变量）
    _connection_pool = None
    
    def __init__(self, connection_string: Optional[str] = None, use_mcp: bool = False, 
                 pool_size: int = 10, user_id: str = "default_user"):
        """
        初始化数据库服务
        
        Args:
            connection_string: 数据库连接字符串
            use_mcp: 是否使用MCP连接 (默认为False，使用直接连接)
            pool_size: 连接池大小
            user_id: 用户ID，用于权限控制
        """
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        self.use_mcp = use_mcp
        self.pool_size = pool_size
        self.user_id = user_id
        self.conn = None
        
        # 检查用户是否有数据库访问权限
        if not permission_controller.check_user_permission(user_id, "access_database"):
            logger.warning(f"用户 {user_id} 没有数据库访问权限")
        
        # 初始化连接池（仅初始化一次）
        if not self.use_mcp and DatabaseService._connection_pool is None:
            self._initialize_connection_pool()
        
        if not use_mcp:
            self._ensure_table()
        else:
            logger.info("MCP连接模式已启用，表结构由MCP服务器管理")
    
    def _initialize_connection_pool(self):
        """初始化连接池"""
        try:
            if not self.connection_string:
                raise ValueError("Database connection string is not provided")
            
            DatabaseService._connection_pool = pool.SimpleConnectionPool(
                1,  # 最小连接数
                self.pool_size,  # 最大连接数
                self.connection_string
            )
            logger.info(f"数据库连接池初始化成功，大小: {self.pool_size}")
        except Exception as e:
            logger.error(f"数据库连接池初始化失败: {e}")
    
    def _get_connection(self):
        """获取数据库连接（支持MCP和直接连接）"""
        if self.use_mcp:
            return self._get_mcp_connection()
        else:
            return self._get_direct_connection()
    
    def _get_direct_connection(self):
        """获取直接数据库连接（使用连接池）"""
        try:
            if not self.connection_string:
                raise ValueError("Database connection string is not provided")
            
            # 使用连接池获取连接
            if DatabaseService._connection_pool is not None:
                conn = DatabaseService._connection_pool.getconn()
                logger.debug("从连接池获取数据库连接")
                return conn
            else:
                # 回退到直接连接
                conn = psycopg2.connect(self.connection_string)
                logger.info("成功通过直接连接连接到PostgreSQL数据库")
                return conn
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return None
    
    def _get_mcp_connection(self):
        """通过MCP协议获取数据库连接"""
        try:
            # 这里应该是MCP客户端连接逻辑
            # 实际实现会根据MCP服务器的具体配置
            logger.info("使用MCP协议连接数据库")
            
            # 模拟MCP连接 - 实际项目中需要替换为真实的MCP客户端
            # 例如：使用MCP客户端库连接到MCP服务器
            mcp_connection_string = os.getenv('MCP_DATABASE_URL') or self.connection_string
            
            if mcp_connection_string:
                # 在实际MCP实现中，这里会通过MCP协议转发到服务器
                conn = psycopg2.connect(mcp_connection_string)
                logger.info("成功通过MCP连接到PostgreSQL数据库")
                return conn
            else:
                raise ValueError("MCP database connection string is not provided")
                
        except Exception as e:
            logger.error(f"MCP数据库连接失败: {e}")
            # 回退到直接连接
            logger.info("尝试回退到直接连接")
            return self._get_direct_connection()
    
    def connect(self):
        """连接到数据库"""
        try:
            self.conn = self._get_connection()
            if self.conn:
                connection_type = "MCP" if self.use_mcp else "直接"
                logger.info(f"成功通过{connection_type}连接连接到PostgreSQL数据库")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            if not self.use_mcp and DatabaseService._connection_pool is not None:
                # 将连接返回到连接池
                DatabaseService._connection_pool.putconn(self.conn)
                logger.debug("数据库连接已返回到连接池")
            else:
                # 直接关闭连接
                self.conn.close()
                logger.info("数据库连接已关闭")
            self.conn = None
    
    def _ensure_table(self):
        """确保数据表存在"""
        if not self.connect():
            return False
        
        try:
            with self.conn.cursor() as cur:
                # 创建财务邮件表
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS financial_emails (
                        id SERIAL PRIMARY KEY,
                        email_id VARCHAR(255) UNIQUE NOT NULL,
                        subject TEXT NOT NULL,
                        from_email TEXT NOT NULL,
                        email_date TIMESTAMP,
                        body_preview TEXT,
                        
                        -- 财务信息
                        document_type VARCHAR(50),
                        status VARCHAR(50),
                        counterparty TEXT,
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
                        raw_data JSONB,
                        
                        -- 索引
                        CONSTRAINT unique_email UNIQUE (email_id)
                    )
                """)
                
                # 创建索引
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_financial_emails_email_id 
                    ON financial_emails(email_id)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_financial_emails_status 
                    ON financial_emails(status)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_financial_emails_document_type 
                    ON financial_emails(document_type)
                """)
                
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_financial_emails_processed_at 
                    ON financial_emails(processed_at)
                """)
                
                self.conn.commit()
                logger.info("数据表检查/创建完成")
                return True
                
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    def insert_financial_email(self, email_data: Dict[str, Any]) -> bool:
        """插入财务邮件数据"""
        # 检查用户是否有修改数据的权限
        if not permission_controller.check_user_permission(self.user_id, "modify_data"):
            logger.warning(f"用户 {self.user_id} 没有修改数据的权限")
            return False
        
        if not self.connect():
            return False
        
        try:
            financial_info = email_data.get('financial_info', {})
            
            # 解析日期
            dates = financial_info.get('dates', {})
            due_date = self._parse_date(dates.get('due_date'))
            issue_date = self._parse_date(dates.get('issue_date'))
            start_date = self._parse_date(dates.get('start_date'))
            email_date = self._parse_date(email_data.get('date'))
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO financial_emails (
                        email_id, subject, from_email, email_date, body_preview,
                        document_type, status, counterparty, 
                        original_amount, original_currency, usd_amount, exchange_rate,
                        due_date, issue_date, start_date, raw_data
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (email_id) 
                    DO UPDATE SET
                        subject = EXCLUDED.subject,
                        from_email = EXCLUDED.from_email,
                        email_date = EXCLUDED.email_date,
                        body_preview = EXCLUDED.body_preview,
                        document_type = EXCLUDED.document_type,
                        status = EXCLUDED.status,
                        counterparty = EXCLUDED.counterparty,
                        original_amount = EXCLUDED.original_amount,
                        original_currency = EXCLUDED.original_currency,
                        usd_amount = EXCLUDED.usd_amount,
                        exchange_rate = EXCLUDED.exchange_rate,
                        due_date = EXCLUDED.due_date,
                        issue_date = EXCLUDED.issue_date,
                        start_date = EXCLUDED.start_date,
                        raw_data = EXCLUDED.raw_data,
                        processed_at = CURRENT_TIMESTAMP
                """, (
                    email_data['id'],
                    email_data['subject'],
                    email_data['from'],
                    email_date,
                    email_data.get('body_preview', ''),
                    financial_info.get('type'),
                    financial_info.get('status'),
                    financial_info.get('counterparty'),
                    financial_info.get('amount'),
                    financial_info.get('currency'),
                    financial_info.get('usd_amount'),
                    financial_info.get('exchange_rate'),
                    due_date,
                    issue_date,
                    start_date,
                    json.dumps(email_data, ensure_ascii=False)
                ))
                
                self.conn.commit()
                logger.info(f"成功插入邮件数据: {email_data['id']}")
                return True
                
        except Exception as e:
            logger.error(f"插入数据失败: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()
    
    def batch_insert_financial_emails(self, emails_data: List[Dict[str, Any]]) -> int:
        """批量插入财务邮件数据"""
        success_count = 0
        for email_data in emails_data:
            if self.insert_financial_email(email_data):
                success_count += 1
        
        logger.info(f"批量插入完成: {success_count}/{len(emails_data)} 条记录成功")
        return success_count
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            formats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%d/%m/%Y', 
                '%m/%d/%Y',
                '%b %d, %Y',
                '%d %b %Y',
                '%Y-%m-%d %H:%M:%S',
                '%a, %d %b %Y %H:%M:%S %z'  # RFC 2822格式
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 如果所有格式都失败，返回None
            return None
            
        except Exception:
            return None
    
    def get_financial_emails(self, limit: int = 100) -> List[Dict]:
        """获取财务邮件数据"""
        # 检查用户是否有访问财务数据的权限
        if not permission_controller.check_user_permission(self.user_id, "access_financial_data"):
            logger.warning(f"用户 {self.user_id} 没有访问财务数据的权限")
            return []
        
        if not self.connect():
            return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM financial_emails 
                    ORDER BY processed_at DESC 
                    LIMIT %s
                """, (limit,))
                
                results = cur.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            logger.error(f"查询数据失败: {e}")
            return []
        finally:
            self.disconnect()
    
    def get_summary_stats(self) -> Dict:
        """获取统计摘要"""
        # 检查用户是否有访问财务数据的权限
        if not permission_controller.check_user_permission(self.user_id, "access_financial_data"):
            logger.warning(f"用户 {self.user_id} 没有访问财务数据的权限")
            return {}
        
        if not self.connect():
            return {}
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 按类型统计
                cur.execute("""
                    SELECT document_type, COUNT(*) as count 
                    FROM financial_emails 
                    GROUP BY document_type
                """)
                by_type = {row['document_type']: row['count'] for row in cur.fetchall()}
                
                # 按状态统计
                cur.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM financial_emails 
                    GROUP BY status
                """)
                by_status = {row['status']: row['count'] for row in cur.fetchall()}
                
                # 金额统计
                cur.execute("""
                    SELECT 
                        SUM(usd_amount) as total_usd,
                        COUNT(*) as total_records,
                        COUNT(DISTINCT original_currency) as currency_count
                    FROM financial_emails 
                    WHERE usd_amount IS NOT NULL
                """)
                amount_stats = cur.fetchone() or {}
                
                return {
                    'by_type': by_type,
                    'by_status': by_status,
                    'total_usd_amount': float(amount_stats.get('total_usd', 0)) if amount_stats.get('total_usd') else 0,
                    'total_records': amount_stats.get('total_records', 0),
                    'currency_count': amount_stats.get('currency_count', 0)
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            self.disconnect()


def create_database_service() -> DatabaseService:
    """创建数据库服务实例"""
    return DatabaseService()


# 示例使用
if __name__ == "__main__":
    # 测试数据库连接
    db_service = DatabaseService()
    
    # 测试插入示例数据
    sample_email = {
        'id': 'test_email_123',
        'subject': 'Invoice #INV-001',
        'from': 'billing@example.com',
        'date': '2024-01-15',
        'body_preview': 'Please pay your invoice...',
        'financial_info': {
            'type': 'invoice',
            'status': '付款',
            'counterparty': 'Example Corp',
            'amount': 100.0,
            'currency': 'USD',
            'usd_amount': 100.0,
            'exchange_rate': 1.0,
            'dates': {
                'due_date': '2024-01-31',
                'issue_date': '2024-01-15'
            }
        }
    }
    
    if db_service.insert_financial_email(sample_email):
        print("示例数据插入成功")
    
    # 查询数据
    emails = db_service.get_financial_emails(5)
    print(f"查询到 {len(emails)} 条记录")
    
    # 获取统计信息
    stats = db_service.get_summary_stats()
    print(f"统计信息: {stats}")