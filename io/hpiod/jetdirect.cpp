/*****************************************************************************\

  jetdirect.cpp - JetDirect channel class 
 
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

#include "hpiod.h"

static const int PrintPort[] = { 0, 9100, 9101, 9102 };
static const int ScanPort0[] = { 0, 9290, 9291, 9292 };
static const int ScanPort1[] = { 0, 8290, 8291, 8292 };        /* hack for CLJ28xx */
static const int GenericPort[] = { 0, 9220, 9221, 9222 };

JetDirectChannel::JetDirectChannel(Device *pDev) : Channel(pDev)
{
   Socket = -1;
}

int JetDirectChannel::ReadReply()
{
   char tmpBuf[LINE_SIZE + HEADER_SIZE];
   MsgAttributes ma;
   int len, num=0, result;
   char *tail;

   len = ReadData(LINE_SIZE, 2000000, tmpBuf, sizeof(tmpBuf), &result);
   tmpBuf[len] = 0;
   pDev->pSys->ParseMsg(tmpBuf, len, &ma);

   if (ma.result == 0)
      num = strtol((char *)ma.data, &tail, 10);

   return num;
}

int JetDirectChannel::Open(char *sendBuf, int *result)
{
   struct sockaddr_in pin;  
   JetDirectDevice *pD = (JetDirectDevice *)pDev;
   char buf[LINE_SIZE];
   int r, len, port;

   *result = R_IO_ERROR;

   bzero(&pin, sizeof(pin));  
   pin.sin_family = AF_INET;  
   pin.sin_addr.s_addr = inet_addr(pD->GetIP());  

   switch (GetSocketID())
   {
      case PRINT_CHANNEL:
         port = PrintPort[pD->GetPort()];
         pin.sin_port = htons(port);
         if ((Socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
         {  
            syslog(LOG_ERR, "unable to open print port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }  
         if (connect(Socket, (struct sockaddr *)&pin, sizeof(pin)) == -1) 
         {  
            syslog(LOG_ERR, "unable to connect to print port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }  
         break;
      case SCAN_CHANNEL:
         if (pDev->GetScanPort() == SCAN_PORT0)
            port = ScanPort0[pD->GetPort()];
         else
            port = ScanPort1[pD->GetPort()];
         pin.sin_port = htons(port);

         if ((Socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
         {  
            syslog(LOG_ERR, "unable to open scan port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }  
         if (connect(Socket, (struct sockaddr *)&pin, sizeof(pin)) == -1) 
         {  
            syslog(LOG_ERR, "unable to connect to scan err=%d port %d JetDirectChannel::Open: %m %s %s %d\n", errno, port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }
         if (pDev->GetScanPort() == SCAN_PORT0)
         {
            r = ReadReply();
            if (r != 0)
            {  
               syslog(LOG_ERR, "invalid scan response %d port %d JetDirectChannel::Open: %s %s %d\n", r, port, pDev->GetURI(), __FILE__, __LINE__);  
               goto bugout;  
            } 
         }
         break;
      case MEMORY_CARD_CHANNEL:
      case FAX_SEND_CHANNEL:
      case CONFIG_UPLOAD_CHANNEL:
      case CONFIG_DOWNLOAD_CHANNEL:
         port = GenericPort[pD->GetPort()];
         pin.sin_port = htons(port);
         if ((Socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
         {  
            syslog(LOG_ERR, "unable to open port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }  
         if (connect(Socket, (struct sockaddr *)&pin, sizeof(pin)) == -1) 
         {  
            syslog(LOG_ERR, "unable to connect to port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         } 
         
         r = ReadReply();
         if (r != 220)
         {  
            syslog(LOG_ERR, "invalid response %d port %d JetDirectChannel::Open: %s %s %d\n", r, port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         } 

         len = sprintf(buf, "open %d\n", GetSocketID());
         send(Socket, buf, len, 0);
         r = ReadReply();
         if (r != 200)
         {  
            syslog(LOG_ERR, "invalid response %d port %d JetDirectChannel::Open: %s %s %d\n", r, port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         } 

         len = sprintf(buf, "data\n");
         send(Socket, "data\n", len, 0);
         r = ReadReply();
         if (r != 200)
         {  
            syslog(LOG_ERR, "invalid response %d port %d JetDirectChannel::Open: %s %s %d\n", r, port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }
         break;
      case EWS_CHANNEL:
         port = 80;
         pin.sin_port = htons(port);
         if ((Socket = socket(AF_INET, SOCK_STREAM, 0)) == -1) 
         {  
            syslog(LOG_ERR, "unable to open ews port %d JetDirectChannel::Open: %m %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }  
         if (connect(Socket, (struct sockaddr *)&pin, sizeof(pin)) == -1) 
         {  
            syslog(LOG_ERR, "unable to connect to ews port %d JetDirectChannel::Open: %m, %s %s %d\n", port, pDev->GetURI(), __FILE__, __LINE__);  
            goto bugout;  
         }
         break; 
      case PML_CHANNEL:
         /* Do nothing here, use GetPml/SetPml instead of ReadData/WriteData. */
         break;
      default:
         syslog(LOG_ERR, "unsupported service %d JetDirectChannel::Open: %s %s %d\n", GetSocketID(), pDev->GetURI(), __FILE__, __LINE__);
         *result = R_INVALID_SN;
         goto bugout;
         break;
   }  

   *result = R_AOK;

bugout:

   return sprintf(sendBuf, "msg=ChannelOpenResult\nresult-code=%d\nchannel-id=%d\n", *result, Index);  
}

int JetDirectChannel::Close(char *sendBuf, int *result)
{
   *result = R_AOK;

   if (Socket >= 0)
      close(Socket);
   Socket = -1;  

   /* Delay for back-to-back scanning using scanimage. */
   sleep(1);

   return sprintf(sendBuf, "msg=ChannelCloseResult\nresult-code=%d\n", *result);
}

int JetDirectChannel::WriteData(unsigned char *data, int length, char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\nbytes-written=%d\n"; 
   int len, size, sLen, total=0;
   struct timeval tmo;
   fd_set master;
   fd_set writefd;
   int maxfd, ret;

   *result=R_IO_ERROR;

   if (Socket<0)
   {
      syslog(LOG_ERR, "invalid data link JetDirectChannel::WriteData: %d %s %s %d\n", Socket, pDev->GetURI(), __FILE__, __LINE__);
      goto bugout;
   }

   FD_ZERO(&master);
   FD_SET(Socket, &master);
   maxfd = Socket;
   size = length;

   while (size > 0)
   {
      tmo.tv_sec = EXCEPTION_TIMEOUT/1000000;  /* note linux select will modify tmo */
      tmo.tv_usec = 0;
      writefd = master;
      if ((ret = select(maxfd+1, NULL, &writefd, NULL, &tmo)) == 0)
      {
         len = -1;
         goto bugout;   /* timeout */
      }
      len = send(Socket, data+total, size, 0);
      if (len < 0)
      {
         syslog(LOG_ERR, "unable to JetDirectChannel::WriteData: %m %s %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
         goto bugout;
      }
      size-=len;
      total+=len;
   }
   
   *result = R_AOK;

bugout:
   sLen = sprintf(sendBuf, res, *result, total);  

   return sLen;
}

//JetdirectChannel::ReadData
//! ReadData() tries to read "length" bytes from the peripheral.  
//! The returned read count may be zero (timeout, no data available), less than "length" or equal "length".
//!
//! The "timeout" specifies how many microseconds to wait for a data packet. 
/*!
******************************************************************************/
int JetDirectChannel::ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result)
{
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int len=0, sLen;
   char buffer[BUFFER_SIZE];
   struct timeval tmo;
   fd_set master;
   fd_set readfd;
   int maxfd, ret;

   *result=R_IO_ERROR;

   if (Socket<0)
   {
      syslog(LOG_ERR, "invalid data link JetDirectChannel::ReadData: %d %s %s %d\n", Socket, pDev->GetURI(), __FILE__, __LINE__);
      sLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   if ((length + HEADER_SIZE) > sendBufLength)
   {
      syslog(LOG_ERR, "invalid data size JetDirectChannel::ReadData: %d %s %s %d\n", length, pDev->GetURI(), __FILE__, __LINE__);
      sLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   FD_ZERO(&master);
   FD_SET(Socket, &master);
   maxfd = Socket;
   tmo.tv_sec = timeout / 1000000;
   tmo.tv_usec = timeout % 1000000;

   readfd = master;
   ret = select(maxfd+1, &readfd, NULL, NULL, &tmo);
   if (ret < 0)
   {
      syslog(LOG_ERR, "unable to JetDirectChannel::ReadData: %m %s %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
      sLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }
   if (ret == 0)
   {
      if (timeout >= EXCEPTION_TIMEOUT)
         syslog(LOG_ERR, "timeout JetDirectChannel::ReadData: %m %s %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
      len = 0;
   }
   else
   {
      if ((len = recv(Socket, buffer, length, 0)) < 0)
      {
         syslog(LOG_ERR, "unable to JetDirectChannel::ReadData: %m %s %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
         sLen = sprintf(sendBuf, res, *result);  
         goto bugout;
      }
   }

   *result=R_AOK;
   sLen = sprintf(sendBuf, "msg=ChannelDataInResult\nresult-code=%d\nlength=%d\ndata:\n", *result, len); 
   memcpy(&sendBuf[sLen], buffer, len);
   sLen += len; 

bugout:
   return sLen;
}

