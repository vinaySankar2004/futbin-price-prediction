import requests
from bs4 import BeautifulSoup
import time
import csv
from selenium import webdriver
import random

'''
def get_html(url):
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None
'''

'''
def get_html(url, max_retries=5):
    # Initialize the Selenium WebDriver with options
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')  # Prevent detection as a bot
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    retry_attempts = 0
    driver = None

    while retry_attempts < max_retries:  # Retry up to max_retries times
        try:
            driver = webdriver.Chrome(options=options)
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                });
                
            })

            # Navigate to the desired webpage
            driver.get(url)

            # Get the page source (HTML content) without delay
            html_content = driver.page_source
            return html_content
        except Exception as e:
            print(f"Exception occurred while retrieving {url}: {e}")
            print("Retrying...")
            retry_attempts += 1
            time.sleep(5)  # Wait for a moment before retrying
        finally:
            if driver:
                driver.quit()

    # If it reaches here, all retries have failed
    print(f"Failed to retrieve {url} after {max_retries} attempts.")
    return None
'''

def get_html(url, max_retries=5):
    # Replace with your ScraperAPI key
    api_key = 'bc9a841ee1ea0fbe0b23d4a2ae43b0c2'

    retry_attempts = 0

    while retry_attempts < max_retries:  # Retry up to max_retries times
        try:
            # Create the payload for ScraperAPI request
            payload = {
                'api_key': api_key,
                'url': url
            }

            # Make a GET request to ScraperAPI
            response = requests.get('https://api.scraperapi.com/', params=payload)

            if response.status_code == 200:
                return response.text  # Return the page source (HTML content)

            else:
                print(f"Failed to retrieve page. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Exception occurred while retrieving {url}: {e}")

        retry_attempts += 1
        print("Retrying...")
        time.sleep(5)  # Wait for a moment before retrying

    # If it reaches here, all retries have failed
    print(f"Failed to retrieve {url} after {max_retries} attempts.")
    return None


def parse_player_table(html, url):
    players = []
    parsed_players_count = 0

    # Loop to ensure table is loaded successfully
    while True:
        try:
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find('table', class_='players-table')

            if not table:
                # Retry until table is found
                print("No player table found on the page. Retrying...")
                time.sleep(5)  # Wait before retrying
                html = get_html(url)  # Refresh the page content
                continue

            # Once the table is found, break out of this loop
            break
        except Exception as e:
            # Handle other possible issues and retry
            print(f"Error while trying to find the table: {e}")
            time.sleep(5)
            html = get_html(url)

    # Extract table rows
    rows = table.find('tbody', class_='with-border with-background').find_all('tr', class_='player-row text-nowrap')
    for row in rows:
        if parsed_players_count >= 30:
            # Stop parsing further players if we have already parsed 30 players
            break

        while True:  # Retry each player until successfully parsed
            try:
                # row - the current row of the player in the table
                player_data = []

                # Extract the title attribute which contains the player's name
                player_div = row.find('div', class_='playersquare round-corner-small table-player-image-base')
                name = player_div['title'].strip()

                # Log player name in case of an error
                print(f"Parsing player: {name}")

                # Extract the version of the card
                player_info = row.find('div', class_='table-player-info')
                version = player_info.find('div', class_='table-player-revision').text.strip()

                # Extract the rating of the card
                player_rating_info = row.find('div', class_='player-rating-card')
                rating = player_rating_info.find('div', class_='player-rating-card-text font-standard bold').text.strip()

                # Available positions in the game, ordered for binary encoding
                positions_list = ['ST', 'CF', 'RW', 'LW', 'RM', 'LM', 'CAM', 'CM', 'CDM', 'CB', 'LB', 'LWB', 'RB', 'RWB', 'GK']

                # Extract the primary position of the card
                primary_position = row.find('td', class_='table-pos').find('div', class_='bold').text.strip()

                # Extract the secondary positions of the card as a list of positions
                secondary_positions_text = row.find('td', class_='table-pos').find('div', class_='font-extra-small text-faded')
                if secondary_positions_text is not None:
                    secondary_positions = [pos.strip().replace("'", "").replace('"', "") for pos in secondary_positions_text.text.strip('[]').split(',')]
                else:
                    secondary_positions = []

                # Combine primary and secondary positions into a set
                all_positions = set(secondary_positions)
                all_positions.add(primary_position)

                if 'GK' in all_positions:
                    break  # IGNORING PLAYERS WITH GK POSITION FOR NOW (as stats don't align with other players)

                positions_binary = ''  # Holds the binary representation of the player's positions (reference positions_list)
                for pos in positions_list:
                    if pos in all_positions:
                        positions_binary += '1'  # Add '1' if the player can play this position
                    else:
                        positions_binary += '0'  # Add '0' if the player cannot play this position

                positions_binary = str(positions_binary).zfill(15)  # Format to be 15-length binary string

                # Extract the price of the card in UT Coins
                player_price_td = row.find('td', class_='table-price no-wrap platform-ps-only')
                price = convert_price_to_string_number(player_price_td.find('div', class_='price').text.strip())

                # Extract the strong foot of the card (either "right" or "left")
                foot_info = row.find('td', class_='table-foot').find('img', alt='Strong Foot')['src']
                if foot_info == '/design2/img/static/filters/foot-right.svg':
                    foot = 'right'
                elif foot_info == '/design2/img/static/filters/foot-left.svg':
                    foot = 'left'
                else:
                    foot = 'unknown'

                # Extract the skill moves of the card (1 <= skill_moves <= 5)
                skill_moves = row.find('td', class_='table-skills').text.strip()

                # Extract the weak foot of the card (1 <= weak_foot <= 5)
                weak_foot = row.find('td', class_='table-weak-foot').text.strip()

                # Extract the work rate info of the card
                work_rate_td = row.find('td', class_='table-attack-defense no-wrap')
                work_rate = work_rate_td.find('span', class_='bold').text.strip().replace(' ', '')

                # Extract the pace attribute of the card
                pace_info = row.find('td', class_='table-pace').find('span', class_='flex justify-center')
                pace_m = pace_info.find('div', class_='table-key-stats').text.strip()

                # Extract the shooting attribute of the card
                shooting_info = row.find('td', class_='table-shooting').find('span', class_='flex justify-center')
                shooting_m = shooting_info.find('div', class_='table-key-stats').text.strip()

                # Extract the passing attribute of the card
                passing_info = row.find('td', class_='table-passing').find('span', class_='flex justify-center')
                passing_m = passing_info.find('div', class_='table-key-stats').text.strip()

                # Extract the dribbling attribute of the card
                dribbling_info = row.find('td', class_='table-dribbling').find('span', class_='flex justify-center')
                dribbling_m = dribbling_info.find('div', class_='table-key-stats').text.strip()

                # Extract the defending attribute of the card
                defending_info = row.find('td', class_='table-defending').find('span', class_='flex justify-center')
                defending_m = defending_info.find('div', class_='table-key-stats').text.strip()

                # Extract the physicality attribute of the card
                physical_info = row.find('td', class_='table-physicality').find('span', class_='flex justify-center')
                physical_m = physical_info.find('div', class_='table-key-stats').text.strip()

                # Extract the height of the card (in cm)
                height_info = row.find('td', class_='table-height').find_all('div', class_='text-center')[0].text.strip()
                height = height_info[:3]  # Only get the cm part of the info

                # Extract the weight (in kg), body type and accelerate of the card
                body_type_info = row.find('td', class_='table-height').find_all('div', class_='text-center')

                if len(body_type_info) > 1:  # Case where weight and body_type exists
                    weight_info = body_type_info[1].find('span', class_='text-faded font-extra-small').text.strip()
                    weight = weight_info[1:-3]  # Remove parentheses and "kg" part of the string
                    body_type = body_type_info[1].find('a').text.strip()
                    accelerate = row.find('td', class_='table-height').find_all('a', class_='bold')[1].text.strip()
                else:
                    weight = -1
                    body_type = 'unknown'  # Set body_type to 'unknown' if it doesn't exist
                    accelerate = row.find('td', class_='table-height').find('a', class_='bold').text.strip()

                # Extract the popularity ranked by Futbin -- (remark: Futbin's popularity)
                popularity = row.find('td', class_='table-popularity').text.strip()

                # Extract the total in-game stats of the card
                total_ingame_stats = row.find('td', class_='table-in-game-stats').text.strip()

                # Extract the URL of the web page in Futbin of the card
                url = row.find('td', class_='table-name').find('a')['href']
                card_page_url = 'https://www.futbin.com' + url

                # Extract the ID of the card
                card_id = extract_id(card_page_url)

                # Now, navigate to the card page to get more attributes of the player
                card_page_html = get_html(card_page_url)

                # Extract the club, nation, league and
                # international_reputation (1 <= intl_rep <= 5) of the card
                nation, league, club, intl_rep = parse_info_table(card_page_html)

                # Extract the in-game stats for the card
                in_game_stats = parse_stats_window(card_page_html)

                # Extract the playstyles and playstyle pluses and encode it
                # 2 - playstyle plus, 1 - regular playstyle, 0 - not a playstyle
                playstyles = parse_playstyles_table(card_page_html)

                player_data = [name, card_id, version, rating, positions_binary, price, foot, skill_moves,
                               weak_foot, work_rate, pace_m, in_game_stats[0], in_game_stats[1], shooting_m, in_game_stats[2], in_game_stats[3], in_game_stats[4],
                               in_game_stats[5], in_game_stats[6], in_game_stats[7], passing_m, in_game_stats[8], in_game_stats[9],
                               in_game_stats[10], in_game_stats[11], in_game_stats[12], in_game_stats[13], dribbling_m, in_game_stats[14],
                               in_game_stats[15], in_game_stats[16], in_game_stats[17], in_game_stats[18], in_game_stats[19], defending_m,
                               in_game_stats[20], in_game_stats[21], in_game_stats[22], in_game_stats[23], in_game_stats[24], physical_m,
                               in_game_stats[25], in_game_stats[26], in_game_stats[27], in_game_stats[28], playstyles, height,
                               weight, body_type, accelerate, popularity, total_ingame_stats, card_page_url,
                               nation, league, club, intl_rep]

                if player_data:
                    players.append(player_data)
                parsed_players_count += 1  # Increment the count of parsed players
                break
            except Exception as e:
                print(f"Error occurred while parsing player data: {e}")
                time.sleep(5)  # Wait before retrying the specific player
    return players

def parse_playstyles_table(html):
    scoring_playstyles = '00000'
    passing_playstyles = '00000'
    ball_control_playstyles = '000000'
    defending_playstyles = '000000'
    physical_playstyles = '000000'
    gk_playstyles = '000000'


    if not html:
        return scoring_playstyles

    soup = BeautifulSoup(html, 'lxml')
    playstyles_window = soup.find('div', class_='player-page-content traits-wrapper-center-desktop standard-box s-column gtSmartphone-only')
    panels = playstyles_window.find_all('div', class_='xs-column')

    # Extract the scoring playstyles
    scoring_panel = panels[0].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(scoring_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            scoring_playstyles = scoring_playstyles[:i] + '1' + scoring_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            scoring_playstyles = scoring_playstyles[:i] + '2' + scoring_playstyles[i+1:]

    # Extract the passing playstyles
    passing_panel = panels[1].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(passing_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            passing_playstyles = passing_playstyles[:i] + '1' + passing_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            passing_playstyles = passing_playstyles[:i] + '2' + passing_playstyles[i+1:]

    # Extract the ball control playstyles
    ball_control_panel = panels[2].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(ball_control_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            ball_control_playstyles = ball_control_playstyles[:i] + '1' + ball_control_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            ball_control_playstyles = ball_control_playstyles[:i] + '2' + ball_control_playstyles[i+1:]

    # Extract the defending playstyles
    defending_panel = panels[3].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(defending_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            defending_playstyles = defending_playstyles[:i] + '1' + defending_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            defending_playstyles = defending_playstyles[:i] + '2' + defending_playstyles[i+1:]

    # Extract the physical playstyles
    physical_panel = panels[4].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(physical_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            physical_playstyles = physical_playstyles[:i] + '1' + physical_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            physical_playstyles = physical_playstyles[:i] + '2' + physical_playstyles[i+1:]

    # Extract the goal keeper playstyles
    gk_panel = panels[5].find('div', class_='playStyle-table-row space-between').find_all('a')
    for i, playstyle in enumerate(gk_panel):
        img_tag = playstyle.find('img')
        if img_tag:
            img_class = img_tag.get('class', [])

        # Check if it's a regular playstyle
        if 'active' in img_class and 'psplus' not in img_class:
            gk_playstyles = gk_playstyles[:i] + '1' + gk_playstyles[i+1:]

        # Check if it's a playstyle plus
        elif 'psplus' in img_class and 'active' in img_class:
            gk_playstyles = gk_playstyles[:i] + '2' + gk_playstyles[i+1:]

    return scoring_playstyles + passing_playstyles + ball_control_playstyles + defending_playstyles + physical_playstyles + gk_playstyles

def parse_stats_window(html):
    in_game_stats = ["n/a"] * 29

    if not html:
        return in_game_stats

    soup = BeautifulSoup(html, 'lxml')
    stats_window = soup.find('div', class_='player-stats-wrapper small-column')
    panels = stats_window.find_all('div', class_='player-stat-wrapper xs-column min-width')

    # Extract the pace in-game stats
    pace_panel = panels[0].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[0] = pace_panel[0].find('div', class_='player-stat-value').text.strip() # acceleration
    in_game_stats[1] = pace_panel[1].find('div', class_='player-stat-value').text.strip() # sprint speed

    # Extract the shooting in-game stats
    shooting_panel = panels[1].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[2] = shooting_panel[0].find('div', class_='player-stat-value').text.strip() # att. position
    in_game_stats[3] = shooting_panel[1].find('div', class_='player-stat-value').text.strip() # finishing
    in_game_stats[4] = shooting_panel[2].find('div', class_='player-stat-value').text.strip() # shot power
    in_game_stats[5] = shooting_panel[3].find('div', class_='player-stat-value').text.strip() # long shots
    in_game_stats[6] = shooting_panel[4].find('div', class_='player-stat-value').text.strip() # volleys
    in_game_stats[7] = shooting_panel[5].find('div', class_='player-stat-value').text.strip() # penalties

    # Extract the passing in-game stats
    passing_panel = panels[2].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[8] = passing_panel[0].find('div', class_='player-stat-value').text.strip() # vision
    in_game_stats[9] = passing_panel[1].find('div', class_='player-stat-value').text.strip() # crossing
    in_game_stats[10] = passing_panel[2].find('div', class_='player-stat-value').text.strip() # fk accuracy
    in_game_stats[11] = passing_panel[3].find('div', class_='player-stat-value').text.strip() # short pass
    in_game_stats[12] = passing_panel[4].find('div', class_='player-stat-value').text.strip() # long pass
    in_game_stats[13] = passing_panel[5].find('div', class_='player-stat-value').text.strip() # curve

    # Extract the dribbling in-game stats
    dribbling_panel = panels[3].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[14] = dribbling_panel[0].find('div', class_='player-stat-value').text.strip() # agility
    in_game_stats[15] = dribbling_panel[1].find('div', class_='player-stat-value').text.strip() # balance
    in_game_stats[16] = dribbling_panel[2].find('div', class_='player-stat-value').text.strip() # reactions
    in_game_stats[17] = dribbling_panel[3].find('div', class_='player-stat-value').text.strip() # ball control
    in_game_stats[18] = dribbling_panel[4].find('div', class_='player-stat-value').text.strip() # dribbling
    in_game_stats[19] = dribbling_panel[5].find('div', class_='player-stat-value').text.strip() # composure

    # Extract the defending in-game stats
    defending_panel = panels[4].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[20] = defending_panel[0].find('div', class_='player-stat-value').text.strip() # interceptions
    in_game_stats[21] = defending_panel[1].find('div', class_='player-stat-value').text.strip() # heading acc
    in_game_stats[22] = defending_panel[2].find('div', class_='player-stat-value').text.strip() # def aware
    in_game_stats[23] = defending_panel[3].find('div', class_='player-stat-value').text.strip() # stand tackle
    in_game_stats[24] = defending_panel[4].find('div', class_='player-stat-value').text.strip() # slide tackle

    # Extract the physicality in-game stats
    physical_panel = panels[5].find('div', class_='column').find_all('div', class_='player-stat-row flex space-between font-small')
    in_game_stats[25] = physical_panel[0].find('div', class_='player-stat-value').text.strip() # jumping
    in_game_stats[26] = physical_panel[1].find('div', class_='player-stat-value').text.strip() # stamina
    in_game_stats[27] = physical_panel[2].find('div', class_='player-stat-value').text.strip() # strength
    in_game_stats[28] = physical_panel[3].find('div', class_='player-stat-value').text.strip() # aggression

    return in_game_stats

def parse_info_table(html):
    nation = league = club = intl_rep = 'n/a'

    if not html:
        return nation, league, club, intl_rep

    soup = BeautifulSoup(html, 'lxml')
    info_table = soup.find('table', class_='narrow-table')

    if not info_table:
        print("No player table found on the page.")
        return nation, league, club, intl_rep

    # Extract attributes in table rows
    rows = info_table.find_all('tr')
    for row in rows:
        table_header = row.find('th').text.strip()
        if table_header == 'Club':
            club = row.find('a').text.strip()
        elif table_header == 'League':
            league = row.find('a').text.strip()
        elif table_header == 'Nation':
            nation = row.find('a').text.strip()
        elif table_header == 'Intl. Rep':
            intl_rep = row.find('td', class_='small-row align-center').text.strip()

    return nation, league, club, intl_rep

def convert_price_to_string_number(price):
    # Check if the string ends with 'K'
    if price.endswith('K'):
        numeric_price = float(price[:-1])
        result = int(numeric_price * 1000)
        return str(result)
    elif price.endswith('M'):
        numeric_price = float(price[:-1])
        result = int(numeric_price * 1000000)
        return str(result)
    else:
        # If the string doesn't end with 'K' or 'M', return the original price
        return price

def extract_id(url):
    parts = url.split('/')
    if len(parts) > 6:  # Ensure the URL has enough parts
        return parts[5]
    return None  # Return None or raise an error if the format is unexpected

def save_to_csv(player_data, filename='futbin_data.csv'):
    # Define the headers for the CSV file
    headers = ['Name', 'ID', 'Version', 'Rating', 'Positions', 'Price', 'Foot', 'Skill Moves',
           'Weak Foot', 'Work Rate', 'Pace_M', 'Acceleration', 'Sprint Speed', 'Shooting_M', 'Att Position', 'Finishing',
           'Shot Power', 'Long Shots', 'Volleys', 'Penalties', 'Passing_M', 'Vision', 'Crossing', 'FK Acc', 'Short Pass',
           'Long Pass', 'Curve', 'Dribbling_M', 'Agility', 'Balance', 'Reactions', 'Ball Control', 'Dribbling', 'Composure',
           'Defending_M', 'Interceptions', 'Heading Acc', 'Def Aware', 'Stand Tackle', 'Slide Tackle', 'Physical_M',
           'Jumping', 'Stamina', 'Strength', 'Aggression', 'Playstyles', 'Height', 'Weight', 'Body Type', 'Accelerate', 'Popularity',
           'Total In-game Stats', 'URL', 'Nation', 'League', 'Club', 'Intl. Rep']

    # Open the file in write mode
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # Write the headers to the file
        writer.writerow(headers)

        # Write the player data
        for player in player_data:
            # Add quotes around binary data to ensure it's treated as text
            player = [f'"{field}"' if i == 4 else field for i, field in enumerate(player)]
            # Write the player data to the file
            writer.writerow(player)

def save_to_csv_incremental(player_data, filename='futbin_data.csv'):
    # Define the headers for the CSV file
    headers = ['Name', 'ID', 'Version', 'Rating', 'Positions', 'Price', 'Foot', 'Skill Moves',
               'Weak Foot', 'Work Rate', 'Pace_M', 'Acceleration', 'Sprint Speed', 'Shooting_M', 'Att Position', 'Finishing',
               'Shot Power', 'Long Shots', 'Volleys', 'Penalties', 'Passing_M', 'Vision', 'Crossing', 'FK Acc', 'Short Pass',
               'Long Pass', 'Curve', 'Dribbling_M', 'Agility', 'Balance', 'Reactions', 'Ball Control', 'Dribbling', 'Composure',
               'Defending_M', 'Interceptions', 'Heading Acc', 'Def Aware', 'Stand Tackle', 'Slide Tackle', 'Physical_M',
               'Jumping', 'Stamina', 'Strength', 'Aggression', 'Playstyles', 'Height', 'Weight', 'Body Type', 'Accelerate', 'Popularity',
               'Total In-game Stats', 'URL', 'Nation', 'League', 'Club', 'Intl. Rep']

    # Check if the file already exists and needs a header
    try:
        with open(filename, mode='r', encoding='utf-8-sig') as file:
            header_present = file.readline().strip() != ''
    except FileNotFoundError:
        header_present = False

    # Open the file in append mode
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # Write the headers if the file is new
        if not header_present:
            writer.writerow(headers)

        # Write the player data
        for player in player_data:
            player = [f'"{field}"' if i == 4 else field for i, field in enumerate(player)]  # Ensure binary data is quoted
            writer.writerow(player)

def scrape_futbin_page_range(start_page, end_page):
    base_url = 'https://www.futbin.com/24/players?page='
    all_players = []

    for current_page in range(start_page, end_page + 1):
        print(f"Scraping page {current_page}...")
        url = base_url + str(current_page)
        html_content = get_html(url)

        # Retry logic inside the scraping function
        retries_left = 2  # Additional retries if page retrieval fails
        while retries_left > 0 and not html_content:
            print(f"Retrying page {current_page} (remaining attempts: {retries_left})...")
            html_content = get_html(url)
            retries_left -= 1

        # If still no HTML content after retries, skip this page
        if not html_content:
            print(f"Skipping page {current_page} due to failed retrieval.")
            continue

        try:
            # Pass both `html_content` and `url` to `parse_player_table`
            players = parse_player_table(html_content, url)
            if players:
                all_players.extend(players)
                save_to_csv_incremental(players, filename=f'futbin_data_pages_{start_page}_to_{end_page}.csv')
                time.sleep(random.uniform(0.5, 1.5))  # Short delay to avoid being blocked
            else:
                print(f"No more players found on page {current_page} or unable to parse the player table.")
        except Exception as e:
            print(f"Error occurred while processing page {current_page}: {e}")

    # Final save after the loop finishes
    if all_players:
        save_to_csv(all_players, filename=f'futbin_data_final_{start_page}_to_{end_page}.csv')


if __name__ == "__main__":
    # scrape_futbin_page_range(1, 172)
    scrape_futbin_page_range(860, 860)
