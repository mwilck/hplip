/*****************************************************************************\

  uppdevice.cpp - Unidirectional parallel port device class 
 
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

#ifdef HAVE_PPORT

int UniParDevice::GetDeviceStatus(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceStatusResult\nresult-code=%d\nstatus-code=%d\nstatus-name=%s\n";
   int len=0;
   unsigned char status = NFAULT_BIT;

   *result = R_AOK;

   len = sprintf(sendBuf, res, *result, status, "NoFault");  /* fake 8-bit status */

   return len;
}

int UniParDevice::GetDeviceID(char *sendBuf, int slen, int *result)
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
      syslog(LOG_ERR, "unable to lock UniParDevice::GetDeviceID: %m\n");
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto hijmp;
   }

   if ((idLen + HEADER_SIZE) > slen)
   {
      syslog(LOG_ERR, "invalid device id size UniParDevice::GetDeviceID: %d\n", idLen);
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

int UniParDevice::Open(char *sendBuf, int *result)
{
   char dev[255];
   char uriModel[128];
   char model[128];
   int len=0;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is already open. */ 

   pSys->GetURIModel(URI, uriModel, sizeof(uriModel));

   //   if (ClientCnt==1)
   if (ID[0] == 0)
   {
      /* First DeviceOpen, open actual kernal device, use blocking i/o. */
      pSys->GetURIDataLink(URI, dev, sizeof(dev));
      if ((OpenFD = open(dev, O_RDWR | O_NOCTTY)) < 0)            
      {
         *result = R_IO_ERROR;
         syslog(LOG_ERR, "unable to UniParDevice::Open %s: %m\n", URI);
         goto blackout;
      }

      if (ioctl (OpenFD, PPCLAIM))
      {
         *result = R_IO_ERROR;
         syslog(LOG_ERR, "unable to claim port UniParDevice::Open: %m\n");
         goto blackout;
      }

      len = DeviceID(ID, sizeof(ID));  /* get new copy and cache it  */ 

      if (len == 0)
      {
         *result = R_IO_ERROR;
         goto blackout;
      }
   }

   /* Make sure uri model matches device id model. Ignor test if uri model equals "ANY" (probe). */
   if (strcmp(uriModel, "ANY") != 0)
   {
      pSys->GetModel(ID, model, sizeof(model));
      if (strcmp(uriModel, model) != 0)
      {
         *result = R_INVALID_DEVICE_NODE;  /* probably a laserjet, or different device plugged in */  
         syslog(LOG_ERR, "invalid model %s != %s UniParDevice::Open\n", uriModel, model);
         goto blackout;
      }
   }

blackout:
   pthread_mutex_unlock(&mutex);

bugout:
   if (*result == R_AOK)
      len = sprintf(sendBuf, "msg=DeviceOpenResult\nresult-code=%d\ndevice-id=%d\n", *result, Index);  
   else
      len = sprintf(sendBuf, "msg=DeviceOpenResult\nresult-code=%d\n", *result);  

   return len;
}

int UniParDevice::ReadData(int length, int channel, int timeout, char *sendBuf, int slen, int *result)
{   
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int sLen;

   syslog(LOG_ERR, "invalid command UniParDevice::ReadData: %m\n");
   *result = R_INVALID_MESSAGE;
   sLen = sprintf(sendBuf, res, *result);  

   return sLen;
}

//UniParDevice::NewChannel
//!  Create channel object given the requested socket id and service name.
/*!
******************************************************************************/
Channel *UniParDevice::NewChannel(unsigned char sockid, char *sn)
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

#endif /* HAVE_PPORT */




