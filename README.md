# Sister Appreciation Website

## Run locally

Start the local server from the project root:

```sh
python3 dev_server.py
```

Open `http://localhost:8765` for the website or `http://localhost:8765/admin.html` to set the home-page photo. The admin photo editor writes the selected image to `assets/sister-photo.jpg` in this project.

GitHub Pages serves static files and cannot accept photo uploads. To publish a new home-page photo, commit and push `assets/sister-photo.jpg` together with the site changes.
