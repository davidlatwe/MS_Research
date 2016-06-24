import binascii

'''
https://board.b-at-s.info/index.php?app=core&module=global&section=register
'''

print 'Question:\n'

sec = \
'30 31 31 31 31 30 30 30 20 30 31 30 31 31 31 31 30 20 30 30 31 31 30 30 31 30 20 30 30 31 30 30 30 30 30 20 30 30 31 30 31 31 30 31 20 30 30 31 30 30 30 ' + \
'30 30 20 30 30 31 31 31 30 30 30 20 30 31 31 31 31 30 30 30 20 30 30 31 30 30 30 30 30 20 30 30 31 30 31 30 31 31 20 30 30 31 30 30 30 30 30 20 30 30 31 ' + \
'31 30 30 30 31 20 30 30 31 31 30 31 31 30 20 30 30 31 30 30 30 30 30 20 30 30 31 31 31 31 30 31 20 30 30 31 30 30 30 30 30 20 30 30 31 31 30 30 30 30 20 ' + \
'30 30 31 30 31 31 30 30 20 30 30 31 30 30 30 30 30 20 30 31 30 30 30 31 30 31 20 30 31 31 30 31 31 31 30 20 30 31 31 31 30 31 30 30 20 30 31 31 30 30 31 ' + \
'30 31 20 30 31 31 31 30 30 31 30 20 30 30 31 30 30 30 30 30 20 30 30 31 30 31 30 30 30 20 30 31 31 31 31 30 30 30 20 30 30 31 30 30 30 30 30 20 30 30 31 ' + \
'30 31 30 31 30 20 30 30 31 30 30 30 30 30 20 30 30 31 31 30 30 31 31 20 30 30 31 31 30 31 30 31 20 30 30 31 31 30 30 30 30 20 30 30 31 30 31 30 30 31 20\n'

for m in range(0,6):
	t = str(sec[153 * m : 153 * (m + 1)])
	print t
	trans += t






























# Ans down below







#############################################################################################################################################











'''







secArr = sec.split()
newArr = ''

code = {'30': ' 0 ',
		'31': ' 1 ',
		'20': ' . '}

for s in secArr:
	for k in code.keys():
		if s == k:
			newArr += code[k]

unitLength = len(code[k]) * 51
trans = ''
for m in range(0,6):
	t = str(newArr[unitLength * m : unitLength * (m + 1)])
	print t.strip()
	trans += t

form = '\n'
for i, t in enumerate(trans.split(code['20'])):
	t = t.replace(' ', '')
	form += t + ('\n' if i % 17 == 16 else ' ')
print form
	
bin = form.split()
result = ''
for b in bin:
	n = int(b, 2)
	result += binascii.unhexlify('%x' % n)

print result

print '\nANS: 1400'





'''
