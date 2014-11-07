##Are Police Stations optimially located and staffed in SF?
>Using clustering to determine optimal locations according to where crime occurs and estimate the minimum number of cops needed at any given time

####Presentation:  
>Show a timelapse heatmap of crime in SF as it relates to size and location/staff/budget of current PD compared to optimal.

####Steps:
######Data Collection
> Ideally, Obtain officer count by district, response times by district, and crime by location

######Currently found/available:  
>Salary by employee without location  
>Crime by location, type and severity  
>Staffing in aggregate by county
>Outdated aggregated response times for 2001-2003

######Still need:
>Staffing by police district
>Recent response times

#####Analysis  
1. Use clustering to group crime data by geolocation, type/severity, and various time metrics, and identify cluster centers as hypothetical police stations
2. Look at the relationship between staffing counts by PD vs the number of incidents each PD responds to
3. Identify relationship between response time vs traffic data, distance from incident, and available police staff
 1. If 2 & 3 are available, look at the relationship between response times and staffing.
 2. If 2 & 3 are not available, estimate a minimum staff per district by the incidents that were covered, and look at the relationship between the number of handled incidents vs distance from police station.
4. Predict response time/coverage with hypothetical optimal locations
5. [Extra] Predict probability of a crime incident by crime cluster/type looking at historic data.

#####Data Product:  
1. Create visual circuitry of police stations to crime incidents.
2. Color edges by estimated response time
3. Add time progression
4. Do the same with predicted optimal locations
5. Show optimal locations if PD can be dynamically located. In this case, PD is conceptually where the majority of the patrols should be occuring.

####Datasources:
* [2013-2014 Staffing Counts by County and District](http://post.ca.gov/Data/Sites/1/post_docs/hiring/le-employment-stats.pdf)
* [2013-2014 Salary by Department and Title](https://data.sfgov.org/City-Management-and-Ethics/Employee-Compensation/88g8-5mnd)
* [SF Police Stations](https://data.sfgov.org/Public-Safety/San-Francisco-Police-Stations/8xyy-6zfh)
* [2003-Present Reported Incidents](https://data.sfgov.org/Public-Safety/SFPD-Reported-Incidents-2003-to-Present/dyj4-n68b)
* [2001-2003 Police Response Times](http://sfcontroller.org/Modules/ShowDocument.aspx?documentid=1063)

####References:
* [Model crime with Levy flights](https://dl.dropboxusercontent.com/u/67300625/tum_summer_2012_levicrime.pdf)
* [A very similar study](http://ced.berkeley.edu/faculty/ratt/classes/c188/2009Posters/Visconti%20Zhang%20Poster.pdf)
