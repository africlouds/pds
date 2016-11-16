import frappe
from frappe import _
import requests 
import googlemaps
from pubnub import Pubnub
import json

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


def process_location(doc, method):
	location = frappe.get_doc("Location", doc.name)
	send_location('dashboard', location)
	#check client or clerk
	if location.type == "Client":
		#get the corresponding delivery request
		order_number = location.order_number
		delivery_request = frappe.get_list("Delivery Request", filters={'order_number':order_number},fields=['name'])
		delivery_request = frappe.get_doc("Delivery Request", delivery_request[0]['name'])
		#if it is the first location, set it as the drop off point and assign a clerk
		if not delivery_request.dropoff_point:
			delivery_request.dropoff_point = "%s,%s" % (location.latitude, location.longitude) 
			assign_clerk(delivery_request)
		#update client location every time a new client location is received``
		delivery_request.client_location = "%s,%s" % (location.latitude, location.longitude) 
		delivery_request.save()
		#send location to the assigned delivery clerk
		send_location(delivery_request.assigned_clerk, location)
	elif location.type == "Delivery Clerk":
		#get assigned delivery request
		send_location(location.order_number, location)
		delivery_clerk = location.delivery_clerk
		delivery_request = frappe.get_list("Delivery Request", filters={'assigned_clerk':delivery_clerk},fields=['name'])
		delivery_request = frappe.get_doc("Delivery Request", delivery_request[0]['name'])
		if delivery_request.status == 'Delivering':
			send_location(delivery_request.order_number, location)
			

	
def send_location(channel, location):
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	message = {
		location.order_number if location.type ==  'Client' else location.delivery_clerk:{
            		'latlng': [location.latitude,location.longitude]
		}
          }
	pubnub.publish(channel=channel, message=message)

def send_pubnub(doc, method):
	location = frappe.get_doc("Location", doc.name)
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	#message = {'lat':location.latitude, 'lng':location.longitude}
	#all_locations = frappe.get_list("Location", fields=['name','longitude','latitude'])
	message = {
		location.delivery_clerk:{
            		'latlng': [location.latitude,location.longitude]
		}
          }

	pubnub.publish(channel='mymaps', message=message)

def send_pubnub_clerk(doc, method):
	message = frappe.get_doc("Message", doc.name)
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	pubnub.publish(channel=message.delivery_clerk, message={'type':message.type, 'order_id':message.order_id} )

def assign_clerk(delivery_request):
	closest_clerk = get_closest_clerk(delivery_request.pickup_point)
	delivery_request.assigned_clerk = closest_clerk.name
	delivery_request.save()
	frappe.get_doc({
	  	"doctype": "Message", 
	  	"delivery_clerk": closest_clerk.name,
		"message":"A delivery task from %s to %s is assigned to you" % (delivery_request.pickup_point, delivery_request.dropoff_point),
		"from_client": delivery_request.client_names,
		"type":"Delivery Request",
		"order_number": delivery_request.order_number,
		"order_id": delivery_request.name
	}).insert()

def get_closest_clerk(pickup_point):
	#get all clerks
	all_clerks = frappe.get_list("User", fields=['name','location'])
	#make the first clerk as the closest
	clerk_locations = []
	pickup_point = pickup_point.split(",")
	#loop over all clerk comparing their current locations to the closest
	for clerk in all_clerks:
		if clerk.location:
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

