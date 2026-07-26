import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Maintain English font settings
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')


class RobustnessAnalyzer:
    def __init__(self):
        # Basic parameters
        self.D = 1e8  # Total demand (metric tons)
        self.P_e_base = 537000  # Base elevator capacity (metric tons/year)
        self.P_r_base = 625000  # Base rocket capacity (scaled by 10)
        self.c_e_base = 10100  # Base elevator unit cost (USD/ton)
        self.c_r_base = 800000  # Base rocket unit cost (USD/ton)
        self.F_e = 6e8  # Elevator construction cost (USD)
        self.V_mat = 50000  # Material value (USD/ton)

    def calculate_impact(self, scenario_name, eta_e, eta_r, p_fail, k_e):
        # Adjust effective capacities
        P_e_eff = self.P_e_base * eta_e
        P_r_eff = self.P_r_base * eta_r * (1 - p_fail)

        # Adjust effective costs
        # Elevator cost = base * maintenance factor
        c_e_eff = self.c_e_base * k_e
        # Rocket cost = (launch cost + failure probability * material value) / success probability
        c_r_eff = (self.c_r_base + p_fail * self.V_mat) / (1 - p_fail)

        # Recalculate critical alpha (shortest time point)
        alpha_crit = P_e_eff / (P_e_eff + P_r_eff)

        # Calculate optimal time scenario data
        D_e = alpha_crit * self.D
        D_r = (1 - alpha_crit) * self.D

        T = max(D_e / P_e_eff, D_r / P_r_eff)
        C = (D_e * c_e_eff + D_r * c_r_eff + self.F_e) / 1e12  # Convert to trillion USD

        return {
            'Scenario': scenario_name,
            'Minimum_Time_years': T,
            'Total_Cost_trillion_USD': C,
            'Elevator_Effective_Ratio': alpha_crit,
            'Elevator_Effective_Capacity': P_e_eff,
            'Rocket_Effective_Capacity': P_r_eff
        }


analyzer = RobustnessAnalyzer()

# Define scenarios
scenarios = [
    # eta_e (elevator efficiency), eta_r (rocket weather efficiency),
    # p_fail (rocket failure rate), k_e (elevator maintenance cost factor)
    ('Ideal Conditions', 1.0, 1.0, 0.0, 1.0),
    ('Mild Disruption', 0.85, 0.90, 0.02, 1.1),  # Elevator swaying, 2% rocket failure
    ('Moderate Failure', 0.75, 0.85, 0.05, 1.3),
    ('Severe Failure', 0.60, 0.75, 0.10, 1.5)  # Significant downtime, 10% rocket failure
]

results = [analyzer.calculate_impact(*s) for s in scenarios]
df_res = pd.DataFrame(results)

print("=" * 60)
print("Impact Analysis under Non-Ideal Conditions")
print("=" * 60)
print(df_res.round(2).to_string(index=False))

# --- Plot: Time and Cost Changes under Different Scenarios ---
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

x = df_res['Scenario']
ax1.plot(x, df_res['Minimum_Time_years'], 'g-o', linewidth=2, label='Minimum Schedule (years)')
ax2.plot(x, df_res['Total_Cost_trillion_USD'], 'r--s', linewidth=2, label='Total Cost (trillion USD)')

ax1.set_ylabel('Schedule (years)', color='green', fontsize=12)
ax2.set_ylabel('Cost (trillion USD)', color='red', fontsize=12)
plt.title('Figure 5: Impact of System Failure Severity on Project Schedule and Cost')

# Combine legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('5_Non_Ideal_Conditions_Comparison.png', dpi=300)
plt.show()

# Save data
df_res.to_csv('Question2_Robustness_Analysis_Data.csv', index=False, encoding='utf-8-sig')
