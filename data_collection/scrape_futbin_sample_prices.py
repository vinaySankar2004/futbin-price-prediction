import asyncio
from playwright.async_api import async_playwright
import csv

async def extract_price_data(player_id, player_url, writer, max_retries=5):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-gpu", "--no-sandbox", "--start-minimized"]  # Launch in minimized mode]
        )
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print(f"Navigating to {player_url}...")

            # Navigate to the player page
            await page.goto(player_url, wait_until="domcontentloaded", timeout=30000)

            retries = 0
            while retries < max_retries:
                # Check if Highcharts is available
                highcharts_available = await page.evaluate("""
                    () => typeof Highcharts !== 'undefined' && Highcharts.charts[1]
                """)
                if highcharts_available:
                    break

                print(f"Highcharts not yet available for Player ID {player_id}. Retrying {retries + 1}/{max_retries}...")
                retries += 1
                await asyncio.sleep(5)  # Wait before retrying

            if not highcharts_available:
                print(f"Highcharts not available for Player ID {player_id} after {max_retries} retries. Skipping...")
                return

            # Extract Highcharts data
            data_points = await page.evaluate("""
                () => {
                    const series = Highcharts.charts[1].series[0];
                    return series.processedXData.map((x, i) => ({
                        date: new Date(x).toLocaleDateString('en-US'),
                        price: series.processedYData[i]
                    }));
                }
            """)

            # Write the data to the CSV
            for point in data_points:
                writer.writerow([player_id, point['date'], point['price']])

            print(f"Data for Player ID {player_id} saved successfully.")

        except Exception as e:
            print(f"Error extracting data for Player ID {player_id}: {e}")

        finally:
            await browser.close()


async def scrape_futbin_prices(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as infile, open(output_csv, 'a', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)

        # Write header only if the output file is empty
        if outfile.tell() == 0:
            writer.writerow(['PlayerID', 'Date', 'Price'])

        for row in reader:
            player_id = row['ID']
            player_url = row['URL']
            print(f"Extracting data for Player ID: {player_id}")

            # Extract price data for the current player
            await extract_price_data(player_id, player_url, writer)

            # Add a short delay to avoid overloading the server
            await asyncio.sleep(2)

    print("Data collection completed.")


if __name__ == "__main__":
    input_csv = "futbin_data_final_1_to_9.csv"  # Input CSV file with player info
    output_csv = "player_prices_1_to_9.csv"  # Output CSV file to save price data

    asyncio.run(scrape_futbin_prices(input_csv, output_csv))
