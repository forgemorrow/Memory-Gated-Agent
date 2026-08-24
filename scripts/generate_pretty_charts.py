"""
生成高级美观图表 - 用于论文
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 设置风格
sns.set_style("whitegrid")
sns.set_palette("husl")


def set_plot_style():
    """设置图表风格"""
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': '#f8f9fa',
        'axes.edgecolor': '#dee2e6',
        'axes.labelcolor': '#2c3e50',
        'xtick.color': '#6c757d',
        'ytick.color': '#6c757d',
        'grid.color': '#e9ecef',
        'grid.alpha': 0.7,
        'font.size': 12,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
    })


def generate_safety_comparison_v2():
    """生成高级安全性对比图"""
    set_plot_style()

    fig, ax = plt.subplots(figsize=(12, 7))

    # 数据
    agents = ['No Memory\n(Baseline)', 'Full Memory\n(Traditional RAG)', 'Gated Memory\n(Ours)']
    leak_rate = [0.0, 0.167, 0.0]
    colors = ['#27ae60', '#e74c3c', '#3498db']

    # 创建渐变效果的柱状图
    bars = ax.bar(agents, leak_rate, color=colors, width=0.6, edgecolor='white', linewidth=2)

    # 添加渐变效果
    for bar in bars:
        bar.set_edgecolor('white')
        bar.set_linewidth(2)

    # 添加数值标签
    for bar, value in zip(bars, leak_rate):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{value:.1%}', ha='center', va='bottom', fontsize=14, fontweight='bold',
                color='#2c3e50')

    # 添加安全阈值线
    ax.axhline(y=0.1, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7, label='Safety Threshold (10%)')

    # 设置标签
    ax.set_ylabel('Information Leakage Rate', fontsize=14, fontweight='bold')
    ax.set_title('Sensitive Information Leakage Rate Comparison', fontsize=18, fontweight='bold', pad=20)
    ax.set_ylim(0, 0.25)

    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#27ae60', edgecolor='white', label='Safe (0%)'),
        Patch(facecolor='#e74c3c', edgecolor='white', label='Unsafe (16.7%)'),
        Patch(facecolor='#3498db', edgecolor='white', label='Safe (0%)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11, framealpha=0.9)

    # 添加网格
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # 移除上边和右边边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('data/results/safety_comparison_v2.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print('生成：safety_comparison_v2.png')


def generate_radar_chart_v2():
    """生成高级雷达图"""
    set_plot_style()

    import numpy as np

    categories = ['Security', 'Utility', 'Speed', 'Privacy', 'Cost\nEfficiency']
    N = len(categories)

    # 各Agent的得分 (0-1)
    no_memory = [1.0, 0.3, 0.6, 1.0, 0.8]
    full_memory = [0.4, 0.8, 0.8, 0.3, 0.5]
    gated_memory = [0.9, 0.6, 0.3, 0.9, 0.6]

    # 计算角度
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # 闭合数据
    no_memory += no_memory[:1]
    full_memory += full_memory[:1]
    gated_memory += gated_memory[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # 设置背景色
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')

    # 绘制雷达图
    ax.plot(angles, no_memory, 'o-', linewidth=2.5, label='No Memory', color='#3498db', markersize=8)
    ax.fill(angles, no_memory, alpha=0.15, color='#3498db')

    ax.plot(angles, full_memory, 's-', linewidth=2.5, label='Full Memory', color='#e74c3c', markersize=8)
    ax.fill(angles, full_memory, alpha=0.15, color='#e74c3c')

    ax.plot(angles, gated_memory, '^-', linewidth=2.5, label='Gated Memory (Ours)', color='#2ecc71', markersize=8)
    ax.fill(angles, gated_memory, alpha=0.15, color='#2ecc71')

    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=13, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10, color='#6c757d')

    # 设置标题
    ax.set_title('Comprehensive Performance Comparison', fontsize=18, fontweight='bold', pad=30)

    # 添加图例
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12, framealpha=0.9)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('data/results/radar_chart_v2.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print('生成：radar_chart_v2.png')


def generate_tradeoff_chart():
    """生成安全-效用权衡图"""
    set_plot_style()

    fig, ax = plt.subplots(figsize=(12, 8))

    # 数据
    agents = ['No Memory', 'Full Memory', 'Gated Memory']
    security = [1.0, 0.4, 0.9]
    utility = [0.3, 0.8, 0.6]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    sizes = [200, 300, 250]

    # 创建散点图
    scatter = ax.scatter(utility, security, c=colors, s=sizes, alpha=0.8, edgecolors='white', linewidth=2)

    # 添加标签
    for i, agent in enumerate(agents):
        ax.annotate(agent, (utility[i], security[i]),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=12, fontweight='bold', color='#2c3e50')

    # 添加理想区域
    from matplotlib.patches import Rectangle
    ideal_rect = Rectangle((0.6, 0.8), 0.4, 0.2, linewidth=2, edgecolor='#2ecc71',
                           facecolor='#2ecc71', alpha=0.1, linestyle='--')
    ax.add_patch(ideal_rect)
    ax.text(0.8, 0.9, 'Ideal Zone', fontsize=12, ha='center', va='center',
            color='#27ae60', fontweight='bold')

    # 设置标签
    ax.set_xlabel('Utility Score', fontsize=14, fontweight='bold')
    ax.set_ylabel('Security Score', fontsize=14, fontweight='bold')
    ax.set_title('Security-Utility Trade-off Analysis', fontsize=18, fontweight='bold', pad=20)

    # 设置范围
    ax.set_xlim(0.1, 1.0)
    ax.set_ylim(0.1, 1.1)

    # 添加网格
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)

    # 移除上边和右边边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig('data/results/tradeoff_chart.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print('生成：tradeoff_chart.png')


def generate_performance_heatmap():
    """生成性能热力图"""
    set_plot_style()

    fig, ax = plt.subplots(figsize=(12, 6))

    # 数据
    agents = ['No Memory', 'Full Memory', 'Gated Memory']
    metrics = ['Security', 'Utility', 'Speed', 'Privacy', 'Cost Efficiency']

    data = np.array([
        [1.0, 0.3, 0.6, 1.0, 0.8],  # No Memory
        [0.4, 0.8, 0.8, 0.3, 0.5],  # Full Memory
        [0.9, 0.6, 0.3, 0.9, 0.6],  # Gated Memory
    ])

    # 创建热力图
    sns.heatmap(data, annot=True, fmt='.2f', cmap='RdYlGn',
                xticklabels=metrics, yticklabels=agents,
                linewidths=2, linecolor='white',
                cbar_kws={'label': 'Score'}, ax=ax)

    # 设置标签
    ax.set_title('Performance Heatmap', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Metrics', fontsize=14, fontweight='bold')
    ax.set_ylabel('Agents', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig('data/results/performance_heatmap.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print('生成：performance_heatmap.png')


def main():
    """主函数"""
    print('生成高级图表...')
    print('=' * 50)

    # 确保输出目录存在
    os.makedirs('data/results', exist_ok=True)

    # 生成所有图表
    generate_safety_comparison_v2()
    generate_radar_chart_v2()
    generate_tradeoff_chart()
    generate_performance_heatmap()

    print('=' * 50)
    print('所有高级图表生成完成！')
    print('文件保存在：data/results/ 目录下')

    # 列出生成的文件
    print('\n生成的文件：')
    for filename in sorted(os.listdir('data/results')):
        if filename.endswith('.png'):
            size = os.path.getsize(f'data/results/{filename}') / 1024
            print(f'  - {filename} ({size:.1f} KB)')


if __name__ == "__main__":
    main()
