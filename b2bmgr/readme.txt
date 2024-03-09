START/STOP
		./b2bmgr.py -swtype sfg -action <start/stop>

BACKUP
	
	FOR SFG	
	
		./b2bmgr.py -swtype sfg  -action backup -installdir <SFGINSTALLDIR> -backupdir <BACKUPDIR> -appdatadir <APPDATADIR> -ibmimsharedpath <IBMIMSHAREDPATH> -IBM <IBMPATH> -ibm <ibmPATH>	
		
		./b2bmgr.py -swtype sfg  -action backup -installdir /apps/ibm/sfg -backupdir /apps/ibm/backup -appdatadir /apps/ibm/data -ibmimsharedpath /apps/ibm/im -IBM /home/mftadmin/IBM -ibm /home/mftadmin/var/ibm


UPGRADE
	
	FOR SFG
	
		./b2bmgr.py -swtype sfg -action upgrade -installdir <SFGINSTALLDIR> -imdir <INSTALLATIONMANAGERDIR> -responsefilepath <RESPONSEFILEPATH> -appdatadir <APPDATADIR> -jar <B2BAPIJARPATH> -log <LOG>                  
		
		./b2bmgr.py -swtype sfg -action upgrade -installdir /apps/ibm/sfg -imdir /apps/ibm/sw/sourcefiles/SFG/InstallationManager/IM_Linux/tools -responsefilepath /apps/ibm/sw/sourcefiles/SFG_RES.xml -appdatadir /apps/ibm/data -jar /apps/ibm/sw/SFG/packages/ -log /apps/ibm/backup                  


RESTORE,

	
	FOR SFG
		./b2bmgr.py -swtype sfg -action restore -installdir <SFGINSTALLDIR> -backupdir <BACKUPDIR> -backuptime <TIMEOFBACKUPFORRESTORING> -uiupdatescript <UIUPDATESCRIPT>
		
		./b2bmgr.py -swtype sfg -action restore -installdir /apps/ibm/sfg -backupdir /apps/ibm/backup -backuptime 20240309160549 -uiupdatescript /opt/B2B_Shared/c7r7ff/IMA/modifySFG-UI.sh