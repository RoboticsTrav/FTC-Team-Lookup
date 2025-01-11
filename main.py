import requests, os
from bs4 import BeautifulSoup
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

region = "RO"
season = "2024"

def get_ftc_data(team_number):
    # URLs to search
    urls = [
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR3",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR1",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR2",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR4",
    ]

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all rows in the table
            team_rows = soup.find_all('tr')
            for row in team_rows:
                columns = row.find_all('td')
                if len(columns) > 1:  # Ensure there are enough columns
                    team_link = columns[1].find('a')  # Look for the <a> tag inside the second column
                    if team_link and str(team_number) in team_link.text:  # Check if team number matches
                        return {"team_number": team_number, "region_id": url[-3:],"region_rank": columns[0].text.strip(), "matches_played": columns[7].text.strip()}
        except requests.RequestException as e:
            pass
    return False

def get_ftc_scout_data(team_number):
    url = "https://api.ftcscout.org/rest/v1"

    try:
        general_data = requests.get(url + f"/teams/{team_number}")
        world_data = requests.get(url + f"/teams/{team_number}/quick-stats?season={season}")
        region_data = requests.get(url + f"/teams/{team_number}/quick-stats?season={season}&region={region}")
    except:
        return False

    # Parse the JSON response
    try:
        general_data_json = general_data.json()
        world_data_json = world_data.json()
        region_data_json = region_data.json()
    except:
        return False

    if (general_data_json and world_data_json and region_data_json):
        return {
            "team_number": team_number,
            "general_data": {
                "name": general_data_json["name"],
                "school": general_data_json["schoolName"],
                "state": general_data_json["state"],
                "citiy": general_data_json["city"],
            },
            "world_data": {
                "world_rank": world_data_json["tot"]["rank"],
                "auto_rank": world_data_json["auto"]["rank"],
                "teleop_rank": world_data_json["dc"]["rank"],
                "endgame_rank": world_data_json["eg"]["rank"]
            },
            "region_data": {
                "region_rank": region_data_json["tot"]["rank"],
                "auto_rank": region_data_json["auto"]["rank"],
                "teleop_rank": region_data_json["dc"]["rank"],
                "endgame_rank": region_data_json["eg"]["rank"]
            }
        }
    else:
        return False

if __name__ == "__main__":
    os.system("cls")
    print(Fore.CYAN + "\n----------------------------------------------------------------------------------------")
    print(Fore.CYAN + "-------------------------------- FTC ROMANIA TEAM LOOKUP -------------------------------")
    print(Fore.CYAN + "----------------------------- BY TEAM 19076 - ROBOTICSTRAV -----------------------------\n")

    team_number = input(Fore.GREEN + "Enter the team number: ")
    try:
        team_number = int(team_number)
    except:
        print(Fore.RED + "\nTeam number is invalid\n")
        input()
        exit(0)

    ftc_data = get_ftc_data(team_number)
    ftc_scout_data = get_ftc_scout_data(team_number)

    if (not ftc_data and not ftc_scout_data):
        print(Fore.RED + "\nTeam not found or an error occured\n")
        input()
        exit(0)

    # Print the data with color
    region_name = ""
    try:
        match ftc_data['region_id']:
            case "NR1":
                region_name = "BUCHAREST"
            case "NR2":
                region_name = "CLUJ"
            case "NR3":
                region_name = "TIMISOARA"
            case "NR4":
                region_name = "IASI"
                
        print(Fore.LIGHTBLUE_EX + f"\nTeam Name: {ftc_scout_data['general_data']['name']}")
        print(Fore.LIGHTBLUE_EX + f"Team Number: {ftc_data['team_number']}")
        print(Fore.CYAN + f"Team School: {ftc_scout_data['general_data']['school']}")
        print(Fore.CYAN + f"Team State: {ftc_scout_data['general_data']['state']}")
        print(Fore.CYAN + f"Team Citiy: {ftc_scout_data['general_data']['citiy']}")
        print(Fore.GREEN + f"Region: {ftc_data['region_id']} - {region_name}")
        print(Fore.YELLOW + f"Region Rank: {ftc_data['region_rank']}")
        print(Fore.MAGENTA + f"Total Matches Played: {ftc_data['matches_played']}")

        print(Fore.CYAN + f"\nRegion Data for Team {ftc_scout_data['team_number']} - {ftc_scout_data['general_data']['name']}:")
        print(Fore.GREEN + f"Region Rank: {ftc_scout_data['region_data']['region_rank']}")
        print(Fore.YELLOW + f"Auto Rank: {ftc_scout_data['region_data']['auto_rank']}")
        print(Fore.MAGENTA + f"Teleop Rank: {ftc_scout_data['region_data']['teleop_rank']}")
        print(Fore.RED + f"Endgame Rank: {ftc_scout_data['region_data']['endgame_rank']}")
        
        print(Fore.CYAN + f"\nWorld Data for Team {ftc_scout_data['team_number']} - {ftc_scout_data['general_data']['name']}:")
        print(Fore.GREEN + f"World Rank: {ftc_scout_data['world_data']['world_rank']}")
        print(Fore.YELLOW + f"Auto Rank: {ftc_scout_data['world_data']['auto_rank']}")
        print(Fore.MAGENTA + f"Teleop Rank: {ftc_scout_data['world_data']['teleop_rank']}")
        print(Fore.RED + f"Endgame Rank: {ftc_scout_data['world_data']['endgame_rank']}\n")
        input()
    except:
        print(Fore.RED + "\nTeam not found or an error occured\n")
        input()
        exit(0)