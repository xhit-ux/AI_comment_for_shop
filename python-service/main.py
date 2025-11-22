#!/usr/bin/env python3
"""
电商评论情感分析系统 - Python服务
负责评论爬取、数据清洗和情感分析
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from crawler.jd_crawler import JDCrawler
from crawler.taobao_crawler import TaobaoCrawler
from data_cleaner import DataCleaner
from sentiment_analyzer import SentimentAnalyzer
from database.mongodb import MongoDBClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="电商评论情感分析系统 - Python服务",
    description="负责评论爬取、数据清洗和情感分析的后端服务",
    version="1.0.0"
)

# 全局服务实例
mongodb_client = None
jd_crawler = None
taobao_crawler = None
data_cleaner = None
sentiment_analyzer = None

class TaskRequest(BaseModel):
    task_id: str
    platform: str
    product_url: str
    product_id: Optional[str] = None
    max_comments: int = 100
    include_follow_up: bool = True
    include_image_comments: bool = False
    include_video_comments: bool = False
    time_range: Optional[Dict[str, str]] = None

class AnalysisRequest(BaseModel):
    task_id: str
    batch_size: int = 20

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化组件"""
    global mongodb_client, jd_crawler, taobao_crawler, data_cleaner, sentiment_analyzer
    
    try:
        # 初始化数据库连接
        mongodb_client = MongoDBClient()
        await mongodb_client.connect()
        
        # 初始化爬虫
        jd_crawler = JDCrawler(mongodb_client)
        taobao_crawler = TaobaoCrawler(mongodb_client)
        
        # 初始化数据处理组件
        data_cleaner = DataCleaner(mongodb_client)
        sentiment_analyzer = SentimentAnalyzer(mongodb_client)
        
        logger.info("Python服务组件初始化完成")
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    if mongodb_client:
        await mongodb_client.close()
    logger.info("Python服务已关闭")

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "running",
        "service": "ecommerce-comment-analyzer-python",
        "version": "1.0.0"
    }

@app.post("/api/crawl")
async def start_crawling(request: TaskRequest):
    """开始评论爬取任务"""
    try:
        # 根据平台选择爬虫
        crawler = None
        if request.platform == "jd":
            crawler = jd_crawler
        elif request.platform == "taobao":
            crawler = taobao_crawler
        elif request.platform == "tmall":
            crawler = taobao_crawler  # 天猫使用淘宝爬虫
        else:
            raise HTTPException(status_code=400, detail=f"不支持的平台: {request.platform}")
        
        # 异步执行爬取任务
        asyncio.create_task(
            execute_crawling_task(
                crawler, 
                request.task_id, 
                request.product_url,
                request.product_id,
                request.max_comments,
                request.include_follow_up,
                request.include_image_comments,
                request.include_video_comments,
                request.time_range
            )
        )
        
        return {
            "status": "started",
            "task_id": request.task_id,
            "message": "评论爬取任务已开始"
        }
        
    except Exception as e:
        logger.error(f"启动爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def start_analysis(request: AnalysisRequest):
    """开始情感分析任务"""
    try:
        # 异步执行分析任务
        asyncio.create_task(
            execute_analysis_task(
                request.task_id,
                request.batch_size
            )
        )
        
        return {
            "status": "started",
            "task_id": request.task_id,
            "message": "情感分析任务已开始"
        }
        
    except Exception as e:
        logger.error(f"启动分析任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}/progress")
async def get_task_progress(task_id: str):
    """获取任务进度"""
    try:
        task = await mongodb_client.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 获取评论统计
        stats = await mongodb_client.get_comment_stats(task_id)
        
        return {
            "task_id": task_id,
            "status": task.get("status", "unknown"),
            "total_comments": stats.get("total", 0),
            "cleaned_comments": stats.get("cleaned", 0),
            "analyzed_comments": stats.get("analyzed", 0),
            "progress": {
                "crawling": stats.get("total", 0) / task.get("config", {}).get("maxComments", 1) * 100,
                "cleaning": stats.get("cleaned", 0) / max(stats.get("total", 1), 1) * 100,
                "analysis": stats.get("analyzed", 0) / max(stats.get("cleaned", 1), 1) * 100
            }
        }
        
    except Exception as e:
        logger.error(f"获取任务进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_crawling_task(
    crawler, 
    task_id: str,
    product_url: str,
    product_id: Optional[str],
    max_comments: int,
    include_follow_up: bool,
    include_image_comments: bool,
    include_video_comments: bool,
    time_range: Optional[Dict[str, str]]
):
    """执行评论爬取任务"""
    try:
        logger.info(f"开始执行爬取任务: {task_id}")
        
        # 更新任务状态为采集中
        await mongodb_client.update_task_status(task_id, "collecting")
        
        # 执行爬取
        result = await crawler.crawl_comments(
            product_url=product_url,
            product_id=product_id,
            max_comments=max_comments,
            include_follow_up=include_follow_up,
            include_image_comments=include_image_comments,
            include_video_comments=include_video_comments,
            time_range=time_range,
            task_id=task_id
        )
        
        # 更新任务状态和评论数量
        await mongodb_client.update_task_progress(
            task_id=task_id,
            comment_count=result.get("total_comments", 0),
            status="cleaning" if result.get("success") else "failed",
            error_message=result.get("error_message")
        )
        
        logger.info(f"爬取任务完成: {task_id}, 采集评论数: {result.get('total_comments', 0)}")
        
        # 如果爬取成功，开始数据清洗
        if result.get("success"):
            await data_cleaner.start_cleaning(task_id)
            
    except Exception as e:
        logger.error(f"爬取任务执行失败: {task_id}, 错误: {e}")
        await mongodb_client.update_task_status(task_id, "failed", str(e))

async def execute_analysis_task(task_id: str, batch_size: int):
    """执行情感分析任务"""
    try:
        logger.info(f"开始执行情感分析任务: {task_id}")
        
        # 更新任务状态为分析中
        await mongodb_client.update_task_status(task_id, "analyzing")
        
        # 执行情感分析
        result = await sentiment_analyzer.analyze_task_comments(
            task_id=task_id,
            batch_size=batch_size
        )
        
        # 更新任务状态
        await mongodb_client.update_task_progress(
            task_id=task_id,
            analyzed_count=result.get("analyzed_count", 0),
            status="completed" if result.get("success") else "failed",
            error_message=result.get("error_message")
        )
        
        logger.info(f"情感分析任务完成: {task_id}, 分析评论数: {result.get('analyzed_count', 0)}")
        
    except Exception as e:
        logger.error(f"情感分析任务执行失败: {task_id}, 错误: {e}")
        await mongodb_client.update_task_status(task_id, "failed", str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
