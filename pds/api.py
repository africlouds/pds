import frappe
from frappe import _
import requests 
import googlemaps
from pubnub import Pubnub

gmaps = googlemaps.Client(key='AIzaSyClZw3R63FghnycvQVypPxOTUZyHAXilEU')



def send_fcm(doc, method):
	delivery = frappe.get_doc("Delivery Request", doc.name)
	headers = {'Content-type': 'application/json', 'Authorization': 'key=AIzaSyDzU4JxnT4XoE7igPuvYQy0MgilCKu9W-I'}
	data = { "data": {
	    #"delivery": "Derivery to %s for %s " % (delivery.dropoff_point, delivery.client_names)
	    "delivery": "Derivery for %s. Pick UP: %s, Drop Off: %s" % (delivery.client_names, delivery.pickup_point, delivery.dropoff_point)
	  },
	  "to" : "cHFwFikZz3A:APA91bFL2kr3C5uWU4ol_3WrZA4jGdif3iscCoAth5VMHjRVCq6fB1pVZ4wJNhldwtf6wNv5KVBWcenBJxde58oKAClIOPSE--p2IiMM9R1r50HUTdZJSqK7YNbvCKsjGmwUnUlBkMHM"
	}
	r = requests.post('https://fcm.googleapis.com/fcm/send', json=data, headers=headers)
	frappe.msgprint(str(r.status_code))


def send_pubnub(doc, method):
	location = frappe.get_doc("Location", doc.name)
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	message = {'lat':location.latitude, 'lng':location.longitude}
	pubnub.publish(channel='mymaps', message=message)


def create_message(doc, method):
	delivery_request = frappe.get_doc("Delivery Request", doc.name)
	closest_clerk = get_closest_clerk(delivery_request.pickup_point)
	delivery_request.assigned_clerk = closest_clerk.name
	delivery_request.save()
	frappe.get_doc({
	  	"doctype": "Message", 
	  	"delivery_clerk": closest_clerk.name,
		"message":"A delivery task from %s to %s is assigned to you" % (delivery_request.pickup_point, delivery_request.dropoff_point),
		"from_client":"Tim",
		"type":"Delivery Request"		
	}).insert()

def get_closest_clerk(pickup_point):
	#get all clerks
	all_clerks = frappe.get_list("Delivery Clerk", fields=['name','location'])
	#make the first clerk as the closest
	clerk_locations = []
	pickup_point = pickup_point.split(",")
	#loop over all clerk comparing their current locations to the closest
	for clerk in all_clerks:
		location = clerk.location.split(",")
		clerk_locations.append((float(location[0]), float(location[1])))
	directions_result = gmaps.distance_matrix(clerk_locations,(pickup_point[0], pickup_point[1]))
	closest = 0
	for i, row in enumerate(directions_result['rows']):
		row = row['elements'][0]
		duration = row['duration']['value']
		distance = row['distance']['value']
		closest_clerk = directions_result['rows'][closest]
		if closest_clerk['elements'][0]['duration']['value'] > duration:
			closest = i
	return all_clerks[closest]

