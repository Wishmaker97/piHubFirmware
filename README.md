<div id="top"></div>

<!-- PROJECT LOGO -->
# MQTT client for Raspbery Pi HUB


<!-- ABOUT THE PROJECT -->
## About The Project
This project was developed to provide remote access and control along with periodic reportig for Smart meters working on the `DL/T645-2007` instruction set

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

Burn .img file into a empty SD card using Pi imager (https://www.raspberrypi.com/software/)

### Installation

1. go to /server/piHubFirmware directory

   ```sh
   cd /server/piHubFirmware
   ```
2. update .env file

   ```sh
   sudo nano .env
   ```

<!-- ROADMAP -->
## Roadmap

- [x] periodic reporting based on Cronjob syntax from API configuration
- [x] on demand reporting 
- [x] remotely configurable 
- [x] automatic github firmware update based on `commit ID` provided via API
- [X] automatic NTP server update based on `ntp_server` provided via API


### Built With

* [flask (for testing ONLY)](https://flask.palletsprojects.com/en/2.0.x/) test cosde at https://github.com/Wishmaker97/test_server
* [paho MQTT client for python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)

Special Thanks to 
* [施广源](https://zhuanlan.zhihu.com/p/378137714)


<!-- CONTACT -->
## Contact

[![LinkedIn][linkedin-shield]][linkedin-url]  ![Twitter URL](https://img.shields.io/twitter/url?label=VishmikaFernan1&logo=twitter&style=for-the-badge&url=https%3A%2F%2Ftwitter.com%2FVishmikaFernan1) ![GitHub followers](https://img.shields.io/github/followers/Wishmaker97?logo=github&style=for-the-badge)



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/vishmika-fernando-435923116/

=======
username: piHub
password: admin123

hostname: pihub
SSH: password no certificates

