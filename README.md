# Instagram Reel Automation Tool

A Python-based automation tool for downloading and uploading Instagram reels. This tool helps you manage Instagram reels by downloading them from specified URLs and uploading them to your account with custom captions.

## Features

- Download Instagram reels from a list of URLs
- Automatic aspect ratio checking (9:16) for reels
- Upload reels with custom captions
- Rate limiting and delay management
- Challenge verification handling
- Progress tracking and colored console output
- Temporary file cleanup

## Prerequisites

- Python 3.7 or higher
- FFmpeg installed on your system
- Instagram account credentials

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```
DOWNLOAD_USERNAME=your_download_account_username
DOWNLOAD_PASSWORD=your_download_account_password
UPLOAD_USERNAME=your_upload_account_username
UPLOAD_PASSWORD=your_upload_account_password
REEL_CAPTION=your_default_reel_caption
```

## Usage

1. Add Instagram reel URLs to `reels.txt`, one URL per line.

2. Run the main script:
```bash
python main.py
```

The script will:
- Download reels from the URLs in `reels.txt`
- Check each reel's aspect ratio
- Upload valid reels to your Instagram account
- Handle any Instagram challenges or rate limits
- Clean up temporary files

## Configuration

You can modify the following variables in `main.py`:
- `DOWNLOAD_DELAY`: Delay between downloads (default: 5 seconds)
- `UPLOAD_DELAY`: Delay between uploads (default: 1000 seconds)
- `REEL_LINKS_FILE`: File containing reel URLs (default: "reels.txt")

## Dependencies

- instagrapi: Instagram API wrapper
- opencv-python: Video processing
- numpy: Numerical operations
- colorama: Colored console output
- tqdm: Progress bars
- dotenv: Environment variable management
- Pillow: Image processing
- requests: HTTP requests