import os
from typing import Dict, Any

class Config:
    """系统配置类"""
    
    # MongoDB配置
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "ecommerce_analysis")
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.1")
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
    
    # 爬虫配置
    CRAWLER_DELAY_MIN = float(os.getenv("CRAWLER_DELAY_MIN", "1"))
    CRAWLER_DELAY_MAX = float(os.getenv("CRAWLER_DELAY_MAX", "3"))
    CRAWLER_TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", "30"))
    CRAWLER_MAX_RETRIES = int(os.getenv("CRAWLER_MAX_RETRIES", "3"))
    
    # 数据清洗配置
    CLEANER_BATCH_SIZE = int(os.getenv("CLEANER_BATCH_SIZE", "100"))
    MIN_COMMENT_LENGTH = int(os.getenv("MIN_COMMENT_LENGTH", "5"))
    MIN_WORD_COUNT = int(os.getenv("MIN_WORD_COUNT", "3"))
    
    # 情感分析配置
    SENTIMENT_BATCH_SIZE = int(os.getenv("SENTIMENT_BATCH_SIZE", "20"))
    SENTIMENT_API_DELAY = float(os.getenv("SENTIMENT_API_DELAY", "1"))
    
    # 服务器配置
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "uri": cls.MONGODB_URI,
            "db_name": cls.MONGODB_DB_NAME
        }
    
    @classmethod
    def get_openai_config(cls) -> Dict[str, Any]:
        """获取OpenAI配置"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "max_tokens": cls.OPENAI_MAX_TOKENS,
            "temperature": cls.OPENAI_TEMPERATURE
        }
    
    @classmethod
    def get_crawler_config(cls) -> Dict[str, Any]:
        """获取爬虫配置"""
        return {
            "delay_min": cls.CRAWLER_DELAY_MIN,
            "delay_max": cls.CRAWLER_DELAY_MAX,
            "timeout": cls.CRAWLER_TIMEOUT,
            "max_retries": cls.CRAWLER_MAX_RETRIES
        }
    
    @classmethod
    def get_cleaner_config(cls) -> Dict[str, Any]:
        """获取数据清洗配置"""
        return {
            "batch_size": cls.CLEANER_BATCH_SIZE,
            "min_comment_length": cls.MIN_COMMENT_LENGTH,
            "min_word_count": cls.MIN_WORD_COUNT
        }
    
    @classmethod
    def get_sentiment_config(cls) -> Dict[str, Any]:
        """获取情感分析配置"""
        return {
            "batch_size": cls.SENTIMENT_BATCH_SIZE,
            "api_delay": cls.SENTIMENT_API_DELAY
        }
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """获取服务器配置"""
        return {
            "host": cls.SERVER_HOST,
            "port": cls.SERVER_PORT,
            "debug": cls.DEBUG
        }


# 开发环境配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# 生产环境配置
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "INFO"


# 测试环境配置
class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    MONGODB_DB_NAME = "ecommerce_analysis_test"


# 根据环境选择配置
def get_config(env: str = None) -> Config:
    """根据环境获取配置"""
    if not env:
        env = os.getenv("ENVIRONMENT", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }
    
    return config_map.get(env, DevelopmentConfig)


# 当前配置实例
current_config = get_config()
