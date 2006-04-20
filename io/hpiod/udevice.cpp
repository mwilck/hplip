/*****************************************************************************\

  udevice.cpp - Unidirectional device class 
 
  (c) 2004-2005 Copyright Hewlett-Packard Development Company, LP

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

int UniUsbDevice::GetDeviceStatus(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceStatusResult\nresult-code=%d\nstatus-code=%d\nstatus-name=%s\n";
   int len=0;
   unsigned char status = NFAULT_BIT;

   *result = R_AOK;

   len = sprintf(sendBuf, res, *result, status, "NoFault");  /* fake 8-bit status */

   return len;
}

int UniUsbDevice::GetDeviceID(char *sendBuf, int slen, int *result)
{
   const char res[] = "msg=DeviceIDResult\nresult-code=%d\n";
   int len=0, idLen;

   *result = R_AOK;

//   if (pthread_mutex_trylock(&mutex) == 0)
   if (pthread_mutex_lock(&mutex) == 0)
   {
      if (ClientCnt >= 1)
      {
         idLen = strlen(ID);  /* channel is busy, use cached copy */
      }
      else
      {
         idLen = DeviceID(ID, sizeof(ID));  /* get new copy */
      }
      pthread_mutex_unlock(&mutex);

      if (idLen == 0)
      {
         *result = R_IO_ERROR;
         len = sprintf(sendBuf, res, *result);  
         goto hijmp;
      }
   }
   else
   {
      syslog(LOG_ERR, "unable to lock Device::GetDeviceID: %m\n");
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto hijmp;
   }

   if ((idLen + HEADER_SIZE) > slen)
   {
      syslog(LOG_ERR, "invalid device id size Device::GetDeviceID: %d\n", idLen);
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto hijmp;
   }
   len = sprintf(sendBuf, "msg=DeviceIDResult\nresult-code=%d\nlength=%d\ndata:\n", *result, idLen); 
   memcpy(&sendBuf[len], ID, idLen);
   len += idLen; 

hijmp:
   return len;
}

int UniUsbDevice::ReadData(int length, int channel, int timeout, char *sendBuf, int slen, int *result)
{   
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int sLen;

   syslog(LOG_ERR, "invalid commnad UniUsbDevice::ReadData: %m\n");
   *result = R_INVALID_MESSAGE;
   sLen = sprintf(sendBuf, res, *result);  

   return sLen;
}

//UniUsbDevice::NewChannel
//!  Create channel object given the requested socket id and service name.
/*!
******************************************************************************/
Channel *UniUsbDevice::NewChannel(unsigned char sockid, char *sn)
{
   Channel *pC=NULL;
   int i;

   /* Only support one channel. */
   if (ChannelCnt >= 1)
      goto bugout;

   /* Look for unused slot in channel array. Note, slot 0 is unused. */
   for (i=1; i<MAX_CHANNEL; i++)
   {
      if (pChannel[i] == NULL)
      {
         pC = new RawChannel(this);  /* constructor sets ClientCnt=1 */
         pC->SetIndex(i);
         pC->SetSocketID(sockid);
         pChannel[i] = pC;
         ChannelCnt++;
         break;
      }
   }     

bugout:
   return pC;
}






