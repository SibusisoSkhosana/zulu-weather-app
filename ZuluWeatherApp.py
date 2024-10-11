import os
import sys
import requests
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        load_dotenv()
        self.api_key = os.getenv('OPENWEATHER_API_KEY')

        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.description_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Zulu Weather App")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.description_label)
        vbox.addWidget(self.emoji_label)
        
        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.temperature_label.setObjectName("temperature_label")
        self.description_label.setObjectName("description_label")
        self.emoji_label.setObjectName("emoji_label")
        self.get_weather_button.setObjectName("get_weather_button")

        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family:calibri;           
            }
            QLabel#city_label{
                font-size:40px;
                font-style: italic;
            }
            QLineEdit#city_input{
                font-size: 40px;                              
            }
            QPushButton#get_weather_button{
                font-size:40px;
                font-weight: bold;
            }             
            QLabel#city_input{
                font-size: 40px;                              
            }
            QLabel#temperature_label{
                font-size:75px;
            }   

            QLabel#emoji_label{
                font-size:100px;
                font-family:Segoe UI emoji;           
                           }  

            QLabel#description_label{
                font-size:50px;               
            }                           
                           
        """)
        
        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"

        try:
            response = requests.get(url) 
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200: 
                self.display_weather(data)
        
        except requests.exceptions.HTTPError:
            match response.status_code:
                case 400:
                    self.display_error("Bad request\nPlease check your input")
                case 401:
                    self.display_error("Unauthorized\nInvalid API Key")
                case 403:
                    self.display_error("Forbidden\nAccess is denied")    
                case 404:
                    self.display_error("Not found\nCity not found")
                case 500:
                    self.display_error("Internal Server Error\nPlease try again later")
                case 502:
                    self.display_error("Bad Gateway\nInvalid response from the server")
                case 503:
                    self.display_error("Service Unavailable\nServer is down")
                case 504:
                    self.display_error("Gateway Timeout\nNo response from the server")
                case _:
                    self.display_error("HTTP error occured\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error\nCheck your internet connection")

        except requests.exceptions.Timeout:
            self.display_error("Timeout Error:\nThe request timed out")

        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects\nNo response from the server")

        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:\n{req_error}")


    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size:30px;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size:75px;")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        
        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)
        self.emoji_label.setText(self.get_weather_emoji(data["weather"][0]["icon"]))


    @staticmethod
    def get_weather_emoji(weather_code):
    # Map common weather conditions to emojis
        emoji_map = {
            '01d': '☀️',   # Clear sky (day)
            '01n': '🌙',   # Clear sky (night)
            '02d': '⛅',   # Few clouds (day)
            '02n': '🌙☁️',  # Few clouds (night)
            '03d': '☁️',   # Scattered clouds
            '03n': '☁️',
            '04d': '☁️☁️',  # Broken clouds
            '04n': '☁️☁️',
            '09d': '🌧️',   # Shower rain
            '09n': '🌧️',
            '10d': '🌦️',   # Rain (day)
            '10n': '🌧️',   # Rain (night)
            '11d': '⛈️',   # Thunderstorm
            '11n': '⛈️',
            '13d': '❄️',   # Snow
            '13n': '❄️',
            '50d': '🌫️',   # Mist
            '50n': '🌫️',
    }
        return emoji_map.get(weather_code, '')



if __name__ =="__main__":       
    app= QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())