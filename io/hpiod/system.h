/*****************************************************************************\

  system.h - class provides common system services  
 
  (c) 2004 Copyright Hewlett-Packard Development Company, LP

  Permission is hereby granted, free of charge, to any person obtaining a copy 
  of this software and associated documentation files (the "Software"), to deal 
  in the Software without restriction, including without limitation the rights 
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
  of the Software, and to permit persons to whom the Software is furnished to do 
  so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  (c) 2003-2004 Copyright Hewlett-Packard Development Company, LP

\*****************************************************************************/

#ifndef _SYSTEM_H
#define _SYSTEM_H

class Device;

//System
//! Class that encapsulates common system services.
/*!
******************************************************************************/
class System
{
   pthread_mutex_t mutex;
   SessionAttributes head;   /* linked list of sessions */

   Device *pDevice[MAX_DEVICE];
   int DeviceCnt;
   Device *NewDevice(MsgAttributes *ma);
   int DelDevice(int i);

   int UsbDiscovery(char *list, int *cnt);
   int ParDiscovery(char *list, int *cnt);
   int ProbeDevices(char *sendBuf, char *bus);
   int PmlOidToHex(char *szoid, unsigned char *oid, int oidSize);
   int SnmpToPml(char *snmp_oid, unsigned char *oid, int oidSize);
   int SnmpErrorToPml(int snmp_error);
   int PState(char *sendBuf);
   int ValidURI(MsgAttributes *ma);
 
public:
   System();
   ~System();

   int Permsd;
   int Reset;

   int GetPair(char *buf, char *key, char *value, char **tail);
   int ParseMsg(char *buf, int len, MsgAttributes *ma);
   int ExecuteMsg(SessionAttributes *psa, char *recvBuf, int rlen, char *sendBuf, int slen);
   int GetURIDataLink(char *uri, char *buf, int bufSize);
   int GetURIModel(char *uri, char *buf, int bufSize);
   int GetURISerial(char *uri, char *buf, int bufSize);
   //   int GeneralizeURI(MsgAttributes *ma);
   int ModelQuery(char *uri, MsgAttributes *ma);
   int IsHP(char *id);
   int IsUdev(char *dnode);
   int IsInterface(struct usb_device *dev, int dclass);
   int GetModel(char *id, char *buf, int bufSize);
   int GetSerialNum(char *id, char *buf, int bufSize);
   int DeviceCleanUp(SessionAttributes *sa);
   int SetPml(int device, int channel, char *snmp_iod, int type, unsigned char *data, int dataLen, char *sendBuf);
   int GetPml(int device, int channel, char *snmp_iod, char *sendBuf);
   int GetSnmp(char *ip, int port, char *szoid, unsigned char *buffer, unsigned int size, int *type, int *pml_result, int *result);
   int SetSnmp(char *ip, int port, char *szoid, int type, unsigned char *buffer, unsigned int size, int *pml_result, int *result);
   int MakeUriFromIP(char *ip, int port, char *sendBuf);
   int MakeUriFromUsb(char *bus, char *device, char *sendBuf);
   int MakeUriFromPar(char *dnode, char *sendBuf);
   int RegisterSession(SessionAttributes *psa);
   int UnRegisterSession(SessionAttributes *psa);
   int GeneralizeModel(char *sz, char *buf, int bufSize);
   int GeneralizeSerial(char *sz, char *buf, int bufSize);

}; //System


/*
 * PML definitions
 */

enum PML_REQUESTS
{
   PML_GET_REQUEST = 0,
   PML_GET_NEXT_REQUEST = 0x1,
   PML_BLOCK_REQUEST = 0x3,
   PML_SET_REQUEST = 0x4,
   PML_ENABLE_TRAP_REQUEST = 0x5,
   PML_DISABLE_TRAP_REQUEST = 0x6,
   PML_TRAP_REQUEST = 0x7
};

enum PML_ERROR_VALUES
{
   PML_EV_OK = 0,
   PML_EV_OK_END_OF_SUPPORTED_OBJECTS = 0x1,
   PML_EV_OK_NEAREST_LEGAL_VALUE_SUBSTITUTED = 0x2,
   PML_EV_ERROR_UNKNOWN_REQUEST = 0x80,
   PML_EV_ERROR_BUFFER_OVERFLOW = 0x81,
   PML_EV_ERROR_COMMAND_EXECUTION_ERROR = 0x82,
   PML_EV_ERROR_UNKNOWN_OBJECT_IDENTIFIER = 0x83,
   PML_EV_ERROR_OBJECT_DOES_NOT_SUPPORT_REQUESTED_ACTION = 0x84,
   PML_EV_ERROR_INVALID_OR_UNSUPPORTED_VALUE = 0x85,
   PML_EV_ERROR_PAST_END_OF_SUPPORTED_OBJECTS = 0x86,
   PML_EV_ERROR_ACTION_CAN_NOT_BE_PERFORMED_NOW = 0x87
};

enum PML_DATA_TYPES
{
   PML_DT_OBJECT_IDENTIFIER = 0,
   PML_DT_ENUMERATION = 0x04,
   PML_DT_SIGNED_INTEGER = 0x08,
   PML_DT_REAL = 0x0C,
   PML_DT_STRING = 0x10,
   PML_DT_BINARY = 0x14,
   PML_DT_ERROR_CODE = 0x18,
   PML_DT_NULL_VALUE = 0x1C,
   PML_DT_COLLECTION = 0x20,
   PML_DT_UNKNOWN = 0xff
};

#define PML_MAX_DATALEN 4096    /* must be <= BUFFER_SIZE in hpiod.h */

#endif // _SYSTEM_H

