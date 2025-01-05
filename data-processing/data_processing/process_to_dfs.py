import pandas as pd
import requests
from dotenv import dotenv_values
import json
from pathlib import Path
from bs4 import BeautifulSoup
import re

def place_into_dataframe(df, idValue, field, valueParentDict, dictKey):
	if dictKey in valueParentDict:
		value = valueParentDict[dictKey]
		if value is None or value == "":
			return
		else:
			df.loc[df['id'] == idValue, field] = value
	# else:
		# print(f"Key {dictKey} not found in {valueParentDict}")

def venues_processor(checkinsDataFrame):
	# Create a DataFrame from the list of dictionaries
	venuesDf = pd.DataFrame(columns=[
		'id', # venue id
		'name', # venue name
		'url', # venue url
		'latitude',
		'longitude',
		'tipString', # tip text
		'tipCreatedAt',
		'tipId',
		'tipUrl', # tip canonicalUrl
		'tipViews', # tip viewCount
		'tipAgreeCount', # tip agreeCount
		'tipDisagreeCount', # tip disagreeCount
		'rating', # from ratings file, can be like, dislike, okay
		'imageSuffix', # from photos file, is the `suffix` field
		'imageWidth', # from photos file, is the `width` field
		'imageHeight', # from photos file, is the `height` field
		'imageId', # from photos file, is the `id` field
		'imageCreatedAt', # from photos file, is the `createdAt` field
		'checkIns', # array of string checkin IDs.
		'address',
		'locality',
		'country',
		'postal_code',
		'region',
		'formatted_address'
	])
	for index, row in checkinsDataFrame.iterrows():
		venueRow = venuesDf.loc[venuesDf['id']==row['venueId']]
		if venueRow.empty:
			# print(f"Venue not found for {row['venueId']}")
			# continue
			venuesDf.loc[-1] = [
		row['venueId'],
		row['venueName'],
		row["venueURL"],
		"", # latitude
		"", # longitude
		"", # tipString
		"", # tipCreatedAt
		"", # tipId
		"", # tipUrl
		"", # tipViews
		"", # tipAgreeCount
		"", # tipDisagreeCount
		"", # rating
		"", # imageSuffix
		"", # imageWidth
		"", # imageHeight
		"", # imageId
		"", # imageCreatedAt
		[row['id']], # checkIns,
		"", # address
		"", # locality
		"", # country
		"", # postalCode
		"", # region
		"" # formattedAddress
		]  # adding a row
			venuesDf.index = venuesDf.index + 1  # shifting index
			venuesDf = venuesDf.sort_index()  # sorting by index
		else:
			if row["id"] == "61180ce26f18ec40cccfcf73":
				print('venueRow needs to be appended')
				print(venueRow)
			# add a new checkin to the series of checkins for this venue
			venuesDf.loc[venuesDf['id'] == row['venueId'], 'checkIns'] = venuesDf.loc[venuesDf['id'] == row['venueId'], 'checkIns'].apply(lambda x: x + [row['id']])


	print('Venues Dataframe shape')
	print(venuesDf.shape)
	return venuesDf

def add_venues_ratings(ratingSet, ratingType, venueDFSet):
	for ratingItem in ratingSet:
		venueRatingId = ratingItem['url'].split('/')[-1]
		venueRow = venueDFSet.loc[venueDFSet['id']==venueRatingId]
		if venueRow.empty:
			print(f"Venue not found for {venueRatingId}")
			venueDFSet.loc[-1] = [
				ratingItem['id'],
				ratingItem['name'],
				ratingItem["url"],
				"", # latitude
				"", # longitude
				"", # tipString
				"", # tipCreatedAt
				"", # tipId
				"", # tipUrl
				"", # tipViews
				"", # tipAgreeCount
				"", # tipDisagreeCount
				"", # rating
				"", # imageSuffix
				"", # imageWidth
				"", # imageHeight
				"", # imageId
				"", # imageCreatedAt
				[], # checkIns
				"", # address
				"", # locality
				"", # country
				"", # postalCode
				"", # region
				"" # formattedAddress
			]  # adding a row
			venueDFSet.index = venueDFSet.index + 1  # shifting index
			venueDFSet = venueDFSet.sort_index()  # sorting by index
		venueDFSet.loc[venueDFSet['id'] == venueRatingId, 'rating'] = ratingType

def ratings_processor(ratingsSet, venueDFSet):
	add_venues_ratings(ratingsSet["venueLikes"], "like", venueDFSet)
	add_venues_ratings(ratingsSet["venueDislikes"], "dislike", venueDFSet)
	add_venues_ratings(ratingsSet["venueOkays"], "okay", venueDFSet)

def tip_processor(tipsSetObject, venueDFSet):
	for tip in tipsSetObject:
		tipVenueId = tip["venue"]["id"]
		venueRow = venueDFSet.loc[venueDFSet['id']==tipVenueId]
		if venueRow.empty:
			print(f"Venue not found for {tip['id']}")
			venueDFSet.loc[-1] = [
				tip["venue"]["id"],
				tip["venue"]["name"],
				tip["venue"]["url"],
				"", # latitude
				"", # longitude
				"", # tipString
				"", # tipCreatedAt
				"", # tipId
				"", # tipUrl
				"", # tipViews
				"", # tipAgreeCount
				"", # tipDisagreeCount
				"", # rating
				"", # imageSuffix
				"", # imageWidth
				"", # imageHeight
				"", # imageId
				"", # imageCreatedAt
				[], # checkIns
				"", # address
				"", # locality
				"", # country
				"", # postalCode
				"", # region
				"" # formattedAddress
			]  # adding a row
			venueDFSet.index = venueDFSet.index + 1  # shifting index
			venueDFSet = venueDFSet.sort_index()  # sorting by index
		# print(f"Venue found for {tipVenueId}")
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipString'] = tip["text"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipCreatedAt'] = tip["createdAt"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipId'] = tip["id"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipViews'] = tip["viewCount"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipAgreeCount'] = tip["agreeCount"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipDisagreeCount'] = tip["disagreeCount"]
		venueDFSet.loc[venueDFSet['id'] == tipVenueId, 'tipUrl'] = tip["canonicalUrl"]

def checkin_processing(checkinList, df):
	visCount = 0;
	for item in checkinList:
		if 'venue' not in item:
			continue

		if 'visibility' not in item:
			# print(f"Visibility not found for {item['id']} name {item['venue']['name']}")
			visCount += 1
			item['visibility'] = "private"

		if 'shout' not in item:
			# print(f"Visibility not found for {item['id']} name {item['venue']['name']}")
			item['shout'] = ""

		df = pd.concat([pd.DataFrame([[
      item['id'],
      item['createdAt'],
      item['type'],
      item['visibility'],
      item['timeZoneOffset'],
      item['venue']['id'],
      item['venue']['name'],
      item['venue']['url'],
      item['comments']['count'],
      item['shout']
      ]], columns=df.columns), df], ignore_index=True)

	return df

def checkin_packages_processor(data):
	# Create a DataFrame from the list of dictionaries
	df = pd.DataFrame(columns=[
		'id',
		'createdAt',
		'type',
		'visibility',
		'timeZoneOffset',
		'venueId',
		'venueName',
		'venueURL',
		'commentsCount',
		'shout'
	])
	#for checkinList in data:
	df = checkin_processing(data, df)
	print('Checkins Dataframe shape')
	print(df.shape)
	# print(df.iloc[0])
	return df

def photos_processor(photosSetObject, venueDFSet, checkinDFSet):
	photosDf = pd.DataFrame(columns=[
		'id',
		'venueId',
		'createdAt',
		'suffix',
		'width',
		'height',
	])
	for photoObj in photosSetObject:
		venueId = "";
		if "swarmapp" in photoObj['relatedItemUrl']:
			checkinId = photoObj['relatedItemUrl'].split('/')[-1]
			# print(f"checkinId is {checkinId}")
			checkinRow = checkinDFSet.loc[checkinDFSet['id'] == checkinId]
			if checkinRow.empty:
				print(f"Checkin not found for {checkinId}")
				continue
			venueId = checkinRow['venueId'].values[0]
			#print(f"Checkin found at {venueId} from {checkinId} ")
			#print(checkinRow)
		else:
			venueId = photoObj['relatedItemUrl'].split('/')[-1]
		# print(f"VenueId found for {venueId}")
		photosDf.loc[-1] = [
				photoObj["id"],
				venueId,
				photoObj["createdAt"],
				photoObj["suffix"],
				photoObj["width"],
				photoObj["height"],
			]  # adding a row
		photosDf.index = photosDf.index + 1  # shifting index
		photosDf = photosDf.sort_index()  # sorting by index

		if not venueDFSet.loc[venueDFSet['id'] == venueId, 'imageSuffix'].empty:
			# print(f"Image already in place for {venueRatingId}")
			continue

		venueRow = venueDFSet.loc[venueDFSet['id']==venueId]
		if venueRow.empty:
			# A photo without a preexisting venue.
		# print(f"Venue not found for {row['venueId']}")
		# continue
			venueDFSet.loc[-1] = [
		venueId,
		"",
		"",
		"", # latitude
		"", # longitude
		"", # tipString
		"", # tipCreatedAt
		"", # tipId
		"", # tipUrl
		"", # tipViews
		"", # tipAgreeCount
		"", # tipDisagreeCount
		"", # rating
		"", # imageSuffix
		"", # imageWidth
		"", # imageHeight
		"", # imageId
		"", # imageCreatedAt
		[], # checkIns
		"", # address
		"", # locality
		"", # country
		"", # postalCode
		"", # region
		"" # formattedAddress
		]  # adding a row
			venueDFSet.index = venueDFSet.index + 1  # shifting index
			venueDFSet = venueDFSet.sort_index()  # sorting by index

		#print(f"Venue found for {venueId} from {checkinId}")
		venueDFSet.loc[venueDFSet['id'] == venueId, 'imageSuffix'] = photoObj["suffix"]
		venueDFSet.loc[venueDFSet['id'] == venueId, 'imageWidth'] = photoObj["width"]
		venueDFSet.loc[venueDFSet['id'] == venueId, 'imageHeight'] = photoObj["height"]
		venueDFSet.loc[venueDFSet['id'] == venueId, 'imageId'] = photoObj["suffix"]
		venueDFSet.loc[venueDFSet['id'] == venueId, 'imageCreatedAt'] = photoObj["createdAt"]

	print('Photos Dataframe shape')
	print(photosDf.shape)
	return photosDf

def process_to_dfs(data):
	"""Process Foursquare file data into DataFrames

	This takes a dictionary of Foursquare data as generated by
	the `pull_in_data_files` function and processes it into a set
	of DataFrames. The DataFrames are returned in a dictionary
	with keys for each type of data: 'venues', 'checkins',
	and 'photos'.
	"""

	# Process the checkins
	checkinsDataFrame = checkin_packages_processor(data['checkins'])
	# print('Checkins Dataframe check')
	# print(checkinsDataFrame.iloc[0])
	# Process the venues
	venuesDataFrame = venues_processor(checkinsDataFrame)
	# Process the ratings
	ratings_processor(data['ratings'], venuesDataFrame)
	# Process the tips
	tip_processor(data['tips'], venuesDataFrame)
	# Process the photos
	photosDataFrame = photos_processor(data['photos'], venuesDataFrame, checkinsDataFrame)
	return {
     'venues': venuesDataFrame,
     'checkins': checkinsDataFrame,
     'photos': photosDataFrame
    }

def place_html_string_into_html_results_dict(field, data, dictObj):
	if (data is not False and data is not None):
			dictObj[field] = data.string

def fallback_to_place_html_page(venueUrl, venueId):
	"""Fallback to using the Foursquare place HTML page

	This function is a fallback for when the Foursquare API
	does not return the expected data. It will crawl the
	HTML page for the venue.
	"""

	headers = {
		"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
		"cache-control": "max-age=0",
		"Dnt": "1",
		"sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
		"Cookie": "_vwo_uuid_v2=D022F50277B8F568C31F2384412C8E938|c2523875cc0db7f1faabb7bedeac9bfc; _gcl_au=1.1.1865371039.1732480250; OptanonAlertBoxClosed=2024-11-24T20:30:52.942Z; PixelDensity=2; __utmc=51454142; __utmz=51454142.1732480253.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _hjSessionUser_1179695=eyJpZCI6IjI4Mjk3MTJiLWRiZDYtNWY2OS1iYTZlLTcyZmI3OGIxYjhjOCIsImNyZWF0ZWQiOjE3MzI0ODAyNTMzMTAsImV4aXN0aW5nIjp0cnVlfQ==; bbhive=K0TR5XMU5QKZWWMKDSASRW0UCQR3U2%3A%3A1795552254; oauth_token=HT3JK0K33IBNO54FK5FWIMRYCWMHN1DNP3DOLFY52ZSGKLZH-0; _ga_H5VDLC686V=GS1.2.1733094270.1.0.1733094270.0.0.0; _mkto_trk=id:579-FAI-132&token:_mch-foursquare.com-1735151044827-21603; __stripe_mid=fdd39a37-2c08-4687-90de-eff277a55c9844c53a; ajs_user_id=15234; _hjSessionUser_3001104=eyJpZCI6ImJmMGU5ZDA5LTc5ZWMtNWIyYS1hMDc5LWVkODQ5YzRhYzg5NyIsImNyZWF0ZWQiOjE3MzU1MDc2OTI0MDcsImV4aXN0aW5nIjp0cnVlfQ==; _gid=GA1.2.1299664207.1736051893; _ga_NR4YD3CNG5=GS1.2.1736051893.4.1.1736051893.0.0.0; dpi_utmOrigVals={\"originalutmmedium\":\"none\",\"originalutmsource\":\"none\"}; hubspotutk=09a2f75afe4a2b4de1a410353bf4dc2f; __hssrc=1; _hjSessionUser_3229441=eyJpZCI6IjAyZGZmZDllLWM5YTUtNTMzZS05ZjVhLTdlMTdhYjVmOTBhYSIsImNyZWF0ZWQiOjE3MzYwNTE5MTM4OTYsImV4aXN0aW5nIjp0cnVlfQ==; _legacy_auth0.dVy71k6Exz7zcpIRpQhBhXfSN4ocgjFE.is.authenticated=true; auth0.dVy71k6Exz7zcpIRpQhBhXfSN4ocgjFE.is.authenticated=true; ajs_anonymous_id=9011fca1-a3f7-4889-bc11-ba0d9581cdc1; _rdt_uuid=1732480253088.b9dae147-c6d7-49a7-95f3-903b0fcdc6e3; __hstc=72593292.09a2f75afe4a2b4de1a410353bf4dc2f.1736051914948.1736051914948.1736054431966.2; _ga_13W256ZLLK=GS1.1.1736051913.7.1.1736054442.7.0.0; _ga_F1K4V3ER0C=GS1.1.1736051915.7.1.1736054442.7.0.0; _ga_3W40YQDD7J=GS1.1.1736097750.10.0.1736097750.60.0.0; _ga_LQHG2J83EJ=GS1.1.1736097750.5.0.1736097750.0.0.0; _ga_NRM9LCS9XM=GS1.1.1736097750.9.0.1736097750.60.0.0; lc=%7B%22lat%22%3A40.00665808881941%2C%22lng%22%3A-75.15176344614736%2C%22loc%22%3A%22Philadelphia%2C+PA%22%2C%22cc%22%3A%22US%22%2C%22longGeoId%22%3A%2272057594042488285%22%7D; AWSALBTG=7dSLFVe8ajSousUvWZHP+F0jMKqQaWm4p2zHby30jPRzDLuxUq1t6U8lcXI7ZWTCeZktnurFLBNcOF5n6HlQI+RW6VAYneYoa4EjuLsjPaAp4tv9nwMifLf4FnsEoQOr35leBsyUfTVUL3eacMx2z+I/goHeOmwCoy680sTCF3FZ; AWSALBTGCORS=7dSLFVe8ajSousUvWZHP+F0jMKqQaWm4p2zHby30jPRzDLuxUq1t6U8lcXI7ZWTCeZktnurFLBNcOF5n6HlQI+RW6VAYneYoa4EjuLsjPaAp4tv9nwMifLf4FnsEoQOr35leBsyUfTVUL3eacMx2z+I/goHeOmwCoy680sTCF3FZ; AWSALB=LV7DbtWnMzKYrnLS7U18WRD6YLuM+FhFFU5qgBmhDJJtLVu6AQrJXS7doQgZM+9V7xUiUJ9X9xMcit6IWo4LymngKiMXaPKR+KS6rtSE/aupvIMbUjvbeYYwVM+h; AWSALBCORS=LV7DbtWnMzKYrnLS7U18WRD6YLuM+FhFFU5qgBmhDJJtLVu6AQrJXS7doQgZM+9V7xUiUJ9X9xMcit6IWo4LymngKiMXaPKR+KS6rtSE/aupvIMbUjvbeYYwVM+h; XSESSIONID=120z2lmeks8ro1qtx2s7b5aq4k; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Jan+05+2025+13%3A37%3A59+GMT-0500+(Eastern+Standard+Time)&version=202304.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0004%3A1%2CC0005%3A1%2CC0003%3A1&geolocation=US%3BNY&AwaitingReconsent=false; _ga=GA1.2.1195756786.1732480253; __utma=51454142.1195756786.1732480253.1736051893.1736102279.8; __utmb=51454142.0.10.1736102279; _ga_05JP5TT14W=GS1.2.1736102279.8.0.1736102279.0.0.0; __gads=ID=d5839be2a157df17:T=1733094438:RT=1736102279:S=ALNI_Ma3SBq_ouOfWNFE8z04LclmOvVYig; __gpi=UID=00000ea4f50f9470:T=1733094438:RT=1736102279:S=ALNI_MbIjTbhLxjPh9NSMsnp1cWNX0vFfQ; __eoi=ID=fd81ffeb3e2647d9:T=1733094438:RT=1736102279:S=AA-AfjZTlR5n7sXc-CU09a0ITmhB",
		"User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
	}
	# print(f"Getting details for {venueId} with {apiKey}")
	url = venueUrl
	locationDataDict = {}
	fileName = f"../venueHTML/{venueId}.json"
	# print(jsonData)
	filepath = Path(fileName)
	soup = None
	if filepath.is_file():
		# file exists
		with open(filepath, 'r') as f:
			# print(f"Reading {file}")
			htmlContent = f.read()
			soup = BeautifulSoup(htmlContent, "html.parser")
	else:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			htmlContent = response.content
			# print(htmlContent)
			soup = BeautifulSoup(htmlContent, "html.parser")
			with open(f"../venueHTML/{venueId}.html", 'w') as f:
				f.write(str(soup.prettify()))
		else:
			print(f'The url {url} returned a status of {response.status_code}')
			with open(f"../failedVenueHTML/{venueId}.html", 'w') as f:
				f.write(f"status_code:{response.status_code},venue:{venueId},url:{url}");

	if soup is None:
		print(f'The url {url} could not be turned into soup')
		return False
	else:
		locationDataDict = {}

		htmlLatitude = soup.find("meta", property="playfoursquare:location:latitude")
		#print(htmlLatitude)
		#print(f"Latitude is {htmlLatitude['content']}")
		locationDataDict["latitude"] = htmlLatitude['content'];

		htmlLongitude = soup.find("meta", property="playfoursquare:location:longitude")
		#print(htmlLongitude)
		#print(f"Latitude is {htmlLongitude['content']}")
		locationDataDict["longitude"] = htmlLongitude['content'];

		# Country pull
		pattern = r'","country":"([^"]+)","'
		match = re.search(pattern, str(htmlContent))
		#print("country match")
		#print(match.groups()[0])
		locationDataDict["country"] = match.groups()[0];

		htmlAddressBlock = soup.find("div", itemprop="address")
		if htmlAddressBlock is None:
			#print("No address block found")
			locationDataDict["address"] = False;
		else:
			htmlStreetAddress = soup.find("span", itemprop="streetAddress")
			# print(htmlStreetAddress)
			# print(f"address is {htmlStreetAddress.string}")
			place_html_string_into_html_results_dict("address", htmlStreetAddress, locationDataDict)

			# locationDataDict["address"] = htmlStreetAddress.string;

			htmlAddressLocality = soup.find("span", itemprop="addressLocality")
			# print(htmlAddressLocality)
			# print(f"address is {htmlAddressLocality.string}")
			# locationDataDict["locality"] = htmlAddressLocality.string;
			place_html_string_into_html_results_dict("locality", htmlAddressLocality, locationDataDict)

			htmlAddressRegion = soup.find("span", itemprop="addressRegion")
			# print(htmlAddressRegion)
			# print(f"address is {htmlAddressRegion.string}")
			# locationDataDict["region"] = htmlAddressRegion.string;
			place_html_string_into_html_results_dict("region", htmlAddressRegion, locationDataDict)

			htmlPostalCode = soup.find("span", itemprop="postalCode")
			# print(htmlPostalCode)
			# print(f"address is {htmlPostalCode.string}")
			# locationDataDict["postal_code"] = htmlPostalCode.string;
			place_html_string_into_html_results_dict("postal_code", htmlPostalCode, locationDataDict)

		return locationDataDict


def get_place_details(venueId, apiKey):
	apiBase = "https://api.foursquare.com/v3/places/" # add venueID
	jsonData = False
	headers = {
		"accept": "application/json",
		"Authorization": apiKey
	}
	fileName = f"../venueData/{venueId}.json"
	# print(jsonData)
	filepath = Path(fileName)
	if filepath.is_file():
		# file exists
		# print(f"File exists for {venueId}")
		with open(filepath, 'r') as f:
			# print(f"Reading {file}")
			jsonData = json.load(f)
	else:
		# print(f"Getting details for {venueId} with {apiKey}")
		response = requests.get(apiBase+venueId, headers=headers)
		print(response.status_code)
		if response.status_code == 200:
			jsonData = response.json()
			with open(fileName, 'w') as f:
				json.dump(jsonData, f)
		else:
			print(f"Foursquare API request failed for ID {venueId}")
			print(response.status_code)
			failFileName = f"../failedVenueData/{venueId}.txt"
			with open(failFileName, 'w') as f:
				f.write(f"status_code:{response.status_code},venue:{venueId},url:{apiBase+venueId}");
	return jsonData


def process_foursquare_data_into_venues(venuesDataFrame, envLocation):
	config = dotenv_values(envLocation)
	apiKey = config['FSQ_API_KEY']
	print(f"Foursquare API Key is {apiKey}")
	for index, row in venuesDataFrame.iterrows():
		venueDictionary = get_place_details(row['id'], apiKey)
		if (False == venueDictionary):
			print(f"Failed to get details for {row['id']}")

			htmlPageData = fallback_to_place_html_page(row['url'], row['id'])
			place_into_dataframe(venuesDataFrame, row['id'], 'latitude', htmlPageData,'latitude')
			place_into_dataframe(venuesDataFrame, row['id'], 'longitude', htmlPageData,'longitude')
			if 'address' in htmlPageData and htmlPageData['address'] is not False:
				place_into_dataframe(venuesDataFrame, row['id'], 'address', htmlPageData,'address')
				place_into_dataframe(venuesDataFrame, row['id'], 'locality', htmlPageData,'locality')
				place_into_dataframe(venuesDataFrame, row['id'], 'country', htmlPageData, 'country')
				place_into_dataframe(venuesDataFrame, row['id'], 'postal_code', htmlPageData, 'postal_code')
				place_into_dataframe(venuesDataFrame, row['id'], 'region', htmlPageData, 'region')
			continue

		# venuesDataFrame.loc[venuesDataFrame['id'] == row['id'], 'latitude'] = venueDictionary['geocodes']['main']['latitude']
		if 'main' in venueDictionary['geocodes']:
			place_into_dataframe(venuesDataFrame, row['id'], 'latitude', venueDictionary['geocodes']['main'],'latitude')
			place_into_dataframe(venuesDataFrame, row['id'], 'longitude', venueDictionary['geocodes']['main'],'longitude')
		if 'location' in venueDictionary:
			place_into_dataframe(venuesDataFrame, row['id'], 'address', venueDictionary['location'],'address')
			place_into_dataframe(venuesDataFrame, row['id'], 'locality', venueDictionary['location'],'locality')
			place_into_dataframe(venuesDataFrame, row['id'], 'country', venueDictionary['location'], 'country')
			place_into_dataframe(venuesDataFrame, row['id'], 'postal_code', venueDictionary['location'], 'postcode')
			place_into_dataframe(venuesDataFrame, row['id'], 'region', venueDictionary['location'], 'region')
			place_into_dataframe(venuesDataFrame, row['id'], 'formatted_address', venueDictionary['location'],'formatted_address')
		# row['latitude'] = venueDictionary['geocodes']['main']['latitude']
		# row['longitude'] = venueDictionary['geocodes']['main']['longitude']

	# print(response.text)
	# 	venuesDf.loc[venuesDf['id'] == venueId, 'imageId'] = photoObj["suffix"]
