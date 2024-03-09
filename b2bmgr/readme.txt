START/STOP
		./b2bmgr.py -swtype sfg/gm -action <start/stop>

BACKUP

    FOR GM

		./b2bmgr.py -swtype gm -action backup -installdir <GMINSTALLDIR> -backupdir <BACKUPDIR> -appdatadir <APPDATADIR> -ibmimsharedpath <IBMIMSHAREDPATH>
		
        ./b2bmgr.py -swtype gm -action backup -installdir /apps/ibm/gm -backupdir /apps/ibm/backup -appdatadir /apps/ibm/data -ibmimsharedpath /apps/ibm/im
	
	FOR SFG	
	
		./b2bmgr.py -swtype sfg  -action backup -installdir <SFGINSTALLDIR> -backupdir <BACKUPDIR> -appdatadir <APPDATADIR> -ibmimsharedpath <IBMIMSHAREDPATH> -IBM <IBMPATH> -ibm <ibmPATH>	
		
		./b2bmgr.py -swtype sfg  -action backup -installdir /apps/ibm/sfg -backupdir /apps/ibm/backup -appdatadir /apps/ibm/data -ibmimsharedpath /apps/ibm/im -IBM /home/mftadmin/IBM -ibm /home/mftadmin/var/ibm


UPGRADE
	
    FOR GM
    
		./b2bmgr.py -swtype gm -action upgrade -installdir <GMINSTALLDIR> -imdir <INSTALLATIONMANAGERDIR> -responsefilepath <RESPONSEFILEPATH>  -appdatadir <APPDATADIR> -log <LOG>

		./b2bmgr.py -swtype gm -action upgrade -installdir /apps/ibm/gm -imdir apps/ibm/sw/sourcefiles/SFG/InstallationManager/IM_Linux/tools -responsefilepath /apps/ibm/sw/sourcefiles/CASS_RES.xml  -appdatadir /apps/ibm/data -log /apps/ibm/backup

	FOR SFG
	
		./b2bmgr.py -swtype sfg -action upgrade -installdir <SFGINSTALLDIR> -imdir <INSTALLATIONMANAGERDIR> -responsefilepath <RESPONSEFILEPATH> -appdatadir <APPDATADIR> -jar <B2BAPIJARPATH> -log <LOG>                  
		
		./b2bmgr.py -swtype sfg -action upgrade -installdir /apps/ibm/sfg -imdir /apps/ibm/sw/sourcefiles/SFG/InstallationManager/IM_Linux/tools -responsefilepath /apps/ibm/sw/sourcefiles/SFG_RES.xml -appdatadir /apps/ibm/data -jar /apps/ibm/sw/SFG/packages/ -log /apps/ibm/backup                  


RESTORE

    FOR GM

	    ./b2bmgr.py -swtype gm -action restore -installdir <GMINSTALLDIR> -backupdir <BACKUPDIR> -backuptime <TIMEOFBACKUPFORRESTORING>

		./b2bmgr.py -swtype gm  -action restore -installdir /apps/ibm/gm -backupdir /apps/ibm/backup -backuptime <TIMEOFBACKUPFORRESTORING>
	
	FOR SFG

		./b2bmgr.py -swtype sfg -action restore -installdir <SFGINSTALLDIR> -backupdir <BACKUPDIR> -backuptime <TIMEOFBACKUPFORRESTORING> -uiupdatescript <UIUPDATESCRIPT>
		
		./b2bmgr.py -swtype sfg -action restore -installdir /apps/ibm/sfg -backupdir /apps/ibm/backup -backuptime 20240309160549 -uiupdatescript /opt/B2B_Shared/c7r7ff/IMA/modifySFG-UI.sh