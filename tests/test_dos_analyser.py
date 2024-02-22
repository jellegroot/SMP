import sys
import os.path
import pytest



# Use the absolute folder (where this file is located) and move one directory up 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dos_analyser.dos_analyser import DosAnalyzer
# Dataset to use
dataset = 'dataset.json'

#Positive test 
#Test if json file has a list
def test_read_json_positive():
   dos_analyzer = DosAnalyzer(dataset)
   assert type(dos_analyzer.dataset) == list
   
#Negative test
#Test if an non existing file gives an error
def test_read_json_negative():
   with pytest.raises(FileNotFoundError):
      DosAnalyzer('not-found.testfile')

#Positive test
#Test if average output is as expected
def test_average_session_length():
   dos_analyzer = DosAnalyzer(dataset)

   dos_analyzer.average_communication_length()
   expected_output = float(1052.2096836421053)
   assert expected_output == dos_analyzer.average_session_length

#Negative test
#Test if the program gives an error when the input value is not a list
def test_average_session_length_input():
   dos_analyzer = DosAnalyzer(dataset)
   with pytest.raises(TypeError):
      dos_analyzer.average_communication_length({"test": "1"})