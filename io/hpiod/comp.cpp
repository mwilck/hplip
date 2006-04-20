/*****************************************************************************\

  comp.cpp - composite USB channel class 
 
  (c) 2006 Copyright Hewlett-Packard Development Company, LP

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

CompChannel::CompChannel(Device *pD) : Channel(pD)
{
   ChannelFD = -1;
}

int CompChannel::Open(char *sendBuf, int *result)
{
   const char res[] = "msg=OpenChannelResult\nresult-code=%d\n";
   int slen, fd;
   int config, interface, altset;
   int iclass, isub, iproto;

   *result = R_IO_ERROR;
   slen = sprintf(sendBuf, res, R_IO_ERROR);  

   /* Check for multiple opens on the same channel. */
   if (ClientCnt==1)
   {
      /* Get requested interface based on SocketID. */
      fd = FD_ff_1_1;        /* currently only EWS is suppported */
      iclass = 0xff;
      isub = 1;
      iproto = 1;
 
      /* Get interface descriptors and claim it. */
      if (pDev->GetInterface(iclass, isub, iproto, &config, &interface, &altset))
      {
         syslog(LOG_ERR, "invalid interface: %d/%d/%d %s %s %d\n", iclass, isub, iproto, pDev->GetURI(), __FILE__, __LINE__);
         goto bugout;
      }
      if (pDev->ClaimInterface(fd, config, interface, altset))
         goto bugout;

      ChannelFD = fd;

   } /* if (ClientCnt==1) */

   *result = R_AOK;
   slen = sprintf(sendBuf, "msg=ChannelOpenResult\nresult-code=%d\nchannel-id=%d\n", *result, Index);

bugout:

   return slen;  
}

int CompChannel::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelCloseResult\nresult-code=%d\n";
   int len=0;

   *result = R_AOK;

   if (ClientCnt==1)
   {
      pDev->ReleaseInterface(ChannelFD);
      ChannelFD = -1;
   }

   len = sprintf(sendBuf, res, *result);  

   return len;
}

int CompChannel::WriteData(unsigned char *data, int length, char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\nbytes-written=%d\n"; 
   int len, size, sLen, total=0;

   *result=R_IO_ERROR;
   size = length;

   while (size > 0)
   {
      len = pDev->Write(ChannelFD, data+total, size);
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

//CompChannel::ReadData
//! ReadData() tries to read "length" bytes from the peripheral.  
//! The returned read count may be zero (timeout, no data available), less than "length" or equal "length".
//!
//! The "timeout" specifies how many microseconds to wait for a data packet. 
/*!
******************************************************************************/
int CompChannel::ReadData(int length, int timeout, char *sendBuf, int sendBufLength, int *result)
{
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int len=0, sLen;
   char buffer[BUFFER_SIZE];

   *result=R_IO_ERROR;

   if ((length + HEADER_SIZE) > sendBufLength)
   {
      syslog(LOG_ERR, "invalid data size CompChannel::ReadData: %d %s %s %d\n", length, pDev->GetURI(), __FILE__, __LINE__);
      sLen = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   len = pDev->Read(ChannelFD, buffer, length, timeout);
   if (len < 0)
   {
      if (len < -1)
      {
         sLen = sprintf(sendBuf, res, *result);  
         goto bugout;
      }
      else if (timeout >= EXCEPTION_TIMEOUT)
         syslog(LOG_ERR, "timeout CompChannel::ReadData: %m %s %s %d\n", pDev->GetURI(), __FILE__, __LINE__);
      len = 0;
   }

   *result=R_AOK;
   sLen = sprintf(sendBuf, "msg=ChannelDataInResult\nresult-code=%d\nlength=%d\ndata:\n", *result, len); 
   memcpy(&sendBuf[sLen], buffer, len);
   sLen += len; 

bugout:
   return sLen;
}

