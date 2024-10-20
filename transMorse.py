"""helper functions for morse code translation from blink series"""

# set default long/short morse code frame counts for blinks

DAH_LEN = 12
DIT_LEN = 6
TOO_SHORT = 2

# sample sequence using positive numbers for blink lens and -1 for extended pause
SAMPLE_SEQ = [7, 7, 7, -1, 12, 11, 13, -1, 7, 6, 6]

# standard text to morse mapping
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
     	'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.' 
        }

# also get reverse mapping from morse to text
INV_CODE = {val: key for key, val in CODE.items()}

def transBlinkLens(series, dah=12, dit=6, too_short=2):
	"""" returns translation to dash or dot in morse code, 
	based on preprocessed blink length time series"""
	# check that the dah/dit/short lengths make sense:
	assert dah>too_short and dit>too_short and dah>dit
	# calc midpoint of dah and dit length in order to attribute ambiguous lengths
	pivot = (dah + dit) / 2
	# now create empty morse list and populate over loop:
	morse = []
	for sig in series:
		if sig == -1:
			morse.append(" ")
		elif sig > -1 and sig <= too_short:
			pass
		elif sig < pivot:
			morse.append(".")
		elif sig > pivot:
			morse.append("-")
	# now join the list into string and remove the commas
	output = ",".join(morse).replace(",","")
	return output


def morseStringToText(morse, alphabet=INV_CODE):
	"""uses standard or user-defined alphabet to translate morse dots/dash STRING 
	to roman alphabet"""
	output = ""
	for group in morse.split(" "):
		try:
			output += INV_CODE[group]
		except KeyError as k:
			output += "?"
	return output

def transRaw(series, dah=12, dit=6, too_short=2):
	"""" returns translation to dash or dot in morse code, 
	based on raw binary time series"""
	pass

def morseListToText(morse, alphabet=INV_CODE):
	"""uses standard or user-defined alphabet to translate morse dots/dash LIST 
	to roman alphabet"""
	build_string = ""
	for m in morse:
		pass

if __name__ == "__main__":
	myline = transBlinkLens(SAMPLE_SEQ)
	translation = morseStringToText(myline)
	print ("original sequence: {0}".format(myline))
	print ("translated sequence: {0}".format(translation))
