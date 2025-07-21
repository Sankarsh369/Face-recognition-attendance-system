import matplotlib.pyplot as plt

# Sample data for Face Recognition Performance Analysis
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
values = [0.95, 0.93, 0.92, 0.925]  # hypothetical performance values

# Create a bar chart
plt.figure(figsize=(8, 6))
bars = plt.bar(metrics, values, color=['skyblue', 'lightgreen', 'orange', 'salmon'])
plt.ylim(0, 1.1)
plt.title('Face Recognition Performance Metrics')
plt.ylabel('Score')

# Add value labels on top of each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}", ha='center', va='bottom')

# Save the chart
plt.tight_layout()
bar_chart_path = "/mnt/data/face_recognition_performance_chart.png"
plt.savefig(bar_chart_path)
plt.close()

bar_chart_path
