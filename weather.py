import tkinter as tk
from tkinter import Toplevel, messagebox
import threading
import requests
import time

API_KEY = "794eac17c9d7cb5fb86e532d70237cf8"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Global list to keep track of all timer threads
active_timers = []

def fetch_weather_data(location):
    start_time = time.time()

    response = requests.get(BASE_URL, params={"q": location, "appid": API_KEY, "units": "metric"})
    data = response.json()

    end_time = time.time()
    execution_time = end_time - start_time

    if response.status_code == 200:
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        
        weather_data = (f"Location: {location}\n"
                        f"Temperature: {temperature}°C\n"
                        f"Humidity: {humidity}%\n"
                        f"Pressure: {pressure}\n")
    else:
        weather_data = f"Location: {location}\nError: Unable to fetch data."
    return location, weather_data, execution_time

def periodic_weather_update(location, weather_window, interval=60):
    # Check if the window is still open before updating
    if weather_window.winfo_exists():
        # Fetch the weather data again (new request)
        _, weather_data_str, _ = fetch_weather_data(location)

        # Update the label with the new weather data
        if weather_window.winfo_exists():
            weather_window.children["label"].config(text=weather_data_str)

        # Create a new timer to call this function again after the specified interval
        timer = threading.Timer(interval, periodic_weather_update, [location, weather_window, interval])
        active_timers.append(timer)
        timer.start()

def run_weather_app():
    def process_weather_data(locations):
        # Create windows for each location
        weather_windows = {}
        for location in locations:
            # Create a new weather window for each location
            weather_window = Toplevel(root)
            weather_window.title(f"Weather Data - {location}")
            weather_window.geometry("300x250")
            weather_window.config(bg="#f0f0f0")

            label = tk.Label(weather_window, text="Fetching data...", font=("Arial", 12), bg="#f0f0f0", justify=tk.LEFT)
            label.pack(pady=20, padx=20)
            weather_window.children["label"] = label  # Save reference to the label

            weather_windows[location] = weather_window

        # Timing and thread management
        threads = []
        weather_data_list = []
        thread_locations = []

        # Start timing BEFORE creating threads
        overall_start_time = time.time()

        # Create and start threads
        for location in locations:
            # Thread will fetch weather data once and store the data in the weather_data_list
            thread = threading.Thread(target=lambda loc: weather_data_list.append(fetch_weather_data(loc)),
                                    args=(location,))
            thread_locations.append(location)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # overall execution time
        overall_end_time = time.time()
        overall_execution_time = overall_end_time - overall_start_time

        # Display results and update weather windows
        print("\nIndividual Thread Execution Times :")
        for loc, weather_data in zip(thread_locations, weather_data_list):
            _, weather_data_str, execution_time = weather_data
            print(f"{loc}: {execution_time:.4f} seconds")

            # Update the corresponding weather window
            weather_window = weather_windows[loc]
            if weather_window.winfo_exists():
                weather_window.children["label"].config(text=weather_data_str)

        # Start periodic updates after displaying the initial data
        for location, weather_window in weather_windows.items():
            # Updates
            periodic_weather_update(location, weather_window, interval=60)


        print(f"\nOverall Thread Execution Time: {overall_execution_time:.4f} seconds")

    def start_aggregation():
        # Cancel any existing timers
        for timer in active_timers:
            timer.cancel()
        active_timers.clear()

        num_threads = int(thread_input.get())
        if 1 <= num_threads <= 20:
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
            messagebox.showerror("Input Error", "Please enter a number between 1 and 20.")

    def on_closing():
        # Cancel all active timers
        for timer in active_timers:
            timer.cancel()
        active_timers.clear()
        root.destroy()

    # main GUI
    root = tk.Tk()
    root.title("Weather Data Aggregator")
    root.geometry("400x500")
    root.config(bg="#f0f0f0")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    title_label = tk.Label(root, text="Weather Data Aggregator", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#4CAF50")
    title_label.pack(pady=20)

    thread_label = tk.Label(root, text="Enter number of threads between (1:20) :", font=("Arial", 12), bg="#f0f0f0")
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
