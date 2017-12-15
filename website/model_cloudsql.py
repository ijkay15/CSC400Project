# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['uid'] = row.uid
    data.pop('_sa_instance_state')
    return data


# [START model]
class User(db.Model):
    __tablename__ = 'users'

    uid = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique = True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(50))
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    

    def __repr__(self):
        return "<User(uid='%s', username='%s', password='%s', email='%s', firstname='%s', lastname='%s')>" \
		% (self.uid, self.username, self.password, self.email, self.firstname, self.lastname)
# [END model]

# [START model]
class Report(db.Model):
    __tablename__ = 'Reports'

    RID = db.Column(db.Integer, unique = True, primary_key=True)
    Date = db.Column(db.Date)
    UID = db.Column(db.Integer())    

    def __repr__(self):
        return "<Report(RID='%s', Date='%s', UID='%s')>" \
		% (self.RID, self.Date, self.UID)
# [END model]

# [START model]
class Address(db.Model):
	__tablename__ = 'Address'
	
	AID = db.Column(db.Integer, unique = True, primary_key=True)
	City = db.Column(db.String(20))
	State = db.Column(db.String(2))
	ZipCode = db.Column(db.String(5))
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	StreetAddress = db.Column(db.String(50))
	Requester = db.Column(db.String(30))
    
	def __repr__(self):
		return "<Address(AID='%s', City='%s', State='%s', ZipCode='%s', RID='%s', StreetAddress='%s', Requester='%s')>" \
			% (self.AID, self.City, self.State, self.ZipCode, self.RID, self.StreetAddress, self.Requester)
# [END model]

class RoofAttic(db.Model):
	__tablename__ = 'RoofAttic'
	
	RAID = db.Column(db.Integer, unique = True, primary_key=True)
	RoofCoverings = db.Column(db.String(255))
	RCInsp = db.Column(db.Boolean)
	Flashings = db.Column(db.String(255))
	FlasInsp = db.Column(db.Boolean)
	SkylightChimney = db.Column(db.String(255))
	SkChInsp = db.Column(db.Boolean)
	aVentilation = db.Column(db.String(255))
	aVentInsp = db.Column(db.Boolean)
	aDrainage = db.Column(db.String(255))
	aDraiInsp = db.Column(db.Boolean)
	StructureAttic = db.Column(db.String(255))
	StAtInsp = db.Column(db.Boolean)
	FansThermostat = db.Column(db.String(255))
	FaThInsp = db.Column(db.Boolean)
	aInsulation = db.Column(db.String(255))
	aInsuInsp = db.Column(db.Boolean)
	VisibleWiring = db.Column(db.String(255))
	ViWiInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<RoofAttic(RAID='%s', RoofCoverings='%s', RCInsp='%s', Flashings='%s', FlasInsp='%s', SkylightChimney='%s', SkChInsp='%s', " \
			"Ventilation='%s', VentInsp='%s', Drainage='%s', DraiInsp='%s', StructureAttic='%s', StAtInsp='%s', FansThermostat='%s', " \
			"FaThInsp='%s', Insulation='%s', InsuInsp='%s', VisibleWiring='%s', ViWiInsp='%s', RID='%s')>" \
			% (self.RAID, self.RoofCoverings, self.RCInsp, self.Flashings, self.FlasInsp, self.SkylightChimney, self.SkChInsp, 
			self.aVentilation, self.aVentInsp, self.aDrainage, self.aDraiInsp, self.StructureAttic, self.StAtInsp, self.FansThermostat, 
			self.FaThInsp, self.aInsulation, self.aInsuInsp, self.VisibleWiring, self.ViWiInsp, self.RID)
# [END model]

class Exterior(db.Model):
	__tablename__ = 'Exterior'
	
	EID = db.Column(db.Integer, unique = True, primary_key=True)
	WallFlashTrim = db.Column(db.String(255))
	WaFTInsp = db.Column(db.Boolean)
	exDoors = db.Column(db.String(255))
	exDoorInsp = db.Column(db.Boolean)
	exWindows = db.Column(db.String(255))
	exWindInsp = db.Column(db.Boolean)
	DeckBalcSteps = db.Column(db.String(255))
	DeBSInsp = db.Column(db.Boolean)
	VegetDrainDriveWalk = db.Column(db.String(255))
	VDDWInsp = db.Column(db.Boolean)
	EavesFascia = db.Column(db.String(255))
	EaFaInsp = db.Column(db.Boolean)
	exPlumbing = db.Column(db.String(255))
	exPlumInsp = db.Column(db.Boolean)
	Outlets = db.Column(db.String(255))
	OutlInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Exterior(EID='%s', WallFlashTrim='%s', WaFTInsp='%s', exDoors='%s', DoorInsp='%s', Windows='%s', WindInsp='%s', " \
			"DeckBalcSteps='%s', DeBSInsp='%s', VegetDrainDriveWalk='%s', VDDWInsp='%s', EavesFascia='%s', EaFaInsp='%s', Plumbing='%s', " \
			"PlumInsp='%s', Outlets='%s', OutlInsp='%s', RID='%s')>" \
			% (self.EID, self.WallFlashTrim, self.WaFTInsp, self.exDoors, self.exDoorInsp, self.exWindows, self.exWindInsp, 
			self.DeckBalcSteps, self.DeBSInsp, self.VegetDrainDriveWalk, self.VDDWInsp, self.EavesFascia, self.EaFaInsp, self.exPlumbing, 
			self.exPlumInsp, self.Outlets, self.OutlInsp, self.RID)
# [END model]

class Garage(db.Model):
	__tablename__ = 'Garage'
	
	GID = db.Column(db.Integer, unique = True, primary_key=True)
	gCeiling = db.Column(db.String(255))
	gCeilInsp = db.Column(db.Boolean)
	gWalls = db.Column(db.String(255))
	gWallInsp = db.Column(db.Boolean)
	gFloor = db.Column(db.String(255))
	gFlooInsp = db.Column(db.Boolean)
	gDoor = db.Column(db.String(255))
	gDoorInsp = db.Column(db.Boolean)
	InnerDoor = db.Column(db.String(255))
	InDoInsp = db.Column(db.Boolean)
	GDOperator = db.Column(db.String(255))
	GDOpInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Garage(GID='%s', Ceiling='%s', CeilInsp='%s', Walls='%s', WallInsp='%s', Floor='%s', FlooInsp='%s', " \
			"Door='%s', DoorInsp='%s', InnerDoor='%s', InDoInsp='%s', GDOperator='%s', GDOpInsp='%s', RID='%s')>" \
			% (self.GID, self.gCeiling, self.gCeilInsp, self.gWalls, self.gWallInsp, self.gFloor, self.gFlooInsp, 
			self.gDoor, self.gDoorInsp, self.InnerDoor, self.InDoInsp, self.GDOperator, self.GDOpInsp, self.RID)
# [END model]

class Kitchen(db.Model):
	__tablename__ = 'Kitchen'
	
	KID = db.Column(db.Integer, unique = True, primary_key=True)
	kCeiling = db.Column(db.String(255))
	kCeilInsp = db.Column(db.Boolean)
	kWalls = db.Column(db.String(255))
	kWallInsp = db.Column(db.Boolean)
	kFloor = db.Column(db.String(255))
	kFlooInsp = db.Column(db.Boolean)
	PantryDoor = db.Column(db.String(255))
	PaDoInsp = db.Column(db.Boolean)
	kWindows = db.Column(db.String(255))
	kWindInsp = db.Column(db.Boolean)
	kCountersCabinets = db.Column(db.String(255))
	kCoCaInsp = db.Column(db.Boolean)
	kPlumbing = db.Column(db.String(255))
	kPlumInsp = db.Column(db.Boolean)
	kOutletSwitchFix = db.Column(db.String(255))
	kOuSFInsp = db.Column(db.Boolean)
	Dishwash = db.Column(db.String(255))
	DishInsp = db.Column(db.Boolean)
	RangeOven = db.Column(db.String(255))
	RaOvInsp = db.Column(db.Boolean)
	Microwave = db.Column(db.String(255))
	MicrInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Kitchen(KID='%s', Ceiling='%s', CeilInsp='%s', Walls='%s', WallInsp='%s', Floor='%s', FlooInsp='%s', " \
			"PantryDoor='%s', PaDoInsp='%s', kWindows='%s', WindInsp='%s', CountersCabinets='%s', CoCaInsp='%s', Plumbing='%s', " \
			"PlumInsp='%s', OutletSwitchFix='%s', OuSFInsp='%s', Dishwash='%s', DishInsp='%s', RangeOven='%s', RaOvInsp='%s', " \
			"Microwave='%s', MicrInsp='%s', RID='%s')>" \
			% (self.KID, self.kCeiling, self.kCeilInsp, self.kWalls, self.kWallInsp, self.kFloor, self.kFlooInsp, 
			self.PantryDoor, self.PaDoInsp, self.kWindows, self.kWindInsp, self.kCountersCabinets, self.kCoCaInsp, self.kPlumbing, 
			self.kPlumInsp, self.kOutletSwitchFix, self.kOuSFInsp, self.Dishwash, self.DishInsp, self.RangeOven, self.RaOvInsp,
			self.Microwave, self.MicrInsp, self.RID)
# [END model]

class Rooms(db.Model):
	__tablename__ = 'Rooms'
	
	ROID = db.Column(db.Integer, unique = True, primary_key=True)
	rCeiling = db.Column(db.String(255))
	rCeilInsp = db.Column(db.Boolean)
	rWalls = db.Column(db.String(255))
	rWallInsp = db.Column(db.Boolean)
	rFloor = db.Column(db.String(255))
	rFlooInsp = db.Column(db.Boolean)
	StairRailBalc = db.Column(db.String(255))
	SRBaInsp = db.Column(db.Boolean)
	rDoor = db.Column(db.String(255))
	rDoorInsp = db.Column(db.Boolean)
	rWindows = db.Column(db.String(255))
	rWindInsp = db.Column(db.Boolean)
	rOutletSwitchFix = db.Column(db.String(255))
	rOuSFInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Rooms(ROID='%s', Ceiling='%s', CeilInsp='%s', Walls='%s', WallInsp='%s', Floor='%s', FlooInsp='%s', " \
			"StairRailBalc='%s', SRBaInsp='%s', Door='%s', DoorInsp='%s', rWindows='%s', rWindInsp='%s', OutletSwitchFix='%s', " \
			"OuSFInsp='%s', RID='%s')>" \
			% (self.ROID, self.rCeiling, self.rCeilInsp, self.rWalls, self.rWallInsp, self.rFloor, self.rFlooInsp, 
			self.StairRailBalc, self.SRBaInsp, self.rDoor, self.rDoorInsp, self.rWindows, self.rWindInsp, self.rOutletSwitchFix,
			self.rOuSFInsp, self.RID)
# [END model]

class Bathrooms(db.Model):
	__tablename__ = 'Bathrooms'
	
	BID = db.Column(db.Integer, unique = True, primary_key=True)
	CounterCabinet = db.Column(db.String(255))
	bCoCaInsp = db.Column(db.Boolean)
	bDoor = db.Column(db.String(255))
	bDoorInsp = db.Column(db.Boolean)
	bWindows = db.Column(db.String(255))
	bWindInsp = db.Column(db.Boolean)
	bPlumbing = db.Column(db.String(255))
	bPlumInsp = db.Column(db.Boolean)
	bOutletSwitchFix = db.Column(db.String(255))
	bOuSFInsp = db.Column(db.Boolean)
	ExhaustFan = db.Column(db.String(255))
	ExFaInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Bathrooms(BID='%s', CounterCabinet='%s', CoCaInsp='%s', Door='%s', DoorInsp='%s', Windows='%s', WindInsp='%s', " \
			"Plumbing='%s', PlumInsp='%s', OutletSwitchFix='%s', OuSFInsp='%s', ExhaustFan='%s', ExFaInsp='%s', RID='%s')>" \
			% (self.BID, self.CounterCabinet, self.bCoCaInsp, self.bDoor, self.bDoorInsp, self.bWindows, self.bWindInsp, 
			self.bPlumbing, self.bPlumInsp, self.bOutletSwitchFix, self.bOuSFInsp, self.ExhaustFan, self.ExFaInsp, self.RID)
# [END model]

class Structure(db.Model):
	__tablename__ = 'Structure'
	
	SID = db.Column(db.Integer, unique = True, primary_key=True)
	FoundBasement = db.Column(db.String(255))
	FoBaInsp = db.Column(db.Boolean)
	sWalls = db.Column(db.String(255))
	sWallInsp = db.Column(db.Boolean)
	Columns = db.Column(db.String(255))
	ColuInsp = db.Column(db.Boolean)
	sFloors = db.Column(db.String(255))
	sFlooInsp = db.Column(db.Boolean)
	sCeiling = db.Column(db.String(255))
	sCeilInsp = db.Column(db.Boolean)
	sInsulation = db.Column(db.String(255))
	sInsuInsp = db.Column(db.Boolean)
	VaporRetarders = db.Column(db.String(255))
	VaReInsp = db.Column(db.Boolean)
	sVentilation = db.Column(db.String(255))
	sVentInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Structure(SID='%s', FoundBasement='%s', FoBaInsp='%s', Walls='%s', WallInsp='%s', Columns='%s', ColuInsp='%s', " \
			"Floors='%s', FlooInsp='%s', Ceiling='%s', CeilInsp='%s', Insulation='%s', InsuInsp='%s', VaporRetarders='%s', " \
			"VaReInsp='%s', Ventilation='%s', VentInsp='%s',RID='%s')>" \
			% (self.SID, self.FoundBasement, self.FoBaInsp, self.sWalls, self.sWallInsp, self.Columns, self.ColuInsp, 
			self.sFloors, self.sFlooInsp, self.sCeiling, self.sCeilInsp, self.sInsulation, self.sInsuInsp, self.VaporRetarders,
			self.VaReInsp, self.sVentilation, self.sVentInsp, self.RID)
# [END model]

class Plumbing(db.Model):
	__tablename__ = 'Plumbing'
	
	PID = db.Column(db.Integer, unique = True, primary_key=True)
	DrainWasteVent = db.Column(db.String(255))
	DrWVInsp = db.Column(db.Boolean)
	H2OSupplyDist = db.Column(db.String(255))
	HSDiInsp = db.Column(db.Boolean)
	HotWaterSupply = db.Column(db.String(255))
	HWSuInsp = db.Column(db.Boolean)
	MainShut = db.Column(db.String(255))
	MaShInsp = db.Column(db.Boolean)
	FuelStorDist = db.Column(db.String(255))
	FSDiInsp = db.Column(db.Boolean)
	FuelShut = db.Column(db.String(255))
	FuShInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Plumbing(PID='%s', DrainWasteVent='%s', DrWVInsp='%s', H2OSupplyDist='%s', HSDiInsp='%s', HotWaterSupply='%s', HWSuInsp='%s', " \
			"MainShut='%s', MaShInsp='%s', FuelStorDist='%s', FSDiInsp='%s', FuelShut='%s', FuShInsp='%s', RID='%s')>" \
			% (self.PID, self.DrainWasteVent, self.DrWVInsp, self.H2OSupplyDist, self.HSDiInsp, self.HotWaterSupply, self.HWSuInsp, 
			self.MainShut, self.MaShInsp, self.FuelStorDist, self.FSDiInsp, self.FuelShut, self.FuShInsp, self.RID)
# [END model]

class Electrical(db.Model):
	__tablename__ = 'Electrical'
	
	ELID = db.Column(db.Integer, unique = True, primary_key=True)
	EntrConductor = db.Column(db.String(255))
	EnCoInsp = db.Column(db.Boolean)
	ServGroundOverMainPanel = db.Column(db.String(255))
	SGOPInsp = db.Column(db.Boolean)
	BranchEquip = db.Column(db.String(255))
	BrEqInsp = db.Column(db.Boolean)
	DevFix = db.Column(db.String(255))
	DeFiInsp = db.Column(db.Boolean)
	PolarityGround = db.Column(db.String(255))
	PoGrInsp = db.Column(db.Boolean)
	OpGFCI = db.Column(db.String(255))
	GFCIInsp = db.Column(db.Boolean)
	SmokeDetect = db.Column(db.String(255))
	SmDeInsp = db.Column(db.Boolean)
	CarbMonDet = db.Column(db.String(255))
	CaMoInsp = db.Column(db.Boolean)
	LocatMainDistPan = db.Column(db.String(255))
	LMDPInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<Electrical(ELID='%s', EntrConductor='%s', EnCoInsp='%s', ServGroundOverMainPanel='%s', SGOPInsp='%s', BranchEquip='%s', BrEqInsp='%s', " \
			"DevFix='%s', DeFiInsp='%s', PolarityGround='%s', PoGrInsp='%s', OpGFCI='%s', GFCIInsp='%s', SmokeDetect='%s', " \
			"SmDeInsp='%s', CarbMonDet='%s', CaMoInsp='%s', LocatMainDistPan='%s', LMDPInsp='%s', RID='%s')>" \
			% (self.ELID, self.EntrConductor, self.EnCoInsp, self.ServGroundOverMainPanel, self.SGOPInsp, self.BranchEquip, self.BrEqInsp, 
			self.DevFix, self.DeFiInsp, self.PolarityGround, self.PoGrInsp, self.OpGFCI, self.GFCIInsp, self.SmokeDetect, 
			self.SmDeInsp, self.CarbMonDet, self.CaMoInsp, self.LocatMainDistPan, self.LMDPInsp, self.RID)
# [END model]

class HeatCentAir(db.Model):
	__tablename__ = 'HeatCentAir'
	
	HID = db.Column(db.Integer, unique = True, primary_key=True)
	HeatEquip = db.Column(db.String(255))
	HeEqInsp = db.Column(db.Boolean)
	NormOpCont = db.Column(db.String(255))
	NOCoInsp = db.Column(db.Boolean)
	AutoSafeCont = db.Column(db.String(255))
	ASCoInsp = db.Column(db.Boolean)
	DistSys = db.Column(db.String(255))
	DiSyInsp = db.Column(db.Boolean)
	ChimneyFlueVent = db.Column(db.String(255))
	CFVeInsp = db.Column(db.Boolean)
	SolidFuelHeatDev = db.Column(db.String(255))
	SFHDInsp = db.Column(db.Boolean)
	CoolAirHandEq = db.Column(db.String(255))
	CAHEInsp = db.Column(db.Boolean)
	NormOpEq = db.Column(db.String(255))
	NOEqInsp = db.Column(db.Boolean)
	RID = db.Column(db.Integer, db.ForeignKey('Reports.RID'))
	
	def __repr__(self):
		return "<HeatCentAir(HID='%s', HeatEquip='%s', HeEqInsp='%s', NormOpCont='%s', NOCoInsp='%s', AutoSafeCont='%s', ASCoInsp='%s', " \
			"DistSys='%s', DiSyInsp='%s', ChimneyFlueVent='%s', CFVeInsp='%s', SolidFuelHeatDev='%s', SFHDInsp='%s', CoolAirHandEq='%s', " \
			"CAHEInsp='%s', NormOpEq='%s', NOEqInsp='%s', RID='%s')>" \
			% (self.HID, self.HeatEquip, self.HeEqInsp, self.NormOpCont, self.NOCoInsp, self.AutoSafeCont, self.ASCoInsp, 
			self.DistSys, self.DiSyInsp, self.ChimneyFlueVent, self.CFVeInsp, self.SolidFuelHeatDev, self.SFHDInsp, self.CoolAirHandEq, 
			self.CAHEInsp, self.NormOpEq, self.NOEqInsp, self.RID)
# [END model]

# [START list]
def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (User.query
             .order_by(User.username)
             .limit(limit)
             .offset(cursor))
    users = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(users) == limit else None
    return (users, next_page)
# [END list]


# [START read]
def read(id):
    result = Book.query.get(id)
    if not result:
        return None
    return from_sql(result)
# [END read]


# [START create]
def createUser(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return
# [END create]

# [START create]
def createReport(reportData, addressData, roofAtticData, exteriorData, garageData, kitchenData,
	roomsData, bathroomsData, structureData, plumbingData, electricalData, heatCentAirData):
	report = Report(**reportData)
	address = Address(**addressData)
	roofAttic = RoofAttic(**roofAtticData)
	exterior = Exterior(**exteriorData)
	garage = Garage(**garageData)
	kitchen = Kitchen(**kitchenData)
	rooms = Rooms(**roomsData)
	bathrooms = Bathrooms(**bathroomsData)
	structure = Structure(**structureData)
	plumbing = Plumbing(**plumbingData)
	electrical = Electrical(**electricalData)
	heatCentAir = HeatCentAir(**heatCentAirData)
	db.session.add(report)
	db.session.commit()
	db.session.add(address)
	db.session.add(roofAttic)
	db.session.add(exterior)
	db.session.add(garage)
	db.session.add(kitchen)
	db.session.add(rooms)
	db.session.add(bathrooms)
	db.session.add(structure)
	db.session.add(plumbing)
	db.session.add(electrical)
	db.session.add(heatCentAir)
	db.session.commit()
	return
# [END create]

# [START update]
def updateReport(addressData, roofAtticData, exteriorData, garageData, kitchenData, 
				roomsData, bathroomsData, structureData, plumbingData, electricalData, heatCentAirData):
	address = Address.query.get(addressData['RID'])
	roof = RoofAttic.query.get(roofAtticData['RID'])
	exterior = Exterior.query.get(exteriorData['RID'])
	garage = Garage.query.get(garageData['RID'])
	kitchen = Kitchen.query.get(kitchenData['RID'])
	rooms = Rooms.query.get(roomsData['RID'])
	bathrooms = Bathrooms.query.get(bathroomsData['RID'])
	structure = Structure.query.get(structureData['RID'])
	plumbing = Plumbing.query.get(plumbingData['RID'])
	electrical = Electrical.query.get(electricalData['RID'])
	heat = HeatCentAir.query.get(heatCentAirData['RID'])
	for k, v in addressData.items():
		setattr(address, k, v)
		db.session.commit()
	for k, v in roofAtticData.items():
		setattr(roof, k, v)
		db.session.commit()
	for k, v in exteriorData.items():
		setattr(exterior, k, v)
		db.session.commit()
	for k, v in garageData.items():
		setattr(garage, k, v)
		db.session.commit()
	for k, v in kitchenData.items():
		setattr(kitchen, k, v)
		db.session.commit()
	for k, v in roomsData.items():
		setattr(rooms, k, v)
		db.session.commit()
	for k, v in bathroomsData.items():
		setattr(bathrooms, k, v)
		db.session.commit()
	for k, v in structureData.items():
		setattr(structure, k, v)
		db.session.commit()
	for k, v in plumbingData.items():
		setattr(plumbing, k, v)
		db.session.commit()
	for k, v in electricalData.items():
		setattr(electrical, k, v)
		db.session.commit()
	for k, v in heatCentAirData.items():
		setattr(heat, k, v)
		db.session.commit()
	return
# [END update]

def retrieveLoginInfo(un):
	userInfo = User.query.filter_by(username=un).first()
	return userInfo

def getReportInfo():
	return Report.query.all()
	
def getAddressInfo(rid):
	return Address.query.filter_by(RID=rid)
	
def getRoofAtticInfo(rid):
	return RoofAttic.query.filter_by(RID=rid)
	
def getExteriorInfo(rid):
	return Exterior.query.filter_by(RID=rid)
	
def getGarageInfo(rid):
	return Garage.query.filter_by(RID=rid)
	
def getKitchenInfo(rid):
	return Kitchen.query.filter_by(RID=rid)
	
def getRoomsInfo(rid):
	return Rooms.query.filter_by(RID=rid)
	
def getBathroomsInfo(rid):
	return Bathrooms.query.filter_by(RID=rid)

def getStructureInfo(rid):
	return Structure.query.filter_by(RID=rid)	

def getPlumbingInfo(rid):
	return Plumbing.query.filter_by(RID=rid)

def getElectricalInfo(rid):
	return Electrical.query.filter_by(RID=rid)

def getHeatCentAirInfo(rid):
	return HeatCentAir.query.filter_by(RID=rid)
	
def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
