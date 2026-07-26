import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置绘图风格
sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'  # 确保字体兼容


def plot_cost_comparison():
    # 数据准备 (单位: 十亿美元 Billion USD)
    scenarios = ['Scenario A:\nPure Rocket', 'Scenario B:\nPure Elevator', 'Scenario C:\nHybrid (Recommended)']
    costs = [497.66, 186.66, 217.76]

    # 定义颜色 (红色代表昂贵，绿色代表便宜，蓝色代表推荐)
    colors = ['#e74c3c', '#2ecc71', '#3498db']

    # 创建画布
    plt.figure(figsize=(10, 6))
    bars = plt.bar(scenarios, costs, color=colors, width=0.6, alpha=0.9)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 5,
                 f'${height:.2f} B',
                 ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 设置标题和标签 (英文)
    plt.title('Annual Water Logistics Cost Comparison (2050)', fontsize=16, pad=20)
    plt.ylabel('Total Annual Cost (Billion USD)', fontsize=12)
    plt.ylim(0, 600)  # 设置Y轴范围留出空间

    # --- 修改了这里 ---
    # 添加网格线 (仅Y轴，关闭X轴网格)
    plt.grid(visible=False, axis='x')
    # ------------------

    # 保存图片
    plt.tight_layout()
    plt.savefig('Figure_1_Cost_Comparison.png', dpi=300)
    plt.show()




def plot_hybrid_breakdown():
    # 数据准备
    # 质量分布 (Mass Distribution)
    mass_labels = ['Space Elevator (90%)', 'Rocket (10%)']
    mass_sizes = [90, 10]  # 百分比

    # 成本分布 (Cost Distribution)
    # 计算逻辑: SE cost = 55980t * $300k = 16.79B, Rocket cost = 6220t * $800k = 4.98B
    # Total transport cost approx 21.77B (忽略微小的水处理费以简化图表)
    se_cost = 16.79
    rocket_cost = 4.98
    total_c = se_cost + rocket_cost
    cost_sizes = [se_cost / total_c * 100, rocket_cost / total_c * 100]
    cost_labels = [f'SE Cost\n(${se_cost:.2f}B)', f'Rocket Cost\n(${rocket_cost:.2f}B)']

    # 颜色设置
    colors = ['#3498db', '#e67e22']  # 蓝色对应电梯，橙色对应火箭

    # 创建画布 (1行2列)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

    # 绘制左图：质量分布
    wedges1, texts1, autotexts1 = ax1.pie(mass_sizes, labels=mass_labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, explode=(0, 0.1), shadow=True)
    ax1.set_title('Logistics Mass Distribution', fontsize=14, fontweight='bold')

    # 绘制右图：成本分布
    wedges2, texts2, autotexts2 = ax2.pie(cost_sizes, labels=cost_labels, autopct='%1.1f%%',
                                          startangle=90, colors=colors, explode=(0, 0.1), shadow=True)
    ax2.set_title('Logistics Cost Distribution', fontsize=14, fontweight='bold')

    # 统一字体设置
    for text in texts1 + texts2 + autotexts1 + autotexts2:
        text.set_fontsize(11)

    # 添加总标题
    plt.suptitle('Analysis of Recommended Hybrid Strategy (Scenario C)', fontsize=18)

    # 保存图片
    plt.tight_layout()
    plt.savefig('Figure_2_Hybrid_Breakdown.png', dpi=300)
    plt.show()


if __name__ == "__main__":
     plot_cost_comparison()
     plot_hybrid_breakdown()