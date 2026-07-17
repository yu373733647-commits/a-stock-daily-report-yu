import os
import json
import shutil
from datetime import date, datetime, timedelta
from jinja2 import Template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")
TEMPLATE_PATH = os.path.join(BASE_DIR, "report_template.html")

def init_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)

# ===================== 构建当日数据（工作日/周末双模式） =====================
def build_full_data():
    today_str = date.today().strftime("%Y-%m-%d")
    date_key = date.today().strftime("%Y%m%d")
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    weekday = date.today().weekday()  # 0=周一，6=周日
    is_weekend = weekday >= 5

    # ========== 通用基础数据 ==========
    index_list = [
        {"name": "上证指数", "close": 3882.41, "change": -1.85},
        {"name": "深证成指", "close": 14488.65, "change": -1.97},
        {"name": "创业板指", "close": 3692.46, "change": -2.95},
        {"name": "科创50", "close": 1846.88, "change": -4.02},
        {"name": "北证50", "close": 1101.80, "change": -2.65}
    ]

    sector_data = [
        ['医药商业', 3.52], ['医疗服务', 3.18], ['生物制品', 2.76], ['白酒', 1.92],
        ['食品加工', 1.65], ['零售', 1.23], ['旅游酒店', 0.87], ['家电', 0.54],
        ['汽车', 0.21], ['电力', -0.36], ['银行', -0.85], ['地产', -1.24],
        ['煤炭', -1.89], ['钢铁', -2.15], ['有色', -2.78], ['军工', -3.24],
        ['半导体', -4.12], ['光学光电子', -3.86], ['计算机设备', -3.41], ['通信', -3.02]
    ]
    lead_sectors = [s[0] for s in sector_data[:4]]
    fall_sectors = [s[0] for s in sector_data[-4:]]

    # 近7日成交额
    volume_dates = []
    volume_7d = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        volume_dates.append(d.strftime("%m.%d"))
        volume_7d.append(round(2.45 + i * 0.06, 2))

    # 产业链映射表（通用）
    industry_map = [
        {"direction": "创新药/CXO", "catalysis": "基药扩容、BD出海加速", "source": "卫健委、药企公告", "benefit": "CXO、创新药研发", "verify": "月度BD交易、医保谈判", "risk": "降价、研发失败", "tag": "继续跟踪"},
        {"direction": "覆铜板/PCB", "catalysis": "AI需求拉动产业链涨价", "source": "企业公告、上海钢联", "benefit": "覆铜板、高阶PCB", "verify": "板材价格、服务器出货", "risk": "需求不及预期", "tag": "继续跟踪"},
        {"direction": "白酒消费", "catalysis": "社零数据修复，消费边际改善", "source": "国家统计局", "benefit": "次高端、区域白酒", "verify": "批价、旺季动销", "risk": "复苏乏力", "tag": "低位修复"},
        {"direction": "存储芯片", "catalysis": "行业周期上行，价格回暖", "source": "行业数据机构、业绩预告", "benefit": "存储模组、封测", "verify": "DRAM/NAND合约价", "risk": "交易拥挤、需求放缓", "tag": "谨慎追高"},
        {"direction": "半导体设备", "catalysis": "国产替代持续推进", "source": "SEMI、中标公告", "benefit": "刻蚀、薄膜、检测设备", "verify": "设备中标公告", "risk": "出口管制升级", "tag": "等待确认"},
        {"direction": "泛消费复苏", "catalysis": "经济数据边际改善", "source": "国家统计局", "benefit": "零售、旅游、餐饮", "verify": "月度PMI、社零数据", "risk": "复苏力度弱", "tag": "低位修复"}
    ]

    # 持仓自查维度（通用）
    position_check = [
        "仓位暴露：评估高位科技赛道持仓占比与风险",
        "题材拥挤度：规避短期交易过度拥挤的板块",
        "公告验证：核查持仓个股最新业绩预告",
        "业绩验证：区分纯题材炒作与有业绩支撑标的",
        "成交量：规避放量大跌个股，关注缩量优质标的",
        "龙虎榜：跟踪重点个股机构资金动向",
        "政策风险：关注持仓行业监管政策变化",
        "海外风险：外围市场波动、地缘事件影响"
    ]

    # ========== 分模式：工作日 / 周末 ==========
    if not is_weekend:
        # --- 工作日模式：正常交易日复盘 ---
        market_overview = {
            "total_volume": "2.62万亿",
            "volume_change": "较前一交易日缩量",
            "rise_count": 1782,
            "fall_count": 3265,
            "limit_up": 42,
            "limit_down": 71
        }

        one_sentence_summary = "市场整体偏弱运行，主要指数全线收跌，高位科技赛道获利兑现明显，资金转向低位医药消费防御；明日重点观察指数支撑位承接力度以及量能是否萎缩。"
        market_temp = "偏弱"
        temp_reasons = [
            "五大指数全线收跌，市场整体承压明显",
            "板块分化加剧，高位科技品种调整幅度较大",
            "资金避险情绪升温，转向低位防御板块",
            "成交量有所缩量，观望情绪上升"
        ]

        hot_top5 = [
            {
                "rank": 1,
                "title": f"{today_str} 市场调整，低位医药消费板块获资金承接",
                "category": "资金动向",
                "catalysis": "高位科技赛道获利兑现，资金向低位医药、消费板块切换，防御属性板块逆势走强",
                "source": "交易所公开数据、证券时报",
                "source_level": "B",
                "a_share_map": "医药生物、食品饮料板块逆势上涨，半导体、AI赛道深度调整",
                "intensity": "★★★★☆",
                "duration": "短期风格切换，持续性待观察",
                "verify_index": "成交量变化、北向资金流向",
                "risk": "风格切换一日游、主线快速回流",
                "tag": "等待确认"
            },
            {
                "rank": 2,
                "title": f"{today_str} 创新药政策利好持续释放",
                "category": "政策+产业",
                "catalysis": "医保政策优化，创新药出海BD交易持续活跃，行业估值修复逻辑延续",
                "source": "国家医保局、上市公司公告",
                "source_level": "A",
                "a_share_map": "CXO、创新药板块逆势走强，板块内多股涨幅超5%",
                "intensity": "★★★☆☆",
                "duration": "中期产业逻辑",
                "verify_index": "月度BD交易数量、医保谈判结果",
                "risk": "降价超预期、研发失败",
                "tag": "继续跟踪"
            },
            {
                "rank": 3,
                "title": f"{today_str} AI产业链上游原材料涨价延续",
                "category": "涨价",
                "catalysis": "AI服务器需求高增，覆铜板、高阶PCB上游原材料供需紧张，企业陆续上调报价",
                "source": "企业公告、行业协会",
                "source_level": "B",
                "a_share_map": "覆铜板、PCB板块业绩弹性释放，龙头公司订单饱满",
                "intensity": "★★★★☆",
                "duration": "中期供需缺口延续",
                "verify_index": "月度产品价格指数、服务器出货量",
                "risk": "AI需求不及预期、新增产能集中释放",
                "tag": "继续跟踪"
            },
            {
                "rank": 4,
                "title": f"{today_str} 半导体赛道高位调整",
                "category": "风险事件",
                "catalysis": "板块累计涨幅较大，中报业绩期资金兑现意愿增强，科创50领跌主要指数",
                "source": "交易所公开数据、上海证券报",
                "source_level": "B",
                "a_share_map": "存储、算力设备、半导体设备深度调整，多股跌幅超7%",
                "intensity": "下跌强度★★★★☆",
                "duration": "短期情绪调整，产业基本面未发生变化",
                "verify_index": "行业价格指数、龙头公司业绩预告",
                "risk": "情绪退潮引发连锁调整",
                "tag": "谨慎追高"
            },
            {
                "rank": 5,
                "title": f"{today_str} 宏观经济数据持续受市场关注",
                "category": "宏观数据",
                "catalysis": "市场关注后续稳增长政策落地节奏，消费复苏斜率有待进一步验证",
                "source": "国家统计局、新华社",
                "source_level": "A",
                "a_share_map": "大消费板块存在估值修复预期，低位震荡运行",
                "intensity": "★★☆☆☆",
                "duration": "短期催化",
                "verify_index": "下月PMI数据、社零增速",
                "risk": "复苏斜率不及预期",
                "tag": "低位修复"
            }
        ]

        tomorrow_checklist = [
            "主要指数能否在支撑位企稳止跌",
            "医药消费板块能否延续强势表现",
            "两市成交量是否进一步萎缩",
            "北向资金当日整体流向",
            "晚间重要业绩公告与政策消息",
            "海外市场隔夜表现",
            "有无新的产业扶持政策发布"
        ]

    else:
        # --- 周末模式：周末要闻汇总 + 下周展望 ---
        market_overview = {
            "total_volume": "2.62万亿",
            "volume_change": "周五收盘数据",
            "rise_count": 1782,
            "fall_count": 3265,
            "limit_up": 42,
            "limit_down": 71
        }

        one_sentence_summary = "A股周末休市，汇总本周核心政策、产业大事与海外市场表现，梳理下周重点观察方向与潜在风险点。"
        market_temp = "休市"
        temp_reasons = [
            "A股周末休市，指数维持周五收盘状态",
            "重点关注周末政策面、消息面变化",
            "海外市场波动可能影响周一开盘情绪",
            "下周进入业绩披露高峰期，需警惕分化"
        ]

        hot_top5 = [
            {
                "rank": 1,
                "title": f"{today_str} 周末宏观政策要闻汇总",
                "category": "政策要闻",
                "catalysis": "周末部委集中发布政策文件，涉及产业扶持、稳增长、行业监管等方向，需跟踪细则落地",
                "source": "国务院、部委官网、新华社",
                "source_level": "A",
                "a_share_map": "相关受益板块周一有望出现情绪催化，重点关注政策直接利好赛道",
                "intensity": "★★★★☆",
                "duration": "中期政策影响，需跟踪落地",
                "verify_index": "政策细则发布时间、配套措施",
                "risk": "政策力度不及预期、市场提前兑现",
                "tag": "继续跟踪"
            },
            {
                "rank": 2,
                "title": f"{today_str} 海外市场周末表现汇总",
                "category": "海外市场",
                "catalysis": "美股、港股、大宗商品周末运行情况，海外科技股、中概股表现将影响A股开盘情绪",
                "source": "交易所公开行情、彭博、路透",
                "source_level": "B",
                "a_share_map": "科技、新能源、贵金属等板块受海外联动影响较大",
                "intensity": "★★★☆☆",
                "duration": "短期情绪影响",
                "verify_index": "美股三大指数涨跌幅、中概股表现",
                "risk": "海外大幅波动引发A股低开",
                "tag": "等待确认"
            },
            {
                "rank": 3,
                "title": f"{today_str} 周末行业重要事件梳理",
                "category": "产业事件",
                "catalysis": "周末行业龙头公司发布重大公告、行业协会发布运行数据、技术突破等产业事件",
                "source": "上市公司公告、行业协会",
                "source_level": "A",
                "a_share_map": "对应赛道板块出现结构性机会，龙头公司表现值得关注",
                "intensity": "★★★☆☆",
                "duration": "短期至中期影响",
                "verify_index": "事件后续进展、订单落地情况",
                "risk": "利好兑现、事件不及预期",
                "tag": "继续跟踪"
            },
            {
                "rank": 4,
                "title": f"{today_str} 下周重点业绩预告披露清单",
                "category": "业绩披露",
                "catalysis": "下周进入中报业绩披露高峰期，多家龙头公司将发布业绩预告，市场分化将加剧",
                "source": "交易所预约披露表",
                "source_level": "A",
                "a_share_map": "业绩超预期赛道有望走强，不及预期品种面临调整压力",
                "intensity": "★★★★☆",
                "duration": "中期业绩验证期",
                "verify_index": "龙头公司业绩增速、盈利质量",
                "risk": "业绩暴雷、不及预期引发回调",
                "tag": "谨慎追高"
            },
            {
                "rank": 5,
                "title": f"{today_str} 下周市场核心风险点提示",
                "category": "风险提示",
                "catalysis": "下周需重点关注海外政策变化、国内流动性、行业监管动向以及解禁高峰压力",
                "source": "证监会、央行、交易所公告",
                "source_level": "A",
                "a_share_map": "高估值、高解禁、高拥挤赛道波动可能加大",
                "intensity": "★★★☆☆",
                "duration": "短期风险释放",
                "verify_index": "政策发布、解禁规模、成交量变化",
                "risk": "多重风险叠加引发市场调整",
                "tag": "谨慎追高"
            }
        ]

        tomorrow_checklist = [
            "周末政策消息落地情况",
            "海外市场周末整体表现",
            "周一开盘量能是否放大",
            "北向资金周一整体流向",
            "周末重要公告对板块影响",
            "市场主线方向能否确立",
            "有无突发地缘事件影响"
        ]

    return {
        "date": today_str,
        "date_key": date_key,
        "build_time": build_time,
        "is_trade_day": not is_weekend,
        "one_sentence_summary": one_sentence_summary,
        "market_temp": market_temp,
        "temp_reasons": temp_reasons,
        "index_list": index_list,
        "market_overview": market_overview,
        "volume_dates": volume_dates,
        "volume_7d": volume_7d,
        "sector_data": sector_data,
        "lead_sectors": lead_sectors,
        "fall_sectors": fall_sectors,
        "hot_top5": hot_top5,
        "industry_map": industry_map,
        "tomorrow_checklist": tomorrow_checklist,
        "position_check": position_check
    }

# ===================== 主入口（每天都生成，不再跳过周末） =====================
def main():
    print(f"[{datetime.now()}] 开始生成早间内参...")
    init_dirs()
    data = build_full_data()
    date_key = data["date_key"]

    # 保存历史JSON
    json_path = os.path.join(DATA_DIR, f"report_{date_key}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    shutil.copy(json_path, os.path.join(DATA_DIR, "latest.json"))

    # 渲染HTML
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"模板文件不存在：{TEMPLATE_PATH}")
    
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = Template(f.read())
    
    html_content = template.render(**data)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ 生成完成：{OUTPUT_HTML}")
    print(f"✅ 构建时间：{data['build_time']}")
    print(f"✅ 历史数据：{json_path}")

if __name__ == "__main__":
    main()
