/*****************************************************************************\

  device.h - base class for all devices 
 
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

\*****************************************************************************/

#ifndef _DEVICE_H
#define _DEVICE_H

enum IO_MODE
{
   UNI_MODE=0, /* uni-di */
   RAW_MODE,   /* bi-di */
   MLC_MODE,
   DOT4_MODE,
   DOT4_PHOENIX_MODE,  /* (ie: clj2840, lj3055, clj4730mfp) */
   DOT4_BRIDGE_MODE  /* (ie: clj2500) */
};

enum FLOW_CONTROL
{
   GUSHER=0,
   MISER
};

enum SCAN_PORT
{
   SCAN_PORT0=0,
   SCAN_PORT1
};

enum FD_ID
{
   FD_7_1_2,         /* bi-di interface */
   FD_7_1_3,         /* 1284.4 interface */
   FD_ff_1_1,        /* HP EWS interface */
   MAX_FD
};

enum BRIGE_REG_ID
{
   ECRR=2,
   CCTR=3,
   ATAA=8
};

/* USB file descriptor, one for each USB protocol. */
typedef struct
{
   usb_dev_handle *pHD;
   int Config;
   int Interface;
   int AltSetting;
   int urb_write_active;             /* 0=no, 1=yes */
#if (defined(__APPLE__) && defined(__MACH__)) || defined(__FreeBSD__)
#else
   struct usbdevfs_urb urb_write;     /* host to device */
   struct usbdevfs_urb urb_read;     /* device to host */
#endif
   unsigned char ubuf[BUFFER_SIZE];           /* usb read packet buffer */     
   int uindex;
   int ucnt;             
} FileDescriptor;

/* Channel attributes that must remain persistant for life of the device object. */
typedef struct
{
   unsigned short h2psize;  /* host to peripheral packet size in bytes */
   unsigned short p2hsize;  /* peripheral to host packet size in bytes */
} ChannelAttributes;

class Channel;

//Device
//! Abstract base class that encapsulates common device services. Each Device
//! has a unique URI. Multiple clients can open a Device. 
/*!
******************************************************************************/
class Device
{
friend class Channel;
friend class MlcChannel;
friend class ParMlcChannel;
friend class Dot4Channel;
friend class ParDot4Channel;
friend class JetDirectChannel;
friend class CompChannel;

protected:
   char URI[LINE_SIZE];
   int OpenFD;            /* kernal file descriptor from Open */ 
   int ClientCnt;         /* number of clients using this device */
   int Index;             /* System::pDevice[index] of this object */
   char ID[1024];         /* device id */
   pthread_mutex_t mutex;

   struct usb_device *dev;       /* usb device referenced by URI */
   FileDescriptor FD[MAX_FD];    /* usb file descriptors */

   int PrintMode;         /* 0=uni-di | 1=raw | 2=mlc | 3=dot4 (io-mode) */
   int MfpMode;           /* 2=mlc | 3=dot4 (io-mfp-mode) */
   int FlowCtl;           /* 0=gusher | 1=miser (io-control) */
   int ScanPort;          /* 0=normal | 1=CLJ28xx (io-scan-port) */

   Channel *pChannel[MAX_CHANNEL];
   int ChannelCnt;
   virtual Channel *NewChannel(unsigned char sockid, char *sn);
   int DelChannel(int i);
   int ChannelMode;            /* raw | mlc */
   int MlcUp;
   //   int CurrentProtocol;
   //   int NewProtocol;
   ChannelAttributes CA[MAX_SOCKETID];

   System *pSys;
   virtual int DeviceID(char *buffer, int size);
   int DeviceStatus(unsigned int *status);
   int SFieldPrinterState(char *id);
   int PowerUp();
   virtual int Write(int fd, const void *buf, int size);
   virtual int Read(int fd, void *buf, int size, int usec=EXCEPTION_TIMEOUT);
   int CutBuf(int fd, void *buf, int size);

   int Detach(usb_dev_handle *hd, int interface);
   int GetInterface(int dclass, int subclass, int protocol, int *config, int *interface, int *altset);
   int GetOutEP(struct usb_device *dev, int config, int interface, int altset, int type);
   int GetInEP(struct usb_device *dev, int config, int interface, int altset, int type);
   int IsUri(struct usb_device *dev, char *uri);
   struct usb_device *GetDevice(char *uri);
   int WriteECPChannel(int fd, int value);
   int BridgeChipUp(int fd);
   int BridgeChipDown(int fd);
   int ClaimInterface(int fd, int config, int interface, int altset);
   int ReleaseInterface(int fd);
   int WritePhoenixSetup(int fd);

public:
   Device(System *pSys);
   virtual ~Device();

   inline int GetIndex() { return Index; }
   inline void SetIndex(int i) { Index=i; }
   inline int GetClientCnt() { return ClientCnt; }
   inline void SetClientCnt(int i) { ClientCnt=i; }
   inline int GetOpenFD() { return OpenFD; }
   inline int GetMlcUp() { return MlcUp; }
   inline char *GetURI() { return URI; }
   inline void SetURI(char *uri) { strcpy(URI, uri); }
   inline char *GetID() { return ID; }
   inline int GetChannelMode() { return ChannelMode; }
   inline int GetChannelCnt() { return ChannelCnt; }
   inline int GetPrintMode() { return PrintMode; }
   inline void SetPrintMode(int m) { PrintMode=m; }
   inline int GetMfpMode() { return MfpMode; }
   inline void SetMfpMode(int m) { MfpMode=m; }
   inline int GetFlowCtl() { return FlowCtl; }
   inline void SetFlowCtl(int c) { FlowCtl=c; }
   inline int GetScanPort() { return ScanPort; }
   inline void SetScanPort(int p) { ScanPort=p; }
   virtual int Open(char *sendBuf, int *result);
   virtual int Close(char *sendBuf, int *result);
   int ChannelOpen(char *sn, int *channel_result, char *sendBuf, int *result);
   int ChannelClose(int channel, char *sendBuf, int *result);
   virtual int GetDeviceID(char *sendBuf, int sendBufLength, int *result);
   virtual int GetDeviceStatus(char *sendBuf, int *result);
   virtual int WriteData(unsigned char *data, int length, int channel, char *sendBuf, int *result);
   virtual int ReadData(int length, int channel, int timeout, char *sendBuf, int sendBufLength, int *result);   
}; //Device

//UsbDevice
//! Class that encapsulates common bi-di usb device services.
/*!
******************************************************************************/
class UsbDevice : public Device
{
public:
   UsbDevice(System *pSys) : Device(pSys) {}
}; //UsbDevice

//UniUsbDevice
//! Class that encapsulates common uni-di usb device services.
/*!
******************************************************************************/
class UniUsbDevice : public Device
{
protected:
   Channel *NewChannel(unsigned char sockid, char *sn);

public:
   UniUsbDevice(System *pSys) : Device(pSys) {}

   int GetDeviceID(char *sendBuf, int sendBufLength, int *result);
   int GetDeviceStatus(char *sendBuf, int *result);
   //   int Open(char *sendBuf, int *result);
   int ReadData(int length, int channel, int timeout, char *sendBuf, int sendBufLength, int *result);   
}; //UniUsbDevice

//ParDevice
//! Base class that encapsulates common parallel device services.
/*!
******************************************************************************/
class ParDevice : public Device
{
friend class ParMlcChannel;
friend class ParDot4Channel;

protected:
   virtual Channel *NewChannel(unsigned char sockid, char *sn);
   int DeviceID(char *buffer, int size);

   int frob_control(int fd, unsigned char mask, unsigned char val);
   unsigned char read_status(int fd);
   int wait_status(int fd, unsigned char mask, unsigned char val, int usec);
   int wait(int usec);
   int ecp_is_fwd(int fd);
   int ecp_is_rev(int fd);
   int ecp_rev_to_fwd(int fd);
   int ecp_fwd_to_rev(int fd);
   int ecp_write_addr(int fd, unsigned char data);
   int ecp_write_data(int fd, unsigned char data);
   int ecp_read_data(int fd, unsigned char *data);
   int ecp_read(int fd, void *buffer, int size, int sec);
   int ecp_write(int fd, const void *buffer, int size);
   int nibble_read_data(int fd, unsigned char *data);
   int nibble_read(int fd, int flag, void *buffer, int size, int sec);
   int compat_write_data(int fd, unsigned char data);
   int compat_write(int fd, const void *buffer, int size);

   int Write(int fd, const void *buf, int size);
   int Read(int fd, void *buf, int size, int usec=EXCEPTION_TIMEOUT);

public:
   ParDevice(System *pSys) : Device(pSys) {}

   virtual int GetDeviceID(char *sendBuf, int sendBufLength, int *result);
   virtual int GetDeviceStatus(char *sendBuf, int *result);
   virtual int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
}; //ParDevice

//UniParDevice
//! Class that encapsulates uni-di parallel device services.
/*!
******************************************************************************/
class UniParDevice : public ParDevice
{
protected:
   Channel *NewChannel(unsigned char sockid, char *sn);

public:
   UniParDevice(System *pSys) : ParDevice(pSys) {}

   int GetDeviceID(char *sendBuf, int sendBufLength, int *result);
   int GetDeviceStatus(char *sendBuf, int *result);
   int Open(char *sendBuf, int *result);
   int ReadData(int length, int channel, int timeout, char *sendBuf, int sendBufLength, int *result);   
}; //UniParDevice

//JetDirectDevice
//! Class that encapsulates common JetDirect device services.
/*!
******************************************************************************/
class JetDirectDevice : public Device
{
protected:
   char IP[LINE_SIZE];
   int Port;      /* jetdirect port specified by uri */

   Channel *NewChannel(unsigned char sockid, char *sn);
   int DeviceID(char *buffer, int size);
   int GetSnmpStr(char *oid, char *buffer, int size);

public:

   JetDirectDevice(System *pSys) : Device(pSys) {}

   inline char *GetIP() { return IP; }
   inline int GetPort() { return Port; }
   int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
   int GetDeviceStatus(char *sendBuf, int *result);
   int WriteData(unsigned char *data, int length, int channel, char *sendBuf, int *result);
   int ReadData(int length, int channel, int timeout, char *sendBuf, int sendBufLength, int *result);   
}; //JetDirectDevice

#endif // _DEVICE_H

