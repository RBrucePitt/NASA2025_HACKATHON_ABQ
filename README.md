# NASA2025_HACKATHON_ABQ
The ABQ505 Teams 2025 NASA SpaceAppsChallenge Site

# About the Challenge

NASA’s oldest daily Earth-viewing satellite – Terra – just turned 25 years old, and with five continuously operating instruments onboard (most taking imagery at the same time), Terra has piled up a LOT of data over the years (over 9,000 days and counting!). This data has the potential to shed light on everything from scientific processes to unique events, all while helping solve problems that affect humans. Your challenge is to use data from any or all of Terra’s five instruments to create an animated product showcasing an Earth science story and emphasizing the impacts to you, your community, and/or the environment. (Earth Science Division)

# Project Summary

We are using the Terra Satellite sensors to show an interactive website that shows fires and their smoke plumes and then the vegetation regrowth rate with the ability to enter a start date and zoom in/out to anywhere in the world. This is intended as education showing that the environment and the earth can recover from fire, but that it takes months and years.

# To Test

Copy the html file to your local machine and then run in your FireFox or other browser.

# Project Details

We developed Python programs that implemented two type of access to the FIRMS data: (1) Pulls FIRMS fire location data and then generates this information as a Blue/White dot with the location of the fire detection on a zoomable map of the world with links to the NASA World View application; The second was a canvas/flask based python server (local 127.0.0.1:5000) that would pull this information dynamically based on start times and date ranges. 

We utilized Google and the Nasa Resources pages provided to determine sensor types that we needed, how to access them, and what types of earth-science information we could gather.

While the first one worked well, we could not get the server mode one to successfully pull data from the FIRMS and then display a time lapse update of the fire and subsequent vegetation changes over the years. While this remains our goal, we abandoned this due to the time constraints of the weekend.

Most of the factors that we considered were: (a) what data could we use; (b) could we actually write the code to get this data; (c) could we display it in a useful way; (d) what NASA apps exist that we could link to save time; (e) what we could realistically produce in the short weekend time.

# Use of Artificial Intelligence (AI)

We used (AI) tools, namely Google Gemini to create a lot of the Python programs initially and then went in and modified them as we got access tokens, adding addition buttons and links. We did not use any (AI) to generate content as all of our content is from NASA sources and applications. We did not provide (AI) with any of the access information or our final programs.

# Links/Tools

FIRMS: https://firms.modaps.eosdis.nasa.gov/api/area/cs
World View: https://www.earthdata.nasa.gov/data/tools/worldview
Data Tools: https://www.earthdata.nasa.gov/data/tools
FIRMs: https://www.earthdata.nasa.gov/data/tools/firms
TERRA Instruments: https://terra.nasa.gov/about/terra-instruments
NASA APIs: https://api.nasa.gov/


