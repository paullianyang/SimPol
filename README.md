##Are Police Stations optimially located and staffed in SF?
>Using clustering to determine optimal locations according to where crime occurs and estimate the minimum number of cops needed at any given time

####Presentation:  
>Show a timelapse heatmap of crime in SF as it relates to size and location/staff/budget of current PD compared to optimal.

####Steps:
#####Data Collection
> Ideally, Obtain officer count by district, response times by district, and crime by location

####Currently found/available:
  >Salary by employee without location
  >Crime by location, type and severity
  >Staffing in aggregate by police district
  >Outdated aggregated response times for 2001-2003

#####Analysis  
1. Use clustering to group crime data by geolocation and various time metrics
2. Identify cluster centers and intersections as an initial hypothesis for optimal locations.
3. Measure response time distribution per destination for each police station  
4. Identify relationship between response time vs traffic data, distance from incident, and available police staff
  >If 3 & 4 are available, see if there's a relationship between response time and total salary per PD
  >If 3 & 4 are not available, assume response time is solely dependent on distance between PD and crime, and the ratio between staff and crime occurences.
  >Predict when and where crime may occur possibly using time series or markov chains.
5. Predict response time with hypothetical optimal locations

#####Data Product:  
1. Create visual circuitry of police stations to crime incidents.
2. Color edges by response time
3. Add time progression
4. Do the same with predicted optimal locations
5. Show optimal locations if PD can be dynamically located. In this case, PD is conceptually where the majority of the patrols should be occuring.

####Datasources:
* 2013-2014 Staffing Counts by County and District  
  >http://post.ca.gov/Data/Sites/1/post_docs/hiring/le-employment-stats.pdf
* 2013-2014 Salary by Department and Title  
  >https://data.sfgov.org/City-Management-and-Ethics/Employee-Compensation/88g8-5mnd
* SF Police Stations  
  >https://data.sfgov.org/Public-Safety/San-Francisco-Police-Stations/8xyy-6zfh
* 2003-Present Reported Incidents  
  >https://data.sfgov.org/Public-Safety/SFPD-Reported-Incidents-2003-to-Present/dyj4-n68b  
* 2001-2003 Police Response Times
  >http://sfcontroller.org/Modules/ShowDocument.aspx?documentid=1063
