import logging
from typing import Optional, Dict, Any
import pymongo
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB数据库客户端"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.connection_string = connection_string
        self.client: Optional[MongoClient] = None
        self.db = None
        
    async def connect(self):
        """连接数据库"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client["ecommerce_analysis"]
            logger.info("MongoDB连接成功")
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
            
    async def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
            
    def get_collection(self, collection_name: str):
        """获取集合"""
        if not self.db:
            raise Exception("数据库未连接")
        return self.db[collection_name]
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        try:
            tasks_collection = self.get_collection("tasks")
            task = tasks_collection.find_one({"_id": ObjectId(task_id)})
            return task
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None
            
    async def update_task_status(self, task_id: str, status: str, error_message: str = None):
        """更新任务状态"""
        try:
            tasks_collection = self.get_collection("tasks")
            update_data = {"status": status}
            if error_message:
                update_data["errorMessage"] = error_message
                
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            logger.info(f"任务 {task_id} 状态更新为: {status}")
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")
            
    async def update_task_progress(self, task_id: str, comment_count: int = None, 
                                 analyzed_count: int = None, status: str = None, 
                                 error_message: str = None):
        """更新任务进度"""
        try:
            tasks_collection = self.get_collection("tasks")
            update_data = {}
            
            if comment_count is not None:
                update_data["commentCount"] = comment_count
            if analyzed_count is not None:
                update_data["analyzedCount"] = analyzed_count
            if status:
                update_data["status"] = status
            if error_message:
                update_data["errorMessage"] = error_message
                
            tasks_collection.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_data}
            )
            logger.info(f"任务 {task_id} 进度更新: {update_data}")
        except Exception as e:
            logger.error(f"更新任务进度失败: {e}")
            
    async def save_comment(self, comment_data: Dict[str, Any]) -> str:
        """保存评论数据"""
        try:
            comments_collection = self.get_collection("raw_comments")
            result = comments_collection.insert_one(comment_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"保存评论失败: {e}")
            raise
            
    async def get_uncleaned_comments(self, task_id: str, limit: int = 100):
        """获取未清洗的评论"""
        try:
            comments_collection = self.get_collection("raw_comments")
            comments = comments_collection.find({
                "task_id": task_id,
                "cleaned": {"$ne": True}
            }).limit(limit)
            return list(comments)
        except Exception as e:
            logger.error(f"获取未清洗评论失败: {e}")
            return []
            
    async def update_comment_cleaning_status(self, comment_id: str, cleaned_data: Dict[str, Any]):
        """更新评论清洗状态"""
        try:
            comments_collection = self.get_collection("raw_comments")
            comments_collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$set": {
                    "cleaned": True,
                    "clean_text": cleaned_data.get("clean_text"),
                    "cleaned_at": cleaned_data.get("cleaned_at")
                }}
            )
        except Exception as e:
            logger.error(f"更新评论清洗状态失败: {e}")
            
    async def get_unanalyzed_comments(self, task_id: str, limit: int = 20):
        """获取未分析的评论"""
        try:
            comments_collection = self.get_collection("raw_comments")
            comments = comments_collection.find({
                "task_id": task_id,
                "cleaned": True,
                "sentiment_analyzed": {"$ne": True}
            }).limit(limit)
            return list(comments)
        except Exception as e:
            logger.error(f"获取未分析评论失败: {e}")
            return []
            
    async def update_comment_sentiment(self, comment_id: str, sentiment_data: Dict[str, Any]):
        """更新评论情感分析结果"""
        try:
            comments_collection = self.get_collection("raw_comments")
            comments_collection.update_one(
                {"_id": ObjectId(comment_id)},
                {"$set": {
                    "sentiment_analyzed": True,
                    "sentiment_label": sentiment_data.get("sentiment_label"),
                    "sentiment_score": sentiment_data.get("sentiment_score"),
                    "sentiment_reason": sentiment_data.get("sentiment_reason"),
                    "model_name": sentiment_data.get("model_name"),
                    "analyzed_at": sentiment_data.get("analyzed_at")
                }}
            )
        except Exception as e:
            logger.error(f"更新评论情感分析结果失败: {e}")
            
    async def get_comment_stats(self, task_id: str) -> Dict[str, int]:
        """获取评论统计信息"""
        try:
            comments_collection = self.get_collection("raw_comments")
            
            total = comments_collection.count_documents({"task_id": task_id})
            cleaned = comments_collection.count_documents({
                "task_id": task_id,
                "cleaned": True
            })
            analyzed = comments_collection.count_documents({
                "task_id": task_id,
                "sentiment_analyzed": True
            })
            
            return {
                "total": total,
                "cleaned": cleaned,
                "analyzed": analyzed
            }
        except Exception as e:
            logger.error(f"获取评论统计失败: {e}")
            return {"total": 0, "cleaned": 0, "analyzed": 0}
