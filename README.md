<div id="top"></div>

<!-- PROJECT LOGO -->
# MQTT client for Raspbery Pi HUB


<!-- ABOUT THE PROJECT -->
## About The Project
This project was developed to provide remote access and control along with periodic reporting for Smart meters working on the `DL/T645-2007` instruction set

<!-- GETTING STARTED -->
## Getting Started
* if there are multiple lines of instruction please copy them line by line

### Prerequisites

   `Burn .img file into a empty SD card using Pi imager (https://www.Raspberrypi.com/software/)`

### Installation

1. git clone

   ```sh
   mkdir server
   cd server/
   git clone https://github.com/Wishmaker97/piHubFirmware.git
   ```

2. go to /server/piHubFirmware/ directory

   ```sh
   cd /piHubFirmware/
   ```
3. update .env file to add the device_id

   ```sh
   sudo nano .env
   ```
   copy and paste the text from https://jstrieb.github.io/link-lock/#eyJ2IjoiMC4wLjEiLCJlIjoiSEEyRTNYblFjbjBUZm1iTmtzOWx3UDlKenlXeFByTUpjNHFyUGdSd0RZZEhXR0FtSmpuVEdBdkJhRlNBZXpUbVNVTkhjdnA5N084NXpiMmllMStzSUxLeVJtOE9QbWtSM2NrUjU2bW1qa009IiwiaCI6ImFzayBzdW5ueSIsInMiOiIwdnRUWDAxZlVKMzZMc3lvRXlRYnpRPT0iLCJpIjoiZzBqTjdHU2k1NkZzbDBETyJ9 Remember to update the data for the device_id

4. make venv

   ```sh
   python -m venv venv
   ```

5. activate venv

   ```sh
   source /venv/bin/activate
   ```
6. activate venv

   ```sh
   python pip install -r requirements.txt
   ```

7. create Shell script

   ```sh
   touch /usr/local/sbin/service_worker.sh
   ```

8. add data to shell script (type ```sudo nano /usr/local/sbin/service_worker.sh``` first)

   ```sh
      #!/bin/bash
      source "/home/pihub/server/piHubFirmware/venv/bin/activate"
      cd /home/pihub/server/piHubFirmware/
      python service_worker.py
   ```

9. create service script

   ```sh
   touch /etc/systemd/system/service_worker.service
   ```

10. add data to service script (type ```sudo nano /etc/systemd/system/service_worker.service``` first)

   ```sh
      [Unit]
      Description=MQTT service worker
      [Service]
      Restart=always
      ExecStartPre=/bin/sleep 10
      ExecStart=/usr/local/sbin/service_worker.sh
      PIDFile=/var/run/service_worker.pid
      [Install]
      WantedBy=multi-user.target
   ```

11. create service script

   ```sh
   chmod u+x /usr/local/sbin/service_worker.sh
   ```

12. create service script

   ```sh
   chmod u+x service_worker.py
   ```

13. create service script

   ```sh
   sudo systemctl start service_worker.service
   ```

14. create service script

   ```sh
   sudo systemctl enable service_worker.service
   ```



<!-- CONTACT -->
## Contact

[![LinkedIn][linkedin-shield]][linkedin-url]  ![Twitter URL](https://img.shields.io/twitter/url?label=VishmikaFernan1&logo=twitter&style=for-the-badge&url=https%3A%2F%2Ftwitter.com%2FVishmikaFernan1) ![GitHub followers](https://img.shields.io/github/followers/Wishmaker97?logo=github&style=for-the-badge)



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/vishmika-fernando-435923116/

