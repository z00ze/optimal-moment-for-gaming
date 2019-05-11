# optimal-moment-for-gaming
Optimal moment for gaming.

### Description
When user signs first time to our website, he/she is redirected to Fitbit login to give permission for our system to fetch data from Fitbit WebAPI. Every hour there is process to fetch new data for the user and to update Fitbit access tokens. Fetched data from Fitbit (and from tobii, benchmarks, etc.) is processed by additional processing unit for better Frontend usage.

Backend is Python3. Front-end is Node.js and React. Database is MySQL. Server is running on Ubuntu 18.04.2 x64 and in DigitalOcean.
