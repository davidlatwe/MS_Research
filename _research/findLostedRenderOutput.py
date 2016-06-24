

filepath = 'O:/201603_SongOfKnights/Maya/images/0618/velocity/co_cut15_charVelocity_v30/charVelocity/velocity'
start = 101
end = 213

def getLostedFrameList(filepath, start, end):
	def getsn(filename):
		return int(filename.split('.')[-2])
	
	lost = [num for num in range(start, end + 1)]
	lostShortGrp = []
	for fn in os.listdir(filepath):
		if getsn(fn) in lost:
			lost.remove(getsn(fn))	
	for id in lost:
		if lost.index(id) == 0:
			lostShortGrp.append([id])
		else:
			if lost[lost.index(id) - 1] == id - 1:
				lostShortGrp[-1].append(id)
			else:
				lostShortGrp.append([id])
	for grp in lostShortGrp:
		if len(grp) > 1:
			lostShortGrp[lostShortGrp.index(grp)] = str(grp[0]) + '-' + str(grp[-1])
		else:
			lostShortGrp[lostShortGrp.index(grp)] = str(grp[0])
	
	lostShort = ', '.join(lostShortGrp)
	lostLong = str(lost)[1:-1]
	
	return 	lostShort, lostLong


print getLostedFrameList(filepath, start, end)[0]