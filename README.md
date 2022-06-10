# stc_automation
stc automation scripts

Anatomy_run.py is the main script to run

steps to start Anatomy
++++++++++++++++++++++++++

copy over to stc_automation folder
C:\Program Files (x86)\Spirent Communications\Spirent TestCenter 5.32\Spirent TestCenter Application\API\Python\StcPython.py

add the following line into StcPython.py
os.environ['STC_PRIVATE_INSTALL_DIR'] = "C:\\Program Files (x86)\\Spirent Communications\\Spirent TestCenter 5.32\\Spirent TestCenter Application"
