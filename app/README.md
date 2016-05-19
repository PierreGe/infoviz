# Folders

`src` : contains the javascript code

`static`: contains the static files (html, css, images, framework)


# Install

You need NodeJS to compile the frontend app, Python to use
the scrapping/data scripts and the web API endpoint (server).

## Install Python, Node and dependencies

`apt-get install python-dev python-virtualenv postgresql-server-dev-9.4 npm`

## Install Python and Node libs

```
virtualenv ve
source ve/bin/activate
pip install -r ../requirements.txt
npm install
```

## Compile static assets and launch website

`npm run build && python api.py`
