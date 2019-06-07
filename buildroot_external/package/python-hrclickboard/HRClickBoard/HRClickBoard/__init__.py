import sys
from .hr_click_board import read_temp
from .hr_click_board import set_red_led_current
from .hr_click_board import calculate_bpm

#Banner
#Banner
print ( "########################################" )
print ( "Python {0}".format(sys.version) )
print ( "Heart Rate Click Board Python Controller" )

#Get revision ID of MAX30100
rev_id = hr_click_board.get_revision_ID()
print ("Click board FW Revision: " + hex(rev_id))

#Get part ID of MAX30100
part_id = hr_click_board.get_part_ID()
print ("Click board part ID: " + hex(part_id))
print ( "########################################" )

#Reset MAX30100
hr_click_board.reset()

#Init MAX30100
hr_click_board.initialize()
