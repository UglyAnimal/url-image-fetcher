import re
import os
import sys
import getopt
import time
import asyncio
import aiohttp

pattern = r"img .*?(?:src=|data-src=)\"(https.*?\.(?:png|apng|jpg|jpeg|jfif|pjpeg|pjp|svg|webp|avif|gif|bmp|ico|cur|tif|tiff))\""
folder = "images"


def arguments(argv):
    help_msg = "{0} [-w <website url>], e.g. {0} -w https://varjo.com or {0} --web-site=https://varjo.com".format(argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hw:", ["help", "web-site="])
    except:
        print(help_msg)
        sys.exit(2)

    if not opts:
        print(help_msg)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_msg)
            sys.exit(2)
        elif opt in ("-w", "--web-site"):
            global url
            url = arg
            if url == "":
                print(help_msg)
                sys.exit(2)
            if "http" not in url:
                url ="https://" + url

async def get_files_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            img_urls_list = re.findall(pattern, await response.text())
    img_urls_list = list(set(img_urls_list))
    return img_urls_list

async def download_file(url, filepath):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            with open(filepath, "wb") as file:
                while True:
                    body = await response.content.read()
                    if not body:
                        break
                    file.write(body)

async def download_files_concurrently(img_urls_list, folder):
    tasks = []
    for url in img_urls_list:
        filename = os.path.basename(url)
        filepath = os.path.join(folder, filename)
        task = asyncio.create_task(download_file(url, filepath))
        tasks.append(task)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    arguments(sys.argv)
    if not os.path.exists(folder):
        os.makedirs(folder)
    img_urls_list = asyncio.run(get_files_list())
    start_time = time.time()
    asyncio.run(download_files_concurrently(img_urls_list, folder))
    end_time = time.time()
    print(f"Downloaded {len(img_urls_list)} urls in {end_time - start_time} seconds")
