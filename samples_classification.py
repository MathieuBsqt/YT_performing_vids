import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import mplcursors
from graphs import hover_callback

def classify_samples(filename):
    df = pd.read_csv(filename)
    output_filename = filename.split("_")[0]

    # Delete today's upload video (Video Age = 0 which causes errors)
    df = df[df['Video_Age'] != 0]

    # Define a binary target variable: 1 for high potential, 0 otherwise
    df['High_Potential'] = (df['Views_per_day'] > df['Views_per_day'].mean()).astype(int)

    # Features for classification
    X = df[['Video_Age', 'Views_per_day']]

    # Create a logistic regression model
    model = LogisticRegression()
    model.fit(X, df['High_Potential'])

    # Create a scatter plot
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df['Video_Age'], df['Views_per_day'], c=df['High_Potential'], cmap='viridis', s=15, alpha=0.7)

    # Set axis labels and title
    plt.xlabel('Video Age (Days)')
    plt.ylabel('Views per Day')
    plt.title('YouTube Video Performance - High Potential vs. Others')

    # Connect mplcursors to the scatter plot
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: hover_callback(sel, df))

    # Plot the decision boundary
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Create grid to evaluate model
    xx, yy = np.meshgrid(np.linspace(xlim[0], xlim[1], 100),
                         np.linspace(ylim[0], ylim[1], 100))
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.contour(xx, yy, Z, colors='red', linestyles='dashed')
    plt.savefig(output_filename + "classification_graph.png")

    # Predict the class probabilities for all samples
    df['Predicted_High_Potential'] = model.predict(X)

    # Filter the DataFrame to include only interesting samples
    interesting_samples = df[df['Predicted_High_Potential'] == 1]

    # To export to a CSV file:
    output_filename+= "interesting_samples.csv"
    interesting_samples.to_csv(output_filename, index=False)

    # Show the plot
    plt.show()

    print("Results exported to: ", output_filename)
