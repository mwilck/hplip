/*****************************************************************************\

  ppdevice.cpp - Bidirectional parallel port device class 
 
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

/*
 * PC-style parallel port bit definitions.
 *
 * Status
 *  bit
 *   7 - Busy * 
 *   6 - NAck
 *   5 - PError (PARPORT_STATUS_PAPEROUT)
 *   4 - Select  
 *
 *   3 - NFault (PARPORT_STATUS_ERROR)
 *   2 -
 *   1 -
 *   0 -
 *
 * Control
 *  bit
 *   7 - 
 *   6 - 
 *   5 - 
 *   4 -   
 *
 *   3 - Select *
 *   2 - Init
 *   1 - AutoFD *
 *   0 - Strobe *
 * 
 *              * inverted
 *
 * Notes:
 *   For ECP mode use low-level parport ioctl instead of high-level parport read/writes because its more reliable. High-level support
 *   for Compatible and Nibble modes are probably ok, but for consistency low-level parport ioctl is used.
 *
 */

#define PP_DEVICE_TIMEOUT 30000000   /* device timeout (us) */
#define PP_SIGNAL_TIMEOUT 1000000   /* signal timeout (us) */
#define PP_SETUP_TIMEOUT 10   /* setup timeout (us) */

int ParDevice::frob_control(int fd, unsigned char mask, unsigned char val)
{
   struct ppdev_frob_struct frob;

   /* Convert ieee1284 control values to PC-style (invert Strobe, AutoFd and Select) . */
   frob.val = val ^ (mask & (PARPORT_CONTROL_STROBE | PARPORT_CONTROL_AUTOFD | PARPORT_CONTROL_SELECT));

   frob.mask = mask;
   return ioctl(fd, PPFCONTROL, &frob);
}

unsigned char ParDevice::read_status(int fd)
{
   unsigned char status;
   if (ioctl(fd, PPRSTATUS, &status))
      syslog(LOG_ERR, "ParDevice::read_status error: %m\n");
   
   /* Convert PC-style status values to ieee1284 (invert Busy). */
   return (status ^ PARPORT_STATUS_BUSY); 
} 

int ParDevice::wait_status(int fd, unsigned char mask, unsigned char val, int usec)
{
   struct timeval tmo, now;
   struct timespec min;
   unsigned char status;
   int cnt=0;
   
   gettimeofday (&tmo, NULL);
   tmo.tv_usec += usec;
   tmo.tv_sec += tmo.tv_usec / 1000000;
   tmo.tv_usec %= 1000000;

   min.tv_sec = 0;
   min.tv_nsec = 5000000;  /* 5ms */

   while (1)
   {
      status = read_status(fd);
      if ((status & mask) == val)
      {
	//         bug("found status=%x mask=%x val=%x cnt=%d: %s %d\n", status, mask, val, cnt, __FILE__, __LINE__);
         return 0;
      } 
      cnt++;
      //      nanosleep(&min, NULL);
      gettimeofday(&now, NULL);
      if ((now.tv_sec > tmo.tv_sec) || (now.tv_sec == tmo.tv_sec && now.tv_usec > tmo.tv_usec))
      {
         syslog(LOG_ERR, "ParDevice::wait_status timeout status=%x mask=%x val=%x us=%d: %s %d\n", status, mask, val, usec, __FILE__, __LINE__);
         return -1;   /* timeout */
      }
   }
}

int ParDevice::wait(int usec)
{
   struct timeval tmo, now;
   int cnt=0;
   
   gettimeofday (&tmo, NULL);
   tmo.tv_usec += usec;
   tmo.tv_sec += tmo.tv_usec / 1000000;
   tmo.tv_usec %= 1000000;

   while (1)
   {
      cnt++;
      gettimeofday(&now, NULL);
      if ((now.tv_sec > tmo.tv_sec) || (now.tv_sec == tmo.tv_sec && now.tv_usec > tmo.tv_usec))
      {
         return 0;   /* timeout */
      }
   }
}

int ParDevice::ecp_is_fwd(int fd)
{
   unsigned char status;

   status = read_status(fd);
   if ((status & PARPORT_STATUS_PAPEROUT) == PARPORT_STATUS_PAPEROUT)
      return 1;
   return 0;
}

int ParDevice::ecp_is_rev(int fd)
{
   unsigned char status;

   status = read_status(fd);
   if ((status & PARPORT_STATUS_PAPEROUT) == 0)
      return 1;
   return 0;
}

int ParDevice::ecp_rev_to_fwd(int fd)
{
   int dir=0;

   if (ecp_is_fwd(fd))
      return 0;

   /* Event 47: write NReverseRequest/nInit=1 */
   frob_control(fd, PARPORT_CONTROL_INIT, PARPORT_CONTROL_INIT);

   /* Event 48: wait PeriphClk/nAck=1, PeriphAck/Busy=0 */
   //   wait_status(fd, PARPORT_STATUS_PAPEROUT | PARPORT_STATUS_BUSY, PARPORT_STATUS_PAPEROUT, SIGNAL_TIMEOUT);

   /* Event 49: wait nAckReverse/PError=1 */
   wait_status(fd, PARPORT_STATUS_PAPEROUT, PARPORT_STATUS_PAPEROUT, PP_SIGNAL_TIMEOUT);

   ioctl(fd, PPDATADIR, &dir);

   return 0;
}

int ParDevice::ecp_fwd_to_rev(int fd)
{
   int dir=1;

   if (ecp_is_rev(fd))
      return 0;

   /* Event 33: NPeriphRequest/nFault=0, PeriphAck/Busy=0 */
   wait_status(fd, PARPORT_STATUS_BUSY | PARPORT_STATUS_ERROR, 0, PP_DEVICE_TIMEOUT);

   /* Event 38: write HostAck/nAutoFd=0 */
   ioctl(fd, PPDATADIR, &dir);
   frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);
   wait(PP_SETUP_TIMEOUT);
   
   /* Event 39: write NReverseRequest/nInit=0 (start bus reversal) */
   frob_control(fd, PARPORT_CONTROL_INIT, 0);

   /* Event 40: wait nAckReverse/PError=0 */
   wait_status(fd, PARPORT_STATUS_PAPEROUT, 0, PP_SIGNAL_TIMEOUT);

   return 0;
}

int ParDevice::ecp_write_addr(int fd, unsigned char data)
{
   int cnt=0, len=0;
   unsigned d=(data | 0x80); /* set channel address bit */

   ecp_rev_to_fwd(fd);

   /* Event 33: PeriphAck/Busy=0 */
   if (wait_status(fd, PARPORT_STATUS_BUSY, 0, PP_SIGNAL_TIMEOUT))
   {
      syslog(LOG_ERR, "ParDevice::ecp_write_addr transfer stalled: %s %d\n", __FILE__, __LINE__); 
      goto bugout;
   }

   while (1)
   {   
      /* Event 34: write HostAck/nAutoFD=0 (channel command), data */
      frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);
      ioctl(fd, PPWDATA, &d);

      /* Event 35: write HostClk/NStrobe=0 */
      frob_control(fd, PARPORT_CONTROL_STROBE, 0);

      /* Event 36: wait PeriphAck/Busy=1 */
      if (wait_status(fd, PARPORT_STATUS_BUSY, PARPORT_STATUS_BUSY, PP_SIGNAL_TIMEOUT))
      {

         /* Event 72: write NReverseRequest/nInit=0 (Host Transfer Recovery) */
         frob_control(fd, PARPORT_CONTROL_INIT, 0);

         /* Event 73: wait nAckReverse/PError=0 */
         wait_status(fd, PARPORT_STATUS_PAPEROUT, 0, PP_SIGNAL_TIMEOUT);

         /* Event 74: write NReverseRequest/nInit=1 */
         frob_control(fd, PARPORT_CONTROL_INIT, PARPORT_CONTROL_INIT);

         /* Event 75: wait nAckReverse/PError=1 */
         wait_status(fd, PARPORT_STATUS_PAPEROUT, PARPORT_STATUS_PAPEROUT, PP_SIGNAL_TIMEOUT);

         cnt++;
         if (cnt > 4)
         {
            syslog(LOG_ERR, "ParDevice::ecp_write_addr transfer stalled: %s %d\n", __FILE__, __LINE__); 
            goto bugout;
         }
         syslog(LOG_ERR, "ParDevice::ecp_write_addr host transfer recovery cnt=%d: %s %d\n", cnt, __FILE__, __LINE__); 
         continue;  /* retry */
      }
      break;  /* done */
   } /* while (1) */

   len = 1;
      
bugout:

   /* Event 37: write HostClk/NStrobe=1 */
   frob_control(fd, PARPORT_CONTROL_STROBE, PARPORT_CONTROL_STROBE);

   return len;
}

int ParDevice::ecp_write_data(int fd, unsigned char data)
{
   int cnt=0, len=0;

   //   ecp_rev_to_fwd(fd);

   /* Event 33: check PeriphAck/Busy=0 */
   if (wait_status(fd, PARPORT_STATUS_BUSY, 0, PP_SIGNAL_TIMEOUT))
   {
      syslog(LOG_ERR, "ParDevice::ecp_write_data transfer stalled: %s %d\n", __FILE__, __LINE__); 
      goto bugout;
   }

   while (1)
   {   
      /* Event 34: write HostAck/nAutoFD=1 (channel data), data */
      frob_control(fd, PARPORT_CONTROL_AUTOFD, PARPORT_CONTROL_AUTOFD);
      ioctl(fd, PPWDATA, &data);

      /* Event 35: write HostClk/NStrobe=0 */
      frob_control(fd, PARPORT_CONTROL_STROBE, 0);

      /* Event 36: wait PeriphAck/Busy=1 */
      if (wait_status(fd, PARPORT_STATUS_BUSY, PARPORT_STATUS_BUSY, PP_SIGNAL_TIMEOUT))
      {

         /* Event 72: write NReverseRequest/nInit=0 (Host Transfer Recovery) */
         frob_control(fd, PARPORT_CONTROL_INIT, 0);

         /* Event 73: wait nAckReverse/PError=0 */
         wait_status(fd, PARPORT_STATUS_PAPEROUT, 0, PP_SIGNAL_TIMEOUT);

         /* Event 74: write NReverseRequest/nInit=1 */
         frob_control(fd, PARPORT_CONTROL_INIT, PARPORT_CONTROL_INIT);

         /* Event 75: wait nAckReverse/PError=1 */
         wait_status(fd, PARPORT_STATUS_PAPEROUT, PARPORT_STATUS_PAPEROUT, PP_SIGNAL_TIMEOUT);

         cnt++;
         if (cnt > 4)
         {
            syslog(LOG_ERR, "ParDevice::ecp_write_data transfer stalled: %s %d\n", __FILE__, __LINE__); 
            goto bugout;
         }
         syslog(LOG_ERR, "ParDevice::ecp_write_data host transfer recovery cnt=%d: %s %d\n", cnt, __FILE__, __LINE__); 
         continue;  /* retry */
      }
      break;  /* done */
   } /* while (1) */

   len = 1;
      
bugout:

   /* Event 37: write HostClk/NStrobe=1 */
   frob_control(fd, PARPORT_CONTROL_STROBE, PARPORT_CONTROL_STROBE);

   return len;
}

int ParDevice::ecp_read_data(int fd, unsigned char *data)
{
   int len=0;

   //   ecp_fwd_to_rev(fd);

   /* Event 43: wait PeriphClk/NAck=0 */
   if (wait_status(fd, PARPORT_STATUS_ACK, 0, PP_SIGNAL_TIMEOUT))
   {
      len = -1;
      goto bugout;
   }
   ioctl(fd, PPRDATA, data);

   /* Event 44: write HostAck/nAutoFd=1 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, PARPORT_CONTROL_AUTOFD);

   /* Event 45: wait PeriphClk/NAck=1 */
   wait_status(fd, PARPORT_STATUS_ACK, PARPORT_STATUS_ACK, PP_SIGNAL_TIMEOUT);

   /* Event 46: write HostAck/nAutoFd=0 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);

   len = 1;
      
bugout:

   return len;
}

int ParDevice::ecp_read(int fd, void *buffer, int size, int sec)
{
   int i=0;
   unsigned char *p = (unsigned char *)buffer;
   
   ecp_fwd_to_rev(fd);

   while (i < size)
   {
      if (ecp_read_data(fd, p+i) != 1)
      {
         if (sec > 0)
         {
            sec--;
            continue;
	 }
         return -1;
      }
      i++;
   }
   return i;
}

int ParDevice::ecp_write(int fd, const void *buffer, int size)
{
   int i;
   unsigned char *p = (unsigned char *)buffer;
   static int timeout=0;

   if (timeout)
   {
      timeout=0;
      return -1;        /* report timeout */
   }
   
   ecp_rev_to_fwd(fd);

   for (i=0; i < size; i++)
   {
      if (ecp_write_data(fd, p[i]) != 1)
      {
         if (i)
            timeout=1;  /* save timeout, report bytes written */
         else
            i=-1;       /* report timeout */
         break;
      }
   }
   return i;
}

int ParDevice::nibble_read_data(int fd, unsigned char *data)
{
   int len=0;
   unsigned char nibble;   

   /* Event 7: write HostBusy/nAutoFd=0 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);

   /* Event 8: peripheral sets low-order nibble. */

   /* Event 9: wait PtrClk/NAck=0 */
   if (wait_status(fd, PARPORT_STATUS_ACK, 0, PP_SIGNAL_TIMEOUT))
   {
      len = -1;
      goto bugout;
   }
   nibble = read_status(fd) >> 3;
   nibble = ((nibble & 0x10) >> 1) | (nibble & 0x7);
   *data = nibble;

   /* Event 10: write HostBusy/nAutoFd=1 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, PARPORT_CONTROL_AUTOFD);

   /* Event 11: wait PtrClk/NAck=1 */
   wait_status(fd, PARPORT_STATUS_ACK, PARPORT_STATUS_ACK, PP_SIGNAL_TIMEOUT);

   /* Event 7: write HostBusy/nAutoFd=0 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);

   /* Event 8: peripheral sets high-order nibble. */

   /* Event 9: wait PtrClk/NAck=0 */
   if (wait_status(fd, PARPORT_STATUS_ACK, 0, PP_SIGNAL_TIMEOUT))
   {
      len = -1;
      goto bugout;
   }
   nibble = read_status(fd) >> 3;
   nibble = ((nibble & 0x10) >> 1) | (nibble & 0x7);
   *data |= (nibble<<4);

   /* Event 10: write HostBusy/nAutoFd=1 */
   frob_control(fd, PARPORT_CONTROL_AUTOFD, PARPORT_CONTROL_AUTOFD);

   /* Event 11: wait PtrClk/NAck=1 */
   wait_status(fd, PARPORT_STATUS_ACK, PARPORT_STATUS_ACK, PP_SIGNAL_TIMEOUT);

   len = 1;
      
bugout:

   return len;
}

int ParDevice::nibble_read(int fd, int flag, void *buffer, int size, int sec)
{
   int i=0;
   unsigned char *p = (unsigned char *)buffer;
   int m = IEEE1284_MODE_NIBBLE | flag;
   int mc = IEEE1284_MODE_COMPAT;
   unsigned char status;

   ioctl (OpenFD, PPNEGOT, &mc);
   if (ioctl (OpenFD, PPNEGOT, &m))
   {
     //      syslog(LOG_ERR, "ParDevice::nibble_read failed: %m\n");
      goto bugout;
   }

   while (i < size)
   {
      if (nibble_read_data(fd, p+i) != 1)
      {
         if (sec > 0)
         {
            sec--;
            continue;
	 }
         return -1;
      }

      i++;

      /* More data? */
      status = read_status(fd);
      if (status & PARPORT_STATUS_ERROR)
      {
         /* Event 7: write HostBusy/nAutoFd=0, idle phase */
         frob_control(fd, PARPORT_CONTROL_AUTOFD, 0);
         
         break;  /* done */
      }
   }

bugout:
   return i;
}

int ParDevice::compat_write_data(int fd, unsigned char data)
{
   int len=0;

   /* wait Busy=0 */
   if (wait_status(fd, PARPORT_STATUS_BUSY, 0, PP_DEVICE_TIMEOUT))
   {
      syslog(LOG_ERR, "ParDevice::compat_write_data transfer stalled: %s %d\n", __FILE__, __LINE__); 
      goto bugout;
   }

   ioctl(fd, PPWDATA, &data);
   wait(PP_SETUP_TIMEOUT);

   /* write NStrobe=0 */
   frob_control(fd, PARPORT_CONTROL_STROBE, 0);

   /* wait Busy=1 */
   if (wait_status(fd, PARPORT_STATUS_BUSY, PARPORT_STATUS_BUSY, PP_SIGNAL_TIMEOUT))
   {
      syslog(LOG_ERR, "ParDevice::compat_write_data transfer stalled: %s %d\n", __FILE__, __LINE__); 
      goto bugout;
   }

   /* write nStrobe=1 */
   frob_control(fd, PARPORT_CONTROL_STROBE, PARPORT_CONTROL_STROBE);

   len = 1;
      
bugout:
   return len;
}

int ParDevice::compat_write(int fd, const void *buffer, int size)
{
   int i=0;
   unsigned char *p = (unsigned char *)buffer;
   int m = IEEE1284_MODE_COMPAT;
   static int timeout=0;

   if (timeout)
   {
      timeout=0;
      return -1;        /* report timeout */
   }

   if (ioctl(OpenFD, PPNEGOT, &m))
   {
      syslog(LOG_ERR, "ParDevice::compat_read failed: %m\n");
      goto bugout;
   }

   for (i=0; i < size; i++)
   {
      if (compat_write_data(fd, p[i]) != 1)
      {
         if (i)
            timeout=1;  /* save timeout, report bytes written */
         else
            i=-1;       /* report timeout */
         break;
      }
   }

bugout:
   return i;
}

int ParDevice::Write(int fd, const void *buf, int size)
{
   int len=0, m;

   ioctl(OpenFD, PPGETMODE, &m);

   if (m & (IEEE1284_MODE_ECPSWE | IEEE1284_MODE_ECP))
   {
      len = ecp_write(OpenFD, buf, size);
   }
   else
   {  
      len = compat_write(OpenFD, buf, size);
   }

   return len;
}

int ParDevice::Read(int fd, void *buf, int size, int usec)
{
   int len=0, m;
   int sec = usec/1000000;

   ioctl(OpenFD, PPGETMODE, &m);

   if (m & (IEEE1284_MODE_ECPSWE | IEEE1284_MODE_ECP))
   {  
      len = ecp_read(OpenFD, buf, size, sec);
   }
   else
   {
      len = nibble_read(OpenFD, 0, buf, size, sec);
   }

   return len;
}

int ParDevice::DeviceID(char *buffer, int size)
{
   int len=0, maxSize;

   maxSize = (size > 1024) ? 1024 : size;   /* RH8 has a size limit for device id */

   len = nibble_read(OpenFD, IEEE1284_DEVICEID, buffer, maxSize, 0);
   if (len < 0)
   {
     syslog(LOG_ERR, "unable to read ParDevice::DeviceID: %s %d\n", __FILE__, __LINE__);
     len = 0;
     goto bugout;
   }
   if (len > (size-1))
      len = size-1;   /* leave byte for zero termination */
   if (len > 2)
      len -= 2;
   memcpy(buffer, buffer+2, len);    /* remove length */
   buffer[len]=0;

bugout:
   return len; /* length does not include zero termination */
}

int ParDevice::GetDeviceStatus(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceStatusResult\nresult-code=%d\nstatus-code=%d\nstatus-name=%s\n";
   const char eres[] = "msg=DeviceStatusResult\nresult-code=%d\n";
   int len=0;
   unsigned char status;
   char vstatus[16];
   int m;

   *result = R_AOK;

   //   if (pthread_mutex_trylock(&mutex) == 0)
   if (pthread_mutex_lock(&mutex) == 0)
   {
      ioctl(OpenFD, PPGETMODE, &m);
      if (m & (IEEE1284_MODE_ECPSWE | IEEE1284_MODE_ECP))
      {
         status = NFAULT_BIT;        /* channel is busy, fake 8-bit status */
      }
      else
      {
         m = IEEE1284_MODE_COMPAT;
         if (ioctl (OpenFD, PPNEGOT, &m))
         {
            syslog(LOG_ERR, "unable to read ParDevice::GetDeviceStatus: %m\n");
            *result = R_IO_ERROR;
            len = sprintf(sendBuf, eres, *result);  
            goto bugout;
         }
         status = read_status(OpenFD);
      }
      pthread_mutex_unlock(&mutex);
   }
   else
   {
      syslog(LOG_ERR, "unable to lock ParDevice::GetDeviceStatus: %m\n");
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, eres, *result);  
      goto bugout;
   }

   vstatus[0] = 0;
   if (DEVICE_IS_OOP(status))
      strcpy(vstatus, "OutOfPaper");
   if (DEVICE_PAPER_JAMMED(status))
      strcpy(vstatus, "PaperJam");
   if (DEVICE_IO_TRAP(status))
      strcpy(vstatus, "IOTrap");

   if (vstatus[0] == 0)
      len = sprintf(sendBuf, res, *result, status, "NoFault");
   else  
      len = sprintf(sendBuf, res, *result, status, vstatus);

bugout:
   return len;
}

int ParDevice::GetDeviceID(char *sendBuf, int slen, int *result)
{
   const char res[] = "msg=DeviceIDResult\nresult-code=%d\n";
   int len=0, idLen, m;

   *result = R_AOK;

//   if (pthread_mutex_trylock(&mutex) == 0)
   if (pthread_mutex_lock(&mutex) == 0)
   {
      ioctl(OpenFD, PPGETMODE, &m);
      if (m & (IEEE1284_MODE_ECPSWE | IEEE1284_MODE_ECP))
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
      syslog(LOG_ERR, "unable to lock ParDevice::GetDeviceID: %m\n");
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto hijmp;
   }

   if ((idLen + HEADER_SIZE) > slen)
   {
      syslog(LOG_ERR, "invalid device id size ParDevice::GetDeviceID: %d\n", idLen);
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

//ParDevice::NewChannel
//!  Create channel object given the requeste socket id and service name.
/*!
******************************************************************************/
Channel *ParDevice::NewChannel(unsigned char sockid, char *sn)
{
   Channel *pC=NULL;
   int i, n, mode;

   /* Check for existing name service already open. */
   for (i=1, n=0; i<MAX_CHANNEL && n<ChannelCnt; i++)
   {
      if (pChannel[i] != NULL)
      {
         n++;
         if (strcasecmp(sn, pChannel[i]->GetService()) == 0)
         {
            if (sockid == PML_CHANNEL)
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

   /* Get requested IO mode. */
   if (sockid == PRINT_CHANNEL)
      mode = GetPrintMode();
   else
      mode = GetMfpMode();

   /* Make sure requested io mode matches any current io mode. */
   if (ChannelCnt && ChannelMode != mode)
      goto bugout;  /* requested io mode does not match current */

   /* Look for unused slot in channel array. Note, slot 0 is unused. */
   for (i=1; i<MAX_CHANNEL; i++)
   {
      if (pChannel[i] == NULL)
      {
         if (mode == RAW_MODE)
            pC = new RawChannel(this);  /* constructor sets ClientCnt=1 */
         else if (mode == MLC_MODE)
            pC = new ParMlcChannel(this);  /* constructor sets ClientCnt=1 */
         else
            pC = new ParDot4Channel(this);  /* constructor sets ClientCnt=1 */

         pC->SetIndex(i);
         pC->SetSocketID(sockid);
         pC->SetService(sn);
         pChannel[i] = pC;
         ChannelCnt++;
         ChannelMode = mode;
         break;
      }
   }     

bugout:
   return pC;
}

int ParDevice::Open(char *sendBuf, int *result)
{
   char dev[255];
   char uriModel[128];
   char model[128];
   int len=0, m;

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
         syslog(LOG_ERR, "unable to ParDevice::Open %s: %m: %s %d\n", URI, __FILE__, __LINE__);
         goto blackout;
      }

      /* Silently check the port for valid device (no syslog errors during ProbeDevices). */
      if (ioctl(OpenFD, PPGETMODES, &m))
      {
         *result = R_IO_ERROR;
         if (strcmp(uriModel, "ANY") != 0)
            syslog(LOG_ERR, "unable to ParDevice::Open %s: %m: %s %d\n", URI, __FILE__, __LINE__);
         goto blackout;
      }

      if (ioctl(OpenFD, PPCLAIM))
      {
         *result = R_IO_ERROR;
         syslog(LOG_ERR, "unable to claim port ParDevice::Open %s: %m\n", URI);
         goto blackout;
      }

      len = DeviceID(ID, sizeof(ID));  /* get new copy and cache it  */ 

      if (len == 0)
      {
         *result = R_IO_ERROR;
         goto blackout;
      }

      if (pSys->IsHP(ID) && strcmp(uriModel, "ANY") != 0)
      {
         PowerUp();
      }
   }

   /* Make sure uri model matches device id model. Ignor test if uri model equals "ANY" (probe). */
   if (strcmp(uriModel, "ANY") != 0)
   {
      pSys->GetModel(ID, model, sizeof(model));
      if (strcmp(uriModel, model) != 0)
      {
         *result = R_INVALID_DEVICE_NODE;  /* probably a laserjet, or different device plugged in */  
         syslog(LOG_ERR, "invalid model %s != %s ParDevice::Open\n", uriModel, model);
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

int ParDevice::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceCloseResult\nresult-code=%d\n";
   int len=0;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is still in use */

   if (OpenFD >=0 && ClientCnt==1)
   {
      ioctl(OpenFD, PPRELEASE);
      close(OpenFD);

      /* Reset variables here while locked, don't count on constructor with threads. */
      OpenFD = -1;
      ID[0] = 0;
   }

   pthread_mutex_unlock(&mutex);

bugout:
   len = sprintf(sendBuf, res, *result);  

   return len;
}

#endif /* HAVE_PPORT */


