##Are Police Districts optimally located?
>Using clustering to determine optimal locations according to where crime occurs

####[Web App (coming soon)](http://simpol.paullianyang.com/)

###Running Locally
####Dependencies
To effectively run the simulation, OSRM needs to be installed and running on the machine  
OSRM (Open Source Routing Machine) will be used to calculate driving distance and duration
>[Install Dependencies](https://github.com/Project-OSRM/osrm-backend/wiki/Building%20OSRM#mac-os-x-1071-1082)  
>[Fetch and compile source](https://github.com/Project-OSRM/osrm-backend/wiki/Building%20OSRM#fetch-the-source)  
>[Download OSM data for California](http://download.geofabrik.de/north-america/us/california.html)  
>[Extract the road network](https://github.com/Project-OSRM/osrm-backend/wiki/Running-OSRM#extracting-the-road-network)

The simulation also uses the [Google Distance Matrix API](https://developers.google.com/maps/documentation/distancematrix/). You will need to create a "gmaps_apikey" method in a filed called keys.py that will return the API string.

[Install Anaconda](http://continuum.io/downloads) to ensure you have the proper python packages

[Install sqlite](https://www.sqlite.org/download.html)

####Using the simulation with pretrained clusters
Run OSRM: ./osrm-routed [location of california osrm file]  
Run python simulation.py -h to see a description of the parameters to be passed
>The region passed corresponds to the regions labelled below:
![](https://raw.githubusercontent.com/paullianyang/SimPol/master/data/trained_clusters.png)



####Datasources:
* [2013-2014 Staffing Counts by County and District](http://post.ca.gov/Data/Sites/1/post_docs/hiring/le-employment-stats.pdf)
* [2013-2014 Salary by Department and Title](https://data.sfgov.org/City-Management-and-Ethics/Employee-Compensation/88g8-5mnd)
* [SF Police Stations](https://data.sfgov.org/Public-Safety/San-Francisco-Police-Stations/8xyy-6zfh)
* [2003-Present Reported Incidents](https://data.sfgov.org/Public-Safety/SFPD-Reported-Incidents-2003-to-Present/dyj4-n68b)
* [2001-2003 Police Response Times](http://sfcontroller.org/Modules/ShowDocument.aspx?documentid=1063)

####References:
* [Model crime with Levy flights](https://dl.dropboxusercontent.com/u/67300625/tum_summer_2012_levicrime.pdf)
* [A very similar study](http://ced.berkeley.edu/faculty/ratt/classes/c188/2009Posters/Visconti%20Zhang%20Poster.pdf)
