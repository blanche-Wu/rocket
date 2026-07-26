import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch, FancyBboxPatch, Polygon
import seaborn as sns
from scipy import interpolate
import matplotlib.cm as cm

# ========== 1. 设置中文字体和样式 ==========
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
sns.set_style("whitegrid")

# 定义颜色方案
colors = {
    'cost_priority': '#2E86AB',  # 成本优先 - 深蓝
    'balanced': '#A23B72',  # 平衡型 - 紫色
    'time_priority': '#F18F01',  # 时间优先 - 橙色
    'env_optimal': '#73AB84',  # 环保最优 - 绿色
    'elevator': '#3498DB',  # 太空电梯 - 蓝色
    'rocket': '#E74C3C',  # 火箭 - 红色
    'good': '#27AE60',  # 好 - 绿色
    'medium': '#F39C12',  # 中等 - 橙色
    'bad': '#C0392B'  # 差 - 红色
}

# ========== 2. 数据定义 ==========
strategies = ['成本优先型', '平衡型', '时间优先型', '环保最优型']
alpha_values = [0.96, 0.88, 0.46, 0.98]

# 环境指标数据 (归一化到0-1，值越低越好)
env_data = {
    '碳排放': [0.12, 0.23, 0.71, 0.08],
    '能耗': [0.15, 0.25, 0.85, 0.10],
    '大气污染': [0.08, 0.15, 0.65, 0.05],
    '碎片风险': [0.02, 0.05, 0.45, 0.01],
    '生态扰动': [0.10, 0.18, 0.55, 0.08]
}

env_scores = [0.12, 0.23, 0.71, 0.08]  # 综合环境评分

# 时间-成本-环境数据
alpha_range = np.linspace(0, 1, 21)
time_data = []
cost_data = []
env_data_full = []

for alpha in alpha_range:
    # 模拟模型计算
    time = 86.1 + (186.2 - 86.1) * (1 - alpha) ** 1.5  # 非线性关系
    cost = 30.6 + (80.0 - 30.6) * (1 - alpha) ** 0.8
    env = 0.08 + (0.88 - 0.08) * (1 - alpha) ** 1.2

    time_data.append(time)
    cost_data.append(cost)
    env_data_full.append(env)

# ========== 3. 图表1：综合环境评分对比图 ==========
plt.figure(figsize=(12, 8))
ax = plt.subplot(111)

x = np.arange(len(strategies))
width = 0.6

bars = ax.bar(x, env_scores, width,
              color=[colors['cost_priority'], colors['balanced'],
                     colors['time_priority'], colors['env_optimal']],
              edgecolor='black', linewidth=1.5)

ax.set_xlabel('transportation strategy', fontsize=14, fontweight='bold')
ax.set_ylabel('comprehensive environmental score (0-1)', fontsize=14, fontweight='bold')
ax.set_title('Comparison of Environmental Impact of Different Transportation Strategies', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels([f'{s}\n(α={α})' for s, α in zip(strategies, alpha_values)],
                   fontsize=12)
ax.set_ylim(0, 0.8)
ax.grid(axis='y', alpha=0.3)

# 添加数据标签
for bar, score in zip(bars, env_scores):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
            f'{score:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# 添加说明文本
plt.figtext(0.5, 0.01,
            'Note: A lower environmental score indicates reduced environmental impact, with α representing the proportion of space elevator transportation.',
            ha='center', fontsize=10, style='italic')

plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('图1_综合环境评分对比.png', bbox_inches='tight', dpi=300)
plt.show()

# ========== 4. 图表2：各指标雷达图 ==========
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(111, projection='polar')

# 雷达图设置
categories = list(env_data.keys())
N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # 闭合图形

# 绘制四种策略的雷达图
for i, strategy in enumerate(strategies):
    values = []
    for category in categories:
        values.append(env_data[category][i])
    values += values[:1]  # 闭合数据

    color_map = [colors['cost_priority'], colors['balanced'],
                 colors['time_priority'], colors['env_optimal']]

    ax.plot(angles, values, 'o-', linewidth=2, label=strategies[i],
            color=color_map[i], markersize=8)
    ax.fill(angles, values, alpha=0.1, color=color_map[i])

# 设置雷达图
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'], fontsize=10)
ax.set_title('Environmental Index Radar Chart of Different Strategies', fontsize=16, fontweight='bold', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=11)

plt.tight_layout()
plt.savefig('图2_环境指标雷达图.png', bbox_inches='tight', dpi=300)
plt.show()

# ========== 5. 图表3：运输方式贡献分解图 ==========
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

# 数据：各运输方式对总环境影响的贡献比例
categories = ['Carbon emissions', 'Energy consumption', 'Air pollution', 'Ecological disturbance', 'Fragmented risks']
elevator_contrib = [0.05, 0.45, 0.10, 0.80, 0.01]  # 太空电梯贡献
rocket_contrib = [0.95, 0.55, 0.90, 0.20, 0.99]  # 火箭贡献

x = np.arange(len(categories))
width = 0.35

# 左侧：绝对值对比
bars1 = ax1.bar(x - width / 2, elevator_contrib, width,
                label='space elevator', color=colors['elevator'], edgecolor='black')
bars2 = ax1.bar(x + width / 2, rocket_contrib, width,
                label='rocket', color=colors['rocket'], edgecolor='black')

ax1.set_xlabel('Environment pointers', fontsize=13, fontweight='bold')
ax1.set_ylabel('Proportion of contribution', fontsize=13, fontweight='bold')
ax1.set_title('(a) The Contribution of Transportation Mode to Environmental Indicators', fontsize=14, fontweight='bold', pad=15)
ax1.set_xticks(x)
ax1.set_xticklabels(categories, fontsize=11)
ax1.set_ylim(0, 1.1)
ax1.legend(fontsize=11)
ax1.grid(axis='y', alpha=0.3)

# 添加百分比标签
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
             f'{height * 100:.0f}%', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.02,
             f'{height * 100:.0f}%', ha='center', va='bottom', fontsize=9)

# 右侧：堆叠条形图
bottom = np.zeros(2)
colors_detail = ['#2980B9', '#27AE60', '#F1C40F', '#E67E22', '#E74C3C']

for i, category in enumerate(categories):
    contributions = [elevator_contrib[i], rocket_contrib[i]]
    ax2.bar(['space elevator', 'Traditional rocket'], contributions, bottom=bottom,
            label=category, color=colors_detail[i], edgecolor='black', width=0.6)
    bottom += contributions

ax2.set_ylabel('Cumulative contribution ratio', fontsize=13, fontweight='bold')
ax2.set_title('(b) mode contribution decomposition', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylim(0, 2.5)
ax2.legend(title='Environment pointers', fontsize=10, title_fontsize=11)
ax2.grid(axis='y', alpha=0.3)

plt.suptitle('Contribution Decomposition of Transportation Mode to Environmental Impact', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('图3_运输方式贡献分解.png', bbox_inches='tight', dpi=300)
plt.show()

# ========== 6. 图表4：时间-环境权衡曲线 ==========
fig, ax1 = plt.subplots(figsize=(12, 8))

# 主坐标轴：时间
ax1.plot(alpha_range, time_data, 'b-', linewidth=3, label='运输时间',
         color=colors['elevator'], marker='o', markersize=6)
ax1.set_xlabel('space elevator transport ratio (α)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Transportation time (years)', fontsize=14, fontweight='bold', color=colors['elevator'])
ax1.tick_params(axis='y', labelcolor=colors['elevator'])
ax1.set_ylim(80, 200)
ax1.grid(True, alpha=0.3)

# 次坐标轴：环境评分
ax2 = ax1.twinx()
ax2.plot(alpha_range, env_data_full, 'g-', linewidth=3, label='Environmental rating',
         color=colors['env_optimal'], marker='s', markersize=6)
ax2.set_ylabel('Environmental rating (0-1)', fontsize=14, fontweight='bold', color=colors['env_optimal'])
ax2.tick_params(axis='y', labelcolor=colors['env_optimal'])
ax2.set_ylim(0, 1.0)

# 标记关键点
key_alphas = [0.0, 0.46, 0.88, 0.96, 1.0]
key_labels = ['纯火箭', '时间优先', '平衡型', '成本优先', '纯电梯']

for alpha, label in zip(key_alphas, key_labels):
    idx = np.abs(alpha_range - alpha).argmin()
    time_val = time_data[idx]
    env_val = env_data_full[idx]

    ax1.plot(alpha, time_val, 'ro', markersize=10)
    ax2.plot(alpha, env_val, 'go', markersize=10)

    ax1.annotate(f'{label}\nα={alpha}', xy=(alpha, time_val),
                 xytext=(10, 10), textcoords='offset points',
                 fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

# 添加拐点标记
inflection_alpha = 0.88
idx_inf = np.abs(alpha_range - inflection_alpha).argmin()
ax1.axvline(x=inflection_alpha, color='r', linestyle='--', alpha=0.5, linewidth=2)
ax1.text(inflection_alpha + 0.02, 150, 'optimal inflection point\nα=0.88', fontsize=11,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

# 组合图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=11)

plt.title('Analysis of Time-Environment Trade-off Curve', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('图4_时间环境权衡曲线.png', bbox_inches='tight', dpi=300)
plt.show()

# ========== 7. 图表5：碳约束下的可行域分析 ==========
fig, ax = plt.subplots(figsize=(12, 8))

# 生成网格数据
alpha_mesh = np.linspace(0, 1, 100)
co2_mesh = np.linspace(0, 1, 100)
A, C = np.meshgrid(alpha_mesh, co2_mesh)

# 计算碳排放函数：E(α) = 0.05α + 0.5(1-α)
E = 0.05 * A + 0.5 * (1 - A)

# 绘制等高线
contour = ax.contourf(A, C, E, levels=20, cmap='RdYlGn_r', alpha=0.7)
plt.colorbar(contour, ax=ax, label='carbon emission intensity(t CO₂/t payload)')

## Draw constraint lines
co2_constraints = [0.1, 0.3, 0.5]
colors_constraint = ['#27AE60', '#F39C12', '#E74C3C']
labels_constraint = ['Strict Constraint (0.1 Gt)', 'Medium Constraint (0.3 Gt)', 'Loose Constraint (0.5 Gt)']

for constraint, color, label in zip(co2_constraints, colors_constraint, labels_constraint):
    # Solve equation: 0.05α + 0.5(1-α) = constraint
    if constraint <= 0.5:
        alpha_solution = (0.5 - constraint) / 0.45
        if 0 <= alpha_solution <= 1:
            ax.axvline(x=alpha_solution, color=color, linestyle='--', linewidth=2.5,
                       label=f'{label}: α≥{alpha_solution:.2f}')

            # Fill feasible region
            if constraint == 0.1:  # Strictest constraint
                ax.fill_betweenx([0, 1], alpha_solution, 1, color='green', alpha=0.2)
            elif constraint == 0.3:
                ax.fill_betweenx([0, 1], alpha_solution, 1, color='yellow', alpha=0.2)
            else:
                ax.fill_betweenx([0, 1], alpha_solution, 1, color='red', alpha=0.1)

# Mark recommended strategy points
strategy_points = {
    'Time Priority': (0.46, 0.27),
    'Balanced': (0.88, 0.06),
    'Cost Priority': (0.96, 0.05),
    'Environmental Optimal': (0.98, 0.048)
}

for name, (alpha, co2) in strategy_points.items():
    ax.plot(alpha, co2, 'o', markersize=12, markeredgecolor='black',
            markeredgewidth=2, color='white')
    ax.annotate(name, xy=(alpha, co2), xytext=(5, 5),
                textcoords='offset points', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))

ax.set_xlabel('Space Elevator Transport Ratio (α)', fontsize=14, fontweight='bold')
ax.set_ylabel('Carbon Emission Intensity (t CO₂/t payload)', fontsize=14, fontweight='bold')
ax.set_title('Feasible Region Analysis under Carbon Constraints', fontsize=16, fontweight='bold', pad=20)
ax.set_xlim(0, 1)
ax.set_ylim(0, 0.6)
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('Figure5_Carbon_Constraint_Feasible_Region.png', bbox_inches='tight', dpi=300)
plt.show()

# ========== 8. Figure 6: Sensitivity Analysis ==========
fig = plt.figure(figsize=(14, 10))
gs = gridspec.GridSpec(2, 2, hspace=0.3, wspace=0.25)

# Subplot 1: Weight Sensitivity
ax1 = plt.subplot(gs[0, 0])
weight_scenarios = ['Baseline Weights', 'Emphasize Carbon', 'Emphasize Debris Risk', 'Balanced Weights']
optimal_alphas = [0.88, 0.92, 0.85, 0.87]
colors_scenario = [colors['balanced'], colors['good'], colors['medium'], colors['cost_priority']]

bars = ax1.bar(weight_scenarios, optimal_alphas,
               color=colors_scenario, edgecolor='black', linewidth=1.5)

ax1.set_ylabel('Optimal α Value', fontsize=12, fontweight='bold')
ax1.set_title('(a) Optimal Strategy under Different Weight Settings', fontsize=13, fontweight='bold', pad=10)
ax1.set_ylim(0.8, 1.0)
ax1.grid(axis='y', alpha=0.3)

for bar, alpha in zip(bars, optimal_alphas):
    ax1.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.005,
             f'{alpha:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Subplot 2: Technical Parameter Sensitivity
ax2 = plt.subplot(gs[0, 1])
params = ['Rocket Carbon\n-20%', 'Grid Carbon Intensity\n-30%', 'Rocket Success Rate\n+5%', 'Elevator Efficiency\n+10%']
alpha_changes = [-0.05, +0.08, -0.03, +0.04]
colors_change = [colors['good'] if x > 0 else colors['bad'] for x in alpha_changes]

bars = ax2.bar(params, np.abs(alpha_changes), color=colors_change,
               edgecolor='black', linewidth=1.5)

ax2.set_ylabel('Change in α Value', fontsize=12, fontweight='bold')
ax2.set_title('(b) Impact of Technical Parameter Changes on Optimal α', fontsize=13, fontweight='bold', pad=10)
ax2.set_ylim(0, 0.1)
ax2.grid(axis='y', alpha=0.3)

for bar, change in zip(bars, alpha_changes):
    sign = '+' if change > 0 else '-'
    ax2.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.002,
             f'{sign}{abs(change):.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Subplot 3: Marginal Benefit Analysis
ax3 = plt.subplot(gs[1, :])
alpha_for_margin = np.linspace(0.8, 1.0, 21)
marginal_time = [15 * (1 - x) ** 2 for x in alpha_for_margin]  # Simulated data
marginal_cost = [8 * (1 - x) ** 1.5 for x in alpha_for_margin]  # Simulated data
marginal_env = [0.2 * (1 - x) ** 0.8 for x in alpha_for_margin]  # Simulated data

ax3.plot(alpha_for_margin, marginal_time, 'b-', linewidth=3, label='Time Marginal Benefit')
ax3.plot(alpha_for_margin, marginal_cost, 'r-', linewidth=3, label='Cost Marginal Benefit')
ax3.plot(alpha_for_margin, marginal_env, 'g-', linewidth=3, label='Environmental Marginal Benefit')

ax3.set_xlabel('Space Elevator Ratio (α)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Marginal Benefit (Normalized)', fontsize=12, fontweight='bold')
ax3.set_title('(c) Marginal Benefit Analysis: Finding the Optimal Balance Point', fontsize=13, fontweight='bold', pad=10)
ax3.legend(fontsize=11)
ax3.grid(True, alpha=0.3)

# Mark balance point
balance_alpha = 0.88
ax3.axvline(x=balance_alpha, color='black', linestyle='--', alpha=0.7, linewidth=2)
ax3.text(balance_alpha + 0.01, 0.5, 'Recommended Balance Point\nα=0.88', fontsize=11,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

plt.suptitle('Sensitivity Analysis of Environmental Impact Model', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('Figure6_Sensitivity_Analysis.png', bbox_inches='tight', dpi=300)
plt.show()

print("所有6张图表已生成完成！")
print("已保存文件：")
print("1. 图1_综合环境评分对比.png")
print("2. 图2_环境指标雷达图.png")
print("3. 图3_运输方式贡献分解.png")
print("4. 图4_时间环境权衡曲线.png")
print("5. 图5_碳约束可行域分析.png")
print("6. 图6_敏感性分析.png")