import pandas as pd
import requests
from dotenv import dotenv_values
import json

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
		'checkIns' # array of string checkin IDs.
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
		[row['id']] # checkIns
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
				[] # checkIns
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
				[] # checkIns
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
	for checkinList in data:
		checkin_processing(checkinList, df)

	print(f"Total checkins without visibility: {visCount}")
	print(df.shape)
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
			checkinRow = checkinDFSet.loc[df['id'] == checkinId]
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
		[] # checkIns
		]  # adding a row
			venuesDf.index = venuesDf.index + 1  # shifting index
			venuesDf = venuesDf.sort_index()  # sorting by index

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

def get_place_details(venueId, apiKey):
	apiBase = "https://api.foursquare.com/v3/places/" # add venueID

	headers = {
		"accept": "application/json",
		"Authorization": apiKey
	}
	# print(f"Getting details for {venueId} with {apiKey}")
	response = requests.get(apiBase+venueId, headers=headers)
	print(response.status_code)
	if response.status_code == 200:
		print(response.json())
	else:
		print(f"Foursquare API request failed for ID {venueId}")
		print(response.status_code)
	print(response)


def process_foursquare_data_into_venues(venuesDataFrame, envLocation):
	config = dotenv_values(envLocation)
	apiKey = config['FSQ_API_KEY']

	apiBase = "https://api.foursquare.com/v3/places/" # add venueID

	print(response.text)
