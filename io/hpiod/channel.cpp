/*****************************************************************************\

  channel.cpp - channel base class (RAW) 
 
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

Channel::Channel(Device *pD) : pDev(pD)
{
   sockid = 0;
   ClientCnt = 1;
}

Channel::~Channel()
{
}

int Channel::Open(char *sendBuf, int *result)
{
   *result = R_AOK;
   return sprintf(sendBuf, "msg=ChannelOpenResult\nresult-code=%d\nchannel-id=%d\n", *result, Index);  
}

int Channel::Close(char *sendBuf, int *result)
{
   *result = R_AOK;
   return sprintf(sendBuf, "msg=ChannelCloseResult\nresult-code=%d\n", *result);
}

int Channel::WriteData(unsigned char *data, int length, char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\nbytes-written=%d\n"; 
   int len, size, sLen, total=0;

   *result=R_IO_ERROR;
   size = length;

   while (size > 0)
   {
      len = pDev->Write(pDev->GetOpenFD(), data+total, size);
      if (len < 0)
      {
         syslog(LOG_ERR, "unable to write data %s: %m %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
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

int Channel::CutBuf(char *sendBuf, int length)
{
   const char res[] =  "msg=ChannelDataInResult\nresult-code=%d\nlength=%d\ndata:\n";
   int sendLen, total;

   if (rcnt > length)
   {
      /* Return part of rbuf. */
      total = length;
      sendLen = sprintf(sendBuf, res, R_AOK, total); 
      memcpy(&sendBuf[sendLen], &rbuf[rindex], total);
      sendLen += total; 
      rindex += total;
      rcnt -= total;
   }
   else
   {
      /* Return all of rbuf. */
      total = rcnt;
      sendLen = sprintf(sendBuf, res, R_AOK, total); 
      memcpy(&sendBuf[sendLen], &rbuf[rindex], total);
      sendLen += total; 
      rindex = rcnt = 0;
   }

   return sendLen;
} 

//Channel::ReadData
//! This base class for reading data (raw).
//!
//! ReadData() tries to read "length" bytes from the peripheral.  
//! The returned read count may be zero (timeout, no data available), less than "length" or equal "length".
//!
//! The "timeout" specifies how many microseconds to wait for a data packet. 
/*!
******************************************************************************/
int Channel::ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result)
{
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int len=0, sLen;
   char buffer[BUFFER_SIZE];

   *result=R_IO_ERROR;

   if ((length + HEADER_SIZE) > sendBufLength)
   {
      syslog(LOG_ERR, "invalid data size Channel::ReadData: %d\n", length);
      sLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   while (len==0)
   {
      len = pDev->Read(pDev->GetOpenFD(), buffer, length, timeout);
      if (len < 0)
      {
         syslog(LOG_ERR, "unable to read data Channel::ReadData %s: %m %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
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

