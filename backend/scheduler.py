# -*- coding: utf-8 -*-
"""
定时调度器
使用 APScheduler 实现 13F 数据的定期自动采集
"""

import sys
import os
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCHEDULE_MONTHS, SCHEDULE_DAY, SCHEDULE_HOUR
from scraper import scrape_all
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def scheduled_scrape():
    """定时任务: 爬取最新一期 13F"""
    logger.info("=== 定时任务触发: 开始爬取最新 13F 数据 ===")
    try:
        scrape_all(latest_only=True)
        logger.info("=== 定时任务完成 ===")
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")


def main():
    init_db()

    scheduler = BlockingScheduler()

    # 每季度自动执行 (2月/5月/8月/11月 的 16 日上午 9 点)
    trigger = CronTrigger(
        month=SCHEDULE_MONTHS,
        day=SCHEDULE_DAY,
        hour=SCHEDULE_HOUR,
        minute="0"
    )

    scheduler.add_job(
        scheduled_scrape,
        trigger=trigger,
        id="13f_quarterly_scrape",
        name="13F 季度数据采集",
        replace_existing=True,
    )

    logger.info(f"调度器已启动")
    logger.info(f"定时任务: 每年 {SCHEDULE_MONTHS} 月 {SCHEDULE_DAY} 日 {SCHEDULE_HOUR}:00 自动执行")
    logger.info("按 Ctrl+C 停止")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器已停止")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # 立即执行一次
        init_db()
        scheduled_scrape()
    else:
        main()
