import glob
import json

def turn_list_of_files_into_objects(json_files):
	# Load each JSON file into a list of dictionaries
	data = []
	for file in json_files:
		with open(file, 'r') as f:
			print(f"Reading {file}")
			data.append(json.load(f))
	return data

def get_files_from_archive(base_path, archiveType):
    json_files = glob.glob(f"{base_path}/{archiveType}*.json")
    return json_files

def pull_in_data_files(base_path):
    ## @TODO: Process the set of files here just like the checkin version.
    # Get list of all JSON files in the current directory
	json_files = get_files_from_archive(base_path, 'checkin')
	checkins = turn_list_of_files_into_objects(json_files)
    # Get tips file
	tipsFile = get_files_from_archive(base_path, 'tip')
	print(f"Reading tips file")
	tipsObject = json.load(tipsFile)
	tipsSetObject = tipsObject['items']

	# get Venue Ratings
	ratingsFile = get_files_from_archive(base_path, 'venueRating')
	print(f"Reading ratings file")
	ratingsObject = json.load(ratingsFile)

	venueLikes = ratingsObject['venueLikes']
	venueDislikes = ratingsObject['venueDislikes']
	venueOkays = ratingsObject['venueOkays']

	photosFile = get_files_from_archive(base_path, 'photo')
	print(f"Reading photos file")
	photosObject = json.load(photosFile)
	photosSetObject = photosObject['items']
