import requests
import warnings
import time
import os
import re
from bs4 import BeautifulSoup
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm_rich
from rich import print
from rich import box
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.progress import track

BASE_URL = "https://anitaku.bz"
CAPTCHA_V3 = "03AFcWeA5Phyls8xv9gUYojSUiGR6tmA6CHcpFLjGx3WWSh7DZOnYTlP78j0QwLR7lfmGpmYFLgzCExJJnEMFy7jKwZdDFcf7s8Y9UXhaHsUvB95A6qCvTps_qcyPn6oieU2IoTymVwvQYcg7hK66ioEfzuvUlLUfGr8r47nnJzxe-geY6KfElW86yrcnjUVg2ChyJ0ROOYC2wz9K18DeLKqf7yt2w5VsCfLBqoqaIeiFInZ2U508MKsewFtnIRf6DarTfnRPdIa1gCmZwQixgfLIUd-rTaZZLI5Aaa33AnU18r-3x2qfp7MruJ5uB9k1SLgfD9R7pUz7si0UP67V6qPNjhdyS3UKQfoBC26KJbWHLGNZtKFPQw73AzSOqdugWdVjFJ3LQdDQHgqDE6iojJNq82-wBo2g9_sZpzI-9EBDzTYEBC-9UxZE-ZXA6TpxnLCX2YPj4ZKsWXYfMWATXHtmIxBLqpnzRoMHoKuajX8Kw15Sk7c2ih696PLJzeMsLXumVRjHJgambHD-CwOrwZnkDg5rjX8KikrfnFPTIzloFn1EeSdju6EEl4hXQDhWgtlarmKAh_iEvj4GNMBXjj8gXl_-84xSBXHHw3q6YyELh4o6TsS2y4tm3HdjdNWiMZCqMFgiWTdanUC8LFq6bjs8GlxTdmkWBjD46GtsL0TwgHCItF2Kge6lDULiJj2PEnbzMy7QiUWKPZGzpamMDA7iOfE9oA_JguOl-Pi5yQd_PYHGyhL-BWE7UN34cjKoPNERWO_0PxRO42UJj7zR8uUcwSznv9E2kNeiIXogQsIy3oxBckBBtPyDHXi5QQ5klg8oUVzRCD7Rg"

def choosing_anime():
    global selected_title
    global video_path
    anime_search = Prompt.ask("[cyan]Search[/cyan]")

    anime_links = []
    anime_titles = []
    anime_counter = 0
    table = Table(box=box.DOUBLE)
    table.add_column("[grey37]No[/grey37]",style="grey37 bold", justify="right")
    table.add_column("[yellow]Anime Name[/yellow]", style="yellow")
    table.add_column("[green]Released[/green]", style="green", justify="center")

    search_result = requests.get(f"{BASE_URL}/search.html?keyword={anime_search}&page=1")
    soup = BeautifulSoup(search_result.content, 'html.parser')

    search_items = soup.find('ul', class_="items").find_all('p')

    for item,date in zip(search_items[::2], search_items[1::2]):
        link = f"{BASE_URL}{item.a.get('href')}"
        anime_links.append(link)
        title = item.a.string
        anime_titles.append(title)
        rel_date = date.text.strip()
        anime_counter += 1
        table.add_row(str(anime_counter), title, rel_date.removeprefix("Released: "))

    if len(anime_links) > 0:
        print(table)
        choose_anime = IntPrompt.ask("[cyan]Pick Anime[/cyan]") - 1
        selected_title = anime_titles[choose_anime]
        sanitized_name = re.sub(r'[\\/*?:"<>|]', "", selected_title)
        video_path = os.path.expanduser(f"~/Anime/{sanitized_name}")
        if not os.path.exists(video_path):
            os.makedirs(video_path, exist_ok=True)
        max_ep(anime_links[choose_anime], selected_title)
    else:
        print("[red bold]There's no anime, Try again...[/red bold]")
        return

def max_ep(choosed_anime, anime_title):
    anime_page = requests.get(choosed_anime)
    anime_soup = BeautifulSoup(anime_page.content, 'html.parser')

    episodes = anime_soup.find('ul', id='episode_page').find_all('a')[-1]
    ep_end = episodes.get('ep_end')
    print(f"[bold]{anime_title} ({ep_end})[/bold]")
    download_id(anime_soup, ep_end)

def download_id(anime_soup, ep_end):
    anime_id = anime_soup.find('input', id="movie_id").get('value')

    starting_ep = IntPrompt.ask("[cyan]Starting episode[/cyan]") if ep_end != '1' else 1
    ending_ep = IntPrompt.ask("[cyan]Ending episode[/cyan]") if ep_end != '1' else 1

    if starting_ep <= ending_ep:
        eps_links_page = requests.get(f"https://ajax.gogocdn.net/ajax/load-list-episode?ep_start={starting_ep}&ep_end={ending_ep}&id={anime_id}")
    else:
        print("[red bold]Starting ep should be smaller or equal to the ending ep[/red bold]")
        return
    eps_soup = BeautifulSoup(eps_links_page.content, 'html.parser')

    ep_links = eps_soup.find_all('a')
    ep_links.reverse()
    id_list = []
    for i in track(ep_links, "[purple4 italic]Processing...[/purple4 italic]", transient=True):
        ep_page = requests.get(f"{BASE_URL}{i.get('href').strip()}")
        ep_soup = BeautifulSoup(ep_page.content, 'html.parser')
        download_link = ep_soup.find('li', class_="dowloads").a.get('href')
        id = download_link.split('id=')[1].split('&')[0]
        id_list.append(id)
        time.sleep(0.1)
    get_res(id_list, starting_ep, ending_ep)

def get_res(id_list, ep_start, ep_end):
    low_res_dict = {}
    mid_res_dict = {}
    high_res_dict = {}
    extreame_res_dict = {}
    counter = ep_start
    for i in track(id_list, "[purple4 italic]Getting Links...[/purple4 italic]", transient=True):
        data = {
            "captcha_v3": f"{CAPTCHA_V3}",
            "id": f"{i}"
        }
        downloads = requests.post("https://s3embtaku.pro/download", data=data)
        downloads_soup = BeautifulSoup(downloads.content, 'html.parser')

        res_list = downloads_soup.find('div', class_='mirror_link').find_all('div', class_='dowload')

        for j in res_list:
            resolution = f"{j.a.string}".replace(" ", "").replace("\n"," ")
            res_link = j.a.get('href')
            if res_link:
                match resolution:
                    case "Download (360P-mp4)":
                        low_res_dict[f"EP.{counter}"] = f"{res_link}"
                    case "Download (480P-mp4)":
                        mid_res_dict[f"EP.{counter}"] = f"{res_link}"
                    case "Download (720P-mp4)":
                        high_res_dict[f"EP.{counter}"] = f"{res_link}"
                    case "Download (1080P-mp4)":
                        extreame_res_dict[f"EP.{counter}"] = f"{res_link}"
        counter += 1

    pick_res(low_res_dict, mid_res_dict, high_res_dict, extreame_res_dict, ep_start, ep_end)

def download_file(url, filename, max_retries=5):
    warnings.filterwarnings('ignore', category=TqdmExperimentalWarning)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }

    retries = 0

    while retries < max_retries:
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('Content-Length', 0))
            chunk_size = 8192

            # If total_size is zero, increment retries and try again
            if total_size == 0:
                retries += 1
                print(f"[yellow bold]Total size is zero. Retrying... ({retries}/{max_retries})[/yellow bold]")
                continue

            # If total_size is valid, proceed with the download
            m_filename = filename.removeprefix(f"{video_path}/")
            with open(f"{filename}.mp4", 'wb') as f:
                with tqdm_rich(total=total_size, unit='B', unit_scale=True, desc=f"[orange_red1]{m_filename}.mp4[/orange_red1]", dynamic_ncols=True) as pbar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            print(f"[bright_green bold]Download Completed {m_filename} \n[/bright_green bold]")
            return

    print(f"[red bold]Failed to download {filename} after {max_retries} attempts. Exiting.[/red bold]")

def pick_res(low_res, mid_res, high_res, extreame_res, ep_start, ep_end):
    ep_range = int(ep_end) - int(ep_start) + 1

    table = Table(box=box.DOUBLE)
    table.add_column("[grey37]No[/grey37]",style="grey37 bold", justify="right")
    table.add_column("[yellow]Resolutions[/yellow]", style="yellow bold", justify="center")
    if len(low_res) == ep_range:
        table.add_row("1","[yellow]360P[/yellow]")
    if len(mid_res) == ep_range:
        table.add_row("2","[yellow]480P[/yellow]")
    if len(high_res) == ep_range:
        table.add_row("3","[yellow]720P[/yellow]")
    if len(extreame_res) == ep_range:
        table.add_row("4","[yellow]1080P[/yellow]")
    if len(low_res) < ep_range and len(mid_res) < ep_range and len(high_res) < ep_range and len(extreame_res) < ep_range:
        print("[red bold]No common resolution is available, Lower the episode range.[/red bold]")
        return
    else:
        print(table)
    if len(low_res) == ep_range or len(mid_res) == ep_range or len(high_res) == ep_range or len(extreame_res) == ep_range:
        choosing_res = Prompt.ask('[cyan]Choose resolution[/cyan]')
        match choosing_res:
            case '1':
                for link, num in zip(low_res.values(), range(ep_start, ep_end + 1)):
                    download_file(link, f"{video_path}/EP.{num}.360P")
                    time.sleep(1)
            case '2':
                for link, num in zip(mid_res.values(), range(ep_start, ep_end + 1)):
                    download_file(link, f"{video_path}/EP.{num}.480P")
                    time.sleep(1)
            case '3':
                for link, num in zip(high_res.values(), range(ep_start, ep_end + 1)):
                    download_file(link, f"{video_path}/EP.{num}.720P")
                    time.sleep(1)
            case '4':
                for link, num in zip(extreame_res.values(), range(ep_start, ep_end + 1)):
                    download_file(link, f"{video_path}/EP.{num}.1080P")
                    time.sleep(1)

if __name__ == "__main__":
    choosing_anime()
