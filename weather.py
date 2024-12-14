import tkinter as tk
from tkinter import Toplevel, messagebox
import threading
import requests

# OpenWeatherMap API setup (replace with your own API key)
API_KEY = "794eac17c9d7cb5fb86e532d70237cf8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Global list to keep track of all timer threads
active_timers = []

def fetch_and_display_weather(location, weather_window):
    try:
        # Request weather data
        response = requests.get(BASE_URL, params={"q": location, "appid": API_KEY, "units": "metric"})
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            weather_data = f"Location: {location}\nTemperature: {temperature}°C\nHumidity: {humidity}%\nPressure: {pressure}"
        else:
            weather_data = f"Location: {location}\nError: Unable to fetch data."
    except Exception as e:
        weather_data = f"Location: {location}\nError: {e}"

    # Check if the window still exists before updating
    if weather_window.winfo_exists():
        weather_window.config(bg="#f0f0f0")
        weather_window.children["label"].config(text=weather_data)

def periodic_weather_update(location, weather_window, interval=60):
    # Check if the window is still open before updating
    if weather_window.winfo_exists():
        fetch_and_display_weather(location, weather_window)
        # Create a new timer and add it to the active timers list
        timer = threading.Timer(interval, periodic_weather_update, [location, weather_window, interval])
        active_timers.append(timer)
        timer.start()

def run_weather_app():
    def process_weather_data(locations):
        for location in locations:
            # Create a new weather window for each location
            weather_window = Toplevel(root)
            weather_window.title(f"Weather Data - {location}")
            weather_window.geometry("300x200")
            weather_window.config(bg="#f0f0f0")

            label = tk.Label(weather_window, text="Fetching data...", font=("Arial", 12), bg="#f0f0f0", justify=tk.LEFT)
            label.pack(pady=20, padx=20)
            weather_window.children["label"] = label  # Save reference to the label for future updates

            # Start periodic updates for this location's weather data
            periodic_weather_update(location, weather_window, 60)

    def start_aggregation():
        try:
            # Cancel any existing timers
            for timer in active_timers:
                timer.cancel()
            active_timers.clear()

            num_threads = int(thread_input.get())
            if 1 <= num_threads <= 5:
                # Clear any previously entered location entries
                for widget in location_entries_frame.winfo_children():
                    widget.destroy()

                # Create new entry fields for the locations
                location_entries = []
                for i in range(num_threads):
                    location_label = tk.Label(location_entries_frame, text=f"Location {i+1}:", font=("Arial", 12), bg="#f0f0f0")
                    location_label.pack(pady=5)

                    location_entry = tk.Entry(location_entries_frame, font=("Arial", 12), width=20)
                    location_entry.pack(pady=5)
                    location_entries.append(location_entry)

                submit_button = tk.Button(location_entries_frame, text="Fetch Weather Data", 
                                          command=lambda: process_weather_data([entry.get() for entry in location_entries]), 
                                          font=("Arial", 12, "bold"), bg="#2196F3", fg="white", padx=10, pady=5)
                submit_button.pack(pady=20)

            else:
                messagebox.showerror("Input Error", "Please enter a number between 1 and 5.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number.")

    # Setup the main GUI for the weather data aggregator
    root = tk.Tk()
    root.title("Weather Data Aggregator")
    root.geometry("400x500")
    root.config(bg="#f0f0f0")

    # Add a function to handle application closure
    def on_closing():
        # Cancel all active timers
        for timer in active_timers:
            timer.cancel()
        active_timers.clear()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    title_label = tk.Label(root, text="Weather Data Aggregator", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#4CAF50")
    title_label.pack(pady=20)

    thread_label = tk.Label(root, text="Enter number of threads (1-5):", font=("Arial", 12), bg="#f0f0f0")
    thread_label.pack(pady=10)

    thread_input = tk.Entry(root, font=("Arial", 12), width=10)
    thread_input.pack(pady=5)

    fetch_button = tk.Button(root, text="Submit", command=start_aggregation, 
                              font=("Arial", 12, "bold"), bg="#2196F3", fg="white", padx=10, pady=5)
    fetch_button.pack(pady=20)

    location_entries_frame = tk.Frame(root, bg="#f0f0f0")
    location_entries_frame.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_weather_app()