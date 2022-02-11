import logging, sys, requests, json
import time
from winsound import SND_FILENAME, PlaySound
from playsound import playsound

# define urls
atisUrl = 'https://api.ivao.aero/v2/tracker/whazzup/atis'


def fetch_content(url):
    logging.info("Requesting Whazzup ATIS data")
    response = requests.get(url)
    if response.status_code == 200:
        logging.debug("Received data")
        return response.content
    else:
        logging.error(f"Status code received was {response.status_code}")


def fetch_whazzup():
    content = fetch_content(atisUrl)
    logging.debug("Loading data")
    content = json.loads(content)
    logging.info("Returning Whazzup ATIS data")
    return content

def check_station(data, station):
    res = ""
    for i in range(0, len(data) - 1):
        if str(data[i]['lines'][0]).find(station) != -1:
            res = "Station online"
            break
    if res == "":
        res = "Station offline"
        logging.warning(f"Station {station} offline")
        return res, -1
    if station.find("CTR") != -1:
        logging.warning(f"No METAR for station {station}")
        return "Make sure you choose a facility featuring a METAR!", -1
    logging.info(f"Station {station} online and has METAR")
    return res

def get_metar(data):
    try:
        if data[3].find(station[:4]) != -1:
            metar = data[3]
        elif data[2].find(station[:4]) != -1:
            metar = data[2]
        if metar:
            logging.info("Returned metar")
            return metar
        else:
            logging.error(f"Error while parsing, check data: {data}")
    except AttributeError:
        print("Station seems to be offline or your connection to \"https://api.ivao.aero/v2/tracker/whazzup/atis\" is unavailable! Exiting...")
        logging.critical("Station seems to be offline or your connection to \"https://api.ivao.aero/v2/tracker/whazzup/atis\" is unavailable! Exiting...")
        exit(-1)

def get_station_data(data, station):
    try:
        for i in range(0, len(data) - 1):
            if str(data[i]['lines'][0]).find(station) != -1:
                data = data[i]['lines']
                break
        return data
    except AttributeError:
        print("Station seems to be offline or your connection to \"https://api.ivao.aero/v2/tracker/whazzup/atis\" is unavailable! Exiting...")
        logging.critical("Station seems to be offline or your connection to \"https://api.ivao.aero/v2/tracker/whazzup/atis\" is unavailable! Exiting...")
        exit(-1)

if __name__ == '__main__':
    res, data, station = "", "", ""
    data = fetch_whazzup()
    while res != "Station online":
        station = input("What is your callsign? ")
        res = check_station(data, station)
        print(res)
    data = get_station_data(fetch_whazzup(), station)
    metar = get_metar(data)
    while True:
        ndata = get_station_data(fetch_whazzup(), station)
        nmetar = get_metar(ndata)
        if nmetar != metar:
            PlaySound("METAR.wav", SND_FILENAME)
            PlaySound("METAR.wav", SND_FILENAME)
        metar = nmetar
        time.sleep(15)

