<div id="top"></div>

<!-- PROJECT LOGO -->
# MQTT client for Raspbery Pi HUB


<!-- ABOUT THE PROJECT -->
## About The Project
This project was developed to provide remote access and control along with periodic reportig for Smart meters working on the `DL/T645-2007` instruction set

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* create .env file in base directory with the following variables
  ```
  CONFIG_URL_ENDPOINT = "<enter url here>"
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Wishmaker97/pi-hub.git
   ```
2. cd to Enter to project directory
   ```sh
   cd pi-hub
   pip3 install virtualenv
   ```

3. create virtual environment 
   ```sh
   python3 -m venv venv
   ```
4. activate virtual environment
   ```sh
   source ./venv/bin/activate
   ```
5. install all neccessary packages 
   ```sh
   pip3 install -r ./requirements.txt
   ```
6. run script
   ```sh
   python3 incomming_traffic.py
   python3 outging_traffic.py
   ```

<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme

### Built With

* [flask (for testing ONLY)](https://flask.palletsprojects.com/en/2.0.x/)
* [paho MQTT client for python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)



<!-- CONTACT -->
## Contact

[![LinkedIn][linkedin-shield]][linkedin-url]  ![Twitter URL](https://img.shields.io/twitter/url?label=VishmikaFernan1&logo=twitter&style=for-the-badge&url=https%3A%2F%2Ftwitter.com%2FVishmikaFernan1) ![GitHub followers](https://img.shields.io/github/followers/Wishmaker97?logo=github&style=for-the-badge)



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/vishmika-fernando-435923116/

