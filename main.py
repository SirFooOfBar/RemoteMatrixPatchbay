#!/usr/bin/env python3
from aiohttp import web
import jack

jack_cli=jack.Client("web_controller")
routes = web.RouteTableDef()

def get_group(port):
	len1=len(port.name)
	len2=len(port.shortname)
	return port.name[:len1-len2-1]

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
	for port in jack_cli.get_ports(is_audio=v_filter=="audio",is_midi=v_filter=="midi"):
		group_name=get_group(port)
		iout = "inputs" if port.is_input else "outputs" if port.is_output else None

		if not client_list[iout].get(group_name):
			client_list[iout][group_name]=[]

		if iout=="inputs":
			client_list[iout][group_name].append({"name":port.name,"short_name":port.shortname})
		else:
			client_list[iout][group_name].append({"name":port.name,"short_name":port.shortname,"connected_to":[con_port.name for con_port in jack_cli.get_all_connections(port)]})


	return web.json_response(client_list)

@routes.get('/flat_list_clients/{filter}')
@routes.get('/flat_list_clients')
async def list_clients(request):
	try:
		v_filter=request.match_info['filter']
	except KeyError as e:
		v_filter=None
	return web.json_response([port.name for port in jack_cli.get_ports(is_audio=v_filter=="audio",is_midi=v_filter=="midi")])

@routes.get('/')
async def index(request):
    return web.FileResponse('client/simple.html')

routes.static("/","client")
app = web.Application()
app.add_routes(routes)
web.run_app(app)
