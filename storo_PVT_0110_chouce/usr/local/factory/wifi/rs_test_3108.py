# coding=utf-8
# print("Start Test!")

import socket
import struct
import os
import sys
import time
import datetime

import threading

from time import sleep
import subprocess



class SockClient(threading.Thread):
    def __init__(self, host_ip, host_port):
        threading.Thread.__init__(self)
        self.running = False
        self.sock = socket.socket()
        # self.sock.settimeout(120)  # 60 seconds

        #miao:3108 the order of taking picture
        # self.command_1 = "setprop vendor.debug.camera.dump.JpegNode 1"
        # self.command_2 = "setprop vendor.debug.camera.ufo_off 1"
        # self.command_3 = "setprop vendor.debug.camera.p2.dump 1"
        # self.command_4 = "cros_camera_test --camera_hal_path=/usr/lib/camera_hal/mtk_cam_hal.so --gtest_filter=*TakePictureTest/0 --v=0"
        self.command = "cros_camera_test --gtest_filter='*DumpCaptureResult/0' --dump_still_capture_path=/var/cache/camera/0.jpg"
        
        
        self.command_1 = "factory run main_storo:FFT.RearCameraCapture && sleep 4 && mv /tmp/aaa.jpg /var/cache/camera/BackMid.jpg"
        self.command_2 = "factory run main_storo:FFT.RearCameraCapture && sleep 4 && mv /tmp/aaa.jpg /var/cache/camera/BackFar.jpg"
        self.command_3 = "cros_camera_test --gtest_filter='*DumpCaptureResult/0' --dump_still_capture_path=/var/cache/camera/BackWhite.jpg"

        #miao:make three dirs
        self.dirPath_1 = "/var/cache/camera/BackMid"
        self.dirPath_2 = "/var/cache/camera/BackFar"
        self.dirPath_3 = "/var/cache/camera/BackWhite"

        #miao:path of three pictures
        # self.filePath_1 = os.path.join(self.dirPath_1,"BackMid.jpg")
        # self.filePath_2 = os.path.join(self.dirPath_2,"BackFar.jpg")
        # self.filePath_3 = os.path.join(self.dirPath_3,"BackWhite.jpg")
        self.filePath_1 = "/var/cache/camera/BackMid/BackMid.jpg"
        self.filePath_2 = "/var/cache/camera/BackFar/BackFar.jpg"
        self.filePath_3 = "/var/cache/camera/BackWhite/BackWhite.jpg"
        

        #miao:check picture whether exist or not:0 no,1 yes
        self.command_imgExist = "ls /var/cache/camera/*jpg 2> /dev/null | wc -l"

        #miao:move picture to different dir
        self.command_move_1 = "mv /var/cache/camera/*.jpg /var/cache/camera/BackMid/BackMid.jpg"
        self.command_move_2 = "mv /var/cache/camera/*.jpg /var/cache/camera/BackFar/BackFar.jpg"
        self.command_move_3 = "mv /var/cache/camera/*.jpg /var/cache/camera/BackWhite/BackWhite.jpg"

        #miao:clean the files
        self.command_clean = "rm /var/cache/camera/*.jpg"
        self.command_clean_1 = "rm /var/cache/camera/BackMid/BackMid.jpg"
        self.command_clean_2 = "rm /var/cache/camera/BackFar/BackFar.jpg"
        self.command_clean_3 = "rm /var/cache/camera/BackWhite/BackWhite.jpg"



        #miao:get the serial number
        self.command_sn = "vpd -g serial_number"
        self.command_productName = "vpd -g model_name"
        self.command_pn = "factory device-data"
        

        self.str_sntest = ""
        self.str_sn = ""
        self.str_productname =""
        self.str_pn = ""

        
        #miao:create dirs
        if not os.path.exists(self.dirPath_1):
            os.makedirs(self.dirPath_1)
        if not os.path.exists(self.dirPath_2):
            os.makedirs(self.dirPath_2)
        if not os.path.exists(self.dirPath_3):
            os.makedirs(self.dirPath_3)


        bConnect = True
        while(bConnect):
            try:    
                self.sock.connect((host_ip, host_port))
                bConnect = False
            except socket.error as e:
                print("Socket Connect Error:%s" % e)
                bConnect = True
                
        print(bConnect)        
        print("connect success")
        sys.stdout.writelines("Connect Success!" + "\n")
        sys.stdout.flush()

        #miao:Open the log file
        # self.f_log = open("log.txt","a+")
        self.Fc_Log("The Pad is Connected!")
        self.running = True

        self.error_cnt = 0
        self.image_cnt = 0
        self.b_Img = False

        

    def run(self):
        while self.running:
            try:
                self.image_cnt += 1

                #miao:wait for PC msg
                recvData = self.sock.recv(1024)
                print(recvData)
                str_log = "receive msg: " + recvData.decode('utf-8')
                self.Fc_Log(str_log)
                sys.stdout.writelines("receive msg: {}".format(str_log) + "\n")
                sys.stdout.flush()

                if len(recvData) > 0:
                     #miao:test over
                    if recvData.decode('utf-8') == "testover":
                        print("test over")
                        sys.stdout.writelines("test over!" + "\n")
                        sys.stdout.flush()
                        self.sock.close()
                        self.running = False
                    elif recvData.decode('utf-8') == "testexit":
                        print("exit")
                        self.sock.close()
                        self.running = False
                        sys.stderr.writelines("test exit!" + "\n")
                        sys.stderr.flush()
                        
                        self.f_log = open("rear_camera_result.txt","w")
                        self.f_log.writelines("result: FAIL" + "\n")
                        self.f_log.close()

                    elif recvData.decode('utf-8') == "pass":
                        print("the result:  PASS")
                        sys.stdout.writelines("test result:  PASS!" + "\n")
                        sys.stdout.flush()

                        self.f_log = open("rear_camera_result.txt","w")
                        self.f_log.writelines("result: PASS" + "\n")
                        self.f_log.close()

                    elif recvData.decode('utf-8') == "fail":
                        print("the result:  FAIL")
                        sys.stdout.writelines("test result:  FAIL!" + "\n")
                        sys.stdout.flush()

                        self.f_log = open("rear_camera_result.txt","w")
                        self.f_log.writelines("result: FAIL" + "\n")
                        self.f_log.close()

                    #miao:get and send serial number 
                    elif recvData.decode('utf-8') == "sntest":
                        #miao:sn
                        p = subprocess.Popen(self.command_sn,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        self.str_sn = p.stdout.read().decode("utf-8").replace("\n", "")
                        print("SN: {}".format(self.str_sn))
                        sys.stdout.writelines("SN: {}".format(self.str_sn) + "\n")
                        sys.stdout.flush()

                        #miao:productname
                        p = subprocess.Popen(self.command_productName,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        self.str_productname = p.stdout.read().decode("utf-8").replace("\n", "")
                        print("ProductName: {}".format(self.str_productname))
                        sys.stdout.writelines("ProductName: {}".format(self.str_productname) + "\n")
                        sys.stdout.flush()

                        #miao:pn
                        p = subprocess.Popen(self.command_pn,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        str_rtn = p.stdout.read().decode("utf-8")
                        self.str_pn = str_rtn[str_rtn.find("pn") + 4 :str_rtn.find("product_name") - 1]
                        print("PN:  {}".format(self.str_pn))
                        sys.stdout.writelines("PN:  {}".format(self.str_pn) + "\n")
                        sys.stdout.flush()

                        #miao:Send SN to PC
                        self.str_sntest = self.str_sn + "," + self.str_productname + "," + self.str_pn
                        self.sock.send(bytes(self.str_sntest.encode("utf-8")))

                        str_log = "The serial number of the Pad: " + self.str_sntest
                        print(str_log)
                        self.Fc_Log(str_log)
                        sys.stdout.writelines("The serial number of the Pad:  {}".format(self.str_sntest) + "\n")
                        sys.stdout.flush()
                    else:
                         #miao:Clean all files
                        p = subprocess.Popen(self.command_clean,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        # p = subprocess.Popen(self.command_clean_1,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        # p = subprocess.Popen(self.command_clean_2,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        # p = subprocess.Popen(self.command_clean_3,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        self.Fc_Log("Clean all files over!")
                        sys.stdout.writelines("Clean all files over" + "\n")
                        sys.stdout.flush()

                        #miao:before taking picture,delete the exising picture
                        p = subprocess.Popen(self.command_imgExist,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        if(p.stdout.readlines()[0].decode("ascii").split("\n")[0] == '0'):
                            print("before take image,there is not exist images")
                            sys.stdout.writelines("before take image,there is not exist images" + "\n")
                            sys.stdout.flush()
                        else:
                            subprocess.Popen("rm /var/cache/camera/*.jpg",shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                            print("delete the existed picture successfully")
                            sys.stdout.writelines("delete the existed picture successfully" + "\n")
                            sys.stdout.flush()


                        self.b_Img = False
                        #miao:take picture
                        time_takePicture_start = time.time()
                        self.Fc_Log("Start to Take Picture!")
                        print("prepare to take a picture")
                        sys.stdout.writelines("prepare to take a picture!" + "\n")
                        sys.stdout.flush()

                        p = subprocess.Popen(self.command,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        print("take picture order 1")
                        sleep(0.1)
                        self.Fc_Log("The first order send over!")
                        sys.stdout.writelines("Take Picture Command Send Over!" + "\n")
                        sys.stdout.flush()

                        time_takePicture_start_1 = time.time()
                        while self.b_Img == False:
                            p = subprocess.Popen(self.command_imgExist,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                            str_rtn = p.stdout.read().decode("utf-8").replace("\n", "")

                            if(str_rtn != "0"):
                                print("image exsist!")
                                sys.stdout.writelines("Wait for image exsist! Image exsist" + "\n")
                                sys.stdout.flush()
                                self.b_Img = True
                                # break
                            else:
                                # print("image not exsist!")
                                sleep(0.2)

                        time_takePicture_end = time.time()
                        str_log = "Take Picture over,cast time: " + str(time_takePicture_end - time_takePicture_start_1)
                        self.Fc_Log(str_log)
                        sys.stdout.writelines("Take Picture over,cast time: {}".format(str(time_takePicture_end - time_takePicture_start_1)) + "\n")
                        sys.stdout.flush()
                        

                        # time_takePicture_end = time.time()
                        # print("take picture cast time: ")
                        print(time_takePicture_end - time_takePicture_start)

                        # print("the order of taking image send over")
                        #miao:check taking picture success or fail
                        # p = subprocess.Popen(self.command_imgExist,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                        # if(p.stdout.readlines()[0].decode("ascii").split("\n")[0] == '0'):
                        #     print("take image failed")
                        # print("start check picture exist or not")
                        # if(p.stdout.readlines()[0].decode("ascii").split("\n")[0] == '1'):
                        print("take image successfully")
                        sys.stdout.writelines("Take image successfully!" + "\n")
                        sys.stdout.flush()

                        #miao:move the picture to dir
                        time_movePicture_start = time.time()
                        if recvData.decode('utf-8') == "middletest": #middletest
                            p = subprocess.Popen(self.command_move_1,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                            self.filepath = self.filePath_1
                            print("move middleTest image")
                            self.Fc_Log("Set Back Middle path!")
                            sys.stdout.writelines("Set Back Middle Path!" + "\n")
                            sys.stdout.flush()
                        elif recvData.decode('utf-8') == "fartest": #fartest
                            p = subprocess.Popen(self.command_move_2,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                            self.filepath = self.filePath_2
                            print("move backFar image")
                            self.Fc_Log("Set Back Far path!")
                            sys.stdout.writelines("Set Back Far Path!" + "\n")
                            sys.stdout.flush()
                        elif recvData.decode('utf-8') == "whitetest":  #whitetest
                            p = subprocess.Popen(self.command_move_3,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
                            self.filepath = self.filePath_3
                            print("move backWhite image")
                            self.Fc_Log("Set Back White path!")
                            sys.stdout.writelines("Set Back White Path!" + "\n")
                            sys.stdout.flush()
                            
                        sleep(0.2)
                        time_movePicture_end = time.time()
                        print("move picture cast time: ")
                        print(time_movePicture_end - time_movePicture_start)
                        sys.stdout.writelines("move picture cast time: {}".format(str(time_movePicture_end - time_movePicture_start)) + "\n")
                        sys.stdout.flush()

                        #miao:the size of picture
                        time_sendPicture_start = time.time()
                        fileinfo_size = struct.calcsize('128sq')
                        fhead = struct.pack('128sq',bytes(os.path.basename(self.filepath).encode('utf-8')),os.stat(self.filepath).st_size)
                        str_size = str(os.stat(self.filepath).st_size)
                        self.sock.send(bytes(str_size.encode('utf_8')))
                        time.sleep(0.1)
                        print("client send the size of image: {}".format(str_size))
                        sys.stdout.writelines("client send the size of image: {}".format(str_size) + "\n")
                        sys.stdout.flush()


                        #miao:transfer picture
                        with open(self.filepath,'rb') as fp:
                            print("prepare to sending picture...")
                            sys.stdout.writelines("Prepare to sending picture..." + "\n")
                            sys.stdout.flush()
                            while True:
                                data = fp.read(1024)
                                if not data:
                                    print('{0} file send over...'.format(self.filepath))
                                    sys.stdout.writelines("{} file send over...".format(self.filepath) + "\n")
                                    sys.stdout.flush()
                                    break
                                self.sock.send(data)

                        time_sendPicture_end = time.time()
                        print("send picture cast time: {}".format(str(time_sendPicture_end - time_sendPicture_start)))
                        # print(time_sendPicture_end - time_sendPicture_start)
                        self.Fc_Log("Send Picture Over! Send picture cast time: {}".format(str(time_sendPicture_end - time_sendPicture_start)))
                        sys.stdout.writelines("Send Picture Over! Send picture cast time: {}".format(str(time_sendPicture_end - time_sendPicture_start)) + "\n")
                        sys.stdout.flush()
                    # else:
                    #     print("image not exsist!")

            except socket.error as e:
                print('socket running error:', str(e))
                sys.stderr.writelines("socket running error: {}".format(str(e)))
                sys.stderr.flush()
                break

        print('SockClient Thread Exit\n')
        sys.stdout.writelines("SockClient Thread Exit!" + "\n")
        sys.stdout.flush()
        self.f_log.close()
    
    def Fc_Log(self, text):
        self.f_log = open("log.txt","a+")
        self.str_time ="[Log:] " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.f_log.writelines(self.str_time + text + "\n")
        self.f_log.close()


def get_host_ip():
    try:
        mSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mSocket.connect(('8.8.8.8', 80))
        ip = mSocket.getsockname()[0]
    except:
        ip = -1
    finally:
        mSocket.close()

    return ip       

if __name__ == "__main__":
    sys.stdout.writelines("Start Test!")
    sys.stdout.flush()
    print("Start Test!")

    # str_wifi_name = ""

    # while(str_wifi_name == ""):
    #     wifi_name_command = "factory device-data -g serials.wifi_name"
    #     p = subprocess.Popen(wifi_name_command,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
    #     str_wifi_name = p.stdout.read().decode("utf-8").replace("\n", "")

    # command_connectWIFI = "/usr/local/autotest/cros/scripts/wifi connect " + str(str_wifi_name) + " 88888888"
    # command_disconnectWIFI = "/usr/local/autotest/cros/scripts/wifi disconnect " + str(str_wifi_name)
    # p = subprocess.Popen(command_connectWIFI,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)

    # sys.stdout.writelines("Waiting for connecting WIFI!")
    # sys.stdout.flush()
    # print("Waiting for connecting WIFI!")
    # time.sleep(3)


    #miao:acquire the ip address,if empty,keep waitting
    while(True):
        rtn = get_host_ip()
        if(rtn != -1):
            ip = rtn
            break
    
    ip_list = ip.split(".")
    # ip_list[0] = '192'
    # ip_list[1] = '168'
    ip_list[2] = '1'
    ip_list[3] = '2'
    ip_new = ip_list[0] + '.' + ip_list[1] + '.' + ip_list[2] + '.'+ ip_list[3]

    print(rtn)
    print(ip_list[0])
    print(ip_list[1])
    print(ip_list[2])
    print(ip_list[3])

    sys.stdout.writelines("the pad ip: {}\n".format(rtn) +"the PC ip: {}\n".format(ip_list))
    sys.stdout.flush()

    #miao:the testing computer ad Client,connect the PC
    sock_client = SockClient(ip_new, 10001)
    sock_client.start()

    try:
        while True:
            sleep(1)

            if not sock_client.is_alive():
                break

    except KeyboardInterrupt:
        print('ctrl+c')
        sock_client.running = False

    sock_client.join()
    # p = subprocess.Popen(command_disconnectWIFI,shell = True,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
    print('exit finally')
    sys.stdout.writelines("Exit finally!")
    sys.stdout.flush()
    
