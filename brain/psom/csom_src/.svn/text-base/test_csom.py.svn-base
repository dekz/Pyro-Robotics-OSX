#import csom
#import sys
import pyrobot.brain.psom._csom as csom
from pyrobot.brain.psom import _ptrset

def init_float_array(mylist):
	nitems = len(mylist)
	#return csom.ptrcreate("float",0,nitems)
	return csom.new_floatarray(nitems)

def init_short_array(mylist):
	nitems = len(mylist)
	#return csom.ptrcreate("short",0,nitems)
	return csom.new_shortarray(nitems)

def init_int_array(mylist): # WKV 2003-07-28
	nitems = len(mylist)
	return csom.new_intarray(nitems)
	
def build_float_array(mylist):
	myarr = init_float_array(mylist)
	list_to_arr(mylist,myarr)
	return myarr

def build_short_array(mylist):
	myarr = init_short_array(mylist)
	list_to_arr(mylist,myarr)
	return myarr

def build_int_array(mylist): # WKV 2003-07-28
	myarr = init_int_array(mylist)
	list_to_arr(mylist,myarr)
	return myarr
	
def list_to_arr(mylist,myarr):
	i = 0
	for item in mylist:
		#ptrset(myarr,item,i)
		_ptrset(myarr,item,i)
		i = i+1
	return myarr

def ptrvalue(myarr, i):
	if myarr[-5:] == 'float':
		return csom.floatarray_getitem(myarr, i)
	elif myarr[-5:] == 'short':
		return csom.shortarray_getitem(myarr, i)
	elif myarr[-3:] == 'int':
		return csom.intarray_getitem(myarr, i)
	else:
		raise TypeError, myarr

def build_list(myarr,nitems):
	mylist = []
	for i in range(0,nitems):
		mylist.append(ptrvalue(myarr,i))
	return mylist

"""
Moved to test 3 (WKV 2003-07-28)

p0 = build_float_array([13.57, 12.61, -1.38, -1.99, 399.77])
p1 = build_float_array([19.58, 13.08, -1.17, -0.84, 400.03])
p2 = build_float_array([29.36, 38.69, -1.10, -0.87, 405.21])
p3 = build_float_array([19.82, 27.08, -2.35, -3.70, 404.86])
mask = build_short_array([0,0,1,0,1])
"""

csom.set_globals()
in_data_file   = "ex.dat"
in_code_file   = "ex.cod"
out_code_file1 = "test1.cod"
out_code_file2 = "test2.cod"

alpha   = 0.02
radius  = 4.0
rlen    = 5000
ewin    = 100
radius2 = 2.0

def test1():
	# test 1:
	# SOM's model vectors are read in from ex.cod.  SOM is then trained using
	# a dataset created from ex.dat.  After training, model vectors are saved to
	# test1.cod.
	
	print "test 1: codes from file, train from file"
	print "----------------------------------------"
	data = csom.open_entries(in_data_file)
	if (data == "NULL"):
		print "\ndata file " + in_data_file + " could not be opened"
		return 1
	codes = csom.open_entries(in_code_file)
	if (codes == "NULL"):
		print "\ncode file " + in_code_file + " could not be opened"
		return 1
	params = csom.construct_teach_params(codes, csom.LINEAR, csom.LINEAR)
	csom.init_training_session(params, alpha, radius, rlen, ewin)
	csom.timing_start(params)
	csom.train_fromdataset(params, data, csom.CYCLIC)
	csom.timing_stop(params)
	time = csom.get_training_time(params)
	print "training session completed in", time, "seconds"
	error = csom.write_entries(codes, out_code_file1)
	if (error):
		print "\nfile " + out_code_file1 + " could not be written"
		return 1
	print "output written to " + out_code_file1
	print "for verification, see test_devrobs.c output"

	# cleanup
	csom.close_entries(data)
	csom.close_entries(codes)
	csom.free_teach_params(params) # WKV 2003-07-28
	
	print "test 1 succesfully completed"
	return 0

def test2():
	
	print "test 2: train from file, codes init. from data"
	print "----------------------------------------------"
	data = csom.open_entries(in_data_file)
	if (data == "NULL"):
		print "\ndata file " + in_data_file + " could not be opened"
		return 1
	codes = csom.randinit_codes(data,csom.TOPOL_HEXA,csom.NEIGH_BUBBLE,12,8)
	params = csom.construct_teach_params(codes, csom.LINEAR, csom.LINEAR)
	csom.init_training_session(params, alpha, radius, rlen, ewin)
	csom.timing_start(params)
	csom.train_fromdataset(params, data, csom.CYCLIC)
	csom.timing_stop(params)
	time = csom.get_training_time(params)
	print "training session completed in", time, "seconds"
	error = csom.write_entries(codes, out_code_file2)
	if (error):
		print "\nfile " + out_code_file2 + " could not be written"
		return 1
	print "output written to " + out_code_file2

	# cleanup
	csom.close_entries(data)
	csom.close_entries(codes)
	csom.free_teach_params(params) # WKV 2003-07-28
	
	print "test 2 succesfully completed"
	return 0

def test3():
	print "test 3: codes from file, data/train dynamically, view SRN levels"
	print "----------------------------------------------------------------"

	# Moved from above WKV 2003-07-28
	p0 = build_float_array([13.57, 12.61, -1.38, -1.99, 399.77])
	p1 = build_float_array([19.58, 13.08, -1.17, -0.84, 400.03])
	p2 = build_float_array([29.36, 38.69, -1.10, -0.87, 405.21])
	p3 = build_float_array([19.82, 27.08, -2.35, -3.70, 404.86])
	mask = build_short_array([0,0,1,0,1])
	
	codes = csom.open_entries(in_code_file)
	if (codes == "NULL"):
		print "\ncode file " + in_code_file + " could not be opened"
		return 1
	params = csom.construct_teach_params(codes, csom.LINEAR, csom.LINEAR)
	csom.init_training_session(params, alpha, radius, rlen, ewin)
	data = csom.init_dataset(5)
	csom.addto_dataset(data, csom.make_data_entry(p0))
	csom.addto_dataset(data, csom.make_data_entry(p1))
	csom.addto_dataset(data,
			   #csom.make_data_entry_weighted_masked(p2, 3, mask, 5))
			   csom.make_data_entry_weighted_masked(p2, 3, mask, 5,
								[])) # WKV 2003-07-28
	csom.addto_dataset(data, csom.make_data_entry(p3))
	print "data set:"
	csom.print_dataset(data)
		
	p = csom.get_eptr()
	input = csom.rewind_entries(data, p)
	last_coords = build_int_array([-1,-1]) # WKV 2003-07-28
	
	while(input != None):
		print "input:", input
		#coords = csom.train_one(params, input)
		coords = csom.train_one(params, input, last_coords, 1) # WKV 2003-07-28
		csom.delete_intarray(last_coords) # WKV 2003-07-28
		last_coords = coords # WKV 2003-07-28
		
		#points = csom._csom.data_entry_points_get(input)
		points = csom.data_entry_points_get(input)
		mylist = build_list(points,5)
		output = csom.get_model_vector(codes, coords)
		print "input: [",
		for pt in mylist:
			print "%.2f" % (pt),
		print "]"
		if(output == "NULL"):
			print "output null"
		#points = csom._csom.data_entry_points_get(output)
		points = csom.data_entry_points_get(output)
		mylist = build_list(points,5)
		print "maps to model: [",
		for pt in mylist:
			print "%.2f" % (pt),
		print "] coords: (", ptrvalue(coords,0), ptrvalue(coords,1), ")"
		sample = input
		input = csom.next_entry(p)
	print "last mapping produces the following gaussian SRN activations:"
	levels = csom.get_activation_levels(params, coords, radius2, # use last_coords?
					    csom.NEIGH_GAUSSIAN)
	levels_list = build_list(levels,96)
	csom.delete_floatarray(levels) # WKV 2003-07-28
	csom.delete_intarray(last_coords) # WKV 2003-07-28
	
	i = 0
	for level in levels_list:
		if(i%24 == 12):
			print "  ",
		print "%.2f" % (level),
		i = i + 1
		if(i%12 == 0):
			print ""
	print "last mapping produces the following dynamic error SRN activations:"
	levels = csom.get_levels_by_error(params, sample, 0.0)
	levels_list = build_list(levels,96)
	csom.delete_floatarray(levels) # WKV 2003-07-28
	
	i = 0
	for level in levels_list:
		if(i%24 == 12):
			print "  ",
		print "%.2f" % (level),
		i = i + 1
		if(i%12 == 0):
			print ""

	# cleanup (mostly written by WKV 2003-07-28)
	for arr in (p0, p1, p2, p3):
		csom.delete_floatarray(arr)
	csom.free_eptr(p)
	csom.delete_shortarray(mask)
	
	csom.close_entries(codes)
	#csom.close_entries(data)
	csom.free_dataset(data)
	csom.free_teach_params(params)
	
	print "test 3 succesfully completed"
	return 0

def cleanup():
	csom.free_labels()
	return 0

error = test1()
if(error):
	print "test 1 aborted"

error = test2()
if(error):
	print "test 2 aborted"

error = test3()
if(error):
	print "test 3 aborted"

error = cleanup()
if(error):
	print "Cleanup had errors"

print "testing completed"

