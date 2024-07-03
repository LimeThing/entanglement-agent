import time

from helper import plot

if __name__ == '__main__':
    file1 = open('a', 'r')
    Lines = file1.readlines()

    count = 0
    plot_scores = []
    plot_average_scores = []
    # Strips the newline character
    for line in Lines:
        count += 1
        print("Line{}: {}".format(count, line.strip()))
        if count < 1600:
            plot_scores.append(0)
            plot_average_scores.append(float(line.split(" ")[1]))
    plot(plot_scores, plot_average_scores)
    time.sleep(100)
