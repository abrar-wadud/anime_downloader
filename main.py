import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import os
from rich import print
from rich.table import Table
from rich.console import Console
from rich.progress import track

console = Console()
base_url = "https://anitaku.pe"
captcha_v3 = "03AFcWeA5Phyls8xv9gUYojSUiGR6tmA6CHcpFLjGx3WWSh7DZOnYTlP78j0QwLR7lfmGpmYFLgzCExJJnEMFy7jKwZdDFcf7s8Y9UXhaHsUvB95A6qCvTps_qcyPn6oieU2IoTymVwvQYcg7hK66ioEfzuvUlLUfGr8r47nnJzxe-geY6KfElW86yrcnjUVg2ChyJ0ROOYC2wz9K18DeLKqf7yt2w5VsCfLBqoqaIeiFInZ2U508MKsewFtnIRf6DarTfnRPdIa1gCmZwQixgfLIUd-rTaZZLI5Aaa33AnU18r-3x2qfp7MruJ5uB9k1SLgfD9R7pUz7si0UP67V6qPNjhdyS3UKQfoBC26KJbWHLGNZtKFPQw73AzSOqdugWdVjFJ3LQdDQHgqDE6iojJNq82-wBo2g9_sZpzI-9EBDzTYEBC-9UxZE-ZXA6TpxnLCX2YPj4ZKsWXYfMWATXHtmIxBLqpnzRoMHoKuajX8Kw15Sk7c2ih696PLJzeMsLXumVRjHJgambHD-CwOrwZnkDg5rjX8KikrfnFPTIzloFn1EeSdju6EEl4hXQDhWgtlarmKAh_iEvj4GNMBXjj8gXl_-84xSBXHHw3q6YyELh4o6TsS2y4tm3HdjdNWiMZCqMFgiWTdanUC8LFq6bjs8GlxTdmkWBjD46GtsL0TwgHCItF2Kge6lDULiJj2PEnbzMy7QiUWKPZGzpamMDA7iOfE9oA_JguOl-Pi5yQd_PYHGyhL-BWE7UN34cjKoPNERWO_0PxRO42UJj7zR8uUcwSznv9E2kNeiIXogQsIy3oxBckBBtPyDHXi5QQ5klg8oUVzRCD7Rg"

def choosing_anime():
    global selected_title
    anime_search = console.input("[blue bold]Anime: [/blue bold]")

    anime_links = []
    anime_titles = []
    table = Table()
    table.add_column("[cyan]No.[/cyan]",style="cyan bold", justify="center")
    table.add_column("[yellow]Anime Name[/yellow]", style="yellow")
    table.add_column("[green]Released[/green]", style="green", justify="center")

    search_result = requests.get(f"https://anitaku.pe/search.html?keyword={anime_search}&page=1")
    soup = BeautifulSoup(search_result.content, 'html.parser')

    try:
        page_list = soup.find('ul', class_='pagination-list').find_all('li')
    except AttributeError:
        page_list = [1]
    
    anime_counter = 0
    for i in track(range(1, len(page_list)+1), "[dark_green]Searching...[/dark_green]", transient=True):
        search_result = requests.get(f"https://anitaku.pe/search.html?keyword={anime_search}&page={i}")
        soup = BeautifulSoup(search_result.content, 'html.parser')
        search_items = soup.find('ul', class_="items").find_all('p')

        for item,date in zip(search_items[::2], search_items[1::2]):
            link = f"{base_url}{item.a.get('href')}"
            anime_links.append(link)
            title = item.a.string
            anime_titles.append(title)
            rel_date = date.text.strip()
            anime_counter += 1  
            table.add_row(str(anime_counter), title, rel_date.removeprefix("Released: "))

    if len(anime_links) > 0:
        print(table)
        choose_anime = int(console.input("[blue bold]Choose an anime: [/blue bold]")) - 1
        selected_title = anime_titles[choose_anime]
        max_ep(anime_links[choose_anime])
    else:
        print("[red bold]There's no anime, Try again...[/red bold]")
        return

def max_ep(choosed_anime):
    anime_page = requests.get(choosed_anime)
    anime_soup = BeautifulSoup(anime_page.content, 'html.parser')

    episodes = anime_soup.find('ul', id='episode_page').find_all('a')
    ep_end = episodes[-1].get('ep_end')
    print(f"[green bold]{ep_end} {'episode' if ep_end == '1' else 'episodes'} available[green bold]")
    download_id(anime_soup, ep_end)

def download_id(anime_soup, ep_end):
    anime_id = anime_soup.find('input', id="movie_id").get('value')
    
    starting_ep = int(console.input("[blue bold]Starting episode: [/blue bold]")) if ep_end != '1' else 1
    ending_ep = int(console.input("[blue bold]Ending episode: [/blue bold]")) if ep_end != '1' else 1
    
    if starting_ep <= ending_ep:
        eps_links_page = requests.get(f"https://ajax.gogocdn.net/ajax/load-list-episode?ep_start={starting_ep}&ep_end={ending_ep}&id={anime_id}")
    else:
        print("[red bold]Starting ep should be smaller or equal to the ending ep[/red bold]")
        return
    eps_soup = BeautifulSoup(eps_links_page.content, 'html.parser')

    ep_links = eps_soup.find_all('a')
    ep_links.reverse()
    id_list = []
    for i in track(ep_links, "[blue bold]Processing...[/blue bold]", transient=True):
        ep_page = requests.get(f"{base_url}{i.get('href').strip()}")
        ep_soup = BeautifulSoup(ep_page.content, 'html.parser')
        download_link = ep_soup.find('li', class_="dowloads").a.get('href')
        id = download_link.split('id=')[1].split('&')[0]
        id_list.append(id)
        time.sleep(1)
    get_res(id_list, starting_ep, ending_ep)

def get_res(id_list, ep_start, ep_end):
    low_res_dict = {}
    mid_res_dict = {}
    high_res_dict = {}
    counter = ep_start - 1
    for i in track(id_list, "[blue bold]Getting Links...[/blue bold]", transient=True):
        data = {
            "captcha_v3": f"{captcha_v3}",
            "id": f"{i}"
        }
        downloads = requests.post("https://s3taku.com/download", data=data)
        downloads_soup = BeautifulSoup(downloads.content, 'html.parser')

        res_list = downloads_soup.find('div', class_='mirror_link').find_all('div', class_='dowload')

        for j in res_list:
            resolution = f"{j.a.string}".replace(" ", "").replace("\n"," ")
            res_link = j.a.get('href')
            if res_link:
                counter += 1
                match resolution:
                    case "Download (360P-mp4)":
                        low_res_dict[f"EP.{counter}"] = f"{res_link}"
                    case "Download (480P-mp4)":
                        mid_res_dict[f"EP.{counter}"] = f"{res_link}"
                    case "Download (720P-mp4)":
                        high_res_dict[f"EP.{counter}"] = f"{res_link}"
    pick_res(low_res_dict, mid_res_dict, high_res_dict, ep_start, ep_end)

def download_file(url, filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    
    # Send a GET request with streaming enabled to download in chunks
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        # Get the total file size from headers
        total_size = int(r.headers.get('Content-Length', 0))
        # Set the chunk size for the download
        chunk_size = 8192
        
        # Open the file for writing in binary mode
        with open(f"{filename}.mp4", 'wb') as f:
            # Initialize tqdm progress bar with the total file size and chunk size
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"{filename}.mp4".removeprefix(f"/home/tawsif/Videos/{selected_title}")) as pbar:
                # Write the file in chunks and update the progress bar
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
    
    print(f"[green bold]Downloaded {filename}.mp4[/green bold]".removeprefix(f"/home/tawsif/Videos/{selected_title}"))

def pick_res(low_res, mid_res, high_res, ep_start, ep_end):
    ep_range = int(ep_end) - int(ep_start) + 1
    
    table = Table()
    table.add_column("[cyan]No[/cyan]",style="cyan bold", justify="center")
    table.add_column("[yellow]Resolutions[/yellow]", style="yellow bold", justify="center")
    if len(low_res) == ep_range:
        table.add_row("1","[yellow]360P[/yellow]")
    if len(mid_res) == ep_range:
        table.add_row("2","[yellow]480P[/yellow]")
    if len(high_res) == ep_range:
        table.add_row("3","[yellow]720P[/yellow]")
    if len(low_res) < ep_range and len(mid_res) < ep_range and len(high_res) < ep_range:
        print("[red bold]No common resolution is available, Lower the episode range.[/red bold]")
    
    print(table)
    if os.path.exists(f'/home/tawsif/Videos/{selected_title}'):
        if len(low_res) == ep_range or len(mid_res) == ep_range or len(high_res) == ep_range:
            choosing_res = console.input('[blue bold]Choose a resolution: [/blue bold]')
            match choosing_res:
                case '1':
                    for link, num in zip(low_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.360P")
                        time.sleep(1)
                case '2':
                    for link, num in zip(mid_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.480P")
                        time.sleep(1)
                case '3':
                    for link, num in zip(high_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.720P")
                        time.sleep(1)
    else:
        os.mkdir(f"/home/tawsif/Videos/{selected_title}")
        if len(low_res) == ep_range or len(mid_res) == ep_range or len(high_res) == ep_range:
            choosing_res = console.input('[blue bold]Choose a resolution: [/blue bold]')
            match choosing_res:
                case '1':
                    for link, num in zip(low_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.360P")
                        time.sleep(1)
                case '2':
                    for link, num in zip(mid_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.480P")
                        time.sleep(1)
                case '3':
                    for link, num in zip(high_res.values(), range(ep_start, ep_end + 1)):
                        download_file(link, f"/home/tawsif/Videos/{selected_title}/EP.{num}.720P")
                        time.sleep(1)

if __name__ == "__main__":
    choosing_anime()