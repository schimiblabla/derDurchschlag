

import os
import sys
import pdb
from datetime import datetime, timedelta
from dateutil import parser

class User:

    def __init__(self, in_pathToUserFile):
        self.pathToUserFile = ""
        self.nick = ""
        self.number = ""
        self.channels = []
        self.muteUntil = False
        self.pathToUserFile = in_pathToUserFile
        self.number = in_pathToUserFile.split("/")[-1]
        with open( in_pathToUserFile ) as userFile:
            lines = userFile.readlines()
        for line in lines:
            key = line.split(" ")[0]
            if len( line.split(" ") ) > 1:
                value = line.split(" ")[1][:-1]
                if key[:-1] == "nick":
                    self.nick = value
                elif key[:-1] == "channels":
                    self.channels = value.split(",")
                elif key[:-1] == "mutedUntil":
                    value = line[:-1].split(": ", 1)[1]              #because we have a white space in the date and need to split the value differently..
                    if value != "":
                        self.muteUntil = datetime.strptime( value, "%Y-%m-%d %H:%M:%S" )
                        if self.muteUntil < datetime.now():         # when the muteUntil-time is in the past, it doesn't need to be saved again
                            self.muteUntil = False
                            self.rewriteUserFile()                  #that is actually not necessary, but looks better
                    else:
                        pass


        

    def getChannels(self):
        return self.channels

    def joinChannel(self, in_newChannel):
        if in_newChannel in self.channels:
            return False
        else:
            self.channels.append( in_newChannel)
            self.rewriteUserFile()
            return True

    def exitChannel(self, in_channel):
        print("entering exitChannel()")
        if in_channel in self.channels:
            self.channels.remove(in_channel)
            self.rewriteUserFile()
            return True
        else:
            return False

    def getMuteUntil(self):
        return self.muteUntil

    def unmute(self):
        self.muteUntil = False
        print( str( self.nick ) + " unmuted" )
        self.rewriteUserFile()
                
    def getNick(self):
        return self.nick

    def getNumber(self):
        return self.number    

    def mute(self):
        #pdb.set_trace()
        self.muteUntil = datetime.now() + timedelta( hours = 6 )
        print( str( self.nick ) + " muted until " + str( self.muteUntil ) )
        self.rewriteUserFile()

    def rewriteUserFile(self):
        print("entering rewriteUserFile()")
        #pdb.set_trace()
        os.remove(self.pathToUserFile)          #need to remove the old file, and make a complete new one..
        userFile = open( self.pathToUserFile, 'a')
        userFile.write( "nick: " + self.nick + "\n" )   #writing nickname in file
        
        try:
            self.channels.remove("")
        except:
            pass
        if len(self.channels) >= 1:                     #writing channels in file
            userFile.write( "channels: " + self.channels[0] )
        if len(self.channels) > 1:                      #if user is in more than in one channle, they will be written in the file just one after the other
            for index in range(1, len(self.channels) ): #but becuase we aready wrote the first one in the file, we start with index '1'
                userFile.write( "," + self.channels[index] )
        if len(self.channels) == 0:
            userFile.write( "channels: " )              #if user is in no channle yet
        userFile.write("\n")
        
        stringMuteUntil = ""
        if self.muteUntil != False:                     #wr
            print( "marked user as muted until: " + stringMuteUntil )
            #serialize mutedUntil:
            stringMuteUntil = '{:%Y-%m-%d %H:%M:%S}'.format( self.muteUntil )
        userFile.write( "mutedUntil: " + stringMuteUntil + "\n")
        userFile.close()


    def sendSMS(self, in_channel, in_time, in_sender, in_text):
        print("entering sendSMS()")
        canBeSent = True
        if self.muteUntil != False:                         #check if there is something at all in the muteUntil-variable
            if self.muteUntil > datetime.now():
                canBeSent = False
        if canBeSent == True:
            toSendString =  'echo "(' + in_channel + ') ' + '[' + in_time + ']' + in_sender + ':  ' + in_text + '" | gammu-smsd-inject TEXT ' + self.number + ' -len ' + str( len(in_text) + len(in_channel) + len(in_sender) + 6 )
            #print("sms sending is suppressed")
            os.system( toSendString )
            print("sending SMS to " + self.number + "[" + in_time + "]" + " (" + self.nick + "): " + str( toSendString ) )
        else:
            print("didn't send message to " + self.nick + " (" + self.number + "), because user is muted")
