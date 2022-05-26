from crawlmap.functions.misc import remove_slash
from urllib import parse
import xml.etree.ElementTree as ET
import base64
import json


def parsing_burp(burp_file_path, exclude_extensions, url_input):
	"""
		Parse the XML from the BurpSuite output

		Return a list of path and the url
	"""

	print("[Parsing Burpsuite file]")
	paths = []

	try:
		root = ET.parse(burp_file_path).getroot()
	except:
		print(f"\tError can't parse your file : {burp_file_path}")
		print("\tIt must be in xml format, go to [https://github.com/Liodeus/Crawlmap/wiki/Burp-Suite], to see an example.")
		exit()

	for type_tag in root.findall("item/request"):
		value = type_tag.text
		try:
			data = base64.b64decode(value).decode("utf-8")
		except:
			continue

		verb = data.split('\r\n')[0].split()
		dict_params = get_params_from_burp(data, verb)
		
		url_to_parse = remove_slash(url_input + verb[1])
		url = parse.urlsplit(url_to_parse)
		paths.append([url, dict_params])

	return paths


def get_params_from_burp(data, request):
	"""
		Get the parameters from a request

		Return a dictionnary of parameters
	"""

	verb = request[0]
	dict_params = {}
	dict_params[f"[{verb}]"] = {"URL_PARM": [], "DATA": [], "JSON": [], "UPLOAD": []}

	# GET
	try:
		get_data = request[1].split('?')[1]
		for element in get_data.split('&'):
			dict_params[f"[{verb}]"]["URL_PARM"].append(element.split('=')[0])
	except IndexError:
		pass

	# UPLOAD
	if "Content-Type: multipart/form-data" in data or "content-type: multipart/form-data" in data:
		data = data.split('\r\n')
		for element in data:
			if "Content-Disposition: form-data; name=" in element:
				upload_form_param = element.split(';')[1].split('=')[1][1:-1]
				dict_params[f"[{verb}]"]["UPLOAD"].append(upload_form_param)

	# JSON
	elif "Content-Type: application/json" in data or "content-type: application/json" in data and verb != "GET":
		d = data.split('\r\n')

		try:
			json_data = json.loads(d[-1].split('\n\n')[-1])
			for key, value in json_data.items():
				dict_params[f"[{verb}]"]["JSON"].append(key)
		except AttributeError:
			json_data = json_data[0]
			for key, value in json_data.items():
				dict_params[f"[{verb}]"]["JSON"].append(key)
		except json.decoder.JSONDecodeError:
			pass
	# OTHER
	else:
		if verb != "GET":
			try:
				data_params = data.split('\r\n')[-1]
				if data_params:
					data_params = data_params.split('&')
					for element in data_params:
						dict_params[f"[{verb}]"]["DATA"].append(element.split('=')[0])
			except:
				pass

	return dict_params
