import pandas as pd

def checkin_processing(checkinList, df):
	visCount = 0;
	for item in checkinList["items"]:
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

def checkin_packages_processing(data):
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
