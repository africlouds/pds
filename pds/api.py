import frappe
from frappe import _
import requests 
import googlemaps
from pubnub import Pubnub
import json

gmaps = googlemaps.Client(key='AIzaSyClZw3R63FghnycvQVypPxOTUZyHAXilEU')



@frappe.whitelist(allow_guest=True)
def start_delivering(order_number):
	delivery_request = frappe.get_doc("Delivery Request", order_number)
	delivery_request.status = "Delivering"
	delivery_request.save()
	frappe.get_doc({
		"doctype": "Message", 
		"destination_type": "Client",
		"destination": delivery_request.order_number,
		"type":"Delivering"
	}).insert()
	frappe.get_doc({
		"doctype": "Location", 
		"type": "Delivery Clerk",
		"delivery_clerk": delivery_request.assigned_clerk,
		"latitude":"0",
		"longitude":"0"
	}).insert()
	return order_number 

@frappe.whitelist(allow_guest=True)
def finish_delivering(order_number):
	delivery_request = frappe.get_doc("Delivery Request", order_number)
	delivery_request.status = "Delivered"
	delivery_request.save()
	frappe.get_doc({
		"doctype": "Message", 
		"destination_type": "Client",
		"destination": delivery_request.order_number,
		"type":"Delivered"
	}).insert()
	clerk = frappe.get_doc("User", delivery_request.assigned_clerk)
	clerk.status = 'Free'
	clerk.delivery_request = None
	clerk.save()
	#TODO: pick the oldest first
	delivery_request = frappe.get_list("Delivery Request", filters={'status':'Pending'},fields=['name'])
	if len(delivery_request) > 0:
		delivery_request = frappe.get_doc("Delivery Request", delivery_request[0]['name'])
		assign_clerk(delivery_request)
	return order_number 



def update_dashboard(doc, method):
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	messages = {'eon': {
		'Delivered': frappe.db.count("Delivery Request", filters={"status": 'Delivered'}),
		'Pending': frappe.db.count("Delivery Request", filters={"status": 'Pending'}),
		'Delivering': frappe.db.count("Delivery Request", filters={"status": 'Delivering'}),
		'Assigned': frappe.db.count("Delivery Request", filters={"status": 'Assigned'})
	}}
	pubnub.publish(channel='dashboard_stats', message=messages)
	delivery_requests = frappe.get_list("Delivery Request", filters={'status':'Delivering'},fields=['name', 'pickup_point','dropoff_point', 'assigned_clerk','order_number'])

	for delivery_request in delivery_requests:
		message = {'eon': delivery_request}
		pubnub.publish(channel='dashboard_requests', message=message)
	

	
def process_location(doc, method):
	location = frappe.get_doc("Location", doc.name)
	#check client or clerk
	if location.type == "Client":
		#get the corresponding delivery request
		order_number = location.order_number
		delivery_request = frappe.get_list("Delivery Request", filters={'order_number':order_number},fields=['name'])
		delivery_request = frappe.get_doc("Delivery Request", delivery_request[0]['name'])
		#if it is the first location, set it as the drop off point and assign a clerk
		if not delivery_request.dropoff_point:
			delivery_request.dropoff_point = "%s,%s" % (location.latitude, location.longitude) 
			delivery_request.dropoff_point_number = location.location_number
			delivery_request.save()
			assign_clerk(delivery_request)
		if delivery_request.status != 'Delivered':
			#update client location every time a new client location is received``
			delivery_request.client_location = "%s,%s" % (location.latitude, location.longitude) 
			delivery_request.save()
		#send location to the assigned delivery clerk
		if delivery_request.status in ['Assigned', 'Delivering']:
			send_location(delivery_request.assigned_clerk, location)
		if delivery_request.status in ['Pending','Delivering']:
			send_location('dashboard', location)
	elif location.type == "Delivery Clerk":
		icon = "pending_delivery_clerk"
		if location.delivery_clerk:
			delivery_clerk = location.delivery_clerk
			#get assigned delivery request
			delivery_request = frappe.get_list("Delivery Request", filters={'assigned_clerk':delivery_clerk},fields=['name'])
			if len(delivery_request) > 0:
				delivery_request = frappe.get_doc("Delivery Request", delivery_request[0]['name'])
				icon = '%s_delivery_clerk' % delivery_request.status.lower()
				if delivery_request.status == 'Delivering':
					delivery_request.clerk_location = "%s,%s" % (location.latitude, location.longitude)
					delivery_request.save()
					#delivery_request.update_stats()
					send_location(delivery_request.order_number, location)
					update = {
						"remaining_time": delivery_request.remaining_time,
						"remaining_distance": delivery_request.remaining_distance
					}
					frappe.get_doc({
						"doctype": "Message", 
						"destination_type": "Client",
						"destination": delivery_request.order_number,
						"type":"Update",
						"message":  json.dumps(update)
					}).insert()
		send_location('dashboard', location, icon)
			

	
def send_location(channel, location, icon=None):
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	clerk_identifier = ""
	if location.type == "Delivery Clerk":
		delivery_clerk = frappe.get_doc("User", location.delivery_clerk)
		delivery_request = frappe.get_doc("Delivery Request", delivery_clerk.delivery_request)
		clerk_identifier = delivery_request.status.lower()+"_"+location.delivery_clerk
		
	message = {
		location.order_number if location.type ==  'Client' else clerk_identifier:{
			'data': {
					'routeTag':location.order_number if location.type ==  'Client' else clerk_identifier,
				 	'type':'client' if location.type ==  'Client' else icon
			},
            		'latlng': [location.latitude,location.longitude]
		}
          }
	pubnub.publish(channel=channel, message=message)


def send_pubnub_clerk(doc, method):
	message = frappe.get_doc("Message", doc.name)
	pubnub = Pubnub(publish_key="pub-c-21663d8a-850d-4d99-adb3-3dda55a02abd", subscribe_key="sub-c-266bcbc0-9884-11e6-b146-0619f8945a4f")
	if message.destination_type == "Delivery Clerk":
		pubnub.publish(channel=message.destination, message={'type':message.type, 'message':message.message, 'order_id':message.order_id} )
	elif message.destination_type == "Client":
		pubnub.publish(channel=message.destination, message={'type':message.type, 'message':message.message} )
	pubnub.publish(channel='dashboard_updates', message={'type':message.type} )
			
		

def assign_clerk(delivery_request):
	closest_clerk = get_closest_clerk(delivery_request.pickup_point)
	if closest_clerk:
		delivery_request.assigned_clerk = closest_clerk.name
		delivery_request.save()
		closest_clerk = frappe.get_doc("User", closest_clerk.name)
		closest_clerk.status = 'Busy'
		closest_clerk.delivery_request = delivery_request.name
		closest_clerk.save()
		frappe.get_doc({
			"doctype": "Message", 
			"destination_type": "Delivery Clerk",
			"destination": closest_clerk.name,
			"message":"A delivery task from %s to %s is assigned to you" % (delivery_request.pickup_point, delivery_request.dropoff_point),
			"type":"Delivery Request",
			"order_id": delivery_request.name
		}).insert()
		frappe.get_doc({
			"doctype": "Message", 
			"destination_type": "Client",
			"destination": delivery_request.order_number,
			"type":"Assigned",
			"message":closest_clerk.name
		}).insert()
		frappe.get_doc({
			"doctype": "Message", 
			"destination_type": "Dashboard",
			"destination": 'dashboard_updates',
			"type":"Assigned",
			"message":"{'order_number':'%s', 'clerk':'%s'}" % (delivery_request.order_number, closest_clerk.name)
		}).insert()


def get_closest_clerk(pickup_point):
	#get all clerks
	filters = {
		'status':'Free'
	}
	all_clerks = frappe.get_list("User", filters=filters, fields=['name','location'])
	if len(all_clerks) > 0:
		#make the first clerk as the closest
		clerk_locations = []
		pickup_point = pickup_point.split(",")
		#loop over all clerk comparing their current locations to the closest
		for clerk in all_clerks:
			if clerk.location:
				location = clerk.location.split(",")
				clerk_locations.append((float(location[0]), float(location[1])))
		"""
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
		"""
		return all_clerks[0]
	else:
		return None

