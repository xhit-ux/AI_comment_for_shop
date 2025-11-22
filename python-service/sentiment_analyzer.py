import logging
import json
import asyncio
import openai
from datetime import datetime
from typing import List, Dict, Any, Optional
import aiohttp

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """情感分析器 - 使用大模型API进行评论情感分析"""
    
    def __init__(self, mongodb_client):
        self.mongodb = mongodb_client
        self.openai_client = None
        self.model_name = "gpt-3.5-turbo"  # 默认模型
        
        # 情感分析系统提示词
        self.system_prompt = """你是一个专业的电商评论情感分析助手。请对每条评论进行情感分析，判断其情感倾向为positive（积极）、negative（消极）或neutral（中立），并给出0-1的情感得分和简短的中文理由。

要求：
1. 严格按JSON数组格式输出，每个元素包含：id, sentiment_label, sentiment_score, reason
2. sentiment_label必须是：positive/negative/neutral
3. sentiment_score是0-1的浮点数，positive接近1，negative接近0，neutral在0.5左右
4. reason是简短的中文分析理由
5. 保持分析客观准确

示例输出格式：
[
  {
    "id": "comment_1",
    "sentiment_label": "positive",
    "sentiment_score": 0.85,
    "reason": "用户对产品功能表示满意，提到使用体验良好"
  },
  {
    "id": "comment_2", 
    "sentiment_label": "negative",
    "sentiment_score": 0.15,
    "reason": "用户反映产品质量问题，存在使用缺陷"
  }
]"""
        
    async def initialize_openai(self, api_key: str = None):
        """初始化OpenAI客户端"""
        try:
            # 这里可以从环境变量或配置文件中获取API密钥
            if not api_key:
                # 使用默认密钥或从配置加载
                api_key = "your_openai_api_key_here"
                
            self.openai_client = openai.AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI客户端初始化成功")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            raise
            
    async def analyze_task_comments(self, task_id: str, batch_size: int = 20) -> Dict[str, Any]:
        """分析任务的所有评论"""
        try:
            logger.info(f"开始情感分析任务: {task_id}")
            
            analyzed_count = 0
            total_batches = 0
            
            while True:
                # 获取一批未分析的评论
                comments = await self.mongodb.get_unanalyzed_comments(task_id, batch_size)
                if not comments:
                    break
                    
                # 批量分析
                analysis_results = await self.analyze_batch(comments)
                
                # 更新数据库
                for result in analysis_results:
                    if result.get("success"):
                        await self.mongodb.update_comment_sentiment(
                            result["comment_id"],
                            result["sentiment_data"]
                        )
                        analyzed_count += 1
                        
                total_batches += 1
                logger.info(f"任务 {task_id} 第 {total_batches} 批分析完成，本批处理 {len(comments)} 条评论")
                
                # 控制请求频率，避免API限制
                await asyncio.sleep(1)
                
            logger.info(f"情感分析任务完成: {task_id}, 共分析 {analyzed_count} 条评论")
            
            return {
                "success": True,
                "analyzed_count": analyzed_count,
                "total_batches": total_batches
            }
            
        except Exception as e:
            logger.error(f"情感分析任务失败: {task_id}, 错误: {e}")
            return {
                "success": False,
                "error_message": str(e),
                "analyzed_count": analyzed_count
            }
            
    async def analyze_batch(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分析评论"""
        if not comments:
            return []
            
        try:
            # 准备分析数据
            analysis_data = []
            for comment in comments:
                analysis_data.append({
                    "id": f"comment_{comment['_id']}",
                    "text": comment.get("clean_text", comment.get("content", "")),
                    "comment_id": str(comment["_id"])
                })
                
            # 调用大模型API
            sentiment_results = await self.call_llm_api(analysis_data)
            
            # 处理分析结果
            results = []
            for i, comment in enumerate(comments):
                sentiment_data = None
                success = False
                
                if i < len(sentiment_results):
                    sentiment_data = sentiment_results[i]
                    success = sentiment_data is not None
                    
                results.append({
                    "comment_id": str(comment["_id"]),
                    "success": success,
                    "sentiment_data": sentiment_data if success else self._get_default_sentiment()
                })
                
            return results
            
        except Exception as e:
            logger.error(f"批量分析失败: {e}")
            # 返回默认结果
            return [{
                "comment_id": str(comment["_id"]),
                "success": False,
                "sentiment_data": self._get_default_sentiment()
            } for comment in comments]
            
    async def call_llm_api(self, comments_data: List[Dict[str, Any]]) -> List[Optional[Dict[str, Any]]]:
        """调用大模型API进行情感分析"""
        try:
            # 构建用户消息
            user_messages = []
            for item in comments_data:
                user_messages.append(f"ID: {item['id']}\n评论: {item['text']}")
                
            user_content = "\n\n".join(user_messages)
            
            # 调用OpenAI API
            if not self.openai_client:
                await self.initialize_openai()
                
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.1,  # 低温度以获得更一致的结果
                max_tokens=2000
            )
            
            # 解析响应
            result_text = response.choices[0].message.content.strip()
            return self._parse_llm_response(result_text, comments_data)
            
        except openai.APIError as e:
            logger.error(f"OpenAI API错误: {e}")
            return [None] * len(comments_data)
        except Exception as e:
            logger.error(f"调用大模型API失败: {e}")
            return [None] * len(comments_data)
            
    def _parse_llm_response(self, response_text: str, comments_data: List[Dict[str, Any]]) -> List[Optional[Dict[str, Any]]]:
        """解析大模型响应"""
        try:
            # 尝试解析JSON
            results = json.loads(response_text)
            
            if not isinstance(results, list):
                logger.error("大模型响应不是有效的JSON数组")
                return [None] * len(comments_data)
                
            # 构建结果映射
            result_map = {}
            for result in results:
                if isinstance(result, dict) and "id" in result:
                    result_map[result["id"]] = {
                        "sentiment_label": result.get("sentiment_label", "neutral"),
                        "sentiment_score": float(result.get("sentiment_score", 0.5)),
                        "sentiment_reason": result.get("reason", "分析完成"),
                        "model_name": self.model_name,
                        "analyzed_at": datetime.now()
                    }
                    
            # 匹配回原始评论
            sentiment_results = []
            for comment_data in comments_data:
                comment_id = comment_data["id"]
                if comment_id in result_map:
                    sentiment_results.append(result_map[comment_id])
                else:
                    sentiment_results.append(self._get_default_sentiment())
                    
            return sentiment_results
            
        except json.JSONDecodeError as e:
            logger.error(f"解析大模型响应JSON失败: {e}, 响应内容: {response_text}")
            return [self._get_default_sentiment() for _ in comments_data]
        except Exception as e:
            logger.error(f"解析大模型响应失败: {e}")
            return [self._get_default_sentiment() for _ in comments_data]
            
    def _get_default_sentiment(self) -> Dict[str, Any]:
        """获取默认情感分析结果"""
        return {
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
            "sentiment_reason": "系统默认分析",
            "model_name": "default",
            "analyzed_at": datetime.now()
        }
        
    async def analyze_single_comment(self, comment_text: str) -> Dict[str, Any]:
        """分析单条评论"""
        try:
            test_data = [{
                "id": "test_comment",
                "text": comment_text,
                "comment_id": "test"
            }]
            
            results = await self.call_llm_api(test_data)
            if results and results[0]:
                return results[0]
            else:
                return self._get_default_sentiment()
                
        except Exception as e:
            logger.error(f"单条评论分析失败: {e}")
            return self._get_default_sentiment()
            
    def validate_sentiment_result(self, result: Dict[str, Any]) -> bool:
        """验证情感分析结果的有效性"""
        try:
            # 检查必要字段
            required_fields = ["sentiment_label", "sentiment_score", "sentiment_reason"]
            for field in required_fields:
                if field not in result:
                    return False
                    
            # 检查情感标签有效性
            valid_labels = ["positive", "negative", "neutral"]
            if result["sentiment_label"] not in valid_labels:
                return False
                
            # 检查情感分数范围
            score = result["sentiment_score"]
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                return False
                
            return True
            
        except Exception:
            return False
            
    async def get_sentiment_statistics(self, task_id: str) -> Dict[str, Any]:
        """获取情感分析统计信息"""
        try:
            # 这里可以从数据库聚合情感分析结果
            # 简化实现，实际应该使用MongoDB聚合管道
            
            comments_collection = self.mongodb.get_collection("raw_comments")
            
            # 获取所有已分析的评论
            analyzed_comments = comments_collection.find({
                "task_id": task_id,
                "sentiment_analyzed": True
            })
            
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            total_score = 0
            comment_count = 0
            
            for comment in analyzed_comments:
                label = comment.get("sentiment_label")
                score = comment.get("sentiment_score", 0.5)
                
                if label in sentiment_counts:
                    sentiment_counts[label] += 1
                    total_score += score
                    comment_count += 1
                    
            avg_score = total_score / comment_count if comment_count > 0 else 0.5
            
            return {
                "total_analyzed": comment_count,
                "sentiment_distribution": sentiment_counts,
                "average_score": round(avg_score, 3),
                "positive_ratio": sentiment_counts["positive"] / comment_count if comment_count > 0 else 0,
                "negative_ratio": sentiment_counts["negative"] / comment_count if comment_count > 0 else 0,
                "neutral_ratio": sentiment_counts["neutral"] / comment_count if comment_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"获取情感统计失败: {e}")
            return {
                "total_analyzed": 0,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                "average_score": 0.5,
                "positive_ratio": 0,
                "negative_ratio": 0,
                "neutral_ratio": 0
            }
