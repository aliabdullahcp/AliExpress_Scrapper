# AliExpress_Scrapper

## How To Run.
1. Install Docker Desktop and Run It
2. Run the Commands Below to get Splash Up and Running
```sh
	docker pull scrapinghub/splash
	docker run -it -p 8050:8050 scrapinghub/splash --disable-private-mode
```
3. Open terminal and navigate to your project root directory.
4. Create a new Virtual Environement and activate it
```sh
	py -m venv venv
	venv/Scripts/Activate
```
5. Install the requirements file
```sh
	pip install -r requirements.txt
```
6. Run the Scrapping spider
```sh
	scrapy crawl products
```
### Other Commands For Scrapy Shell
```sh
scrapy shell
fetch('http://localhost:8050/render.html?url=https://www.aliexpress.com/category/200003482/dresses.html')
```