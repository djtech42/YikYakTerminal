#! /usr/bin/env python3
import API as pk
import pygeocoder
import requests

def main():
	print("\nYik Yak Command Line Edition : Created by djtech42\n\n")
	print("Note: This app is currently only for viewing and posting yaks at any location. There is no ability to vote or delete yet.\n\n")
	
	geocoder = pygeocoder.Geocoder("AIzaSyAGeW6l17ATMZiNTRExwvfa2iuPA1DvJqM")

	try:
		# If location already set in past, read file
		f = open("locationsetting", "r")
		fileinput = f.read()
		coords = fileinput.split('\n')
		currentlatitude = coords[0]
		currentlongitude = coords[1]
		print("Location is set to: ", coords[2])

		coordlocation = pk.Location(currentlatitude, currentlongitude)

		f.close()

	except:
		# If first time using app, ask for preferred location
		coordlocation = newLocation(geocoder)
		# If location retrieval fails, ask user for coordinates
		if coordlocation == 0:
			print("Please enter coordinates manually: ")
			currentlatitude = input("Latitude: ")
			currentlongitude = input("Longitude: ")
			coordlocation = pk.Location(currentlatitude, currentlongitude)

	print()

	try:
		# If user already has ID, read file
		f = open("userID", "r")
		userID = f.read()
		f.close()

		# start API with saved user ID
		remoteyakker = pk.Yakker(userID, coordlocation, False)

	except:
		# start API and create new user ID
		remoteyakker = pk.Yakker(None, coordlocation, True)

		try:
			# Create file if it does not exist and write user ID
			f = open("userID", 'w+')
			f.write(remoteyakker.id)
			f.close()

		except:
			pass

	print("User ID: ", remoteyakker.id, "\n")

	while True:
		choice = input("Read(R), Post(P), Choose New Location(L), or Quit(Q) -> ")
		# Read Yaks
		if choice == 'R' or choice == 'r':
			yaklist = remoteyakker.get_yaks()
			read(yaklist)

		# Post Yak
		elif choice == 'P' or choice == 'p':
			message = input("Enter message to yak: \n")

			handle = input("Add handle: (Blank to omit): \n")
			showlocation = input("Show location? (Y/N)")

			if showlocation == 'Y' or showlocation == 'y':
				allowlocation = True
			else:
				allowlocation = False

			if handle == '':
				posted = remoteyakker.post_yak(message, showloc=allowlocation)
			else:
				posted = remoteyakker.post_yak(message, showloc=allowlocation, handle=handle)

			if posted:
				print("\nYak successful :)\n\n")
			else:
				print("\nYak failed :(\t", end='')
				print (posted.status_code, end='')
				print (" ", end='')
				print (requests.status_codes._codes[posted.status_code][0])

		# Change Location
		elif choice == 'L' or choice == 'l':
			coordlocation = changeLocation(geocoder)
			remoteyakker.update_location(coordlocation)
			yaklist = remoteyakker.get_yaks()

		# Quit App
		elif choice == 'Q' or choice == 'q':
			break;

def newLocation(geocoder):
	# figure out location latitude and longitude based on address
	address = input("Enter college name or address: ")
	try:
		currentlocation = geocoder.geocode(address)
	except:
		print("\nGoogle Geocoding API has reached the limit of queries.\n")
		return 0

	coordlocation = 0
	try:
		coordlocation = pk.Location(currentlocation.latitude, currentlocation.longitude)

		# Create file if it does not exist and write
		f = open("locationsetting", 'w+')
		coordoutput = str(currentlocation.latitude) + '\n' + str(currentlocation.longitude)
		f.write(coordoutput)
		f.write("\n")
		f.write(address)
		f.close()
	except:
		print("Unable to get location.")

	return coordlocation

def changeLocation(geocoder):
	print()
	coordlocation = newLocation(geocoder, address)
	if coordlocation == 0:
		print("Please enter coordinates manually: ")
		currentlatitude = input("Latitude: ")
		currentlongitude = input("Longitude: ")
		coordlocation = pk.Location(currentlatitude, currentlongitude)

def read(yaklist):
	yakNum = 1
	for yak in yaklist:
		# line between yaks
		print ("_" * 93)
		print (yakNum)
		yak.print_yak()

		# comments header
		comments = yak.get_comments()
		print ("\n\t\tComments:", end='')
		print (len(comments))

		# print all comments separated by dashes
		for comment in comments:
			print ("\t\t", end='')
			print ("-" * 77)
			comment.print_comment()

		yakNum += 1

main()