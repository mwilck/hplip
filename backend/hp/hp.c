/*****************************************************************************\

  hp.c - hp cups backend 
 
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

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>
#include <syslog.h>
#include "hplip_api.h"

#define RETRY_TIMEOUT 30  /* seconds */

#define NFAULT_BIT  0x08
#define PERROR_BIT  0x20

#define OOP             (NFAULT_BIT | PERROR_BIT)
#define JAMMED          (PERROR_BIT)
#define ERROR_TRAP      (0)

#define STATUS_MASK (NFAULT_BIT | PERROR_BIT)

#define DEVICE_IS_OOP(reg)  ((reg & STATUS_MASK) == OOP)
#define DEVICE_PAPER_JAMMED(reg)  ((reg & STATUS_MASK) == JAMMED)
#define DEVICE_IO_TRAP(reg)       ((reg & STATUS_MASK) == ERROR_TRAP)

#define HEX2INT(x, i) if (x >= '0' && x <= '9')      i |= x - '0'; \
                       else if (x >= 'A' && x <= 'F') i |= 0xA + x - 'A'; \
                       else if (x >= 'a' && x <= 'f') i |= 0xA + x - 'a'

/* Actual vstatus codes are mapped to 1000+vstatus for DeviceError messages. */ 
typedef enum
{
   VSTATUS_IDLE = 1000,
   VSTATUS_BUSY,
   VSTATUS_PRNT,      /* io printing */
   VSTATUS_OFFF,      /* turning off */
   VSTATUS_RPRT,      /* report printing */
   VSTATUS_CNCL,      /* canceling */
   VSTATUS_IOST,      /* io stall */
   VSTATUS_DRYW,      /* dry time wait */
   VSTATUS_PENC,      /* pen change */
   VSTATUS_OOPA,      /* out of paper */
   VSTATUS_BNEJ,      /* banner eject needed */
   VSTATUS_BNMZ,      /* banner mismatch */
   VSTATUS_PHMZ,      /* photo mismatch */
   VSTATUS_DPMZ,      /* duplex mismatch */
   VSTATUS_PAJM,      /* media jam */
   VSTATUS_CARS,      /* carriage stall */
   VSTATUS_PAPS,      /* paper stall */
   VSTATUS_PENF,      /* pen failure */
   VSTATUS_ERRO,      /* hard error */
   VSTATUS_PWDN,      /* power down */
   VSTATUS_FPTS,      /* front panel test */
   VSTATUS_CLNO       /* clean out tray missing */
} VSTATUS;


#define EVENT_START_JOB 500
#define EVENT_END_JOB 501

int bug(const char *fmt, ...)
{
   char buf[256];
   va_list args;
   int n;

   va_start(args, fmt);

   if ((n = vsnprintf(buf, 256, fmt, args)) == -1)
      buf[255] = 0;     /* output was truncated */

   fprintf(stderr, buf);
   syslog(LOG_WARNING, buf);

   fflush(stderr);
   va_end(args);
   return n;
}

/* Parse URI record from buf. Assumes one record per line. All returned strings are zero terminated. */
int GetUriLine(char *buf, char *uri, char *model, char *description, char **tail)
{
   int i=0, j;
   int maxBuf = LINE_SIZE*64;

   uri[0] = 0;
   model[0] = 0;
   description[0] = 0;
   
   if (strncasecmp(&buf[i], "direct ", 7) == 0)
   {
      i = 7;
      j = 0;
      for (; buf[i] == ' ' && i < maxBuf; i++);  /* eat white space before string */
      while ((buf[i] != ' ') && (i < maxBuf) && (j < LINE_SIZE))
         uri[j++] = buf[i++];
      uri[j] = 0;

      j = 0;
      for (; buf[i] == ' ' && i < maxBuf; i++);  /* eat white space before string */
      model[j++] = buf[i++];               /* get first " */
      while ((buf[i] != '"') && (i < maxBuf) && (j < LINE_SIZE))
         model[j++] = buf[i++];          
      model[j++] = buf[i++];               /* get last " */
      model[j] = 0;

      j = 0;
      for (; buf[i] == ' ' && i < maxBuf; i++);  /* eat white space before string */
      while ((buf[i] != '\n') && (i < maxBuf) && (j < LINE_SIZE))
         description[j++] = buf[i++];
      description[j] = 0;
   }
   else
   {
      for (; buf[i] != '\n' && i < maxBuf; i++);  /* eat line */
   }

   i++;   /* bump past '\n' */

   if (tail != NULL)
      *tail = buf + i;  /* tail points to next line */

   return i;
}

const char *GetVStatusMessage(VSTATUS status)
{
   char *p;

   /* Map VStatus to text message. TODO: text needs to be localized. */
   switch(status)
   {
      case(VSTATUS_IDLE):
         p = "ready to print";
         break;
      case(VSTATUS_BUSY):
         p = "busy";
         break;
      case(VSTATUS_PRNT):
         p = "i/o printing";
         break;
      case(VSTATUS_OFFF):
         p = "turning off";
         break;
      case(VSTATUS_RPRT):
         p = "report printing";
         break;
      case(VSTATUS_CNCL):
         p = "canceling";
         break;
      case(VSTATUS_IOST):
         p = "incomplete job";
         break;
      case(VSTATUS_DRYW):
         p = "dry time wait";
         break;
      case(VSTATUS_PENC):
         p = "pen change";
         break;
      case(VSTATUS_OOPA):
         p = "out of paper";
         break;
      case(VSTATUS_BNEJ):
         p = "banner eject needed";
         break;
      case(VSTATUS_BNMZ):
         p = "banner mismatch";
         break;
      case(VSTATUS_DPMZ):
         p = "duplex mismatch";
         break;
      case(VSTATUS_PAJM):
         p = "media jam";
         break;
      case(VSTATUS_CARS):
         p = "carriage stall";
         break;
      case(VSTATUS_PAPS):
         p = "paper stall";
         break;
      case(VSTATUS_PENF):
         p = "pen failure";
         break;
      case(VSTATUS_ERRO):
         p = "hard error";
         break;
      case(VSTATUS_PWDN):
         p = "power down";
         break;
      case(VSTATUS_FPTS):
         p = "front panel test";
         break;
      case(VSTATUS_CLNO):
         p = "clean out tray missing";
         break;
      case(5000+R_IO_ERROR):
         p = "check device";
         break;
      default:
         p = "unknown state";
         bug("INFO: printer state=%d\n", status);
         break;
   }
   return p;
}

int GetVStatus(int hd)
{
   char id[1024];
   char *pSf;
   int vstatus=VSTATUS_IDLE, ver;

   if (hplip_GetID(hd, id, sizeof(id)) == 0)
   {
      vstatus = 5000+R_IO_ERROR;      /* no deviceid, return some error */
      goto bugout;
   }
   
   /* Check for valid S-field in device id string. */
   if ((pSf = strstr(id, ";S:")) == NULL)
   {
      /* No S-field, use status register instead of device id. */ 
      unsigned char status;
      hplip_GetStatus(hd, (char *)&status, 1);      
      if (DEVICE_IS_OOP(status))
         vstatus = VSTATUS_OOPA;
      else if (DEVICE_PAPER_JAMMED(status))
         vstatus = VSTATUS_PAJM;
      else if (DEVICE_IO_TRAP(status))
         vstatus = VSTATUS_CARS;
      else
         vstatus = 5000+R_IO_ERROR;      /* nothing in status, return some error */
   }
   else
   {
      /* Valid S-field, get version number. */
      pSf+=3;
      ver = 0; 
      HEX2INT(*pSf, ver);
      pSf++;
      ver = ver << 4;
      HEX2INT(*pSf, ver);
      pSf++;

      /* Position pointer to printer state subfield. */
      switch (ver)
      {
         case 0:
         case 1:
         case 2:
            pSf+=12;
            break;
         case 3:
            pSf+=14;
            break;
         case 4:
            pSf+=18;
            break;
         default:
            bug("WARNING: unknown S-field version=%d\n", ver);
            pSf+=12;
            break;            
      }

      /* Extract VStatus.*/
      vstatus = 0; 
      HEX2INT(*pSf, vstatus);
      pSf++;
      vstatus = vstatus << 4;
      HEX2INT(*pSf, vstatus);
      vstatus += 1000;
   }

bugout:
   return vstatus;
}

int DevDiscovery()
{
   char message[LINE_SIZE*64];
   char uri[LINE_SIZE];
   char model[LINE_SIZE];
   char description[LINE_SIZE];
   char id[1024];
   char *tail;
   int i, len=0, cnt=0, hd=-1;  
   MsgAttributes ma, ma2;
 
   len = sprintf(message, "msg=ProbeDevices\n");
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send ProbeDevices: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ProbeDevicesResult: %m\n");  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);

   if (ma.result == R_AOK && ma.length)
   {
      cnt = ma.ndevice;

      /* Add deviceID for CUPS 1.2, if available. */
      tail = ma.data;
      for (i=0; i<cnt; i++)
      {
         id[0] = 0;
         GetUriLine(tail, uri, model, description, &tail);
         hplip_ModelQuery(uri, &ma2);   /* get DeviceOpen parameters */
         if ((hd = hplip_OpenHP(uri, &ma2)) >= 0)
         {
            hplip_GetID(hd, id, sizeof(id));
            hplip_CloseHP(hd);   
         }
         fprintf(stdout, "direct %s %s %s \"%s\"\n", uri, model, description, id);
      }
   }

   if (cnt == 0)
      fprintf(stdout, "direct hp:/no_device_found \"Unknown\" \"hp no_device_found\"\n");

mordor:
   return cnt;
}

int PState()
{
   char message[LINE_SIZE*64];  
   int len=0;
   MsgAttributes ma;
 
   len = sprintf(message, "msg=PState\n");
 
   if (send(hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send PState: %m\n");  
      goto bugout;  
   }  

   if ((len = recv(hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive PStateResult: %m\n");  
      goto bugout;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);

   len = 0;
   if (ma.result == R_AOK && ma.length)
   {
      len = ma.length;
      fprintf(stdout, "%s", ma.data);
   }

bugout:
   return len;
}

int DeviceEvent(char *dev, char *jobid, int code, char *type, int timeout)
{
   char message[512];  
   int len=0;
 
   if (hpssd_socket < 0)
      goto mordor;  

   if (timeout == 0)
      len = sprintf(message, "msg=Event\ndevice-uri=%s\njob-id=%s\nevent-code=%d\nevent-type=%s\n", dev, jobid, code, type);
   else
      len = sprintf(message, "msg=Event\ndevice-uri=%s\njob-id=%s\nevent-code=%d\nevent-type=%s\nretry-timeout=%d\n", 
                     dev, jobid, code, type, timeout);
 
   /* Send message with no response. */
   if (send(hpssd_socket, message, len, 0) == -1) 
   {  
      bug("unable to send Event %s %s %d: %m\n", dev, jobid, code);
   }  

mordor:

   return 0;
}

int main(int argc, char *argv[])
{
   int fd;
   int copies;
   int len, vstatus, cnt;
   char buf[BUFFER_SIZE+HEADER_SIZE];
   MsgAttributes ma;

   if (argc > 1)
   {
      const char *arg = argv[1];
      if ((arg[0] == '-') && (arg[1] == 'h'))
      {
         fprintf(stdout, "HP Linux Imaging and Printing System\nCUPS Backend %s\n", VERSION);
         fprintf(stdout, "(c) 2003-2004 Copyright Hewlett-Packard Development Company, LP\n");
         exit(0);
      }
      if ((arg[0] == '-') && (arg[1] == 's'))
      {
         hplip_Init();
         PState();
         hplip_Exit();
         exit(0);
      }
   }

   if (argc == 1)
   {
      hplip_Init();
      DevDiscovery();
      hplip_Exit();
      exit (0);
   }

   if (argc < 6 || argc > 7)
   {
      bug("ERROR: invalid usage: device_uri job-id user title copies options [file]\n");
      exit (1);
   }

   if (argc == 6)
   {
      fd = 0;         /* use stdin. */
      copies = 1;
   }
   else
   {
      if ((fd = open(argv[6], O_RDONLY)) < 0)  /* use specified file */ 
      {
         bug("ERROR: unable to open print file %s: %m\n", argv[6]);
         exit (1);
      }
      copies = atoi(argv[4]);
   }

   int hd=-1, channel=-1, n, total, retry=0, size;

   hplip_Init();

   /* Get any parameters needed for DeviceOpen. */
   hplip_ModelQuery(argv[0], &ma);  

   DeviceEvent(argv[0], argv[1], EVENT_START_JOB, "event", 0);

   /* Open hp device. */
   do
   {
      if ((hd = hplip_OpenHP(argv[0], &ma)) < 0)
      {
         /* Display user error. */
         DeviceEvent(argv[0], argv[1], 5000+R_IO_ERROR, "error", RETRY_TIMEOUT);

         bug("INFO: open device failed; will retry in %d seconds...\n", RETRY_TIMEOUT);
         sleep(RETRY_TIMEOUT);
         retry = 1;
      }
   }
   while (hd < 0);

   if (retry)
   {
      /* Clear user error. */
      DeviceEvent(argv[0], argv[1], VSTATUS_PRNT, "event", 0);
      retry=0;
   }

   /* Write print file. */
   while (copies > 0)
   {
      copies--;

      if (fd != 0)
      {
         fputs("PAGE: 1 1\n", stderr);
         lseek(fd, 0, SEEK_SET);
      }

      while ((len = read(fd, buf, BUFFER_SIZE)) > 0)
      {
         size=len;
         total=0;

         while (size > 0)
         {
            /* Got some data now open the print channel. This will handle any HPIJS print channel contention. */
            if (channel < 0)
            {
               do
               {
                  if ((channel = hplip_OpenChannel(hd, "PRINT")) < 0)
                  {
                     DeviceEvent(argv[0], argv[1], 5000+R_CHANNEL_BUSY, "error", RETRY_TIMEOUT);
                     bug("INFO: open print channel failed; will retry in %d seconds...\n", RETRY_TIMEOUT);
                     sleep(RETRY_TIMEOUT);
                     retry = 1;
                  }
               }
               while (channel < 0);

               if (retry)
               {
                  /* Clear user error. */
                  DeviceEvent(argv[0], argv[1], VSTATUS_PRNT, "event", 0);
                  retry=0;
               }
            }

            n = hplip_WriteHP(hd, channel, buf+total, size);

            if (n != size)
            {
               /* IO error, get printer status. */
               vstatus = GetVStatus(hd);

               /* Display user error. */
               DeviceEvent(argv[0], argv[1], vstatus, "error", RETRY_TIMEOUT);

               bug("INFO: %s; will retry in %d seconds...\n", GetVStatusMessage(vstatus), RETRY_TIMEOUT);
               sleep(RETRY_TIMEOUT);
               retry = 1;

            }
            total+=n;
            size-=n;
         }

         if (retry)
         {
            /* Clear user error. */
            DeviceEvent(argv[0], argv[1], VSTATUS_PRNT, "event", 0);
            retry=0;
         }
      }
   } /* while (copies > 0) */

   /* Wait for I/O to complete over the wire. */
   sleep(2);

   /* If not uni-di mode, monitor printer status and wait for I/O to finish. */
   if (ma.prt_mode != UNI_MODE)
   {
      /*
       * Since hpiod uses non-blocking i/o (bi-di) we must make sure the printer has received all data
       * before closing the print channel. Otherwise data will be lost.
       */
      vstatus = GetVStatus(hd);
      if (vstatus < 5000)
      {
         /* Got valid status, wait for idle. */
         cnt=0;
         while ((vstatus != VSTATUS_IDLE) && (vstatus < 5000) && (cnt < 5))
         {
           sleep(2);
           vstatus = GetVStatus(hd);
           cnt++;
         } 
      }
      else
      {
         /* No valid status, use fixed delay. */
         sleep(8);
      }
   }
   
   DeviceEvent(argv[0], argv[1], EVENT_END_JOB, "event", 0);
   fprintf(stderr, "INFO: %s\n", GetVStatusMessage(VSTATUS_IDLE));

   if (channel >= 0)
      hplip_CloseChannel(hd, channel);
   if (hd >= 0)
      hplip_CloseHP(hd);   
   hplip_Exit();
   if (fd != 0)
      close(fd);

   exit (0);
}

