#! python3
# xkcd-multitreaded.py - A multi threaded web scrapper that locally stores all of the xkcd comics

import requests
import bs4
import os
import threading


def site_scrap(page, index):
    # Establishes connections to 100 pages given an index
    # Some pages contain 404 statuses -> xkcd.com/404 as a joke
    # If such a page is reached, just continue going
    i = index * 100
    end = i + 100
    while i < end:
        try:
            i += 1
            contents = page_connect(page + r"/" + str(i))
            print("Downloading >> " + page + r"/" + str(i))
            save_comic(get_comic(contents), i)
        except requests.exceptions.HTTPError:
            pass
        except Exception:
            pass


def page_connect(page):
    # Attempts to connect to a page and returns a bs4 object
    resource = requests.get(page)
    resource.raise_for_status()
    soup = bs4.BeautifulSoup(resource.text, "html.parser")
    return soup


def get_comic(soup):
    # Given a bs4 object, locates the comic and returns that content
    comicElement = soup.select("#comic img")
    if comicElement == []:
        raise Exception("Could not find comic image.")
    else:
        comicUrl = "http:" + comicElement[0].get('src')
        resource = requests.get(comicUrl)
        resource.raise_for_status()
        return resource


def save_comic(resource, counter):
    # Saves the comic as an image, chunk by chunk into a file
    imageFile = open(os.path.join('xkcd-multithreaded', 'xkcd-comic[' + str(counter) + '].png'), 'wb')
    for chunk in resource.iter_content(100000):
        imageFile.write(chunk)
    imageFile.close()


def get_counter():
    # Returns how many hundred comics there are
    # Starts from xkcd comic 1900 and goes up from there
    # When it reaches a 404 page, returns
    max_counter = 19
    while True:
        try:
            c = requests.get(url + r"/" + str(max_counter * 100))
            if c.status_code == 404:
                return max_counter
            max_counter += 1
        except requests.exceptions.HTTPError:
            break
        except Exception:
            break


if __name__ == "__main__":
    # Makes the directory to download into and determines the number of threads needing to be created
    url = "http://xkcd.com"
    os.makedirs('xkcd-multithreaded', exist_ok=True)
    max_counter = get_counter()

    downloadThreads = []
    for index in range(0, max_counter):
        downloadThread = threading.Thread(target=site_scrap, args=(url, index))
        downloadThreads.append(downloadThread)

    for downloadThread in downloadThreads:
        downloadThread.start()

    for downloadThread in downloadThreads:
        downloadThread.join()
    print("Finished.")