from __future__ import print_function
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError
from flask import Flask, render_template, flash, request, url_for, redirect, session, current_app
from flask_wtf import Form
from functools import wraps
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from passlib.hash import sha256_crypt
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from wtforms import StringField, TextField, BooleanField, validators, PasswordField, Form, IntegerField, DateField, TextAreaField, validators
from wtforms_components import DateRange
import httplib2 
import gc, logging
import os
import reportForms as rf
import time as _time

# Try & Except block used for Google Calendar Authentication along with scopes &
# client secret file below
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'Google Calendar API'

# Initialization of Flask instance for website application
def create_app(config, debug=False, testing=False, config_overrides=None):
	app = Flask(__name__)
	app.config.from_object(config)
	
	app.debug = debug
	app.testing = testing
	
	if config_overrides:
		app.config.update(config_overrides)
		
	if not app.testing:
		logging.basicConfig(level=logging.INFO)
		
	with app.app_context():
		model = get_model()
		model.init_app(app)
	
	# Credentials method used to retrieve or create necessary credentials for
	# access to Google Calendar API
	def get_credentials():
		home_dir = os.path.expanduser('~')
		credential_dir = os.path.join(home_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir,
									   'google-calendar.json')

		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			if flags:
				credentials = tools.run_flow(flow, store, flags)
			else: # Needed only for compatibility with Python 2.6
				credentials = tools.run(flow, store)
			print('Storing credentials to ' + credential_path)
		return credentials
	
	# Rendering of website homepage
	@app.route('/')
	def Homepage():
		return render_template("main.html")
	
	# Rendering of Services webpage
	@app.route('/Services/')	
	def servicePage():
		return render_template("services.html")
	
	# Method used to convert of appointment date to fit datetime format (YYYY-MM-DD)
	def dayConvert(day):
		if day == '1':
			day = '01'
		elif day == '2':
			day = '02'
		elif day == '3':
			day = '03'
		elif day == '4':
			day = '04'
		elif day == '5':
			day = '05'
		elif day == '6':
			day = '06'
		elif day == '7':
			day = '07'
		elif day == '8':
			day = '08'
		elif day == '9':
			day = '09'
			
		return day
	
	# Method used to convert of appointment month to fit datetime format (YYYY-MM-DD)
	def monthConvert(month):
		if month == 'Jan':
			month = '01'
		elif month == 'Feb':
			month = '02'
		elif month == 'Mar':
			month = '03'
		elif month == 'Apr':
			month = '04'
		elif month == 'May':
			month = '05'
		elif month == 'Jun':
			month = '06'
		elif month == 'Jul':
			month = '07'
		elif month == 'Aug':
			month = '08'
		elif month == 'Sep':
			month = '09'
		elif month == 'Oct':
			month = '10'
		elif month == 'Nov':
			month = '11'
		elif month == 'Dec':
			month = '12'
			
		return month
	
	# Construction of EventID for use in calls to Google Calendar API
	# using month, day, time, and year from appointments method
	def getEventID(month, day, time, year):
		month = monthConvert(month)
		day = dayConvert(day)
		partialEventId = year + month + day + 'T'
		
		if _time.daylight:
			if time == '8AM':
				eventStr = '4hn08j4s4rqdhe3tuls42mgkp2_'
				time = '130000Z'
			else:
				eventStr = '6gqt5n557es3mev7rom2npgbp6_'
				time = '180000Z'
		else:
			if time == '8AM':
				eventStr = '4hn08j4s4rqdhe3tuls42mgkp2_'
				time = '120000Z'
			else:
				eventStr = '6gqt5n557es3mev7rom2npgbp6_'
				time = '170000Z'
		
		fullEventId = eventStr + year + month + day + 'T' + time
	
		return fullEventId
	
	# Validates email information & format when client schedules an appointment
	def validateEmail(email):
		try:
			v = validate_email(email) # validate and get info
			email = v["email"] # replace with normalized form
			return True
		except EmailNotValidError as e:
		# email is not valid, exception message is human-readable
			flash(str(e))
		return False
		
	# Rendering of appointments page that collects information upon 'POST'
	# method, calls the getEventID(), and updates appointment slot in Google Calendar
	@app.route('/Appointments/', methods = ['GET', 'POST'])	
	def appointments():
		try:
			months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
			'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
			days = [x for x in range(1,32)]
			times = ['8AM','1PM']
			years = [x for x in range(2017,2026)]
			services = ['All', 'Home', 'Dryer', 'Vent']
			
			credentials = get_credentials()
			http = credentials.authorize(httplib2.Http())
			service = discovery.build('calendar', 'v3', http=http)
			# List calendar
			calendar_list_entry = service.calendarList().get(calendarId='cosu83stsjnm94l9i1l3ld3cr8@group.calendar.google.com').execute()
			
			if request.method == "POST" and validateEmail(request.form['email']):

				month = request.form['month']
				day = request.form['day']
				time = request.form['time']
				year = request.form['year']
				services = request.form.getlist('service')
				name = request.form['name']
				email = request.form['email']
				address = request.form['address']
				servStr = ''
				for item in services:
					servStr = servStr + item + '\n'
				eventID= getEventID(month,day,time,year)
				event = service.events().get(calendarId='cosu83stsjnm94l9i1l3ld3cr8@group.calendar.google.com', eventId=eventID).execute()
				if event['visibility']  == 'private':
					flash("Please pick a date not marked busy.")
					return render_template("appointments.html", years=years, months=months, days=days, times=times, services=services) 
				event['summary'] = 'Appointment for ' + name
				event['visibility'] = 'private'				
				description = 'Name: %s \nEmail: %s \nServices Required: %s' % (name, email, servStr)
				event['description'] = description
				event['location'] = address
				event['transparency'] = 'opaque'
				updated_event = service.events().update(calendarId='cosu83stsjnm94l9i1l3ld3cr8@group.calendar.google.com', eventId=event['id'], body=event).execute()
				flash('Appointment has been reserved!')

				return render_template("appointments.html", years=years, months=months, days=days, times=times, services=services)
				
				
			return render_template("appointments.html", years=years, months=months, days=days, times=times, services=services)
		except Exception as e:
			return(str(e))
	
	# Rendering of contact information webpage
	@app.route('/Contact/')	
	def contact():
		return render_template("contact.html")
		
	# Rendering of 404 not found page when error occurs
	@app.errorhandler(404)
	def page_not_found(e):
		return render_template("404.html")
	
	# Rendering of 500 error page when server error occurs
	@app.errorhandler(500)
	def page_not_found(e):
		return render_template("500.html")
	
	# Rendering of login webpage for business employee to login	
	@app.route('/Login/', methods = ['GET', 'POST'])
	def login_page():
		error = ''
		try:
			if request.method == "POST":
				userInfo = get_model().retrieveLoginInfo(request.form["username"])
				
				if sha256_crypt.verify(request.form['password'], userInfo.password):
					session['logged_in'] = True
					session['username'] = request.form['username']
					flash("You are now logged in.")
					return redirect(url_for('Homepage'))
					
				else:
					error = "Invalid login credentials. Try again."
					
			gc.collect()
			return render_template("login.html", error = error)
			
		except Exception as e:
			error = "Invalid login credentials. Try again."
			return render_template("login.html", error = error)
	
	# Method used to require logging in for employee functions (managing reports)
	def login_required(f):
		@wraps(f)
		def wrap(*args, **kwargs):
			if 'logged_in' in session:
				#flash('logged in ')
				return f(*args, **kwargs)
			else:
				flash("You need to login first.")
				return redirect(url_for("login_page"))
		return wrap
	
	# Logs user out and redirects to homepage
	@app.route('/Logout/')
	@login_required
	def logout():
		session.clear()
		flash("You have been logged out.")
		gc.collect()
		return redirect(url_for('Homepage'))
	
	# PDF of newly written inspection report displayed after information 
	# stored in database
	@app.route('/PDF/')
	@login_required
	def PDF():
		flash('Please save or print report for your records.')
		return render_template("pdf.html")
	
	# Rendering of registration page for new users/employees
	@app.route('/Register/', methods = ['GET', 'POST'])
	def register_page():
		try:
			form = rf.RegistrationForm(request.form)
			
			if request.method == "POST" and form.validate():
			
				firstname = form.firstname.data
				lastname = form.lastname.data
				username = form.username.data
				email = form.email.data
				password = sha256_crypt.encrypt((str(form.password.data)))
				data = {'firstname': firstname, 'lastname': lastname, 'username': username, 'password': password, 'email': email}
				
				user = get_model().createUser(data)
				session['logged_in'] = True
				session['username'] = username
				gc.collect()
				return redirect(url_for('Homepage'))
			else:
				return render_template('register.html', form=form)
					
		except Exception as e:
			return(str(e))
	
	# Rendering of reports page, allowing employee to write new or edit previous report
	@app.route('/Reports/')
	@login_required
	def Reports():			
		return render_template("reports.html")
	
	# Rendering of edit page; user enters ID of report to edit, report 
	# retrieved, changes made, and database fields updated
	@app.route('/Edit/', methods = ['GET', 'POST'])
	def Edit():
		reports = get_model().getReportInfo()
		repform = rf.ReportForm(request.form)
		idList = []

		# idList used to verify report to be edited is in database
		for item in reports:
			idList.append(item.RID)

		try:
			# 'checked' variable used to flag changes made for updating report infor in database
			checked = 'check' in request.form
			
			# Population of report fields by calling database with RID entered by user
			if request.method == "POST" and repform.RID.data in idList and not checked:
				
				Rid = reports[repform.RID.data-1].RID
				Date = reports[repform.RID.data-1].Date
				Uid = reports[repform.RID.data-1].UID
				addr = get_model().getAddressInfo(Rid)
				
				# Retrieval of data from database
				rat = get_model().getRoofAtticInfo(Rid)
				gar = get_model().getGarageInfo(Rid)
				kit = get_model().getKitchenInfo(Rid)
				roo = get_model().getRoomsInfo(Rid)
				bat = get_model().getBathroomsInfo(Rid)
				stru = get_model().getStructureInfo(Rid)
				plu = get_model().getPlumbingInfo(Rid)
				ele = get_model().getElectricalInfo(Rid)
				ext = get_model().getExteriorInfo(Rid)
				hca = get_model().getHeatCentAirInfo(Rid)
				
				return render_template("edit.html", form=repform, rid=Rid, date=Date, uid=Uid, req=addr[0].Requester, street=str(addr[0].StreetAddress),
				city=addr[0].City, st=addr[0].State, zip=addr[0].ZipCode, rarc = rat[0].RoofCoverings, rarci = rat[0].RCInsp, rafl=rat[0].Flashings, 
				rafli=rat[0].FlasInsp, rasc=rat[0].SkylightChimney, rasci=rat[0].SkChInsp, rave=rat[0].aVentilation, ravei=rat[0].aVentInsp, radr=rat[0].aDrainage,
				radri=rat[0].aDraiInsp, raas=rat[0].StructureAttic, raasi=rat[0].StAtInsp, raft=rat[0].FansThermostat, rafti=rat[0].FaThInsp, rain=rat[0].aInsulation,
				raini=rat[0].aInsuInsp, ravw=rat[0].VisibleWiring, ravwi=rat[0].ViWiInsp, exwf=ext[0].WallFlashTrim, exwfi=ext[0].WaFTInsp, exdo=ext[0].exDoors, 
				exdoi=ext[0].exDoorInsp, exwi=ext[0].exWindows, exwii=ext[0].exWindInsp, exdb=ext[0].DeckBalcSteps, exdbi=ext[0].DeBSInsp, exvd=ext[0].VegetDrainDriveWalk, 
				exvdi=ext[0].VDDWInsp, exea=ext[0].EavesFascia, exeai=ext[0].EaFaInsp, expl=ext[0].exPlumbing, expli=ext[0].exPlumInsp, exou=ext[0].Outlets, exoui=ext[0].OutlInsp, 
				gace=gar[0].gCeiling, gacei=gar[0].gCeilInsp, gawa=gar[0].gWalls, gawai=gar[0].gWallInsp, gafl=gar[0].gFloor, gafli=gar[0].gFlooInsp, gado=gar[0].gDoor, 
				gadoi=gar[0].gDoorInsp, gadg=gar[0].InnerDoor, gadgi=gar[0].InDoInsp, gaop=gar[0].GDOperator, gaopi=gar[0].GDOpInsp, kice=kit[0].kCeiling, kicei=kit[0].kCeilInsp,
				kiwa=kit[0].kWalls, kiwai=kit[0].kWallInsp, kifl=kit[0].kFloor, kifli=kit[0].kFlooInsp, kipd=kit[0].PantryDoor, kipdi=kit[0].PaDoInsp, kiwi=kit[0].kWindows,
				kiwii=kit[0].kWindInsp, kicc=kit[0].kCountersCabinets, kicci=kit[0].kCoCaInsp, kipl=kit[0].kPlumbing, kipli=kit[0].kPlumInsp, kios=kit[0].kOutletSwitchFix, 
				kiosi=kit[0].kOuSFInsp, kidi=kit[0].Dishwash, kidii=kit[0].DishInsp, kiro=kit[0].RangeOven, kiroi=kit[0].RaOvInsp, kimi=kit[0].Microwave, kimii=kit[0].MicrInsp, 
				roce=roo[0].rCeiling, rocei=roo[0].rCeilInsp, rowa=roo[0].rWalls, rowai=roo[0].rWallInsp, rofl=roo[0].rFloor, rofli=roo[0].rFlooInsp, rosb=roo[0].StairRailBalc, 
				rosbi=roo[0].SRBaInsp, rodo=roo[0].rDoor, rodoi=roo[0].rDoorInsp, rowi=roo[0].rWindows, rowii=roo[0].rWindInsp, roos=roo[0].rOutletSwitchFix, roosi=roo[0].rOuSFInsp,
				bacc=bat[0].CounterCabinet, bacci=bat[0].bCoCaInsp, bado=bat[0].bDoor, badoi=bat[0].bDoorInsp, bawi=bat[0].bWindows, bawii=bat[0].bWindInsp, bapl=bat[0].bPlumbing,
				bapli=bat[0].bPlumInsp, baos=bat[0].bOutletSwitchFix, baosi=bat[0].bOuSFInsp, baef=bat[0].ExhaustFan, baefi=bat[0].ExFaInsp, stfb=stru[0].FoundBasement, 
				stfbi=stru[0].FoBaInsp, stwa=stru[0].sWalls, stwai=stru[0].sWallInsp, stco=stru[0].Columns, stcoi=stru[0].ColuInsp, stfl=stru[0].sFloors, stfli=stru[0].sFlooInsp,
				stce=stru[0].sCeiling, stcei=stru[0].sCeilInsp, stin=stru[0].sInsulation, stini=stru[0].sInsuInsp, stvr=stru[0].VaporRetarders, stvri=stru[0].VaReInsp, 
				stve=stru[0].sVentilation, stvei=stru[0].sVentInsp, pldw=plu[0].DrainWasteVent, pldwi=plu[0].DrWVInsp, plws=plu[0].H2OSupplyDist, plwsi=plu[0].HSDiInsp, 
				plhw=plu[0].HotWaterSupply, plhwi=plu[0].HWSuInsp, plmw=plu[0].MainShut, plmwi=plu[0].MaShInsp, plfs=plu[0].FuelStorDist, plfsi=plu[0].FSDiInsp, plmf=plu[0].FuelShut,
				plmfi=plu[0].FuShInsp, elsc=ele[0].EntrConductor, elsci=ele[0].EnCoInsp, elsg=ele[0].ServGroundOverMainPanel, elsgi=ele[0].SGOPInsp, elbc=ele[0].BranchEquip, 
				elbci=ele[0].BrEqInsp, eldf=ele[0].DevFix, eldfi=ele[0].DeFiInsp, elpg=ele[0].PolarityGround, elpgi=ele[0].PoGrInsp, elog=ele[0].OpGFCI, elogi=ele[0].GFCIInsp, 
				elsd=ele[0].SmokeDetect, elsdi=ele[0].SmDeInsp, elcm=ele[0].CarbMonDet, elcmi=ele[0].CaMoInsp, ellm=ele[0].LocatMainDistPan, ellmi=ele[0].LMDPInsp, 
				hvhe=hca[0].HeatEquip, hvhei=hca[0].HeEqInsp, hvno=hca[0].NormOpCont, hvnoi=hca[0].NOCoInsp, hvas=hca[0].AutoSafeCont, hvasi=hca[0].ASCoInsp, hvds=hca[0].DistSys,
				hvdsi=hca[0].DiSyInsp, hvcf=hca[0].ChimneyFlueVent, hvcfi=hca[0].CFVeInsp, hvsf=hca[0].SolidFuelHeatDev, hvsfi=hca[0].SFHDInsp, hvca=hca[0].CoolAirHandEq, 
				hvcai=hca[0].CAHEInsp, hvne=hca[0].NormOpEq, hvnei=hca[0].NOEqInsp)
				
			
			# Storage of newly entered report information using 'checked' variable as flag	
			elif request.method == "POST" and checked:

				# Report info
				RID = request.form['RID']
				Date = request.form['Date']
				UID = request.form['UID']
				reportData = {'RID': RID, 'Date': Date, 'UID': UID}
				
				# Address info
				requester = request.form['req']
				streetAddress = request.form['street']
				city = request.form['city']
				state = request.form['st']
				zipCode = request.form['zip']
				addressData = {'Requester': requester, 'StreetAddress': streetAddress, 'City': city, 'State': state, 'ZipCode': zipCode, 'RID':RID}
				
				# Roof & attic info
				roofCoverings = request.form['rarc']
				RCInsp = request.form.get('rarci')
				flashings = request.form['rafl']
				FlasInsp = request.form.get('rafli')
				skylightChimney = request.form['rasc']
				SkChInsp = request.form.get('rasci')
				aVentilation = request.form['rave']
				aVentInsp = request.form.get('ravei')
				aDrainage = request.form['radr']
				aDraiInsp = request.form.get('radri')
				structureAttic = request.form['raas']
				StAtInsp = request.form.get('raasi')
				fansThermostat = request.form['raft']
				FaThInsp = request.form.get('rafti')
				aInsulation = request.form['rain']
				aInsuInsp = request.form.get('raini')
				visibleWiring = request.form['ravw']
				ViWiInsp = request.form.get('ravwi')
				roofAtticData = {'RoofCoverings': roofCoverings, 'RCInsp': RCInsp, 'Flashings': flashings, 'FlasInsp': FlasInsp,
				'SkylightChimney': skylightChimney, 'SkChInsp': SkChInsp, 'aVentilation': aVentilation, 'aVentInsp': aVentInsp,
				'aDrainage': aDrainage, 'aDraiInsp': aDraiInsp, 'StructureAttic': structureAttic, 'StAtInsp': StAtInsp,
				'FansThermostat': fansThermostat, 'FaThInsp': FaThInsp, 'aInsulation': aInsulation, 'aInsuInsp': aInsuInsp,
				'VisibleWiring': visibleWiring, 'ViWiInsp': ViWiInsp, 'RID': RID}
				for item in roofAtticData:
					if roofAtticData[item] == None:
						roofAtticData[item] = False
				
				# Exterior info
				wallFlashTrim = request.form['exwf']
				WaFTInsp = request.form.get('exwfi')
				exDoors = request.form['exdo']
				exDoorInsp = request.form.get('exdoi')
				exWindows = request.form['exwi']
				exWindInsp = request.form.get('exwii')
				deckBalcSteps = request.form['exdb']
				DeBSInsp = request.form.get('exdbi')
				vegetDrainDriveWalk = request.form['exvd']
				VDDWInsp = request.form.get('exvdi')
				eavesFascia = request.form['exea']
				EaFaInsp = request.form.get('exeai')
				exPlumbing = request.form['expl']
				exPlumInsp = request.form.get('expli')
				outlets = request.form['exou']
				OutlInsp = request.form.get('exoui')
				exteriorData = {'WallFlashTrim': wallFlashTrim, 'WaFTInsp': WaFTInsp, 'exDoors': exDoors, 'exDoorInsp': exDoorInsp,
				'exWindows': exWindows, 'exWindInsp': exWindInsp, 'DeckBalcSteps': deckBalcSteps, 'DeBSInsp': DeBSInsp,
				'VegetDrainDriveWalk': vegetDrainDriveWalk, 'VDDWInsp': VDDWInsp, 'EavesFascia': eavesFascia, 'EaFaInsp': EaFaInsp,
				'exPlumbing': exPlumbing, 'exPlumInsp': exPlumInsp, 'Outlets': outlets, 'OutlInsp': OutlInsp, 'RID': RID}
				for item in exteriorData:
					if exteriorData[item] == None:
						exteriorData[item] = False

				# Garage info		
				gCeiling = request.form['gace']
				gCeilInsp = request.form.get('gacei')
				gWalls = request.form['gawa']
				gWallInsp = request.form.get('gawai')
				gFloor = request.form['gafl']
				gFlooInsp = request.form.get('gafli')
				gDoor = request.form['gado']
				gDoorInsp = request.form.get('gadoi')
				innerDoor = request.form['gadg']
				InDoInsp = request.form.get('gadgi')
				gDOperator = request.form['gaop']
				GDOpInsp = request.form.get('gaopi')
				garageData = {'gCeiling': gCeiling, 'gCeilInsp': gCeilInsp, 'gWalls': gWalls, 'gWallInsp': gWallInsp,
				'gFloor': gFloor, 'gFlooInsp': gFlooInsp, 'gDoor': gDoor, 'gDoorInsp': gDoorInsp,
				'InnerDoor': innerDoor, 'InDoInsp': InDoInsp, 'GDOperator': gDOperator, 'GDOpInsp': GDOpInsp, 'RID': RID}
				for item in garageData:
					if garageData[item] == None:
						garageData[item] = False
				
				# Kitchen info
				kCeiling = request.form['kice']
				kCeilInsp = request.form.get('kicei')
				kWalls = request.form['kiwa']
				kWallInsp = request.form.get('kiwai')
				kFloor = request.form['kifl']
				kFlooInsp = request.form.get('kifli')
				pantryDoor = request.form['kipd']
				PaDoInsp = request.form.get('kipdi')
				kWindows = request.form['kiwi']
				kWindInsp = request.form.get('kiwii')
				kCountersCabinets = request.form['kicc']
				kCoCaInsp = request.form.get('kicci')
				kPlumbing = request.form['kipl']
				kPlumInsp = request.form.get('kipli')
				kOutletSwitchFix = request.form['kios']
				kOuSFInsp = request.form.get('kiosi')
				dishWash = request.form['kidi']
				DishInsp = request.form.get('kidii')
				rangeOven = request.form['kiro']
				RaOvInsp = request.form.get('kiroi')
				microwave = request.form['kimi']
				MicrInsp = request.form.get('kimii')
				kitchenData = {'kCeiling': kCeiling, 'kCeilInsp': kCeilInsp, 'kWalls': kWalls, 'kWallInsp': kWallInsp,
				'kFloor': kFloor, 'kFlooInsp': kFlooInsp, 'PantryDoor': pantryDoor, 'PaDoInsp': PaDoInsp,
				'kWindows': kWindows, 'kWindInsp': kWindInsp, 'kCountersCabinets': kCountersCabinets, 'kCoCaInsp': kCoCaInsp,
				'kPlumbing': kPlumbing, 'kPlumInsp': kPlumInsp, 'kOutletSwitchFix': kOutletSwitchFix, 'kOuSFInsp': kOuSFInsp,
				'Dishwash': dishWash, 'DishInsp': DishInsp, 'RangeOven': rangeOven, 'RaOvInsp': RaOvInsp,
				'Microwave': microwave, 'MicrInsp': MicrInsp, 'RID': RID}
				for item in kitchenData:
					if kitchenData[item] == None:
						kitchenData[item] = False
				
				# Rooms info
				rCeiling = request.form['roce']
				rCeilInsp = request.form.get('rocei')
				rWalls = request.form['rowa']
				rWallInsp = request.form.get('rowai')
				rFloor = request.form['rofl']
				rFlooInsp = request.form.get('rofli')
				stairRailBalc = request.form['rosb']
				SRBaInsp = request.form.get('rosbi')
				rDoor = request.form['rodo']
				rDoorInsp = request.form.get('rodoi')
				rWindows = request.form['rowi']
				rWindInsp = request.form.get('rowii')
				rOutletSwitchFix = request.form['roos']
				rOuSFInsp = request.form.get('roosi')
				roomsData = {'rCeiling': rCeiling, 'rCeilInsp': rCeilInsp, 'rWalls': rWalls, 'rWallInsp': rWallInsp,
				'rFloor': rFloor, 'rFlooInsp': rFlooInsp, 'StairRailBalc': stairRailBalc, 'SRBaInsp': SRBaInsp,
				'rDoor': rDoor, 'rDoorInsp': rDoorInsp, 'rWindows': rWindows, 'rWindInsp': rWindInsp,
				'rOutletSwitchFix': rOutletSwitchFix, 'rOuSFInsp': rOuSFInsp, 'RID': RID}
				for item in roomsData:
					if roomsData[item] == None:
						roomsData[item] = False

				# Bathrooms info		
				counterCabinet = request.form['bacc']
				bCoCaInsp = request.form.get('bacci')
				bDoor = request.form['bado']
				bDoorInsp = request.form.get('badoi')
				bWindows = request.form['bawi']
				bWindInsp = request.form.get('bawii')
				bPlumbing = request.form['bapl']
				bPlumInsp = request.form.get('bapli')
				bOutletSwitchFix = request.form['baos']
				bOuSFInsp = request.form.get('baosi')
				exhaustFan = request.form['baef']
				ExFaInsp = request.form.get('baefi')
				bathroomsData = {'CounterCabinet': counterCabinet, 'bCoCaInsp': bCoCaInsp, 'bDoor': bDoor, 'bDoorInsp': bDoorInsp,
				'bWindows': bWindows, 'bWindInsp': bWindInsp, 'bPlumbing': bPlumbing, 'bPlumInsp': bPlumInsp,
				'bOutletSwitchFix': bOutletSwitchFix, 'bOuSFInsp': bOuSFInsp, 'ExhaustFan': exhaustFan, 'ExFaInsp': ExFaInsp, 'RID': RID}
				for item in bathroomsData:
					if bathroomsData[item] == None:
						bathroomsData[item] = False
				
				# Structure info
				foundBasement = request.form['stfb']
				FoBaInsp = request.form.get('stfbi')
				sWalls = request.form['stwa']
				sWallInsp = request.form.get('stwai')
				columns = request.form['stco']
				ColuInsp = request.form.get('stcoi')
				sFloors = request.form['stfl']
				sFlooInsp = request.form.get('stfli')
				sCeiling = request.form['stce']
				sCeilInsp = request.form.get('stcei')
				sInsulation = request.form['stin']
				sInsuInsp = request.form.get('stini')
				vaporRetarders = request.form['stvr']
				VaReInsp = request.form.get('stvri')
				sVentilation = request.form['stve']
				sVentInsp = request.form.get('stvei')
				structureData = {'FoundBasement': foundBasement, 'FoBaInsp': FoBaInsp, 'sWalls': sWalls, 'sWallInsp': sWallInsp,
				'Columns': columns, 'ColuInsp': ColuInsp, 'sFloors': sFloors, 'sFlooInsp': sFlooInsp,
				'sCeiling': sCeiling, 'sCeilInsp': sCeilInsp, 'sInsulation': sInsulation, 'sInsuInsp': sInsuInsp,
				'VaporRetarders': vaporRetarders, 'VaReInsp': VaReInsp, 'sVentilation': sVentilation, 'sVentInsp': sVentInsp, 'RID': RID}
				for item in structureData:
					if structureData[item] == None:
						structureData[item] = False
				
				# Plumbing info
				drainWasteVent = request.form['pldw']
				DrWVInsp = request.form.get('pldwi')
				h2OSupplyDist = request.form['plws']
				HSDiInsp = request.form.get('plwsi')
				hotWaterSupply = request.form['plhw']
				HWSuInsp = request.form.get('plhwi')
				mainShut = request.form['plmw']
				MaShInsp = request.form.get('plmwi')
				fuelStorDist = request.form['plfs']
				FSDiInsp = request.form.get('plfsi')
				fuelShut = request.form['plmf']
				FuShInsp = request.form.get('plmfi')
				plumbingData = {'DrainWasteVent': drainWasteVent, 'DrWVInsp': DrWVInsp, 'H2OSupplyDist': h2OSupplyDist, 'HSDiInsp': HSDiInsp,
				'HotWaterSupply': hotWaterSupply, 'HWSuInsp': HWSuInsp, 'MainShut': mainShut, 'MaShInsp': MaShInsp,
				'FuelStorDist': fuelStorDist, 'FSDiInsp': FSDiInsp, 'FuelShut': fuelShut, 'FuShInsp': FuShInsp, 'RID': RID}
				for item in plumbingData:
					if plumbingData[item] == None:
						plumbingData[item] = False
				
				# Electrical info
				entrConductor = request.form['elsc']
				EnCoInsp = request.form.get('elsci')
				servGroundOverMainPanel = request.form['elsg']
				SGOPInsp = request.form.get('elsgi')
				branchEquip = request.form['elbc']
				BrEqInsp = request.form.get('elbci')
				devFix = request.form['eldf']
				DeFiInsp = request.form.get('eldfi')
				polarityGround = request.form['elpg']
				PoGrInsp = request.form.get('elpgi')
				opGFCI = request.form['elog']
				GFCIInsp = request.form.get('elogi')
				smokeDetect = request.form['elsd']
				SmDeInsp = request.form.get('elsdi')
				carbMonDet = request.form['elcm']
				CaMoInsp = request.form.get('elcmi')
				locatMainDistPan = request.form['ellm']
				LMDPInsp = request.form.get('ellmi')
				electricalData = {'EntrConductor': entrConductor, 'EnCoInsp': EnCoInsp, 'ServGroundOverMainPanel': servGroundOverMainPanel, 'SGOPInsp': SGOPInsp,
				'BranchEquip': branchEquip, 'BrEqInsp': BrEqInsp, 'DevFix': devFix, 'DeFiInsp': DeFiInsp,
				'PolarityGround': polarityGround, 'PoGrInsp': PoGrInsp, 'OpGFCI': opGFCI, 'GFCIInsp': GFCIInsp,
				'SmokeDetect': smokeDetect, 'SmDeInsp': SmDeInsp, 'CarbMonDet': carbMonDet, 'CaMoInsp': CaMoInsp,
				'LocatMainDistPan': locatMainDistPan, 'LMDPInsp': LMDPInsp, 'RID': RID}
				for item in electricalData:
					if electricalData[item] == None:
						electricalData[item] = False
				
				# Heating & central air info
				heatEquip = request.form['hvhe']
				HeEqInsp = request.form.get('hvhei')
				normOpCont = request.form['hvno']
				NOCoInsp = request.form.get('hvnoi')
				autoSafeCont = request.form['hvas']
				ASCoInsp = request.form.get('hvasi')
				distSys = request.form['hvds']
				DiSyInsp = request.form.get('hvdsi')
				chimneyFlueVent = request.form['hvcf']
				CFVeInsp = request.form.get('hvcfi')
				solidFuelHeatDev = request.form['hvsf']
				SFHDInsp = request.form.get('hvsfi')
				coolAirHandEq = request.form['hvca']
				CAHEInsp = request.form.get('hvcai')
				normOpEq = request.form['hvne']
				NOEqInsp = request.form.get('hvnei')
				heatCentAirData = {'HeatEquip': heatEquip, 'HeEqInsp': HeEqInsp, 'NormOpCont': normOpCont, 'NOCoInsp': NOCoInsp,
				'AutoSafeCont': autoSafeCont, 'ASCoInsp': ASCoInsp, 'DistSys': distSys, 'DiSyInsp': DiSyInsp,
				'ChimneyFlueVent': chimneyFlueVent, 'CFVeInsp': CFVeInsp, 'SolidFuelHeatDev': solidFuelHeatDev, 'SFHDInsp': SFHDInsp,
				'CoolAirHandEq': coolAirHandEq, 'CAHEInsp': CAHEInsp, 'NormOpEq': normOpEq, 'NOEqInsp': NOEqInsp, 'RID': RID}
				for item in heatCentAirData:
					if heatCentAirData[item] == None:
						heatCentAirData[item] = False
				
				# get_model() used to access database and store new information
				get_model().updateReport(addressData, roofAtticData, exteriorData, garageData, kitchenData, 
				roomsData, bathroomsData, structureData, plumbingData, electricalData, heatCentAirData)
				flash('Report %s updated!' % RID)
				return redirect(url_for('Edit'))
			
			# Validates report ID entered for editing
			if request.method == "POST" and repform.RID.data not in idList:
				flash('Please enter a valid report ID number to search for.')
				return redirect(url_for('Edit'))
			
			else:
				return render_template("edit.html", form=repform)
				
		except Exception as e:
			flash('Please enter a valid report ID number to search for')
			return(str(e))
		gc.collect()		
		return render_template("edit.html", form=repform)
	
	# Validates all information entered in forms when writing initial report (length, format, etc.)
	def formValidator(allForms):
		count = 0
		for form in allForms:
			if form.validate():
				count +=1
		if count == len(allForms):
			return True
		else:
			return False
	
	# Returns all forms necessary for writing home insection report
	def getReportForms():
		allReports = []
		reportForm = rf.ReportForm(request.form)
		allReports.append(reportForm)
		addressForm = rf.AddressForm(request.form)
		allReports.append(addressForm)
		roofAtticForm = rf.RoofAtticForm(request.form)
		allReports.append(roofAtticForm)
		garageForm = rf.GarageForm(request.form)
		allReports.append(garageForm)
		kitchenForm = rf.KitchenForm(request.form)
		allReports.append(kitchenForm)
		roomsForm = rf.RoomsForm(request.form)
		allReports.append(roomsForm)
		bathroomsForm = rf.BathroomsForm(request.form)
		allReports.append(bathroomsForm)
		structureForm = rf.StructureForm(request.form)
		allReports.append(structureForm)
		plumbingForm = rf.PlumbingForm(request.form)
		allReports.append(plumbingForm)
		electricalForm = rf.ElectricalForm(request.form)
		allReports.append(electricalForm)
		exteriorForm = rf.ExteriorForm(request.form)
		allReports.append(exteriorForm)
		heatCentAirForm = rf.HeatCentAirForm(request.form)
		allReports.append(heatCentAirForm)
		
		return allReports
	
	# Rendering of report writing page, if method = 'POST' all entered 
	# information validated and stored in database via get_model() method
	@app.route('/Write/', methods = ['GET', 'POST'])
	@login_required
	def Writes():
		userInfo = get_model().retrieveLoginInfo(session["username"])
		nextRID = get_model().getReportInfo()[-1].RID
		
		try:
			allReports = getReportForms()
			reportForm = allReports[0]
			addressForm = allReports[1]
			roofAtticForm = allReports[2]
			garageForm = allReports[3]
			kitchenForm = allReports[4]
			roomsForm = allReports[5]
			bathroomsForm = allReports[6]
			structureForm = allReports[7]
			plumbingForm = allReports[8]
			electricalForm = allReports[9]
			exteriorForm = allReports[10]
			heatCentAirForm = allReports[11]
			
			
			
			if request.method == "POST" and formValidator(allReports):
				
				# Collection of report info
				RID = reportForm.RID.data
				Date = reportForm.Date.data
				UID = reportForm.UID.data
				reportData = {'RID': RID, 'Date': Date, 'UID': UID}
				
				# Collection of address info
				requester = addressForm.Requester.data
				streetAddress = addressForm.StreetAddress.data
				city = addressForm.City.data
				state = addressForm.State.data
				zipCode = addressForm.ZipCode.data
				addressData = {'Requester': requester, 'StreetAddress': streetAddress, 'City': city, 'State': state, 'ZipCode': zipCode, 'RID':RID}
				
				# Collection of roof & attic info
				roofCoverings = roofAtticForm.RoofCoverings.data
				RCInsp = roofAtticForm.RCInsp.data
				flashings = roofAtticForm.Flashings.data
				FlasInsp = roofAtticForm.FlasInsp.data
				skylightChimney = roofAtticForm.SkylightChimney.data
				SkChInsp = roofAtticForm.SkChInsp.data
				aVentilation = roofAtticForm.aVentilation.data
				aVentInsp = roofAtticForm.aVentInsp.data
				aDrainage = roofAtticForm.aDrainage.data
				aDraiInsp = roofAtticForm.aDraiInsp.data
				structureAttic = roofAtticForm.StructureAttic.data
				StAtInsp = roofAtticForm.StAtInsp.data
				fansThermostat = roofAtticForm.FansThermostat.data
				FaThInsp = roofAtticForm.FaThInsp.data
				aInsulation = roofAtticForm.aInsulation.data
				aInsuInsp = roofAtticForm.aInsuInsp.data
				visibleWiring = roofAtticForm.VisibleWiring.data
				ViWiInsp = roofAtticForm.ViWiInsp.data
				roofAtticData = {'RoofCoverings': roofCoverings, 'RCInsp': RCInsp, 'Flashings': flashings, 'FlasInsp': FlasInsp,
				'SkylightChimney': skylightChimney, 'SkChInsp': SkChInsp, 'aVentilation': aVentilation, 'aVentInsp': aVentInsp,
				'aDrainage': aDrainage, 'aDraiInsp': aDraiInsp, 'StructureAttic': structureAttic, 'StAtInsp': StAtInsp,
				'FansThermostat': fansThermostat, 'FaThInsp': FaThInsp, 'aInsulation': aInsulation, 'aInsuInsp': aInsuInsp,
				'VisibleWiring': visibleWiring, 'ViWiInsp': ViWiInsp, 'RID': RID}
				
				# Collection of exterior info
				wallFlashTrim = exteriorForm.WallFlashTrim.data
				WaFTInsp = exteriorForm.WaFTInsp.data
				exDoors = exteriorForm.exDoors.data
				exDoorInsp = exteriorForm.exDoorInsp.data
				exWindows = exteriorForm.exWindows.data
				exWindInsp = exteriorForm.exWindInsp.data
				deckBalcSteps = exteriorForm.DeckBalcSteps.data
				DeBSInsp = exteriorForm.DeBSInsp.data
				vegetDrainDriveWalk = exteriorForm.VegetDrainDriveWalk.data
				VDDWInsp = exteriorForm.VDDWInsp.data
				eavesFascia = exteriorForm.EavesFascia.data
				EaFaInsp = exteriorForm.EaFaInsp.data
				exPlumbing = exteriorForm.exPlumbing.data
				exPlumInsp = exteriorForm.exPlumInsp.data
				outlets = exteriorForm.Outlets.data
				OutlInsp = exteriorForm.OutlInsp.data
				exteriorData = {'WallFlashTrim': wallFlashTrim, 'WaFTInsp': WaFTInsp, 'exDoors': exDoors, 'exDoorInsp': exDoorInsp,
				'exWindows': exWindows, 'exWindInsp': exWindInsp, 'DeckBalcSteps': deckBalcSteps, 'DeBSInsp': DeBSInsp,
				'VegetDrainDriveWalk': vegetDrainDriveWalk, 'VDDWInsp': VDDWInsp, 'EavesFascia': eavesFascia, 'EaFaInsp': EaFaInsp,
				'exPlumbing': exPlumbing, 'exPlumInsp': exPlumInsp, 'Outlets': outlets, 'OutlInsp': OutlInsp, 'RID': RID}
				
				# Collection of garage info
				gCeiling = garageForm.gCeiling.data
				gCeilInsp = garageForm.gCeilInsp.data
				gWalls = garageForm.gWalls.data
				gWallInsp = garageForm.gWallInsp.data
				gFloor = garageForm.gFloor.data
				gFlooInsp = garageForm.gFlooInsp.data
				gDoor = garageForm.gDoor.data
				gDoorInsp = garageForm.gDoorInsp.data
				innerDoor = garageForm.InnerDoor.data
				InDoInsp = garageForm.InDoInsp.data
				gDOperator = garageForm.GDOperator.data
				GDOpInsp = garageForm.GDOpInsp.data
				garageData = {'gCeiling': gCeiling, 'gCeilInsp': gCeilInsp, 'gWalls': gWalls, 'gWallInsp': gWallInsp,
				'gFloor': gFloor, 'gFlooInsp': gFlooInsp, 'gDoor': gDoor, 'gDoorInsp': gDoorInsp,
				'InnerDoor': innerDoor, 'InDoInsp': InDoInsp, 'GDOperator': gDOperator, 'GDOpInsp': GDOpInsp, 'RID': RID}
				
				# Collection of kitchen info
				kCeiling = kitchenForm.kCeiling.data
				kCeilInsp = kitchenForm.kCeilInsp.data
				kWalls = kitchenForm.kWalls.data
				kWallInsp = kitchenForm.kWallInsp.data
				kFloor = kitchenForm.kFloor.data
				kFlooInsp = kitchenForm.kFlooInsp.data
				pantryDoor = kitchenForm.PantryDoor.data
				PaDoInsp = kitchenForm.PaDoInsp.data
				kWindows = kitchenForm.kWindows.data
				kWindInsp = kitchenForm.kWindInsp.data
				kCountersCabinets = kitchenForm.kCountersCabinets.data
				kCoCaInsp = kitchenForm.kCoCaInsp.data
				kPlumbing = kitchenForm.kPlumbing.data
				kPlumInsp = kitchenForm.kPlumInsp.data
				kOutletSwitchFix = kitchenForm.kOutletSwitchFix.data
				kOuSFInsp = kitchenForm.kOuSFInsp.data
				dishWash = kitchenForm.Dishwash.data
				DishInsp = kitchenForm.DishInsp.data
				rangeOven = kitchenForm.RangeOven.data
				RaOvInsp = kitchenForm.RaOvInsp.data
				microwave = kitchenForm.Microwave.data
				MicrInsp = kitchenForm.MicrInsp.data
				kitchenData = {'kCeiling': kCeiling, 'kCeilInsp': kCeilInsp, 'kWalls': kWalls, 'kWallInsp': kWallInsp,
				'kFloor': kFloor, 'kFlooInsp': kFlooInsp, 'PantryDoor': pantryDoor, 'PaDoInsp': PaDoInsp,
				'kWindows': kWindows, 'kWindInsp': kWindInsp, 'kCountersCabinets': kCountersCabinets, 'kCoCaInsp': kCoCaInsp,
				'kPlumbing': kPlumbing, 'kPlumInsp': kPlumInsp, 'kOutletSwitchFix': kOutletSwitchFix, 'kOuSFInsp': kOuSFInsp,
				'Dishwash': dishWash, 'DishInsp': DishInsp, 'RangeOven': rangeOven, 'RaOvInsp': RaOvInsp,
				'Microwave': microwave, 'MicrInsp': MicrInsp, 'RID': RID}
				
				# Collection of rooms info
				rCeiling = roomsForm.rCeiling.data
				rCeilInsp = roomsForm.rCeilInsp.data
				rWalls = roomsForm.rWalls.data
				rWallInsp = roomsForm.rWallInsp.data
				rFloor = roomsForm.rFloor.data
				rFlooInsp = roomsForm.rFlooInsp.data
				stairRailBalc = roomsForm.StairRailBalc.data
				SRBaInsp = roomsForm.SRBaInsp.data
				rDoor = roomsForm.rDoor.data
				rDoorInsp = roomsForm.rDoorInsp.data
				rWindows = roomsForm.rWindows.data
				rWindInsp = roomsForm.rWindInsp.data
				rOutletSwitchFix = roomsForm.rOutletSwitchFix.data
				rOuSFInsp = roomsForm.rOuSFInsp.data
				roomsData = {'rCeiling': rCeiling, 'rCeilInsp': rCeilInsp, 'rWalls': rWalls, 'rWallInsp': rWallInsp,
				'rFloor': rFloor, 'rFlooInsp': rFlooInsp, 'StairRailBalc': stairRailBalc, 'SRBaInsp': SRBaInsp,
				'rDoor': rDoor, 'rDoorInsp': rDoorInsp, 'rWindows': rWindows, 'rWindInsp': rWindInsp,
				'rOutletSwitchFix': rOutletSwitchFix, 'rOuSFInsp': rOuSFInsp, 'RID': RID}
				
				# Collection of bathrooms info
				counterCabinet = bathroomsForm.CounterCabinet.data
				bCoCaInsp = bathroomsForm.bCoCaInsp.data
				bDoor = bathroomsForm.bDoor.data
				bDoorInsp = bathroomsForm.bDoorInsp.data
				bWindows = bathroomsForm.bWindows.data
				bWindInsp = bathroomsForm.bWindInsp.data
				bPlumbing = bathroomsForm.bPlumbing.data
				bPlumInsp = bathroomsForm.bPlumInsp.data
				bOutletSwitchFix = bathroomsForm.bOutletSwitchFix.data
				bOuSFInsp = bathroomsForm.bOuSFInsp.data
				exhaustFan = bathroomsForm.ExhaustFan.data
				ExFaInsp = bathroomsForm.ExFaInsp.data
				bathroomsData = {'CounterCabinet': counterCabinet, 'bCoCaInsp': bCoCaInsp, 'bDoor': bDoor, 'bDoorInsp': bDoorInsp,
				'bWindows': bWindows, 'bWindInsp': bWindInsp, 'bPlumbing': bPlumbing, 'bPlumInsp': bPlumInsp,
				'bOutletSwitchFix': bOutletSwitchFix, 'bOuSFInsp': bOuSFInsp, 'ExhaustFan': exhaustFan, 'ExFaInsp': ExFaInsp, 'RID': RID}
				
				# Collection of structure info
				foundBasement = structureForm.FoundBasement.data
				FoBaInsp = structureForm.FoBaInsp.data
				sWalls = structureForm.sWalls.data
				sWallInsp = structureForm.sWallInsp.data
				columns = structureForm.Columns.data
				ColuInsp = structureForm.ColuInsp.data
				sFloors = structureForm.sFloors.data
				sFlooInsp = structureForm.sFlooInsp.data
				sCeiling = structureForm.sCeiling.data
				sCeilInsp = structureForm.sCeilInsp.data
				sInsulation = structureForm.sInsulation.data
				sInsuInsp = structureForm.sInsuInsp.data
				vaporRetarders = structureForm.VaporRetarders.data
				VaReInsp = structureForm.VaReInsp.data
				sVentilation = structureForm.sVentilation.data
				sVentInsp = structureForm.sVentInsp.data
				structureData = {'FoundBasement': foundBasement, 'FoBaInsp': FoBaInsp, 'sWalls': sWalls, 'sWallInsp': sWallInsp,
				'Columns': columns, 'ColuInsp': ColuInsp, 'sFloors': sFloors, 'sFlooInsp': sFlooInsp,
				'sCeiling': sCeiling, 'sCeilInsp': sCeilInsp, 'sInsulation': sInsulation, 'sInsuInsp': sInsuInsp,
				'VaporRetarders': vaporRetarders, 'VaReInsp': VaReInsp, 'sVentilation': sVentilation, 'sVentInsp': sVentInsp, 'RID': RID}
				
				# Collection of plumbing info
				drainWasteVent = plumbingForm.DrainWasteVent.data
				DrWVInsp = plumbingForm.DrWVInsp.data
				h2OSupplyDist = plumbingForm.H2OSupplyDist.data
				HSDiInsp = plumbingForm.HSDiInsp.data
				hotWaterSupply = plumbingForm.HotWaterSupply.data
				HWSuInsp = plumbingForm.HWSuInsp.data
				mainShut = plumbingForm.MainShut.data
				MaShInsp = plumbingForm.MaShInsp.data
				fuelStorDist = plumbingForm.FuelStorDist.data
				FSDiInsp = plumbingForm.FSDiInsp.data
				fuelShut = plumbingForm.FuelShut.data
				FuShInsp = plumbingForm.FuShInsp.data
				plumbingData = {'DrainWasteVent': drainWasteVent, 'DrWVInsp': DrWVInsp, 'H2OSupplyDist': h2OSupplyDist, 'HSDiInsp': HSDiInsp,
				'HotWaterSupply': hotWaterSupply, 'HWSuInsp': HWSuInsp, 'MainShut': mainShut, 'MaShInsp': MaShInsp,
				'FuelStorDist': fuelStorDist, 'FSDiInsp': FSDiInsp, 'FuelShut': fuelShut, 'FuShInsp': FuShInsp, 'RID': RID}
				
				# Collection of electrical info
				entrConductor = electricalForm.EntrConductor.data
				EnCoInsp = electricalForm.EnCoInsp.data
				servGroundOverMainPanel = electricalForm.ServGroundOverMainPanel.data
				SGOPInsp = electricalForm.SGOPInsp.data
				branchEquip = electricalForm.BranchEquip.data
				BrEqInsp = electricalForm.BrEqInsp.data
				devFix = electricalForm.DevFix.data
				DeFiInsp = electricalForm.DeFiInsp.data
				polarityGround = electricalForm.PolarityGround.data
				PoGrInsp = electricalForm.PoGrInsp.data
				opGFCI = electricalForm.OpGFCI.data
				GFCIInsp = electricalForm.GFCIInsp.data
				smokeDetect = electricalForm.SmokeDetect.data
				SmDeInsp = electricalForm.SmDeInsp.data
				carbMonDet = electricalForm.CarbMonDet.data
				CaMoInsp = electricalForm.CaMoInsp.data
				locatMainDistPan = electricalForm.LocatMainDistPan.data
				LMDPInsp = electricalForm.LMDPInsp.data
				electricalData = {'EntrConductor': entrConductor, 'EnCoInsp': EnCoInsp, 'ServGroundOverMainPanel': servGroundOverMainPanel, 'SGOPInsp': SGOPInsp,
				'BranchEquip': branchEquip, 'BrEqInsp': BrEqInsp, 'DevFix': devFix, 'DeFiInsp': DeFiInsp,
				'PolarityGround': polarityGround, 'PoGrInsp': PoGrInsp, 'OpGFCI': opGFCI, 'GFCIInsp': GFCIInsp,
				'SmokeDetect': smokeDetect, 'SmDeInsp': SmDeInsp, 'CarbMonDet': carbMonDet, 'CaMoInsp': CaMoInsp,
				'LocatMainDistPan': locatMainDistPan, 'LMDPInsp': LMDPInsp, 'RID': RID}
				
				# Collection of heating & central air info
				heatEquip = heatCentAirForm.HeatEquip.data
				HeEqInsp = heatCentAirForm.HeEqInsp.data
				normOpCont = heatCentAirForm.NormOpCont.data
				NOCoInsp = heatCentAirForm.NOCoInsp.data
				autoSafeCont = heatCentAirForm.AutoSafeCont.data
				ASCoInsp = heatCentAirForm.ASCoInsp.data
				distSys = heatCentAirForm.DistSys.data
				DiSyInsp = heatCentAirForm.DiSyInsp.data
				chimneyFlueVent = heatCentAirForm.ChimneyFlueVent.data
				CFVeInsp = heatCentAirForm.CFVeInsp.data
				solidFuelHeatDev = heatCentAirForm.SolidFuelHeatDev.data
				SFHDInsp = heatCentAirForm.SFHDInsp.data
				coolAirHandEq = heatCentAirForm.CoolAirHandEq.data
				CAHEInsp = heatCentAirForm.CAHEInsp.data
				normOpEq = heatCentAirForm.NormOpEq.data
				NOEqInsp = heatCentAirForm.NOEqInsp.data
				heatCentAirData = {'HeatEquip': heatEquip, 'HeEqInsp': HeEqInsp, 'NormOpCont': normOpCont, 'NOCoInsp': NOCoInsp,
				'AutoSafeCont': autoSafeCont, 'ASCoInsp': ASCoInsp, 'DistSys': distSys, 'DiSyInsp': DiSyInsp,
				'ChimneyFlueVent': chimneyFlueVent, 'CFVeInsp': CFVeInsp, 'SolidFuelHeatDev': solidFuelHeatDev, 'SFHDInsp': SFHDInsp,
				'CoolAirHandEq': coolAirHandEq, 'CAHEInsp': CAHEInsp, 'NormOpEq': normOpEq, 'NOEqInsp': NOEqInsp, 'RID': RID}
				
				# Call to pdfWriter() sends necessary information to be written 
				# to pdf version of report, 
				fileExt = pdfWriter(reportData, addressData, roofAtticData)
				
				# Stores all report information in database
				get_model().createReport(reportData, addressData, roofAtticData, exteriorData, garageData, kitchenData, 
				roomsData, bathroomsData, structureData, plumbingData, electricalData, heatCentAirData)
				flash('Report successfully submitted with a report ID of %s! \n Please save or print for your records.' % (RID))
				
				gc.collect()
				return render_template('pdf.html', fileExt=fileExt)
								
			else:
				return render_template('write.html', roform = roomsForm, bform = bathroomsForm, sform = structureForm, pform = plumbingForm, 
				elform = electricalForm, hcaform = heatCentAirForm, gform = garageForm, kform = kitchenForm, exform = exteriorForm, 
				raform = roofAtticForm, aform=addressForm, rform=reportForm, uid=userInfo.uid, rid=nextRID + 1)
				
		except Exception as e:
			return(str(e))
	
	# Receives information to create pdf, creates it, and returns file extension in order to 
	# returns file extension for eventual storage
	def pdfWriter(reportData, addressData, roofAtticData):
		c=None
		currentDay = datetime.date
		dir = os.path.dirname(__file__)
		folderName = dir + '\\static\\reports'
		fileString = str(reportData['Date']) + '_' + str(reportData['UID']) + '_' + str(reportData['RID']) + '.pdf'
		fileName = os.path.join(folderName, fileString)
		#fileName = "C:\\Users\\Ian\\AppData\\Local\\Google\\Cloud SDK\\website\\website\\static\\reports\\" + str(reportData['Date']) + '_' + str(reportData['UID']) + '_' + str(reportData['RID']) + '.pdf'
		
		# Creates canvas object for writing pdf
		c = canvas.Canvas(fileName, pagesize=letter)
		logo = dir + '\\static\\CleanRoadRunner.png'
		c.drawImage(logo, 222, 700, width=160, height=80, mask='auto')
		c.drawString(30,750,'Sacred Ground')
		c.drawString(30,735,'Real Estate')
		c.line(15,732,120,732)
		c.drawString(500,735, str(reportData['Date']))
		c.line(480,732,580,732)
		
		c.drawString(115, 650, 'Customer: %s        Address: %s, %s, %s %s' % (addressData['Requester'], addressData['StreetAddress'], 
		addressData['City'], addressData['State'], addressData['ZipCode']))
		c.line(105, 647, 545, 647)

		c.drawString(40, 603, 'Roof & Attic Information-')
		c.line(35, 600, 175, 600)
		
		c.drawString(50, 580, 'Roof Coverings: %s' % roofAtticData['RoofCoverings'])
		c.drawString(430, 580, 'Inspected: %s' % roofAtticData['RCInsp'])
		c.drawString(50, 560, 'Flashings: %s' % roofAtticData['Flashings'])
		c.drawString(430, 560, 'Inspected: %s' % roofAtticData['FlasInsp'])
		c.drawString(50, 540, 'Skylight & Chimney: %s' % roofAtticData['SkylightChimney'])
		c.drawString(430, 540, 'Inspected: %s' % roofAtticData['SkChInsp'])
		c.drawString(50, 520, 'Ventilation: %s' % roofAtticData['aVentilation'])
		c.drawString(430, 520, 'Inspected: %s' % roofAtticData['aVentInsp'])
		c.drawString(50, 500, 'Drainage: %s' % roofAtticData['aDrainage'])
		c.drawString(430, 500, 'Inspected: %s' % roofAtticData['aDraiInsp'])
		c.drawString(50, 480, 'Attic Structure: %s' % roofAtticData['StructureAttic'])
		c.drawString(430, 480, 'Inspected: %s' % roofAtticData['StAtInsp'])
		c.drawString(50, 460, 'Fans & Thermostat: %s' % roofAtticData['FansThermostat'])
		c.drawString(430, 460, 'Inspected: %s' % roofAtticData['FaThInsp'])
		c.drawString(50, 440, 'Insulation: %s' % roofAtticData['aInsulation'])
		c.drawString(430, 440, 'Inspected: %s' % roofAtticData['aInsuInsp'])
		c.drawString(50, 420, 'Visible Wiring: %s' % roofAtticData['VisibleWiring'])
		c.drawString(430, 420, 'Inspected: %s' % roofAtticData['ViWiInsp'])

		c.save()
		c.showPage()
			
		fileTokens = fileName.split('\\')
		fileExt = fileTokens[-2:]
		fileExt = fileExt[0] + '/' + fileExt[1]
		c=None
		
		return fileExt
		
	return app
	
	
# Initializes model for connection to Google Cloud SQL instance 	
def get_model():
		model_backend = current_app.config['DATA_BACKEND']
		if model_backend == 'cloudsql':
			from . import model_cloudsql
			model = model_cloudsql
		elif model_backend == 'datastore':
			from . import model_datastore
			model = model_datastore
		elif model_backend == 'mongodb':
			from . import model_mongodb
			model = model_mongodb
		else:
			raise ValueError(
				"No appropriate databackend configured. "
				"Please specify datastore, cloudsql, or mongodb")

		return model