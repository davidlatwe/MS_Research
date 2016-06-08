for cf in cmds.ls(typ= 'cacheFile'):
	cmds.setAttr(cf + '.hold', 1)






'''
def autoLayout(data, box):
	def func(key, box):
		tmpKey = key[1:] if key[0].isdigit() else key
		d = group(n= tmpKey, em= 1, a= 1)
		parent(d, box)
		return d

	if type(data) is dict:
		dataList = data.keys()
		dataList.sort()
		for key in dataList:
			d = func(key, box)
			autoLayout(data[key], d)
	else:
		print data

autoLayout(proj, '')
'''