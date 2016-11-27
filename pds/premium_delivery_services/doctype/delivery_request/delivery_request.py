# -*- coding: utf-8 -*-
# Copyright (c) 2015, PDS Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyClZw3R63FghnycvQVypPxOTUZyHAXilEU') 

class DeliveryRequest(Document):
	def update_stats(self):
		if self.clerk_location and self.client_location:
			pickup_point = tuple(self.pickup_point.split(",")) 
			dropoff_point = tuple(self.dropoff_point.split(",")) 
			clerk_location = tuple(self.clerk_location.split(",")) 
			client_location = tuple(self.client_location.split(",")) 
			total_directions_result = gmaps.distance_matrix(pickup_point, dropoff_point)
			directions_result = gmaps.distance_matrix(clerk_location, client_location)

			for i, row in enumerate(total_directions_result['rows']):
				row = row['elements'][0]
				duration = row['duration']['value']
				distance = row['distance']['value']
				self.total_distance =distance 
				self.total_time =duration 
				self.save()

			for i, row in enumerate(directions_result['rows']):
				row = row['elements'][0]
				duration = row['duration']['value']
				distance = row['distance']['value']
				self.clerk_traveled_distance = distance
				self.remaining_distance = self.total_distance - distance 

				self.clerk_traveled_time = duration 
				self.remaining_time = self.total_time - duration 
				self.save()
