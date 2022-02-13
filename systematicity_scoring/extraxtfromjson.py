import json
import glob
import re


phasedict = { "stabilisation_CWK_neck_brace" : "A",
		    "introduction": "A",
		    "air_movement_from_mouth_nose": "A",
		    "mouth_inspection": "A",
		    "head_tilt": "A",
		    "jaw_thrust": "A",
		    "oropharyngeal_airway": "A",
		    "tracheal_deviation": "A",
		    "subcutaneous_emphysema": "A",
		    "jugular_engorgement": "A",
		    "halsvenen": "A",
		    "respiratory_depth": "B",
		    "basal_lung_right": "B",
		    "basal_lung_left": "B",
		    "lung_left_upper": "B", 
		    "lung_right_upper": "B",
		    "percussion_basal_right": "B", 
		    "percussion_basal_left": "B", 
		    "percussion_upper_right": "B", 
		    "percussion_upper_left": "B",
		    "basal_lung_right_back": "B", 
		    "basal_lung_left_back": "B", 
		    "lung_left_upper_back": "B", 
		    "lung_right_upper_back": "B",
		    "percussion_basal_left_back": "B", 
		    "percussion_basal_right_back": "B", 
		    "percussion_upper_right_back": "B", 
		    "percussion_upper_left_back": "B",
		    "non_rebreathingmasker": "B",
		    "nose_glasses": "B",
		    "nebulizer": "B",
		    "arterial_blood_gas": "B",
		    "CXR": "B",
		    "tension_wrap": "C",
		    "capillary_refill_time": "C",
		    "temperature_extremes": "C",
		    "cardiac_ausc_para_sternal": "C",
		    "cardiac_apex_ausc": "C",
		    "carotid_pulse_regular": "C",
		    "radial_pulsations_left_regular": "C",
		    "radial_pulsations_right_frequency": "C",
		    "radial_pulsations_right_pressure": "C",
		    "radial_pulsations_right_regular": "C",
		    "femoral_pulses_frequency": "C",
		    "abdominal_ausc": "C",
		    "percussion_abdomen": "C",
		    "abdominal_palpation": "C",
		    "intravenous_catheter_left_arm": "C",
		    "intravenous_catheter_right_arm": "C",
		    "intravenous_catheter_right_leg": "C",
		    "intravenous_catheter_left_leg": "C",
		    "intravenous_catheter_right_jugular": "C",
		    "intravenous_catheter_left_jugular": "C",
		    "bone_needle_left_tibia": "C",
		    "urinary_catheter": "C",
		    "afl_12_ecg": "C",
		   #  "infusion": "C",
		    "EMV": "D",
		    "eye_inspection": "D",
		    "neck_stiffness": "D",
		    "point_of_care_glucose": "D",
		    "glucose_20_40_50_percent": "D",
		    "body_inspection": "E",
		    "ear_temperature": "E",
		    # "cover": "E"  / not specifc enough
		    }


def getlogentries(inputfilebase):
	#with open(inputfilebase + '_003.json') as f:
	with open(inputfilebase) as f:
		data = json.load(f)
	f.close()
	return data['events'][0]['d']['log']

def detectphases(inputfilebase, dowrite=True):
	logentries = getlogentries(inputfilebase)
	phases = "";
	if dowrite: outfile = open(inputfilebase + '_phases.txt','w') 
	lastpattern = ""
	for logentry in logentries:
		millis = logentry["_millis"]
		s = json.dumps(logentry)
		phase = ""
		pattern = ""
		for k in phasedict.keys():
			if s.find(k) >-1:
				phase=phasedict[k]
				pattern= k
				break
		
		if phase != "" :
			if pattern != lastpattern:
				if dowrite: outfile.write("%s, %s, %s\n" %  (millis, phase, pattern))
				if phases!="":
					phases = phases+","
				phases = phases+str((ord(phase) - ord("A")+1) )
			lastpattern=pattern	
		
	if dowrite: outfile.close()
	#print (phases + "\n")
    
    # This could be written much more nicer ...
	if re.match("^N", inputfilebase) != None:
		print ("list(type=\"N\", id=\"" + re.search("[0-5][0-9]", inputfilebase).group() + "\", seq=c(" + phases + ")),\n")
	else:
		print ("list(type=\"X\", id=\"" + re.search("[0-5][0-9]", inputfilebase).group() + "\", seq=c(" + phases + ")),\n")

def parsegamelog(inputfilebase):
	logentries = getlogentries(inputfilebase)
	
	outfile = open(inputfilebase + '_plain.txt','w') 

	for logentry in logentries:
		millis = logentry["_millis"]
		type = "none"
		name = ""	
		data = ""
		if "signal" in logentry:
			type = "signal"
			name = logentry["signal"][39:];
			if "params" in logentry:
				data = json.dumps(logentry["params"])
		if "event" in logentry:
			type = "event"
			name = logentry["event"];
			if "data" in logentry:
				data = json.dumps(logentry["data"])
		outfile.write("%s, %s, %s, %s\n" % (millis ,type , name , data))
	
	
	outfile.close()

	outfile = open(inputfilebase + '_interpreted.txt','w') 

	for logentry in logentries:
		millis = logentry["_millis"]
		type = "none"
		event = ""	
		if "signal" in logentry:
			name = logentry["signal"][39:]
			type = "some signal ----> " + name	
			if name == "interventions::RequestInterventionDoneSignal":
				type = "action by " + logentry["params"][0]["actor"]
				event = logentry["params"][0]["interventionKey"]
			elif name == "tools::ToolSelectedSignal":
				type = "tool selected"
				event = logentry["params"][0]
			elif name == "tools::SelectToolSignal":
				type = "tool property"
				event = logentry["params"][0]
			elif name == "equipments::EquipmentRemovedSignal":
				type = "tool removed"
				event = logentry["params"][0]["toolID"]
			elif name == "equipments::EquipmentAddedSignal":
				type = "tool added";
				event = logentry["params"][0]["toolID"]
			elif name == "interventions::RequestInterventionMultiselectionDoneSignal":
				type = "multiselection done";
				sel = json.dumps(logentry["params"][0]["selectedOptions"])
				event = logentry["params"][0]["interventionKey"]
				event = event+" "+sel
			elif name == "patienthitareas::OnClickPatientHitAreaSignal":
				type = "player hits area"
				event = logentry["params"][0]
			elif name == "scenario::PatientStateChangedSignal":
				type = "patient state changes"
				event = ""
			elif name == "nurse::NurseBusySignal":
				type = "nurse busy"
				event="no"
				if logentry["params"][0]["busy"]==1:
					event="yes"
			elif name == "patienthitareas::RequestPatientSoundsMixingSignal":
				type = "sound"
				event = "generated"
			elif name == "patienthitareas::RequestPatientSoundsStopMixSignal":
				type = "sound"
				event = "stopped"
			elif name == "interventions::MonitorUpdateSignal":
				type = "monitor status update"
				event = logentry["params"][0]
			elif name == "interventions::InfusionsStateUpdatedSignal":
				type = "Infusion status update"
				event = logentry["params"][0]
			elif name == "tools.medicine::SelectMedicineSignal":
				type = "medicine selected"
				event = logentry["params"][0]
			elif name == "scenario::ResearchRequestedSignal":
				type = "research selected"
				event = str(logentry["params"][0]) + " " + str(logentry["params"][1])
			elif name == "interventions::RequestInterventionChainSignal":
				type = "chain signal"
				event = logentry["params"][0]["chain"]["key"]
			elif name == "medicine::MedicineToPatientSignal":
				type = "medicine to patient"
				event = "-"
			elif name == "interventions::ComputerDataUpdated":
				type = "computer data updated"
				event = "-"
			elif name == "interventions::InfusionFluidBagEmptySignal":
				type = "Infusion fluid bag empty"
				event = logentry["params"][0]["catheterId"]
		elif "event" in logentry:
			name = logentry["event"]
			type = "event ----> " + name	
			if name == "navigate_to":
				type = "player navigates to"
				event = logentry["data"]
			elif name == "rule_match":
				type = "rule match"
				event = logentry["data"]["outcome"]
			elif name == "rule_match_reset":
				type = "rule match reset"
				event = logentry["data"]["outcome"]
			elif name == "patient_value":
				type = "patient value"
				event = str(logentry["data"]["property"]) + " " + str(logentry["data"]["direction"])
			elif name == "cabinetOpenState":
				type = "cabinet open state"
				event = logentry["data"]
			elif name == "patientDialogOptionSelected":
				type = "dialog option selected"
				event = logentry["data"];
			elif name == "openDrawer":
				type = "drawer opened"
				event = logentry["data"]
			elif name == "InterventionMultiselectionDoneSignalCommand.updateDataResultAndChains()":
				type = "multiselecion done and chain"
				event = logentry["data"]["interventionKey"]
				if "selectedOptions" in logentry["data"]:
					sel = json.dumps(logentry["data"]["selectedOptions"])
					event = event+" "+sel		  
			elif name == "monitor_alarm":
				type = "monitor alarm"
				event = "-"
			elif name == "specialist_called":
				type = "specialist called"
				event = logentry["data"]["specialist"]
			elif name == "computer_data_status":
				type = "computer data status"
				event = "-"
			elif name == "research_opened":
				type = "research opened"
				event = logentry["data"]
			elif name == "incorrect_medication":
				type = "incorrect medication"
				event = logentry["data"]["medication"]
			elif name == "apply_medication":
				type = "apply medication"
				event = logentry["data"]["med_id"]
			
		outfile.write("%s, %s, %s\n" % (millis ,type , event))

	outfile.close()
	
		
#==================  END PROCEDURE PARSEGAMELOG ==============


for f  in glob.glob("*.json"):
	# test
    #print (f + "\n")
    
    # parsegamelog(f[:-9])
	#print (f[15:-9]+" ")
	#detectphases(f[:-9], False)
    
    detectphases(f, True)
    #parsegamelog(f)