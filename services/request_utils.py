# CPSC 449-02 Web Back-end Engineering

# Project 5, Polyglot Persistence (sqlite and dynamodb)

# Group members
# 		Brandon Xue (brandonx@csu.fullerton.edu)

import flask
import flask_api
import functools

# Just a quick decorator to simplify the specification of required fields
class require_fields(object):
	def __init__(self, required_fields):
		"""Used as a decorator to specify required fields for a request handling function."""
		self.required_fields = required_fields
		
	def __call__(self, func):
		"""Wraps a function and enforces required fields on it."""
		@functools.wraps(func)
		def require_enforced(*args, **kwargs):
			received_fields = {*flask.request.data}
			if not self.required_fields <= received_fields:
				missing = [field for field in self.required_fields - received_fields]
				return {'missing-fields': missing}, flask_api.exceptions.status.HTTP_400_BAD_REQUEST
				# raise flask_api.exceptions.ParseError(detail=err_msg)
			else:
				return func(*args, **kwargs)

		return require_enforced