import glob
import json

def turn_list_of_item_files_into_objects(json_files):
	# Load each JSON file into a list of dictionaries
	data = []
	for file in json_files:
		with open(file, 'r') as f:
			print(f"Reading {file}")
			jsonLoaded = json.load(f);
			data = data+jsonLoaded['items']
	return data


def turn_list_of_ratings_files_into_objects(json_files):
	# Load each JSON file into a list of dictionaries
	data = {
		'venueLikes': [],
		'venueDislikes': [],
		'venueOkays': []
	}
	for file in json_files:
		with open(file, 'r') as f:
			print(f"Reading {file}")
			ratingsByType = json.load(f)
			data['venueLikes'] = data['venueLikes'] + ratingsByType['venueLikes']
			data['venueDislikes'] = data['venueDislikes'] + ratingsByType['venueDislikes']
			data['venueOkays'] = data['venueOkays'] + ratingsByType['venueOkays']
			#data.append(json.load(f))
	return data

def get_files_from_archive(base_path, archiveType):
    json_files = glob.glob(f"{base_path}/{archiveType}*.json")
    return json_files

def pull_in_data_files(base_path):
    ## @TODO: Process the set of files here just like the checkin version.
    # Get list of all JSON files in the current directory
	json_files = get_files_from_archive(base_path, 'checkin')
	# Load each JSON file into a list of objects
	checkins = turn_list_of_item_files_into_objects(json_files)
    # Get tips file
	tipsFile = get_files_from_archive(base_path, 'tip')
	print(f"Reading tips file")
	tipsSets = turn_list_of_item_files_into_objects(tipsFile)
	# tipsObject = json.load(tipsFile)
	# tipsSetObject = tipsObject['items']

	# get Venue Ratings
	ratingsFile = get_files_from_archive(base_path, 'venueRating')
	print(f"Reading ratings file")
	# ratingsObject = json.load(ratingsFile)
	ratingsSets = turn_list_of_ratings_files_into_objects(ratingsFile)

	photosFile = get_files_from_archive(base_path, 'photo')
	print(f"Reading photos file")
	photosSetObject = turn_list_of_item_files_into_objects(photosFile)
	#photosObject = json.load(photosFile)
	#photosSetObject = photosObject['items']
	return {
		'checkins': checkins,
		'tips': tipsSets,
		'ratings': ratingsSets,
		'photos': photosSetObject
	}
