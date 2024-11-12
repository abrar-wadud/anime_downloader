# Anime Downloader

A Python-based CLI tool for downloading anime episodes with multiple resolution options. This script provides an interactive interface to search, select, and download anime episodes from anitaku.bz with a progress bar and colorful terminal output.

## Features

- 🔍 Search functionality for finding anime titles
- 📺 Support for multiple video resolutions (360P, 480P, 720P, 1080P)
- 📊 Interactive progress bars using rich and tqdm
- 🎨 Colored terminal output for better user experience
- 💾 Automatic download directory creation
- 🔄 Retry mechanism for failed downloads
- 📝 Episode range selection
- 🛡️ Built-in error handling and input validation

## Prerequisites

Make sure you have Python 3.x installed on your system. You'll need the following Python packages:

```bash
pip install requests beautifulsoup4 rich tqdm
```

## Installation

1. Clone this repository or download the script
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python anime_downloader.py
```

2. Follow the interactive prompts:
   - Enter an anime title to search
   - Select an anime from the search results
   - Choose starting and ending episodes
   - Select your preferred resolution

The downloaded episodes will be saved in `~/Anime/[Anime Title]/` directory.

## How It Works

1. The script first prompts for an anime title to search
2. Displays search results in a table format
3. After selecting an anime, shows available episodes
4. Allows selection of episode range and resolution
5. Downloads episodes with progress tracking
6. Saves files in organized directories

## Features In Detail

### Search Interface
- Displays anime titles with release dates
- Numbers each result for easy selection
- Shows colorized output for better readability

### Download Management
- Creates organized folder structure
- Handles network interruptions
- Shows detailed progress bars
- Supports multiple resolution options
- Validates episode ranges

### Error Handling
- Retries failed downloads up to 5 times
- Validates user input
- Checks for available resolutions
- Creates directories safely

## Dependencies

- `requests`: For making HTTP requests
- `beautifulsoup4`: For parsing HTML content
- `rich`: For terminal formatting and progress bars
- `tqdm`: For download progress tracking

## Notes

- The script uses captcha verification
- Downloads are saved to the user's home directory under "Anime"
- Episode filenames include resolution (e.g., "EP.1.720P.mp4")
- The script includes delays between requests to prevent rate limiting

## Limitations

- Only works with anitaku.bz
- Requires stable internet connection
- Downloads one episode at a time
- Resolution availability varies by anime

## Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements or bug fixes.

## License

This project is available under the MIT License. Feel free to modify and distribute as needed.
