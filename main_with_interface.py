import requests
import asyncio
import aiohttp
import os, sys
from bs4 import BeautifulSoup
from ttkbootstrap import Style, Label, Frame, Entry, Button, Combobox, Text, StringVar
from tkinter import END

# Constants
SEASONS = {
    "2024 Into The Deep": 2024,
    "2023 Centerstage": 2023,
    "2022 Power Play": 2022,
    "2021 Freight Frenzy": 2021,
    "2020 Ultimate Goal": 2020,
    "2019 Skystone": 2019,
}
REGIONS = {
    "All": "All",
    "Romania": "RO",
    "United States": "UnitedStates",
    "International": "International",
    "Alaska": "USAK",
    "Alabama": "USAL",
    "Arkansas": "USAR",
    "Arizona": "USAZ",
    "California": "USCA",
    "California - Los Angeles": "USCALA",
    "California - LAUSD": "USCALS",
    "California - Northern": "USCANO",
    "California - San Diego": "USCASD",
    "Chesapeake": "USCHS",
    "Colorado": "USCO",
    "Connecticut": "USCT",
    "Delaware": "USDE",
    "Florida": "USFL",
    "Georgia": "USGA",
    "Hawaii": "USHI",
    "Iowa": "USIA",
    "Idaho": "USID",
    "Illinois": "USIL",
    "Indiana": "USIN",
    "Kentucky": "USKY",
    "Louisiana": "USLA",
    "Massachusetts": "USMA",
    "Maryland": "USMD",
    "Michigan": "USMI",
    "Minnesota": "USMN",
    "Missouri & Kansas": "USMOKS",
    "Mississippi": "USMS",
    "Montana": "USMT",
    "North Carolina": "USNC",
    "North Dakota": "USND",
    "Nebraska": "USNE",
    "New Hampshire": "USNH",
    "New Jersey": "USNJ",
    "New Mexico": "USNM",
    "Nevada": "USNV",
    "New York": "USNY",
    "New York - Excelsior": "USNYEX",
    "New York - Long Island": "USNYLI",
    "New York - NYC": "USNYNY",
    "Ohio": "USOH",
    "Oklahoma": "USOK",
    "Oregon": "USOR",
    "Pennsylvania": "USPA",
    "Rhode Island": "USRI",
    "South Carolina": "USSC",
    "Tennessee": "USTN",
    "Texas": "USTX",
    "Texas - Central": "USTXCE",
    "Texas - Houston": "USTXHO",
    "Texas - North": "USTXNO",
    "Texas - South": "USTXSO",
    "Texas - West & Panhandle": "USTXWP",
    "Utah": "USUT",
    "Virginia": "USVA",
    "Vermont": "USVT",
    "Washington": "USWA",
    "Wisconsin": "USWI",
    "West Virginia": "USWV",
    "Wyoming": "USWY",
    "Alberta": "CAAB",
    "British Columbia": "CABC",
    "Ontario": "CAON",
    "Québec": "CAQC",
    "Australia": "AU",
    "Brazil": "BR",
    "China": "CN",
    "Cyprus": "CY",
    "Germany": "DE",
    "Egypt": "EG",
    "Spain": "ES",
    "France": "FR",
    "Great Britain": "GB",
    "Israel": "IL",
    "India": "IN",
    "Jamaica": "JM",
    "South Korea": "KR",
    "Kazakhstan": "KZ",
    "Libya": "LY",
    "Mexico": "MX",
    "Nigeria": "NG",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Qatar": "QA",
    "Russia": "RU",
    "Saudi Arabia": "SA",
    "Thailand": "TH",
    "Taiwan": "TW",
    "South Africa": "ZA",
    "Innovation Challenge": "CMPIC",
    "FIRST Championship": "CMPZ2",
    "Military & Diplomatic": "ONADOD",
    "Adventist Robotics League": "USARL"
}

# Functions

if getattr(sys, 'frozen', False):
    # If frozen, the icon is bundled with the exe in the same directory
    icon_path = os.path.join(sys._MEIPASS, 'app.ico')
else:
    # Otherwise, use the local path
    icon_path = 'app.ico'

async def fetch_data(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError:
        return None
    
async def get_ftc_data(team_number: int):
    urls = [
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR1",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR2",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR3",
        "https://ftc-events.firstinspires.org/2023/region/RO/league/NR4",
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)

    for url, response_text in zip(urls, responses):
        if response_text:
            soup = BeautifulSoup(response_text, 'html.parser')
            team_rows = soup.find_all('tr')
            for row in team_rows:
                columns = row.find_all('td')
                if len(columns) > 1:
                    team_link = columns[1].find('a')
                    if team_link and str(team_number) == team_link.text:
                        return {
                            "team_number": team_number,
                            "region_id": url[-3:],
                            "region_rank": columns[0].text.strip(),
                            "matches_played": columns[7].text.strip()
                        }
    return False

def get_ftc_scout_data(team_number, selected_season, selected_region):
    url = "https://api.ftcscout.org/rest/v1"

    # Get the year from the season
    season_year = SEASONS[selected_season]

    # Map the region name to its abbreviation (e.g., "RO (Romania)" -> "RO")
    region_abbreviation = REGIONS[selected_region]

    try:
        general_data = requests.get(url + f"/teams/{team_number}")
        world_data = requests.get(url + f"/teams/{team_number}/quick-stats?season={season_year}")
        region_data = requests.get(url + f"/teams/{team_number}/quick-stats?season={season_year}&region={region_abbreviation}")
    except:
        return False

    try:
        general_data_json = general_data.json()
        if (world_data.status_code != 404):
            try:
                world_data_json = world_data.json()
            except:
                world_data_json = None
        else:
            if (f"Team {team_number}" in world_data.text):
                world_data_json = False
            else:
                world_data_json = None
        if (region_data.status_code != 404):
            try:
                region_data_json = region_data.json()
            except:
                region_data_json = None
        else:
            if (f"Team {team_number}" in region_data.text):
                region_data_json = False
            else:
                region_data_json = None
    except:
        return False

    if general_data_json and world_data_json != None and region_data_json != None:
        if not world_data_json:
            world_data_output = False
        else:
            world_data_output = {
                "world_rank": world_data_json["tot"]["rank"],
                "auto_rank": world_data_json["auto"]["rank"],
                "teleop_rank": world_data_json["dc"]["rank"],
                "endgame_rank": world_data_json["eg"]["rank"]
            }
        if not region_data_json:
            region_data_output = False
        else:
            region_data_output = {
                "region_rank": region_data_json["tot"]["rank"],
                "auto_rank": region_data_json["auto"]["rank"],
                "teleop_rank": region_data_json["dc"]["rank"],
                "endgame_rank": region_data_json["eg"]["rank"]
            }

        return {
            "team_number": team_number,
            "general_data": {
                "name": general_data_json["name"],
                "school": general_data_json["schoolName"],
                "country": general_data_json["country"],
                "state": general_data_json["state"],
                "city": general_data_json["city"],
            },
            "world_data": world_data_output,
            "region_data": region_data_output
        }
    return False

async def search_team(team_number, selected_season, selected_region):
    # Colors
    result_box.tag_config("cyan", foreground="cyan")
    result_box.tag_config("green", foreground="green")
    result_box.tag_config("yellow", foreground="yellow")
    result_box.tag_config("magenta", foreground="magenta")
    result_box.tag_config("red", foreground="red")
    result_box.tag_config("lightblue", foreground="lightblue")

    result_box.config(state="normal")
    result_box.delete(1.0, END)
    result_box.insert(END, f"Searching for team {team_number} in {selected_season} ({selected_region})...\n\n")

    region_name_map = {"NR1": "BUCHAREST", "NR2": "CLUJ", "NR3": "TIMISOARA", "NR4": "IASI"}
    
    if (REGIONS[selected_region].lower() in ["ro"] and SEASONS[selected_season] == 2024):
        ftc_data = await get_ftc_data(team_number)
        region_name = region_name_map.get(ftc_data['region_id'], "Unknown") if ftc_data else "Unknown"
    else:
        ftc_data = False
        region_name = "Unknown"
    
    ftc_scout_data = get_ftc_scout_data(team_number, selected_season, selected_region)

    if not ftc_data and not ftc_scout_data:
        result_box.insert(END, "Team not found or an error occurred.")
        return

    try:

        # Example for adding colored text
        result_box.insert(END, f"Team Name: {ftc_scout_data['general_data']['name']}\n", "cyan")
        result_box.insert(END, f"Team Number: {team_number}\n", "cyan")
        result_box.insert(END, f"\nGeneral Data:\n", "cyan")
        result_box.insert(END, f"  Team Country: {ftc_scout_data['general_data']['country']}\n", "lightblue")
        result_box.insert(END, f"  Team State: {ftc_scout_data['general_data']['state']}\n", "lightblue")
        result_box.insert(END, f"  Team City: {ftc_scout_data['general_data']['city']}\n", "lightblue")
        result_box.insert(END, f"  Team School: {ftc_scout_data['general_data']['school']}\n", "lightblue")

        if ftc_data:
            result_box.insert(END, f"\nSub-region Data:\n", "cyan")
            result_box.insert(END, f"  Sub-region: {ftc_data['region_id']} - {region_name}\n", "green")
            result_box.insert(END, f"  Sub-region Rank: {ftc_data['region_rank']}\n", "yellow")
            result_box.insert(END, f"  Total Matches Played: {ftc_data['matches_played']}\n", "magenta")

        if ftc_scout_data:
            if (ftc_scout_data['world_data'] != False and ftc_scout_data['region_data'] != False):
                if (ftc_scout_data['region_data'] != False):
                    result_box.insert(END, f"\nRegion Data:\n", "cyan")
                    result_box.insert(END, f"  Region Rank: {ftc_scout_data['region_data']['region_rank']}\n", "green")
                    result_box.insert(END, f"  Auto Rank: {ftc_scout_data['region_data']['auto_rank']}\n", "yellow")
                    result_box.insert(END, f"  Teleop Rank: {ftc_scout_data['region_data']['teleop_rank']}\n", "magenta")
                    result_box.insert(END, f"  Endgame Rank: {ftc_scout_data['region_data']['endgame_rank']}\n", "red")
                
                if (ftc_scout_data['world_data'] != False):
                    result_box.insert(END, f"\nWorld Data:\n", "cyan")
                    result_box.insert(END, f"  World Rank: {ftc_scout_data['world_data']['world_rank']}\n", "green")
                    result_box.insert(END, f"  Auto Rank: {ftc_scout_data['world_data']['auto_rank']}\n", "yellow")
                    result_box.insert(END, f"  Teleop Rank: {ftc_scout_data['world_data']['teleop_rank']}\n", "magenta")
                    result_box.insert(END, f"  Endgame Rank: {ftc_scout_data['world_data']['endgame_rank']}\n", "red")
            else:
                result_box.insert(END, f"\nTeam {team_number} has no stats for {selected_season}!\n", "red")
    except KeyError:
        result_box.insert(END, "Incomplete data found. Please try again.")
    result_box.config(state="disabled")

def on_search_button_click():
    team_number = team_entry.get()
    selected_season = season_var.get()
    selected_region = region_var.get()

    result_box.tag_config("white", foreground="white")

    try:
        team_number = int(team_number)
    except ValueError:
        result_box.config(state="normal")
        result_box.delete(1.0, END)
        result_box.insert(END, "Invalid team number. Please enter a valid number.", "white")
        result_box.config(state="disabled")
        return

    # Insert the "Searching..." message before the data fetch
    result_box.config(state="normal")   
    result_box.delete(1.0, END)  # Clear the result box
    result_box.insert(END, f"Searching for team {team_number} in {selected_season} ({selected_region})...\n\n", "cyan")
    result_box.config(state="disabled")

    # Schedule the async search function to run after the current Tkinter event loop
    root.after(1, lambda: asyncio.run(search_team(team_number, selected_season, selected_region)))

# GUI Setup
style = Style(theme="darkly")
root = style.master
root.title("FTC Team Lookup")
root.resizable(False, False)
root.geometry("700x500")

# Set the icon
root.wm_iconbitmap(icon_path)

# Header
Label(root, text="FTC Team Lookup", font=("Helvetica", 16), bootstyle="inverse-primary").pack(pady=10)

# Main Frame
frame = Frame(root)
frame.pack(pady=5)

# Team Number Entry
Label(frame, text="Enter Team Number:", bootstyle="inverse-secondary").grid(row=0, column=0, padx=5, pady=5, sticky="w")
team_entry = Entry(frame, width=80, justify="center")  # Center the text inside the entry
team_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Bind the "Enter" key to trigger the search
team_entry.bind("<Return>", lambda event: on_search_button_click())

# Season Dropdown
Label(frame, text="Season:", bootstyle="inverse-secondary").grid(row=1, column=0, padx=5, pady=5, sticky="w")
season_var = StringVar(value=list(SEASONS.keys())[0])  # Use StringVar from tkinter
season_dropdown = Combobox(frame, textvariable=season_var, values=list(SEASONS.keys()), state="readonly", width=80, justify="center")  # Set width to 80
season_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
season_dropdown.set(season_var.get())  # Ensure the initial value is set correctly

# Region Dropdown
Label(frame, text="Region:", bootstyle="inverse-secondary").grid(row=2, column=0, padx=5, pady=5, sticky="w")
region_var = StringVar(value=list(REGIONS.keys())[0])  # Use the first key from the dictionary
region_dropdown = Combobox(frame, textvariable=region_var, values=list(REGIONS.keys()), state="readonly", width=80, justify="center")  # Set width to 80
region_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
region_dropdown.set(region_var.get())  # Ensure the initial value is set correctly

# Search Button
Button(frame, text="Search", command=on_search_button_click, bootstyle="success").grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Results Box
result_box = Text(root, wrap="word", height=15, width=103, bg="#3e3e3e", fg="#ffffff", insertbackground="#ffffff", state="disabled")
result_box.pack(pady=10)

# Footer
style.configure("Footer.TLabel", background="#2e2e2e", foreground="#ffffff", font=("Helvetica", 10))
footer = Label(root, text="Made By 19076 - RoboticsTrav", style="Footer.TLabel")
footer.pack(side="bottom", anchor="se", pady=5, padx=5)

root.mainloop()