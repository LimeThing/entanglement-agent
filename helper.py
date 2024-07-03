import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel("No. Games / 100")
    plt.ylabel("Score")
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
    plt.show()
    plt.pause(0.1)  # Adjust the pause time as needed

def histogram(scores):
    display.clear_output(wait=True)  # Clear the previous output in Jupyter
    display.display(plt.gcf())
    plt.clf()

    # Histogram
    plt.hist(scores, bins=10, edgecolor='black')

    plt.title('Distribution of Scores')
    plt.xlabel('Score')
    plt.ylabel('Number of Games')
    plt.grid(True)

    plt.show()
    plt.pause(0.1)  # Adjust the pause time as needed