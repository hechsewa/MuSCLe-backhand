import pandas as pd
import matplotlib.pyplot as plt


def main():
    df = pd.read_csv('./data.csv')
    ax = plt.gca()
    #df.plot(kind='bar', x='nr', y='bpm', ax=ax)
    #plt.show()

    # Histogram tempo
    df[['bpm']].plot(kind='hist', bins=[100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200], rwidth=0.8)
    plt.xlabel('Tempo [bpm]')
    plt.ylabel('Ilość utworów')
    plt.show()

    df.groupby(['hpss', 'vocal']).size().unstack().plot(kind='bar', stacked=True)
    plt.xlabel('Harmoniczność')
    plt.ylabel('Ilość utworów')
    plt.show()


if __name__ == '__main__':
    main()