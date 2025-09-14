import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_all():
    df = pd.read_csv("results/summary.csv")
    
    # Plot for Downstream Latency TTD
    plt.figure(figsize=(8, 6))
    subset = df[df['Scenario'] == 'Downstream Latency']
    sns.barplot(data=subset, x='System', y='TTD_s')
    plt.title('Time-to-Detect for Downstream Latency Scenario')
    plt.ylabel('Time-to-Detect (seconds)')
    plt.xlabel('System')
    plt.savefig("results/ttd_plot.png")
    plt.show()

    # Plot for CPU Starvation Success Rate
    plt.figure(figsize=(8, 6))
    subset = df[df['Scenario'] == 'CPU Starvation']
    sns.barplot(data=subset, x='System', y='Success_Rate_Percent')
    plt.title('Success Rate During CPU Starvation Scenario')
    plt.ylabel('User Success Rate (%)')
    plt.ylim(0, 100)
    plt.xlabel('System')
    plt.savefig("results/success_rate_plot.png")
    plt.show()

if __name__ == "__main__":
    plot_all()