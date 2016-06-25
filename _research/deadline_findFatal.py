
import sys


def __main__( *args ):
	deadlinePlugin = args[0]
	main(deadlinePlugin)


def main(dp):

	job = dp.GetJob()
	jobId = job.get_ID()
	dp.LogWarning(' JOB ID:  %s' % jobId)
	taskId = int(dp.GetCurrentTaskId())
	dp.LogWarning('TASK ID:  %d' % taskId)

	isFatal = False
	report = getLatestTaskReport(dp, jobId, taskId)
	if report:
		for line in report:
			if 'V-Ray error: There was a fatal error rendering the scene.' in line:
				dp.LogWarning('V-Ray error found. - %s' % line.split(':  ')[0])
				isFatal = True
				#break
	
	if isFatal:
		dp.LogWarning('V-Ray fatal error.')
		dp.FailRender('FUCK.')
	else:
		dp.LogWarning('SAFE.')


def getLatestTaskReport(dp, jobId, taskId):
	
	apiPath = 'O:\\201603_SongOfKnights\\Maya\\scripts\\Deadline'
	dp.LogWarning(' API:  ' + apiPath)

	if not apiPath in sys.path:
		sys.path.insert(0, apiPath)
	
	import DeadlineConnect as Connect
	Deadline = Connect.DeadlineCon('192.168.1.5', 7788)
	Deadline.EnableAuthentication(True)
	Deadline.SetAuthenticationCredentials('moonshinechief', 'moonshine')
	dp.LogWarning('Deadline Web Service Login.')
	
	reports = Deadline.TaskReports.GetAllTaskReportsContents(jobId, taskId)
	if reports:
		dp.LogWarning('Get Report.')
		report = reports[0].split('\n')

		return report

	else:
		dp.LogWarning('No Report.')