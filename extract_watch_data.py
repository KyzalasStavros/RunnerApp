#!/usr/bin/env python3
"""
Smart Watch Data Extractor
Analyzes training session images from smart watch and extracts key metrics
"""

import os
import re
import json
import pandas as pd
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt
from datetime import datetime
import argparse


class WatchDataExtractor:
    """Extract training data from smart watch screenshot images"""
    
    def __init__(self, data_folder="mi data"):
        self.data_folder = data_folder
        self.extracted_data = []
        
    def extract_filename_info(self, filename):
        """Extract week and day info from filename like Session_W1_D1.JPG"""
        pattern = r'Session_W(\d+)_D(\d+)\.JPG'
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            week = int(match.group(1))
            day = int(match.group(2))
            return week, day
        return None, None
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        # Read image
        img = cv2.imread(str(image_path))
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_from_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Convert back to PIL Image for pytesseract
            pil_img = Image.fromarray(processed_img)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(pil_img, config='--psm 6')
            
            return text
        except Exception as e:
            print(f"Error extracting text from {image_path}: {e}")
            return ""
    
    def parse_metrics(self, text, week, day):
        """Parse training metrics from extracted text - focusing on reliable Mi Fitness patterns"""
        metrics = {
            'week': week,
            'day': day,
            'duration': None,
            'distance': None,
            'avg_pace': None,
            'avg_hr': None,
            'max_hr': None,
            'avg_cadence': None,
            'calories': None,
            'active_calories': None,
            'total_calories': None,
            'steps': None
        }
        
        # Clean text - handle OCR quirks
        text_clean = text.replace('\n', ' ').replace('|', 'l').replace('\u00a9', '').replace('©', '')
        text_clean = text_clean.replace('\u00a0', ' ').replace('°', '\'').replace('\u00b0', '\'')
        
        print(f"  Debug: Parsing text snippet: {text_clean[:150]}...")
        
        # Pattern 1: Extract workout duration from "HH:MM:SS number kcal number kcal" format
        # Handle OCR variations: "kcal", "ka", "kcai", etc.
        # Examples: "01:08:09 314 kcal 420 kcal", "00:38:18 324 ka 384 kcal", "00:34:56 269 kcai 323 kcal"
        duration_patterns = [
            r'(\d{2}:\d{2}:\d{2})\s+(\d+)\s+k?cal?\s+(\d+)\s+kcal',  # Standard: "314 kcal 420 kcal"
            r'(\d{2}:\d{2}:\d{2})\s+(\d+)\s+ka\s+(\d+)\s+kcal',      # OCR variant: "324 ka 384 kcal"
            r'(\d{2}:\d{2}:\d{2})\s+(\d+)\s+kcai\s+(\d+)\s+kcal',    # OCR variant: "269 kcai 323 kcal"
            r'(\d{2}:\d{2}:\d{2})\s+(\d+)\s+\w{2,4}\s+(\d+)\s+kcal', # Flexible: any 2-4 chars between numbers
        ]
        
        for pattern in duration_patterns:
            duration_match = re.search(pattern, text_clean, re.IGNORECASE)
            if duration_match:
                metrics['duration'] = duration_match.group(1)
                metrics['active_calories'] = duration_match.group(2)
                metrics['total_calories'] = duration_match.group(3)
                print(f"  ✅ Found duration: {metrics['duration']}, calories: {metrics['active_calories']}/{metrics['total_calories']}")
                break
        
        if not metrics['duration']:
            print(f"  ❌ Duration pattern not found")
        
        # Pattern 2: Extract pace, HR, steps from "MM'SS\" number sem/eeu number" format
        # Examples: "11'20\" 116 sem 7425" or "9'02\" 151 sem 5234" or "8'37\" 144 eeu 5002"
        pace_hr_steps_patterns = [
            r"(\d{1,2})'(\d{2})\"\s+(\d{2,3})\s+(?:sem|eeu)\s+(\d+)",  # Handle sem/eeu OCR variants
            r"(\d{1,2})'(\d{2})\"\s+(\d{2,3})\s+\w{2,3}\s+(\d+)",     # Generic 2-3 char word
            r"(\d{1,2})'(\d{2})\"\s+(\d{2,3})\s+\S+\s+(\d+)"         # Any non-space chars
        ]
        
        for pattern in pace_hr_steps_patterns:
            pace_match = re.search(pattern, text_clean)
            if pace_match:
                pace_min = int(pace_match.group(1))
                pace_sec = int(pace_match.group(2))
                metrics['avg_pace'] = f"{pace_min}:{pace_sec:02d}"
                metrics['avg_hr'] = pace_match.group(3)
                metrics['steps'] = pace_match.group(4)
                print(f"  ✅ Found pace/HR/steps: {metrics['avg_pace']}, {metrics['avg_hr']} bpm, {metrics['steps']} steps")
                break
        
        if not metrics['avg_pace']:
            print(f"  ❌ Pace/HR/steps pattern not found")
        
        # Calculate distance from duration and pace if both available
        if metrics['duration'] and metrics['avg_pace']:
            try:
                # Parse duration: "01:08:09" -> total minutes
                h, m, s = map(int, metrics['duration'].split(':'))
                total_minutes = h * 60 + m + s / 60
                
                # Parse pace: "11:20" -> minutes per km
                pace_min, pace_sec = map(int, metrics['avg_pace'].split(':'))
                pace_per_km = pace_min + pace_sec / 60
                
                # Calculate distance
                estimated_distance = round(total_minutes / pace_per_km, 1)
                if 1 <= estimated_distance <= 15:  # Reasonable range
                    metrics['distance'] = str(estimated_distance)
                    print(f"  ✅ Calculated distance: {metrics['distance']} km")
                else:
                    print(f"  ⚠️  Calculated distance {estimated_distance} km seems unreasonable")
            except (ValueError, ZeroDivisionError) as e:
                print(f"  ❌ Distance calculation failed: {e}")
        
        # Look for explicit distance in "X km | Time:" format
        if not metrics['distance']:
            distance_explicit = re.search(r'(\d+\.?\d*)\s*km\s*[|l]\s*time', text_clean, re.IGNORECASE)
            if distance_explicit:
                metrics['distance'] = distance_explicit.group(1)
                print(f"  ✅ Found explicit distance: {metrics['distance']} km")
        
        # Set main calories field
        if metrics['total_calories']:
            metrics['calories'] = metrics['total_calories']
        elif metrics['active_calories']:
            metrics['calories'] = metrics['active_calories']
        
        # Try to find max HR in the heart rate zones section
        # Look for higher numbers that could be max HR
        if metrics['avg_hr']:
            avg_hr_val = int(metrics['avg_hr'])
            # Find numbers in reasonable max HR range that are higher than avg
            hr_candidates = re.findall(r'\b(1[5-9]\d|200)\b', text_clean)
            if hr_candidates:
                max_hr_values = [int(x) for x in hr_candidates if int(x) > avg_hr_val and 150 <= int(x) <= 200]
                if max_hr_values:
                    metrics['max_hr'] = str(max(max_hr_values))
                    print(f"  ✅ Found max HR: {metrics['max_hr']} bpm")
        
        return metrics
    
    def process_images(self):
        """Process all images in the data folder"""
        data_folder_path = Path(self.data_folder)
        
        if not data_folder_path.exists():
            print(f"Error: Data folder '{self.data_folder}' not found!")
            return
        
        # Find all JPG files matching the pattern
        image_files = list(data_folder_path.glob("Session_W*_D*.JPG"))
        image_files.extend(list(data_folder_path.glob("Session_W*_D*.jpg")))
        
        if not image_files:
            print(f"No training session images found in '{self.data_folder}'")
            return
        
        print(f"Found {len(image_files)} training session images")
        
        for image_file in sorted(image_files):
            week, day = self.extract_filename_info(image_file.name)
            
            if week is None or day is None:
                print(f"Skipping {image_file.name} - invalid filename format")
                continue
            
            print(f"Processing Week {week}, Day {day}: {image_file.name}")
            
            # Extract text from image
            text = self.extract_text_from_image(image_file)
            
            # Parse metrics from text
            metrics = self.parse_metrics(text, week, day)
            
            # Add filename for reference (but not raw text)
            metrics['filename'] = image_file.name
            
            self.extracted_data.append(metrics)
            
            # Show what was extracted
            print(f"  Extracted: Duration={metrics['duration']}, Distance={metrics['distance']}, "
                  f"Avg HR={metrics['avg_hr']}, Max HR={metrics['max_hr']}")
    
    def save_data(self):
        """Save extracted data to both JSON and clean CSV format in mi_data_extracted folder"""
        if not self.extracted_data:
            print("No data to save!")
            return
        
        # Create output directory if it doesn't exist
        output_dir = "mi_data_extracted"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_filename = os.path.join(output_dir, f"training_data_extracted_{timestamp}.json")
        with open(json_filename, 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        print(f"Data saved to {json_filename}")
        
        # Save as clean CSV with proper columns
        df = pd.DataFrame(self.extracted_data)
        csv_filename = os.path.join(output_dir, f"training_data_extracted_{timestamp}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")
    
    def create_summary_report(self):
        """Create a summary report of extracted data"""
        if not self.extracted_data:
            print("No data to summarize!")
            return
        
        print("\n" + "="*60)
        print("TRAINING DATA EXTRACTION SUMMARY")
        print("="*60)
        
        df = pd.DataFrame(self.extracted_data)
        
        for _, row in df.iterrows():
            print(f"\nWeek {row['week']}, Day {row['day']} ({row['filename']}):")
            print(f"  Duration: {row['duration'] or 'Not found'}")
            print(f"  Distance: {row['distance'] or 'Not found'} km")
            print(f"  Avg Pace: {row['avg_pace'] or 'Not found'} /km")
            print(f"  Avg HR: {row['avg_hr'] or 'Not found'} bpm")
            print(f"  Max HR: {row['max_hr'] or 'Not found'} bpm")
            print(f"  Steps: {row['steps'] or 'Not found'}")
            print(f"  Cadence: {row['avg_cadence'] or 'Not found'} spm")
        
        print(f"\nTotal sessions processed: {len(self.extracted_data)}")


def main():
    parser = argparse.ArgumentParser(description='Extract training data from smart watch images')
    parser.add_argument('--folder', default='mi data', help='Folder containing training images')
    
    args = parser.parse_args()
    
    print("Smart Watch Training Data Extractor")
    print("="*40)
    
    # Check if pytesseract is available
    try:
        pytesseract.get_tesseract_version()
    except:
        print("Error: pytesseract/tesseract not found!")
        print("Please install tesseract OCR:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt install tesseract-ocr")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return
    
    # Create extractor and process images
    extractor = WatchDataExtractor(args.folder)
    extractor.process_images()
    
    # Save data and create report
    extractor.save_data()
    extractor.create_summary_report()
    
    print(f"\n✅ Extraction complete! Check the generated files for results.")


if __name__ == "__main__":
    main()
