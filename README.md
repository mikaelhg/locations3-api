Locations API v3, using the MaxMind free City DB + automatic database upgrades.

Open the project with IntelliJ IDEA 14 with the Python plugin installed.

Build:

    sudo docker build --rm -t mikaelhg/locations3-api .

Test:

    curl http://localhost:5000/address/8.8.8.8
    curl -H "X-Forwarded-For: 8.8.8.8" http://localhost:5000/address/current

Run:
     
    sudo docker run -it --rm -p 5000:5000 mikaelhg/locations3-api 

Run with DB update interval of 6 hours:
     
    sudo docker run -it --rm -p 5000:5000 -e UPDATE_HOURS=6 mikaelhg/locations3-api 

When developing locally, just create a python virtualenv, run `pip install -r requirements.txt`,
and execute `locations3.py` for the application, or `rest_tests.py` for the functional tests.

You can also run the unit tests in the Docker container:

    sudo docker run -it --rm mikaelhg/locations3-api python rest_tests.py

This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>.
