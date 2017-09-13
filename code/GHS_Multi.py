"""API for setup/usage of Multi Debugger interface.
"""
#--------------------------------------------------------------------------
# Standard library imports
import os
import sys
import socket
import time
import subprocess

_MPYTHON_IP = "localhost"
_MPYTHON_RCV_BUFF_SZ = 4096
_mpython_port = 10122


#GHS_Multi Class
class GHS_Multi:

    def __init__(self, mpython_path ):
        self.application = None
        self.sock = None
        #check if there is any instance of mpythonrun.exe process
        output = subprocess.check_output('tasklist',shell=True)
        
        mpython_exe_str = os.path.join( mpython_path, "mpythonrun.exe")
        mpython_args_str = "-prompt off -verbose off -socket " + str(_mpython_port)
        #make sure the mpythonrun.exe and svc_python.exe is close properly, otherwise enforce taskkill
        if "mpythonrun.exe" in str(output) or "svc_python.exe" in str(output):
            os.system("taskkill /im mpythonrun.exe /f 2>nul >nul")  
            os.system("taskkill /im svc_python.exe /f 2>nul >nul")
            
        self.application = subprocess.Popen(mpython_exe_str + " " + mpython_args_str)
        self.setup_socket_connection(_MPYTHON_IP,_mpython_port)
            

    def setup_socket_connection(self, host, port):
        
        if (self.sock  == None) and (self.application != None):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host,port))

    def setup_ghs_interface(self,program,target='',setupscript='',target_args=''):

        self.execute_cmd("dbg = GHS_Debugger()",0)
        self.execute_cmd('dw = dbg.DebugProgram("'+program+'")',1)
        self.execute_cmd('dw.ConnectToTarget("' + target + '","' + setupscript + '","","",True, "' + target_args + '",True)')
        
    def close_ghs(self):
        #close mpythonrun simulation
        if (self.application != None) and (self.sock != None) :

            self.execute_cmd("dw.Disconnect()",1)
            self.execute_cmd("dw.CloseWin()",1)
            self.execute_cmd("$quit",0)
            self.sock.close()

        #make sure the mpythonrun.exe and svc_python.exe is close properly, otherwise enforce taskkill
        output = subprocess.check_output('tasklist',shell=True)
        
        if "mpythonrun.exe" in str(output) or "svc_python.exe" in str(output):
            os.system("taskkill /im mpythonrun.exe /f 2>nul >nul")  
            os.system("taskkill /im svc_python.exe /f 2>nul >nul")                  
            
        self.sock = None
        self.application = None
    
    def execute_cmd(self,cmd_str,block=1):

        
        msg = ''
        count = 2
        #print (cmd_str)
        
        #socket available
        if (self.sock != None):
            # for python 3, the tcp/ip accept data in byte array, so enforce encoding from string
            cmd_str = cmd_str.encode('utf-8')
            
            sendcomplete = self.sock.sendall(cmd_str+b"\r\n")
            #successful sendall return none
            if (sendcomplete == None):
            
                self.sock.setblocking(block)

                #blocking communication
                if (block == 1):
                    try:
                        while (count > 0):             
                            data = self.sock.recv(_MPYTHON_RCV_BUFF_SZ)
                            # for python 3, the tcp/ip receive data in byte array, so enforce decoding into string
                            data = data.decode('utf-8')
                            #print (str(count)+":" + data.decode('utf-8'))
                            count -= 1
                            #set non blocking to force receiving data in
                            self.sock.setblocking(0)
                            msg = msg + data


                    except socket.error as e:
                        #skip non blocking exception error:
                        #non 10035 error will b prompt to user
                        if "10035" not in str(e):
                            print(e)
                
                #non-blocking communication           
                else:
                    msg = r"Non-Block communication"
                    
                #print msg    
                return (msg)
            
            #command failed to send, raise error            
            else:
                raise ConnectionError("Command is not send successful")

            
        #socket not establish    
        else:
            raise ConnectionError("Socket not establish")
            

    def is_running(self):

        result = self.execute_cmd("dw.IsRunning()",1)
        return result
        
    def is_alive(self):

        result = self.execute_cmd("dw.IsAlive()",1)
        return result
        
    def restart(self):

        result = self.execute_cmd("dw.RunCmd(\"restart\")",1)
        return result

    def reset(self,go):

        result = execute_cmd("dw.RunCmd(\"reset\")",1)
        if(go):
            self.run()
        return result

    def run(self):

        result = execute_cmd("dw.Run()",1)
        return result

    def halt(self):

        result = execute_cmd("dw.Halt()",1)
        return result



   
    
    
    
    
    
