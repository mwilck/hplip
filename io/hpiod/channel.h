/*****************************************************************************\

  channel.h - base class for MLC and Raw channels 
 
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

#ifndef _CHANNEL_H
#define _CHANNEL_H

//#define MAX_COMMAND_PACKET 64
#define MAX_COMMAND_PACKET BUFFER_SIZE  
#define MAX_SENDER_DATA BUFFER_SIZE
#define MAX_RECEIVER_DATA BUFFER_SIZE
#define MAX_SERVICE_NAME 40

//Channel
//! Class that encapsulates common channel services. Channels
//! have a unique service name and only one service name can be open at a time.
/*!
******************************************************************************/
class Channel
{
   char service[MAX_SERVICE_NAME];

protected:
   unsigned char sockid;    /* socket id */
   Device *pDev;
   int ClientCnt;           /* number of clients using this device */
   int Index;             /* Device::pChannel[index] of this object */

   unsigned char rbuf[MAX_RECEIVER_DATA];  /* read packet buffer */
   int rindex;
   int rcnt;
   int CutBuf(char *sendBuf, int length);
   int Write(int fd, void *buf, int size);
   int Read(int fd, void *buf, int size, int sec, int usec);

public:
   Channel(Device *pDev);
   virtual ~Channel();

   inline int GetIndex() { return Index; }
   inline void SetIndex(int i) { Index=i; }
   inline int GetClientCnt() { return ClientCnt; }
   inline void SetClientCnt(int i) { ClientCnt=i; }
   inline unsigned char GetSocketID() { return sockid; }
   inline void SetSocketID(unsigned char s) { sockid=s; }
   inline char *GetService() { return service; }
   inline void SetService(char *s) { strncpy(service, s, sizeof(service)); }
   virtual int Open(char *sendBuf, int *result);
   virtual int Close(char *sendBuf, int *result);
   virtual int WriteData(unsigned char *data, int length, char *sendBuf, int *result);
   virtual int ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result);   

}; //Channel

//RawChannel
//! Class that encapsulates raw channel services.
/*!
******************************************************************************/
class RawChannel : public Channel
{
public:
   RawChannel(Device *pDev) : Channel(pDev) {}
}; //RawChannel

//JetdirectChannel
//! Class that encapsulates jetdirect channel services.
/*!
******************************************************************************/
class JetDirectChannel : public Channel
{
   int Socket;
   int ReadReply();

public:
   JetDirectChannel(Device *pDev);

   int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
   int WriteData(unsigned char *data, int length, char *sendBuf, int *result);
   int ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result);   
}; //JetdirectChannel

//MlcChannel
//! Class that encapsulates common channel services requiring MLC.
/*!
******************************************************************************/
class MlcChannel : public Channel
{
   unsigned short credit;  /* host to peripheral credit */
   unsigned short p2hcredit;  /* peripheral to host credit */   

public:
   MlcChannel(Device *pDev);

   inline unsigned short GetH2PSize() { return pDev->CA[GetSocketID()].h2psize; }
   inline void SetH2PSize(unsigned short i) { pDev->CA[GetSocketID()].h2psize=i; }
   inline unsigned short GetP2HSize() { return pDev->CA[GetSocketID()].p2hsize; }
   inline void SetP2HSize(unsigned short i) { pDev->CA[GetSocketID()].p2hsize=i; }
   inline unsigned short GetP2HCredit() { return p2hcredit; }
   inline void SetP2HCredit(unsigned short i) { p2hcredit=i; }
   inline unsigned short GetH2PCredit() { return credit; }
   inline void SetH2PCredit(unsigned short i) { credit=i; }

   int MlcSocket2Channel(unsigned char sockid);
   int MlcForwardReply(int fd, unsigned char *buf, int size);
   int MlcExecReverseCmd(int fd, unsigned char *buf);
   int MlcReverseCmd(int fd);
   int MlcReverseReply(int fd, unsigned char *buf, int bufsize);
   int MlcCredit(int fd, unsigned short credit);
   int MlcCreditRequest(int fd, unsigned short credit);
   int MlcForwardData(int fd, int sockid, unsigned char *buf, int size);
   int MlcReverseData(int fd, int sockid, unsigned char *buf, int bufsize, int timeout);
   int MlcInit(int fd);
   int MlcExit(int fd);
   int MlcConfigSocket(int fd);
   int MlcOpenChannel(int fd);
   int MlcCloseChannel(int fd);
   virtual int Open(char *sendBuf, int *result);
   virtual int Close(char *sendBuf, int *result);
   int WriteData(unsigned char *data, int length, char *sendBuf, int *result);
   int ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result);   

}; //MlcDevice

//Dot4Channel
//! Class that encapsulates common channel services requiring 1284.4.
/*!
******************************************************************************/
class Dot4Channel : public Channel
{
   unsigned short pcredit;  /* primary socket id credit for sending */
   unsigned short scredit;  /* secondary socket id credit for sending */  
   unsigned short psize;    /* primary max packet size for sending */
   unsigned short ssize;    /* secondary max packet size for sending */

public:
   Dot4Channel(Device *pDev);

   inline unsigned short GetH2PSize() { return psize; }
   inline void SetH2PSize(unsigned short i) { psize=i; }
   inline unsigned short GetP2HSize() { return ssize; }
   inline void SetP2HSize(unsigned short i) { ssize=i; }
   inline unsigned short GetP2HCredit() { return scredit; }
   inline void SetP2HCredit(unsigned short i) { scredit=i; }
   inline unsigned short GetH2PCredit() { return pcredit; }
   inline void SetH2PCredit(unsigned short i) { pcredit=i; }

   int Dot4Socket2Channel(unsigned char sockid);
   int Dot4ForwardReply(int fd, unsigned char *buf, int size);
   int Dot4ExecReverseCmd(int fd, unsigned char *buf);
   int Dot4ReverseCmd(int fd);
   int Dot4ReverseReply(int fd, unsigned char *buf, int bufsize);
   int Dot4Credit(int fd, unsigned short credit);
   int Dot4CreditRequest(int fd, unsigned short credit);
   int Dot4ForwardData(int fd, int sockid, unsigned char *buf, int size);
   int Dot4ReverseData(int fd, int sockid, unsigned char *buf, int bufsize, int timeout);
   int Dot4Init(int fd);
   int Dot4Exit(int fd);
   int Dot4GetSocket(int fd);
   int Dot4OpenChannel(int fd);
   int Dot4CloseChannel(int fd);
   virtual int Open(char *sendBuf, int *result);
   virtual int Close(char *sendBuf, int *result);
   int WriteData(unsigned char *data, int length, char *sendBuf, int *result);
   int ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result);   

}; //Dot4Device

class ParMlcChannel : public MlcChannel
{

public:
   ParMlcChannel(Device *pDev);

   int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
}; 

class ParDot4Channel : public Dot4Channel
{

public:
   ParDot4Channel(Device *pDev);

   int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
}; 

//CompChannel
//! Class that encapsulates composite USB channel services.
/*!
******************************************************************************/
class CompChannel : public Channel
{
   int ChannelFD;

public:
   CompChannel(Device *pDev);

   int Open(char *sendBuf, int *result);
   int Close(char *sendBuf, int *result);
   int WriteData(unsigned char *data, int length, char *sendBuf, int *result);
   int ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result);   

}; //CompChannel

#endif // _CHANNEL_H

