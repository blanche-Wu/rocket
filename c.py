import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ==================== 配置与参数设置 ====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')


class LunarTransportOptimizer:
    def __init__(self):
        # 基础参数
        self.D = 1e8  # 总需求量 (公吨)
        self.P_e = 537000  # 太空电梯年运力 (公吨/年)
        self.c_e = 10100  # 太空电梯单位成本 (美元/公吨)
        self.C_build_e = 6e8  # 太空电梯建造成本 (美元)

        # 调整后的火箭参数
        self.P_r = 62500 * 10  # 火箭年运力 (公吨/年)
        self.c_r = 800000  # 火箭单位成本 (美元/公吨)

        # 计算临界比例 (时间最短点)
        self.alpha_crit = self.P_e / (self.P_e + self.P_r)

    def calculate_scenario(self, alpha, label=""):
        """计算特定比例下的指标"""
        D_e = alpha * self.D
        D_r = (1 - alpha) * self.D

        # 时间计算
        T_e = D_e / self.P_e if alpha > 0 else 0
        T_r = D_r / self.P_r if alpha < 1 else 0
        T = max(T_e, T_r)

        # 成本计算 (美元)
        cost_transport = (D_e * self.c_e + D_r * self.c_r)

        # 如果使用电梯(alpha > 0)，加入建造成本
        fixed_cost = self.C_build_e if alpha > 0 else 0

        C_total_trillion = (cost_transport + fixed_cost) / 1e12  # 转换为万亿美元

        return {
            'Scenario': label,  # 方案名称
            'Space Elevator Proportion': alpha,  # 太空电梯比例
            'Transport Time (years)': T,  # 运输时间 (年)
            'Total Cost (trillion USD)': C_total_trillion,  # 总成本 (万亿美元)
            'Space Elevator Volume (million tons)': D_e / 1e6,  # 太空电梯量 (百万吨)
            'Rocket Volume (million tons)': D_r / 1e6  # 火箭量 (百万吨)
        }

    def find_optimal_alpha(self, time_weight=0.5, cost_weight=0.5, num_points=100):
        """
        基于加权时间-成本优化找到最优alpha
        time_weight + cost_weight = 1
        """
        alphas = np.linspace(0, 1, num_points)
        results = []

        for alpha in alphas:
            scenario = self.calculate_scenario(alpha, "")
            results.append({
                'alpha': alpha,
                'time': scenario['Transport Time (years)'],
                'cost': scenario['Total Cost (trillion USD)']
            })

        df_results = pd.DataFrame(results)

        # 将时间和成本归一化到 [0, 1] 范围
        max_time = df_results['time'].max()
        min_time = df_results['time'].min()
        max_cost = df_results['cost'].max()
        min_cost = df_results['cost'].min()

        df_results['time_norm'] = (df_results['time'] - min_time) / (max_time - min_time) if max_time > min_time else 0
        df_results['cost_norm'] = (df_results['cost'] - min_cost) / (max_cost - min_cost) if max_cost > min_cost else 0

        # 计算加权得分
        df_results['score'] = time_weight * df_results['time_norm'] + cost_weight * df_results['cost_norm']

        # 找到最优alpha (最小化得分)
        optimal_row = df_results.loc[df_results['score'].idxmin()]

        return optimal_row['alpha'], optimal_row['time'], optimal_row['cost']

    def get_comparison_data(self, time_weight=0.5, cost_weight=0.5):
        """基于权重生成代表性场景"""
        sols = []

        # 1. 方案B: 纯火箭 (alpha = 0)
        sols.append(self.calculate_scenario(0.0, "Scenario B (Rockets only)"))

        # 2. 基于权重计算最优alpha
        optimal_alpha, optimal_time, optimal_cost = self.find_optimal_alpha(time_weight, cost_weight)
        sols.append(self.calculate_scenario(optimal_alpha, f"Optimal (Time={time_weight}, Cost={cost_weight})"))

        # 3. 混合方案: 最短时间点
        sols.append(self.calculate_scenario(self.alpha_crit, "Hybrid (Shortest Time)"))

        # 4. 混合方案: 平衡点
        alpha_balanced = (self.alpha_crit + 1.0) / 2
        sols.append(self.calculate_scenario(alpha_balanced, "Hybrid (Balanced)"))

        # 5. 方案A: 纯太空电梯 (alpha = 1)
        sols.append(self.calculate_scenario(1.0, "Scenario A (Elevator only)"))

        return pd.DataFrame(sols), optimal_alpha, optimal_time, optimal_cost

    def run_sensitivity(self, base_alpha):
        """围绕基础alpha进行敏感性分析"""
        target_alpha = base_alpha
        base_params = {'Elevator Capacity': self.P_e, 'Rocket Capacity': self.P_r,
                       'Elevator Cost': self.c_e, 'Rocket Cost': self.c_r}
        variations = np.linspace(0.8, 1.2, 11)
        results = []

        for p_name, p_val in base_params.items():
            attr_name = {'Elevator Capacity': 'P_e', 'Rocket Capacity': 'P_r',
                         'Elevator Cost': 'c_e', 'Rocket Cost': 'c_r'}[p_name]
            orig_val = getattr(self, attr_name)
            for v in variations:
                setattr(self, attr_name, p_val * v)
                res = self.calculate_scenario(target_alpha)
                results.append({'Parameter': p_name, 'Variation (%)': (v - 1) * 100,
                                'Total Cost (trillion USD)': res['Total Cost (trillion USD)']})
            setattr(self, attr_name, orig_val)
        return pd.DataFrame(results)


# ==================== 交互式权重调整 ====================
def interactive_optimization(time_weight=0.5, cost_weight=0.5):
    """交互式优化的主函数"""
    opt = LunarTransportOptimizer()

    # 确保权重总和为1
    if abs(time_weight + cost_weight - 1) > 0.01:
        print("警告: 权重总和应为1。正在归一化...")
        total = time_weight + cost_weight
        time_weight = time_weight / total
        cost_weight = cost_weight / total

    print(f"\n优化权重: 时间={time_weight:.2f}, 成本={cost_weight:.2f}")

    df_sols, optimal_alpha, optimal_time, optimal_cost = opt.get_comparison_data(time_weight, cost_weight)

    # 打印表格
    print("\n" + "=" * 80)
    print(f"{'运输方案详情 (包含建造成本)':^70}")
    print("=" * 80)
    print(df_sols[['Scenario', 'Space Elevator Proportion', 'Transport Time (years)',
                   'Total Cost (trillion USD)']].to_string(index=False))
    print(f"\n最优配置: alpha={optimal_alpha:.3f}, 时间={optimal_time:.1f}年, 成本={optimal_cost:.2f}万亿美元")

    # 图表1: 运输量分配
    plt.figure(figsize=(12, 7))
    x = df_sols['Scenario']
    plt.bar(x, df_sols['Space Elevator Volume (million tons)'], label='Space Elevator Volume', color='#2c3e50',
            alpha=0.8)
    plt.bar(x, df_sols['Rocket Volume (million tons)'], bottom=df_sols['Space Elevator Volume (million tons)'],
            label='Rocket Volume', color='#e74c3c', alpha=0.8)
    plt.title('Fig 1: Material Transport Volume by Scenario (million tons)', fontsize=14)
    plt.ylabel('Transport Volume (million tons)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'1_Transport_Allocation_Time{time_weight}_Cost{cost_weight}.png', dpi=300)

    # 图表2: 时间-成本双维度对比
    fig, ax1 = plt.subplots(figsize=(12, 7))
    ax2 = ax1.twinx()
    indices = np.arange(len(df_sols))
    width = 0.35

    ax1.bar(indices - width / 2, df_sols['Transport Time (years)'], width, label='Transport Time', color='#27ae60',
            alpha=0.7)
    ax2.bar(indices + width / 2, df_sols['Total Cost (trillion USD)'], width, label='Total Cost', color='#f1c40f',
            alpha=0.7)

    ax1.set_ylabel('Transport Time (years)', color='#27ae60', fontsize=12)
    ax2.set_ylabel('Total Cost (trillion USD)', color='#f39c12', fontsize=12)
    ax1.set_xticks(indices)
    ax1.set_xticklabels(df_sols['Scenario'], rotation=45)
    plt.title(f'Fig 2: Time-Cost Tradeoff Analysis (Time Weight={time_weight}, Cost Weight={cost_weight})', fontsize=14)
    # 合并图例
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc='upper center')
    plt.tight_layout()
    plt.savefig(f'2_Time_Cost_Tradeoff_Time{time_weight}_Cost{cost_weight}.png', dpi=300)

    # 图表3: 帕累托前沿曲线
    alphas = np.linspace(opt.alpha_crit, 1.0, 100)
    pareto_df = pd.DataFrame([opt.calculate_scenario(a) for a in alphas])

    plt.figure(figsize=(12, 7))
    plt.plot(pareto_df['Transport Time (years)'], pareto_df['Total Cost (trillion USD)'], color='blue',
             label='Efficient Frontier (Hybrid Solutions)')
    plt.scatter(df_sols['Transport Time (years)'], df_sols['Total Cost (trillion USD)'], color='red', s=80, zorder=5)
    for i, txt in enumerate(df_sols['Scenario']):
        plt.annotate(txt, (df_sols['Transport Time (years)'][i], df_sols['Total Cost (trillion USD)'][i]),
                     xytext=(5, 5), textcoords='offset points', fontsize=9)

    # 标记最优配置点
    plt.scatter([optimal_time], [optimal_cost], color='green', s=120, zorder=10,
                label=f'Optimal (α={optimal_alpha:.3f})')
    plt.annotate(f'Optimal\nTime={optimal_time:.1f}y\nCost={optimal_cost:.2f}T',
                 (optimal_time, optimal_cost), xytext=(10, 10), textcoords='offset points',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="green", alpha=0.2))

    plt.xlabel('Transport Time (years)')
    plt.ylabel('Total Cost (trillion USD)')
    plt.title(f'Fig 3: Pareto Frontier Analysis with Optimal Point (Time Weight={time_weight})', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'3_Pareto_Frontier_Time{time_weight}_Cost{cost_weight}.png', dpi=300)

    # 图表4: 敏感性分析 (基于最优alpha)
    df_sens = opt.run_sensitivity(optimal_alpha)
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df_sens, x='Variation (%)', y='Total Cost (trillion USD)', hue='Parameter', marker='o')
    plt.title(f'Fig 4: Sensitivity Analysis of Key Parameters (Optimal α={optimal_alpha:.3f})', fontsize=14)
    plt.xlabel('Parameter Variation (%)')
    plt.ylabel('Total Cost (trillion USD)')
    plt.axvline(0, color='black', linestyle='--', alpha=0.3, label='Baseline')
    plt.legend(title='Parameter')
    plt.tight_layout()
    plt.savefig(f'4_Sensitivity_Analysis_Time{time_weight}_Cost{cost_weight}.png', dpi=300)

    plt.show()

    return df_sols, optimal_alpha


# ==================== 测试不同权重组合 ====================
if __name__ == "__main__":
    # 示例权重组合
    weight_combinations = [
        (0.8, 0.2),  # 重视时间
        (0.5, 0.5),  # 平衡
        (0.2, 0.8),  # 重视成本
    ]

    for time_w, cost_w in weight_combinations:
        print("\n" + "=" * 80)
        print(f"执行优化: 时间权重={time_w}, 成本权重={cost_w}")
        print("=" * 80)
        df_results, opt_alpha = interactive_optimization(time_w, cost_w)
        print(f"\n最优太空电梯比例: {opt_alpha:.3f}")

        # 保存结果到CSV
        df_results.to_csv(f'results_Time{time_w}_Cost{cost_w}.csv', index=False)
        print(f"结果已保存至: results_Time{time_w}_Cost{cost_w}.csv")