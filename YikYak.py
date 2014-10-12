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
		coordlocation = newLocation(geocoder)
		# If location retrieval fails, ask user for coordinates
		if coordlocation == 0:
			print("Please enter coordinates manually: ")
			currentlatitude = input("Latitude: ")
			currentlongitude = input("Longitude: ")
			coordlocation = pk.Location(currentlatitude, currentlongitude)
	
	print()
	
	# start API and get list of yaks
	remoteyakker = pk.Yakker(None, coordlocation, False)
	yaklist = remoteyakker.get_yaks()
	
	while True:
		choice = input("Read(R), Post(P), Choose New Location(L), or Quit(Q) -> ")
		# Read Yaks
		if choice == 'R' or choice == 'r':
			for yak in yaklist:
				# line between yaks
				print ("_" * 93)
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
				
		elif choice == 'L' or choice == 'l':
			print()
			coordlocation = newLocation(geocoder)
			if coordlocation == 0:
				print("Please enter coordinates manually: ")
				currentlatitude = input("Latitude: ")
				currentlongitude = input("Longitude: ")
				coordlocation = pk.Location(currentlatitude, currentlongitude)
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

main()