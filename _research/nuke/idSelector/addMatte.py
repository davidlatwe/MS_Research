#nuke.root().begin()

try:
	n = nuke.thisNode()
	print n.name()
	rmin = n['rangemin'].value()
	rmax = n['rangemax'].value()

	n.begin()

	nuke.selectAll()
	nuke.invertSelection()


	for e in nuke.allNodes():
		if e['label'].value() == str(int(n['colorID'].value())):
			nuke.delete(e)
		

	idSel = nuke.toNode('idareaselect')
	

	idSel.setSelected(True)

	nuke.nodeCopy(nukescripts.cut_paste_file())

	if n['use_multiple'].value()==True:
		print int(n['colorID'].value())-int(rmin)
		print int(n['colorID'].value())+int(rmax)
		for i in range( int(n['colorID'].value())-int(rmin), int(n['colorID'].value())+int(rmax) +1):
			for e in nuke.allNodes():
					if e['label'].value() == str(int(i)):
						nuke.delete(e)
			idSel2 = nuke.nodePaste(nukescripts.cut_paste_file())
			idSel2['idselect'].setValue(i)
			idSel2['label'].setValue(str(i))
			idSel2.setSelected(False)
			idSel2.setInput(0, nuke.toNode('Shuffle_renderID'))
			
			
	
	if n['use_multiple'].value()==False:
		print 'c'
		idSel2 = nuke.nodePaste(nukescripts.cut_paste_file())
		idSel2['idselect'].setValue(n['colorID'].value())
		idSel2['label'].setValue(str(int(n['colorID'].value())))
		idSel2.setSelected(False)
		idSel2.setInput(0, nuke.toNode('Shuffle_renderID'))
	
	
		idSel2.begin()
		expNode = nuke.toNode('Expression')
		expNode['temp_expr1'].setValue(str(int(rmin)))
		expNode['temp_expr2'].setValue(str(int(rmax)))  
		idSel2.end()
	

	idNodes=[]
	aa = nuke.toNode('AA')

	for i in nuke.allNodes():
		if i['label'].value() == '':
			try:
				nuke.delete(i)
			except:
				pass
		try:
			if i['label'].value() != 'static':
				try:
					idNodes.append(i)
				except:
					pass
		except:
			pass
			
	m = nuke.createNode('Merge2', inpanel=False)
	m.setInput(0, None)
	m.setInput(1, None)
	m.setInput(2, None)

	m.setSelected(False)
	t = 2

	for i in idNodes:
		t+=1
		print str(int(i['idselect'].value()))
		m.setInput(t, i)
		
	sc = nuke.createNode('ShuffleCopy', inpanel=False)
	sc.setSelected(False)
	sc.setInput(0, nuke.toNode('Shuffle1'))
	sc.setInput(1, aa)

	
	
	nuke.toNode('Output').setInput(0, nuke.toNode('Switch_gui'))
	nuke.toNode('Switch').setInput(0, sc)
	nuke.toNode('ChannelMerge').setInput(1, aa)
	aa.setInput(0, m)
	
	


	n.end()

except:
	nuke.root().begin()
	nuke.message("Select only the ID Selector node.")