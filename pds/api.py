import frappe
from frappe import _
import requests 

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
	
