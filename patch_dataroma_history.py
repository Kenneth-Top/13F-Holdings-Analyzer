import logging
from backend.config import FUNDS
from backend.database import init_db
from backend.scraper import _fallback_dataroma

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    init_db()
    
    # 查找所有配置了 dataroma_id 且没走原 SEC 通道的基金
    d_funds = [f for f in FUNDS if f.get("dataroma_id")]
    
    logger.info(f"即将补充 {len(d_funds)} 家 Dataroma 基金的历史季度数据")
    
    # 我们只补 25Q3, 25Q2, 25Q1
    target_qts = ["2025-Q3", "2025-Q2", "2025-Q1"]
    
    for idx, fund in enumerate(d_funds):
        logger.info(f"--- [{idx+1}/{len(d_funds)}] 处理 {fund['name_cn']} ---")
        cik = fund.get("cik") or f"D-{fund['dataroma_id']}"
        _fallback_dataroma(fund["dataroma_id"], cik, fund["name_cn"], target_quarters=target_qts)

    logger.info("全部历史补充完成！")
