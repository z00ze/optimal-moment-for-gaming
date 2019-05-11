## optimal-moment-for-gaming
Optimal moment for gaming.

# Flow diagram
When user signs first to the system, he/she is redirected to Fitbit login to give permission for our system to fetch data from Fitbit WebAPI. Every hour there is process to fetch new data for the user. Fetched data from Fitbit (and from tobii, benchmarks, etc.) is processed by additional processing unit for better Frontend usage.

Backend is Python3. Front-end is Node.js and React. Database is MySQL.
