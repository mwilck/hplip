/*****************************************************************************\

  jddevice.cpp - JetDirect device class 
 
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

extern const char *kStatusOID;            /* device id oid */

int JetDirectDevice::DeviceID(char *buffer, int size)
{
   int len=0, maxSize, result, dt, status;

   maxSize = (size > 1024) ? 1024 : size;   /* RH8 has a size limit for device id */

   if ((len = pSys->GetSnmp(GetIP(), GetPort(), (char *)kStatusOID, (unsigned char *)buffer, maxSize, &dt, &status, &result)) == 0)
      syslog(LOG_ERR, "unable to read JetDirectDevice::DeviceID\n");

   return len; /* length does not include zero termination */
}

int JetDirectDevice::Open(char *sendBuf, int *result)
{
   char uriModel[128];
   char model[128];
   char *p, *tail;
   int len=0;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is already open. */ 

   //   if (ClientCnt==1)
   if (ID[0] == 0)
   {
      pSys->GetURIDataLink(URI, IP, sizeof(IP));

      if ((p = strstr(URI, "port=")) != NULL)
         Port = strtol(p+5, &tail, 10);
      else
         Port = 1;
      if (Port > 3)
      {
         *result = R_IO_ERROR;
         goto blackout;
      }

      len = DeviceID(ID, sizeof(ID));  /* get new copy and cache it  */ 

      if (len == 0)
      {
         *result = R_IO_ERROR;
         goto blackout;
      }

      /* Powerup??? */
   }
   else
   {
      len = DeviceID(ID, sizeof(ID));  /* refresh */        
      if (len == 0)
      {
         *result = R_IO_ERROR;
         goto blackout;
      }
   }

   /* Make sure uri model matches device id model. Ignor test if uri model equals "ANY" (probe). */
   pSys->GetURIModel(URI, uriModel, sizeof(uriModel));
   if (strcmp(uriModel, "ANY") != 0)
   {
      pSys->GetModel(ID, model, sizeof(model));
      if (strcmp(uriModel, model) != 0)
      {
         *result = R_INVALID_DEVICE_NODE;  /* probably a laserjet, or different device plugged in */  
         syslog(LOG_ERR, "invalid model %s != %s JetdirectDevice::Open\n", uriModel, model);
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

int JetDirectDevice::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceCloseResult\nresult-code=%d\n";
   int len=0;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is still in use */

   if (ClientCnt==1)
   {
      /* Reset variables here while locked, don't count on constructor with threads. */
      ID[0] = 0;
   }

   pthread_mutex_unlock(&mutex);

bugout:
   len = sprintf(sendBuf, res, *result);  

   return len;
}

int JetDirectDevice::GetDeviceStatus(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceStatusResult\nresult-code=%d\nstatus-code=%d\nstatus-name=%s\n";
   int len=0;
   unsigned char status = NFAULT_BIT;

   *result = R_AOK;

   len = sprintf(sendBuf, res, *result, status, "NoFault");  /* there is no 8-bit status, so fake it */

   return len;
}

int JetDirectDevice::WriteData(unsigned char *data, int length, int channel, char *sendBuf, int *result)
{   
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\n";
   int sLen;

   if (pChannel[channel] == NULL)
   {
      syslog(LOG_ERR, "invalid channel descriptor JetDirectDevice::WriteData: %d\n", channel);
      *result = R_INVALID_CHANNEL_ID;
      sLen = sprintf(sendBuf, res, *result);  
      goto wjmp;
   }

   sLen = pChannel[channel]->WriteData(data, length, sendBuf, result);

wjmp:
   return sLen;
}

int JetDirectDevice::ReadData(int length, int channel, int timeout, char *sendBuf, int slen, int *result)
{   
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int sLen;

   if (pChannel[channel] == NULL)
   {
      syslog(LOG_ERR, "invalid channel descriptor JetDirectDevice::ReadData: %d\n", channel);
      *result = R_INVALID_CHANNEL_ID;
      sLen = sprintf(sendBuf, res, *result);  
      goto rjmp;
   }

   sLen = pChannel[channel]->ReadData(length, timeout, sendBuf, slen, result);

rjmp:
   return sLen;
}

//JetdirectDevice::NewChannel
//!  Create channel object given the requested socket id and service name.
/*!
******************************************************************************/
Channel *JetDirectDevice::NewChannel(unsigned char sockid, char *sn)
{
   Channel *pC=NULL;
   int i, n;

   /* Check for existing name service already open. */
   for (i=1, n=0; i<MAX_CHANNEL && n<ChannelCnt; i++)
   {
      if (pChannel[i] != NULL)
      {
         n++;
         if (strcasecmp(sn, pChannel[i]->GetService()) == 0)
         {
            if (sockid == PML_CHANNEL || sockid == EWS_CHANNEL)
            {
               pC = pChannel[i];
               pC->SetClientCnt(pC->GetClientCnt()+1);    /* same channel, re-use it (PML only) */
            }
            goto bugout;
         }
      }
   }

   if (ChannelCnt >= MAX_CHANNEL)
      goto bugout;

   /* Look for unused slot in channel array. Note, slot 0 is unused. */
   for (i=1; i<MAX_CHANNEL; i++)
   {
      if (pChannel[i] == NULL)
      {
         pC = new JetDirectChannel(this);
         pC->SetIndex(i);
         pC->SetSocketID(sockid);
         pC->SetService(sn);
         pChannel[i] = pC;
         ChannelCnt++;
         break;
      }
   }     

bugout:
   return pC;
}





