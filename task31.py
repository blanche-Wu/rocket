import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
def plot_sensitivity_analysis():
    # 数据准备
    # 回收率从 85% 到 99%
    recycle_rates = np.linspace(0.85, 0.99, 50)

    # 常量
    total_demand_year = 5.18e8  # kg (51.8万吨基础需求)
    reserve_factor = 1.2

    # 混合策略加权平均成本 (90% SE @ $300, 10% Rocket @ $800) + $0.1处理费
    # Avg Transport Cost = 0.9*300 + 0.1*800 = 270 + 80 = $350/kg
    # Total Unit Cost = 350 + 0.1 (processing is negligible but let's keep logic) = $350.1/kg
    avg_cost_per_kg = 350

    # 计算总成本 (Billion USD)
    # Cost = Demand * (1 - Rate) * Reserve * Avg_Cost / 1e9
    total_costs = [total_demand_year * (1 - r) * reserve_factor * avg_cost_per_kg / 1e9 for r in recycle_rates]

    # 关键点标记 (90%, 95%, 98%)
    key_points_x = [0.90, 0.95, 0.98]
    key_points_y = [total_demand_year * (1 - r) * reserve_factor * avg_cost_per_kg / 1e9 for r in key_points_x]

    # 创建画布
    plt.figure(figsize=(12, 7))

    # 绘制曲线
    plt.plot(recycle_rates * 100, total_costs, linewidth=3, color='#8e44ad', label='Total Annual Cost')

    # 填充曲线下方区域
    plt.fill_between(recycle_rates * 100, total_costs, color='#8e44ad', alpha=0.1)

    # 标记关键点
    plt.scatter([x * 100 for x in key_points_x], key_points_y, color='red', s=80, zorder=5)

    # 添加注释 (Annotations)
    annotations = [
        (90, key_points_y[0], "Current Tech (90%)\n$21.8 B"),
        (95, key_points_y[1], "Improved (95%)\n$10.9 B (-50%)"),
        (98, key_points_y[2], "Target (98%)\n$4.4 B (-80%)")
    ]

    for x, y, text in annotations:
        plt.annotate(text, xy=(x, y), xytext=(x + 1, y + 10),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                     fontsize=11, fontweight='bold')

    # 设置标题和标签
    plt.title('Sensitivity Analysis: Impact of ECLSS Recycle Rate on Logistics Cost', fontsize=16)
    plt.xlabel('Water Recycling Rate (%)', fontsize=13)
    plt.ylabel('Total Annual Logistics Cost (Billion USD)', fontsize=13)

    # 设置坐标轴格式
    plt.xticks(np.arange(85, 100, 1))
    plt.grid(True, linestyle='--', alpha=0.7)

    # 保存图片
    plt.tight_layout()
    plt.savefig('Figure_3_Sensitivity_RecycleRate.png', dpi=300)
    plt.show()


# 执行绘图
plot_sensitivity_analysis()