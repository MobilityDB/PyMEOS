import faulthandler

faulthandler.enable()

from pymeos import pymeos_initialize, pymeos_finalize

pymeos_initialize()
print("#########################################################################################")
print("##########################################TTime##########################################")
print("#########################################################################################")
import pymeos.examples.time
print("#########################################################################################")
print("##########################################TBool##########################################")
print("#########################################################################################")
import pymeos.examples.tbool
print("#########################################################################################")
print("##########################################TInt###########################################")
print("#########################################################################################")
import pymeos.examples.tint
print("#########################################################################################")
print("#########################################TFloat##########################################")
print("#########################################################################################")
import pymeos.examples.tfloat
print("#########################################################################################")
print("##########################################TText##########################################")
print("#########################################################################################")
import pymeos.examples.ttext
# print("#########################################################################################")
# print("##########################################TBox###########################################")
# print("#########################################################################################")
# import pymeos.examples.box
print("#########################################################################################")
print("#######################################TGeogPoint########################################")
print("#########################################################################################")
import pymeos.examples.tgeogpoint
print("#########################################################################################")
print("#######################################TGeomPoint########################################")
print("#########################################################################################")
import pymeos.examples.tgeompoint


pymeos_finalize()
