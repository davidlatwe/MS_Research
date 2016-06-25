
def openPort(port):
	if cmds.commandPort('127.0.0.1:' + str(port), q=True):
		cmds.commandPort(name='127.0.0.1:' + str(port), cl=True)
		port += 1
	cmds.commandPort(name='127.0.0.1:' + str(port), stp= 'python', eo= 1)

	