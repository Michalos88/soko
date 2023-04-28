# Soko 

```
Soko (其処) - That place, area, or part near you
```

When searching for my first home, I noticed a lack of free tools for analyzing single-family properties in the US. 
While Zillow, Trulia, and Realtor offer some information, I found their analysis to be quite shallow and data dispersed across properties. 
To address this issue, I developed a simple, hacky process for collecting and parsing the data from sources like Zillow.com, Niche.com, and Google Maps.
Then aggregating the data into a master table, that can be then analyzed more in depth.
This allowed me to gain a more thorough understanding of each property and make a more informed decision on which house to purchase.

# Setup

```
git clone https://michalos88/soko.git
cd soko
virtualenv venv
echo source ./venv/bin/activate > .env
source .env
pip install -r requirements.txt
````

## Google Maps API
If you want to also analyze your commute time, make sure to add your google api key to the `.env` file. 
```
echo export google_api_key=YOUR_API_KEY >> .env
source .env
```

# The Process
 
## 1. Collecting Zillow data

I didn't want to waste time building a robust scraper for zillow, and also it would be an overkill, as we don't actaully want to pull all the properties, rather than the selected ones we like.
Whenever you find a property you like, just save the page to html in directory `soko/data/raw/zillow`

## 2. Collecting Niche data

Similarly, for each town/city that your property is in, make sure to go to niche.com, then go to places to live, find the town, and save the webpage to `soko/data/raw/niche/`

## 3. Run Zillow Notebook

The notebook will parse the data and save it into a csv file.

## 4. Run Niche Notebook

The notebook will parse the data and save it into a csv file.

## 5. Run Master notebook

The notebook will join niche, zillow and Google Maps data, and put it into a master table

## 6. Analysis

Now you can analyze the property and location data using your favourite tool. Hope that helps. ;)
