
"""
C:/Program Files/Autodesk/Maya2016/scripts/others/doWrapArgList.mel
"""


# python
mel.eval('doWrapArgList "7" {"1","0","1","2","1","1","0","0"}')

# pymel
mel.doWrapArgList(7, ['1','0','1','2','1','1','0','0'])

#  Description:
#		Starting point of all wrap operations
#
#  Input Arguments:
#      version:  The version used.  1.0 is pre Maya 2.5
#		args[]:
#   Version 1:	
#        [0]  : operation:  1 - Create a new wrap
#                           2 - Add influence
#                           3 - Remove influence
#   Version 2:		
#        [1]  : threshold:  The weight threshold to be used when creating 
#                           a wrap
#        [2]  : maxDist  :  The maxDistance to be used when creating a wrap
#   Version 3:
#        [3]  : inflType :  The influence type (1 = point, 2 = face)
#   Version 4:
#        [4]  : exclusiveBind :  Bind algorithm (0=smooth, 1=exclusive)
#   Version 5:
#        [5]  : autoWeightThreshold :  Auto weight threshold control
#   Version 6:
#        [6]  : renderInfl :  Render influence objects
#   Version 7:
#        [7]  : falloffMode :  Distance falloff algorithm
#
#  Return Value:
#      [string] The name of the wrap node involved in the operation
#
'''
global proc string [] doWrapArgList( string $version,
									 string $args[] )
{
	int $operation   = $args[0];
	int $exclusiveBind = 0;
	int $autoWeightThreshold = 0;
	float $threshold = 0.0;
	float $maxDist = 0.0;
	int $inflType = 2;
	int $versionNum = $version;
	int $renderInfl = 0;
	int $falloffMode = 0;

	if ( $versionNum > 1 )
	{
		$threshold = $args[1];
		$maxDist   = $args[2];
	}

	if ( $versionNum > 2 )
	{
		$inflType = $args[3];
	}

	if ( $versionNum > 3 )
	{
		$exclusiveBind = $args[4];
	}

	if ( $versionNum > 4 )
	{
		$autoWeightThreshold = $args[5];
	}

	if ( $versionNum > 5 )
	{
		$renderInfl = $args[6];
	}
	if ( $versionNum > 6 )
	{
		$falloffMode = $args[7];
	}

	if ($operation == 1) 
	{
		return createWrap($threshold, $maxDist, $inflType, $exclusiveBind, $autoWeightThreshold, $renderInfl, $falloffMode);
	}
	if ($operation == 2)
	{
		return addWrapInfluences($inflType, $renderInfl);
	}
	if ($operation == 3)
	{
		return removeWrapInfluence();
	}
}
'''
