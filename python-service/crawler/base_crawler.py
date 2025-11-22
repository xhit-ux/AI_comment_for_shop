import logging
import asyncio
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类 - 定义所有爬虫的通用接口"""
    
    def __init__(self, mongodb_client):
        self.mongodb = mongodb_client
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # 配置请求头
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 配置请求延迟
        self.min_delay = 1
        self.max_delay = 3
        
    @abstractmethod
    async def crawl_comments(self, product_url: str, product_id: Optional[str], 
                           max_comments: int, include_follow_up: bool,
                           include_image_comments: bool, include_video_comments: bool,
                           time_range: Optional[Dict[str, str]], task_id: str) -> Dict[str, Any]:
        """爬取评论数据 - 子类必须实现此方法"""
        pass
        
    def get_random_delay(self) -> float:
        """获取随机延迟时间"""
        return random.uniform(self.min_delay, self.max_delay)
        
    async def delay_request(self):
        """请求延迟"""
        delay = self.get_random_delay()
        await asyncio.sleep(delay)
        
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """发送HTTP请求"""
        try:
            # 更新User-Agent
            self.headers['User-Agent'] = self.ua.random
            
            # 设置请求参数
            request_kwargs = {
                'headers': self.headers,
                'timeout': 30,
            }
            request_kwargs.update(kwargs)
            
            if method.upper() == 'GET':
                response = self.session.get(url, **request_kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **request_kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
                
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            logger.error(f"请求失败: {url}, 错误: {e}")
            raise
            
    def extract_product_id(self, url: str) -> Optional[str]:
        """从URL中提取商品ID"""
        # 通用商品ID提取逻辑
        # 子类可以重写此方法
        import re
        
        # 匹配数字ID
        patterns = [
            r'/(\d+)\.html',
            r'id=(\d+)',
            r'product/(\d+)',
            r'item/(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        return None
        
    async def save_comment(self, comment_data: Dict[str, Any], task_id: str) -> bool:
        """保存评论数据到数据库"""
        try:
            # 构建完整的评论数据
            full_comment_data = {
                'task_id': task_id,
                'content': comment_data.get('content', ''),
                'rating': comment_data.get('rating', 0),
                'comment_time': comment_data.get('comment_time'),
                'user_name': comment_data.get('user_name', ''),
                'user_level': comment_data.get('user_level', ''),
                'is_follow_up': comment_data.get('is_follow_up', False),
                'has_images': comment_data.get('has_images', False),
                'has_videos': comment_data.get('has_videos', False),
                'product_id': comment_data.get('product_id'),
                'platform': comment_data.get('platform'),
                'source_url': comment_data.get('source_url', ''),
                'created_at': datetime.now(),
                'cleaned': False,
                'sentiment_analyzed': False,
            }
            
            # 保存到数据库
            await self.mongodb.save_comment(full_comment_data)
            return True
            
        except Exception as e:
            logger.error(f"保存评论失败: {e}")
            return False
            
    def validate_comment_data(self, comment_data: Dict[str, Any]) -> bool:
        """验证评论数据的有效性"""
        required_fields = ['content', 'rating', 'comment_time']
        
        for field in required_fields:
            if field not in comment_data or not comment_data[field]:
                return False
                
        # 检查评论内容长度
        content = comment_data.get('content', '')
        if len(content.strip()) < 3:
            return False
            
        # 检查评分范围
        rating = comment_data.get('rating', 0)
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return False
            
        return True
        
    def parse_comment_time(self, time_str: str) -> Optional[datetime]:
        """解析评论时间字符串"""
        try:
            # 常见的时间格式
            time_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d',
                '%Y年%m月%d日 %H:%M',
                '%Y年%m月%d日',
            ]
            
            for fmt in time_formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
                    
            # 如果都不匹配，返回当前时间
            return datetime.now()
            
        except Exception as e:
            logger.error(f"解析评论时间失败: {time_str}, 错误: {e}")
            return datetime.now()
            
    async def update_progress(self, task_id: str, current_count: int, total_expected: int):
        """更新任务进度"""
        try:
            progress_percent = (current_count / total_expected) * 100 if total_expected > 0 else 0
            logger.info(f"任务 {task_id} 进度: {current_count}/{total_expected} ({progress_percent:.1f}%)")
            
            # 这里可以添加进度回调或通知
            # 例如通过WebSocket通知前端
            
        except Exception as e:
            logger.error(f"更新进度失败: {e}")
