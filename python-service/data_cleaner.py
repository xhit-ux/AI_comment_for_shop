import re
import logging
import jieba
from datetime import datetime
from typing import List, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗器 - 负责评论数据的预处理和清洗"""
    
    def __init__(self, mongodb_client):
        self.mongodb = mongodb_client
        
        # 初始化停用词
        self.stop_words = self._load_stop_words()
        
        # 初始化广告词过滤
        self.ad_patterns = [
            r'加微.*信',
            r'微信.*[0-9]',
            r'QQ.*[0-9]',
            r'电话.*[0-9]',
            r'购买.*链接',
            r'点击.*购买',
            r'优惠.*券',
            r'折扣.*码',
            r'推广.*链接',
            r'广告',
            r'营销',
            r'代购',
            r'批发',
            r'代理',
        ]
        
    def _load_stop_words(self) -> set:
        """加载停用词表"""
        # 这里可以加载自定义的停用词表
        basic_stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '但', '什么', '我们', '把', '又', '呢', '吧', '嗯', '啊', '哦', '哈', '嘿', '呵呵', '哈哈'
        }
        return basic_stop_words
        
    async def start_cleaning(self, task_id: str):
        """开始数据清洗任务"""
        try:
            logger.info(f"开始数据清洗任务: {task_id}")
            
            # 批量处理未清洗的评论
            batch_size = 100
            processed_count = 0
            
            while True:
                # 获取一批未清洗的评论
                comments = await self.mongodb.get_uncleaned_comments(task_id, batch_size)
                if not comments:
                    break
                    
                # 批量清洗
                cleaned_comments = []
                for comment in comments:
                    cleaned_data = self.clean_comment(comment)
                    if cleaned_data:
                        cleaned_comments.append({
                            "comment_id": str(comment["_id"]),
                            "cleaned_data": cleaned_data
                        })
                        processed_count += 1
                        
                # 批量更新数据库
                for item in cleaned_comments:
                    await self.mongodb.update_comment_cleaning_status(
                        item["comment_id"],
                        item["cleaned_data"]
                    )
                    
                logger.info(f"任务 {task_id} 已清洗 {processed_count} 条评论")
                
                # 小批量处理，避免内存占用过高
                await asyncio.sleep(0.1)
                
            logger.info(f"数据清洗任务完成: {task_id}, 共清洗 {processed_count} 条评论")
            
        except Exception as e:
            logger.error(f"数据清洗任务失败: {task_id}, 错误: {e}")
            raise
            
    def clean_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """清洗单条评论"""
        try:
            original_text = comment.get("content", "")
            if not original_text or len(original_text.strip()) < 3:
                return None
                
            # 1. 去除HTML标签
            clean_text = self._remove_html_tags(original_text)
            
            # 2. 去除表情符号
            clean_text = self._remove_emojis(clean_text)
            
            # 3. 去除多余空白
            clean_text = self._remove_extra_spaces(clean_text)
            
            # 4. 过滤广告内容
            if self._is_ad_content(clean_text):
                return None
                
            # 5. 过滤过短评论
            if len(clean_text) < 5:
                return None
                
            # 6. 中文分词
            words = self._chinese_segmentation(clean_text)
            
            # 7. 去除停用词
            filtered_words = self._remove_stop_words(words)
            
            # 8. 标准化文本
            normalized_text = " ".join(filtered_words)
            
            return {
                "clean_text": clean_text,
                "segmented_text": normalized_text,
                "word_count": len(filtered_words),
                "cleaned_at": datetime.now(),
                "is_valid": len(filtered_words) >= 3  # 至少3个有效词
            }
            
        except Exception as e:
            logger.error(f"清洗评论失败: {e}")
            return None
            
    def _remove_html_tags(self, text: str) -> str:
        """去除HTML标签"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
        
    def _remove_emojis(self, text: str) -> str:
        """去除表情符号"""
        # 简单的表情符号过滤
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
        
    def _remove_extra_spaces(self, text: str) -> str:
        """去除多余空白"""
        # 去除首尾空白
        text = text.strip()
        # 将多个连续空白替换为单个空格
        text = re.sub(r'\s+', ' ', text)
        return text
        
    def _is_ad_content(self, text: str) -> bool:
        """判断是否为广告内容"""
        text_lower = text.lower()
        
        # 检查广告模式
        for pattern in self.ad_patterns:
            if re.search(pattern, text_lower):
                return True
                
        # 检查联系方式
        phone_pattern = r'1[3-9]\d{9}'
        if re.search(phone_pattern, text):
            return True
            
        # 检查URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        if re.search(url_pattern, text):
            return True
            
        return False
        
    def _chinese_segmentation(self, text: str) -> List[str]:
        """中文分词"""
        try:
            # 使用jieba进行分词
            words = jieba.cut(text, cut_all=False)
            return list(words)
        except Exception as e:
            logger.error(f"分词失败: {e}")
            return [text]
            
    def _remove_stop_words(self, words: List[str]) -> List[str]:
        """去除停用词"""
        return [word for word in words if word.strip() and word not in self.stop_words]
        
    def validate_comment_quality(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """评论质量验证"""
        text = comment.get("content", "")
        clean_data = self.clean_comment(comment)
        
        if not clean_data:
            return {
                "is_valid": False,
                "reason": "清洗后无效"
            }
            
        # 检查评论长度
        if len(text) < 10:
            return {
                "is_valid": False,
                "reason": "评论过短"
            }
            
        # 检查有效词数量
        if clean_data["word_count"] < 3:
            return {
                "is_valid": False,
                "reason": "有效词过少"
            }
            
        # 检查重复字符
        if self._has_repeated_chars(text):
            return {
                "is_valid": False,
                "reason": "重复字符过多"
            }
            
        return {
            "is_valid": True,
            "reason": "质量合格",
            "quality_score": self._calculate_quality_score(clean_data)
        }
        
    def _has_repeated_chars(self, text: str, threshold: int = 5) -> bool:
        """检查是否有过多重复字符"""
        if len(text) < threshold * 2:
            return False
            
        for i in range(len(text) - threshold):
            if text[i:i+threshold] == text[i+threshold:i+threshold*2]:
                return True
        return False
        
    def _calculate_quality_score(self, clean_data: Dict[str, Any]) -> float:
        """计算评论质量分数"""
        score = 0.0
        
        # 基于词数量
        word_count = clean_data["word_count"]
        if word_count >= 10:
            score += 0.4
        elif word_count >= 5:
            score += 0.2
        else:
            score += 0.1
            
        # 基于文本长度
        text_length = len(clean_data["clean_text"])
        if text_length >= 50:
            score += 0.3
        elif text_length >= 20:
            score += 0.2
        else:
            score += 0.1
            
        # 基于多样性（简单的重复检查）
        words = clean_data["segmented_text"].split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        score += unique_ratio * 0.3
        
        return min(score, 1.0)
