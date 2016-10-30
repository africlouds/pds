import frappe
from frappe import _
import requests 
from pubnub import Pubnub



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
	frappe.get_doc({
	  	"doctype": "Message", 
	  	"delivery_clerk": get_closest_clerk(delivery_request.pickup_point),
		"message":"A delivery task from %s to %s is assigned to you" % (delivery_request.pickup_point, delivery_request.dropoff_point),
		"from_client":"Tim",
		"type":"Delivery Request"		
	}).insert()

def get_closest_clerk(origin):
	return "d2a166ca9c"


