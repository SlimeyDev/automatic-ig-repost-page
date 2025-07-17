import os
from instagrapi import Client
import time
from pathlib import Path
import cv2
from datetime import datetime, timedelta
import instaloader
import shutil
import sys
from colorama import init, Fore, Style
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configuration Variables
# Download Account (Instaloader)
DOWNLOAD_USERNAME = os.getenv("DOWNLOAD_USERNAME")
DOWNLOAD_PASSWORD = os.getenv("DOWNLOAD_PASSWORD")
REEL_LINKS_FILE = "reels.txt"
DOWNLOAD_DELAY = 5

# Upload Account (Instagrapi)
UPLOAD_USERNAME = os.getenv("UPLOAD_USERNAME")
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")
REEL_CAPTION = os.getenv("REEL_CAPTION")
UPLOAD_DELAY = 1000

# Initialize colorama
init()

def print_header():
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Instagram Reel Downloader and Uploader")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}{message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")

def format_time(seconds):
    """Format seconds into hours:minutes:seconds"""
    return str(timedelta(seconds=seconds))

def countdown(seconds):
    """Display a countdown timer"""
    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f'{hours:02d}:{mins:02d}:{secs:02d}'
        print(f'\rNext upload in: {timer}', end='')
        time.sleep(1)
        seconds -= 1
    print('\rNext upload in: 00:00:00')

def handle_challenge(client, username):
    """Handle Instagram's challenge verification"""
    try:
        print(f"\nInstagram requires verification for {username}")
        print("Please check your email for the verification code.")
        
        while True:
            code = input("Enter the 6-digit code from your email: ")
            if len(code) == 6 and code.isdigit():
                try:
                    client.challenge_code(code)
                    print("Verification successful!")
                    return True
                except Exception as e:
                    print(f"Invalid code. Please try again. Error: {str(e)}")
            else:
                print("Please enter a valid 6-digit code.")
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return False

def check_video_aspect_ratio(video_path):
    """Check if video has 9:16 aspect ratio"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    # 9:16 aspect ratio is approximately 0.5625
    return abs(aspect_ratio - 0.5625) < 0.1  # Allow small margin of error

def upload_reels(video_folder_path, common_caption):
    # Initialize the Instagram client
    client = Client()
    
    try:
        client.login(UPLOAD_USERNAME, UPLOAD_PASSWORD)
        print_success("Successfully logged in to Instagram!")
    except Exception as e:
        if "challenge_required" in str(e):
            if handle_challenge(client, UPLOAD_USERNAME):
                print_success("Successfully logged in to Instagram!")
            else:
                print_error("Failed to complete verification. Please try again later.")
                return
        else:
            print_error(f"Login failed: {str(e)}")
            return
    
    try:
        # Get all video files from the specified folder
        video_extensions = ('.mp4', '.mov', '.avi')
        video_files = [f for f in os.listdir(video_folder_path) 
                      if f.lower().endswith(video_extensions)]
        
        if not video_files:
            print_error("No video files found in the specified folder!")
            return
        
        print_info(f"Found {len(video_files)} video files to upload.")
        
        # Upload each video as a reel
        for i, video_file in enumerate(video_files, 1):
            video_path = os.path.join(video_folder_path, video_file)
            print_info(f"\nProcessing {video_file} ({i}/{len(video_files)})...")
            
            # Check aspect ratio
            if not check_video_aspect_ratio(video_path):
                print_warning(f"Warning: {video_file} does not have 9:16 aspect ratio. Skipping...")
                continue
            
            try:
                # Upload the video as a reel with common caption
                client.clip_upload(
                    video_path,
                    caption=common_caption
                )
                print_success(f"Successfully uploaded {video_file} as a reel!")
                
                if i < len(video_files):
                    print_info(f"\nWaiting {UPLOAD_DELAY} seconds before next upload...")
                    countdown(UPLOAD_DELAY)
                
            except Exception as e:
                print_error(f"Error uploading {video_file}: {str(e)}")
                continue
        
        print_success("\nAll videos have been processed!")
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")

def clean_downloads_folder():
    download_dir = Path("downloads")
    if download_dir.exists():
        print_info("Cleaning downloads folder...")
        for item in download_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print_success("Downloads folder cleaned.")
    else:
        download_dir.mkdir()
        print_success("Created downloads folder.")

def download_reel(L, reel_url, index, total):
    temp_dir = None
    try:
        # Extract the shortcode from the URL
        shortcode = reel_url.split("/")[-2]
        
        # Get the post
        time.sleep(2)  # Add delay before post fetch
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Create a downloads directory if it doesn't exist
        download_dir = Path("downloads")
        download_dir.mkdir(exist_ok=True)
        
        # Create a temporary directory for the download
        temp_dir = Path("temp_download")
        temp_dir.mkdir(exist_ok=True)
        
        # Download the post to temporary directory
        L.download_post(post, target=temp_dir)
        
        # Find the MP4 file in the temporary directory
        mp4_files = list(temp_dir.glob("*.mp4"))
        if mp4_files:
            # Get the first MP4 file (there should only be one)
            mp4_file = mp4_files[0]
            # Create a filename based on the index
            new_filename = f"{index}.mp4"
            # Move the MP4 file to the downloads directory
            shutil.move(str(mp4_file), str(download_dir / new_filename))
            print_success(f"Downloaded reel {index}/{total} to {download_dir / new_filename}")
            return True
        else:
            print_error("No MP4 file found in the downloaded content")
            return False
            
    except instaloader.exceptions.InstaloaderException as e:
        if "rate limit" in str(e).lower() or "wait a few minutes" in str(e).lower():
            print_warning("Rate limit reached. Please wait a few minutes before trying again.")
        elif "login_required" in str(e).lower():
            print_error("Session expired. Please log in again.")
        else:
            print_error(f"Error downloading reel: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Error downloading reel: {str(e)}")
        return False
    finally:
        # Clean up temporary directory if it exists
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print_warning(f"Could not clean up temporary directory: {str(e)}")

def read_links_from_file(filename):
    try:
        with open(filename, 'r') as file:
            # Read all lines and strip whitespace
            links = [line.strip() for line in file if line.strip()]
        return links
    except FileNotFoundError:
        print_error(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print_error(f"Error reading file: {str(e)}")
        return []

def download_reels():
    print_header()
    
    # Clean downloads folder at startup
    clean_downloads_folder()
    
    # Initialize Instaloader
    L = instaloader.Instaloader()
    
    # Login to Instagram with download account
    print_info("Logging in to Instagram with download account...")
    try:
        L.login(DOWNLOAD_USERNAME, DOWNLOAD_PASSWORD)
        print_success("Successfully logged in with download account.")
    except instaloader.exceptions.InstaloaderException as e:
        if "login_required" in str(e).lower():
            print_error("Login required. Please check your credentials.")
        elif "rate limit" in str(e).lower():
            print_error("Rate limit reached. Please wait a few minutes before trying again.")
        else:
            print_error(f"Login failed: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Login failed: {str(e)}")
        return False
    
    # Read links from file
    links = read_links_from_file(REEL_LINKS_FILE)
    
    if not links:
        print_error("No valid links found in the file.")
        return False
    
    print_info(f"\nFound {len(links)} links to process.")
    
    # Process each link
    successful_downloads = 0
    for i, link in enumerate(links, 1):
        print_info(f"\nProcessing link {i}/{len(links)}")
        if download_reel(L, link, i, len(links)):
            successful_downloads += 1
        time.sleep(DOWNLOAD_DELAY)  # Add delay between downloads
    
    print_info(f"\nDownload complete! Successfully downloaded {successful_downloads} out of {len(links)} reels.")
    return successful_downloads > 0

def main():
    print_header()
    
    # Download reels
    if download_reels():
        print_success("Reels downloaded successfully!")
        
        # Upload the downloaded reels
        print_info("\nStarting upload process...")
        upload_reels("downloads", REEL_CAPTION)
    else:
        print_error("Failed to download reels. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"\nAn unexpected error occurred: {str(e)}")
        sys.exit(1)
