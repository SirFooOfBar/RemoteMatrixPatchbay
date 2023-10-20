#!/usr/bin/env python3
from aiohttp import web
from os import environ
from configuration import hidden_ports
import jack, re

jack_cli=jack.Client("web_controller")
routes = web.RouteTableDef()

http_host=environ.get("HTTP_HOST") or "localhost"
http_port=environ.get("HTTP_PORT") or 8096

def get_shortname(port):
	index=port.name.rindex(":")
	return port.name[index+1:]

def get_group(port, shortname=None):
	if not shortname:
		shortname=get_shortname(port)

	len1=len(port.name)
	len2=len(shortname)
	return port.name[:len1-len2-1]

def match_any(s: str, *patterns):
	for pattern in patterns:
		if re.search(pattern,s):
			return True
	return False

def get_ports(v_filter):
	return [port for port in jack_cli.get_ports(is_audio=v_filter=="audio",is_midi=v_filter=="midi") if not match_any(port.name,*hidden_ports) ]

@routes.post('/connect')
async def jack_connect(request):
	data=await request.json()
	try:
		for in_port, out_port in data:
			jack_cli.connect(in_port,out_port)
		return web.json_response({"status":"success"})
	except jack.JackErrorCode as e:
		return web.json_response({"status":"failure","message":e.message,"code":e.code})

@routes.post('/disconnect')
async def jack_disconnect(request):
	data=await request.json()
	try:
		for in_port, out_port in data:
			jack_cli.disconnect(in_port,out_port)
		return web.json_response({"status":"success"})
	except jack.JackErrorCode as e:
		return web.json_response({"status":"failure","message":e.message,"code":e.code})


@routes.get('/list_clients/{filter}')
@routes.get('/list_clients')
async def list_clients(request):
	try:
		v_filter=request.match_info['filter']
	except KeyError as e:
		v_filter=None
	client_list={"inputs":{},"outputs":{}}
	for port in get_ports(v_filter):
		shortname=get_shortname(port)
		group_name=get_group(port)
		iout = "inputs" if port.is_input else "outputs" if port.is_output else None

		if not client_list[iout].get(group_name):
			client_list[iout][group_name]=[]

		if iout=="inputs":
			client_list[iout][group_name].append({"name":port.name,"short_name":shortname})
		else:
			client_list[iout][group_name].append({"name":port.name,"short_name":shortname,"connected_to":[con_port.name for con_port in jack_cli.get_all_connections(port)]})


	out_keys=list(client_list["outputs"].keys())
	out_keys.sort()

	in_keys=list(client_list["inputs"].keys())
	in_keys.sort()

	return web.json_response({
		"inputs":[{"group_name":k,"ports":client_list["inputs"][k]} for k in in_keys],
		"outputs":[{"group_name":k,"ports":client_list["outputs"][k]} for k in out_keys],
	})

@routes.get('/flat_list_clients/{filter}')
@routes.get('/flat_list_clients')
async def list_clients(request):
	try:
		v_filter=request.match_info['filter']
	except KeyError as e:
		v_filter=None
	in_ports=[{"name":port.name,"short_name":port.shortname} for port in get_ports(v_filter) if port.is_input]
	out_ports=[{"name":port.name,"short_name":port.shortname, "connected_to":[con_port.name for con_port in jack_cli.get_all_connections(port)]} for port in get_ports(v_filter) if port.is_output]
	in_ports.sort(key=lambda a: a["short_name"])
	out_ports.sort(key=lambda a: a["short_name"])
	return web.json_response({"inputs":in_ports,"outputs":out_ports})

@routes.get('/')
async def index(request):
    return web.FileResponse('client/simple.html')

routes.static("/","client")
app = web.Application()
app.add_routes(routes)
web.run_app(app,host=http_host,port=http_port)
