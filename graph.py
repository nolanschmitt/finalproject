import sqlite3
import matplotlib.pyplot as plt

def fetch_joined_data():
    conn_stats = sqlite3.connect("ncaa_teams.db")
    
    cursor_stats = conn_stats.cursor()
    

    cursor_stats.execute("ATTACH DATABASE 'ncaa_teams.db' AS ncaa_teams")

    cursor_stats.execute('''SELECT t_wl.school, t_wl.wins, t_wl.losses, nt.three_points, nt.rpg
                            FROM team_wins_losses AS t_wl
                            JOIN ncaa_teams AS nt ON t_wl.school = nt.team_name''')
    wins_data = cursor_stats.fetchall()

    # Join team_conf_wins_losses and ncaa_teams
    cursor_stats.execute('''SELECT t_cwl.school, t_cwl.confWins, t_cwl.confLosses, nt.three_points, nt.rpg
                            FROM team_conf_wins_losses AS t_cwl
                            JOIN ncaa_teams AS nt ON t_cwl.school = nt.team_name''')
    conf_wins_data = cursor_stats.fetchall()

    conn_stats.close()

    return wins_data, conf_wins_data
   

def create_graph3(data):
    schools = [row[0] for row in data]
    wins = [row[1] for row in data]
    three_points = [row[3] for row in data]

    fig, ax = plt.subplots()

    ax.scatter(three_points, wins, label="Wins", alpha=0.5)
    

    ax.set_xlabel("Three Pointers")
    ax.set_ylabel("Wins")
    ax.set_title("Correlation between Wins and Three Pointers per game")
    ax.legend()

    plt.show()

def create_graphR(data):
    schools = [row[0] for row in data]
    wins = [row[1] for row in data]
    rpg = [row[4] for row in data]

    fig, ax = plt.subplots()

    markerline, stemlines, baseline = ax.stem(rpg, wins, label="Wins")

    # Customize the appearance of the stem plot
    plt.setp(markerline, markersize=5, markeredgecolor="red", color='red')
    plt.setp(stemlines, linestyle="-", color="black", linewidth=1.5)
    plt.setp(baseline, visible=False)

    ax.set_xlabel("Rebounds Per Game")
    ax.set_ylabel("Conference Wins")
    ax.set_title("Correlation between Conference Wins and Rebounds per game")
    ax.legend()

    plt.show()

def winning_percentage_above_below_average(data):
    
    total_three_points = [row[3] for row in data]
    average_three_points = sum(total_three_points) / len(total_three_points)

    above_average = [row for row in data if row[3] > average_three_points]
    below_average = [row for row in data if row[3] <= average_three_points]

    win_percentage_above = sum([row[1] for row in above_average]) / sum([row[1] + row[2] for row in above_average])
    win_percentage_below = sum([row[1] for row in below_average]) / sum([row[1] + row[2] for row in below_average])

    return win_percentage_above, win_percentage_below



def main():
    totaldata,confdata = fetch_joined_data()
    create_graph3(totaldata)
    create_graphR(confdata)

    win_percentage_above, win_percentage_below = winning_percentage_above_below_average(totaldata)
    with open("calc.txt", "w") as f:
        f.write(f"Winning percentage for teams above average three-point value: {win_percentage_above * 100:.2f}%\n")
        f.write(f"Winning percentage for teams below average three-point value: {win_percentage_below * 100:.2f}%\n")

if __name__ == "__main__":
    main()