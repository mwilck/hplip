/*****************************************************************************\

  ptest.c - HP MFP photo card file manager
 
  (c) 2004 Copyright Hewlett-Packard Development Company, LP

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

\*****************************************************************************/

#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <syslog.h>
#include <stdarg.h>
#include <signal.h>
#include <arpa/inet.h>
#include <errno.h>
#include <ctype.h>
#include "ptest.h"
#include "fat.h"
#include "hplip_api.h"

#define DEV_ACK 0x0100

typedef struct
{
   short cmd;
   unsigned short nsector;
} __attribute__((packed)) CMD_READ_REQUEST;

typedef struct{
   short cmd;
   unsigned short nsector;
   short cs;         /* check sum is not used */
} __attribute__((packed)) CMD_WRITE_REQUEST;

typedef struct
{
   short cmd;
   uint32_t nsector;
   short ver;
} __attribute__((packed)) RESPONSE_SECTOR;

static HplipSession *hplip_session;
static int hd=-1, channel=-1;

int verbose=0;
 
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

int last_slash(const char *path, int *number_found, int *path_size)
{
   int i, found=0, lasti=0;

   /* Find last '/'. */
   for (i=0; path[i] && i<HPLIP_LINE_SIZE; i++)
      if (path[i] == '/')
      {
         found++;
         lasti=i;
      }

   *number_found = found;
   *path_size = i;

   return lasti;
} 

int nth_slash(const char *path, int n)
{
   int i, found=0, lasti=0;

   /* Find nth '/'. */
   for (i=0; path[i] && i<HPLIP_LINE_SIZE; i++)
      if (path[i] == '/')
      {
         found++;
         lasti=i;
         if (found == n)
           break;
      }

   return lasti;
} 

char *basename(const char *path)
{
   int len, found=0, slash_index=0;

   slash_index = last_slash(path, &found, &len);
   return found ? (char *)path+slash_index+1 : (char *)path; 
}

int dirname(const char *path, char *dir)
{
   int len, found=0, slash_index=0;

   slash_index = last_slash(path, &found, &len);

   if (found == 0)
      strcpy(dir, ".");              /* no '/' */
   else if (path[slash_index+1]==0 && found==1)
      strcpy(dir, "/");              /* '/' only */
   else if (path[slash_index+1]==0 && found>1)
   {
      slash_index = nth_slash(path, found-1);   /* trailing '/', backup */
      strncpy(dir, path, slash_index);
      dir[slash_index]=0;
   }
   else
   {
      strncpy(dir, path, slash_index);      /* normal '/' */
      dir[slash_index]=0;
   }
   return slash_index;  /* return length of dir */
}

int GetDir(char *path, char *dir, char **tail)
{
   int i=0;

   dir[0] = 0;

   if (path[0] == 0)
   {
      strcpy(dir, ".");   /* end of path */
      i = 0;
   }
   else if ((path[0] == '/') && (*tail != path))
   {
      strcpy(dir, "/");          /* found root '/' at beginning of path */
      i=1;
   }                 
   else
   {
      for (i=0; path[i] && (path[i] != '/') && (i<HPLIP_LINE_SIZE); i++)   /* copy directory entry */
         dir[i] = path[i];
      if (i==0)
         strcpy(dir, ".");   /* end of path */
      else
         dir[i] = 0;
      if (path[i] == '/')
         i++;  /* bump past '/' */
   }

   if (tail != NULL)
      *tail = path + i;  /* tail points to next directory or 0 */

   return i;
}

int DevDiscovery(char *uri, int urisize)
{
   char message[HPLIP_LINE_SIZE*64];  
   int i, len=0;  
   HplipMsgAttributes ma;
   char *pBeg;
 
   uri[0] = 0;

   len = sprintf(message, "msg=ProbeDevices\n");
 
   if (send(hplip_session->hpiod_socket, message, len, 0) == -1) 
   {  
      bug("unable to send ProbeDevices: %m\n");  
      goto mordor;  
   }  

   if ((len = recv(hplip_session->hpiod_socket, message, sizeof(message), 0)) == -1) 
   {  
      bug("unable to receive ProbeDevicesResult: %m\n");  
      goto mordor;
   }  

   message[len] = 0;

   hplip_ParseMsg(message, len, &ma);
   if (ma.result == R_AOK && ma.length)
   {
      if (verbose > 0)
      {
         len = ma.length;
         fprintf(stderr, "%s", ma.data);
      }

      if (ma.ndevice == 1)
      {
         /* Only one device connected make this the default uri. */
         for (i=0; (strncmp((char *)&ma.data[i], "hp:", 3) != 0) && (i < HPLIP_LINE_SIZE); i++)  /* find start of uri */
            ;
         pBeg = (char *)ma.data + i;
         for (i=0; *pBeg != ' ' && (i < urisize); i++, pBeg++)  /* copy uri */
            uri[i] = *pBeg;
         uri[i] = 0;      /* zero terminate */
      }
   }

mordor:
   return len;
}

int ReadSector(int sector, int nsector, void *buf, int size)
{
   char message[HPLIP_HEADER_SIZE];
   int i, len, rlen, stat=1, total=0;
   CMD_READ_REQUEST *pC;
   RESPONSE_SECTOR *pR;
   uint32_t *pSect;
   short cmd=0x0010;  /* read request */
   
   if (nsector <= 0 || (nsector*FAT_HARDSECT) > size)
   {
      bug("ReadSector invalid sector count=%d\n", nsector);
      goto bugout;
   }
      
   /* Write photo card command to device. */
   pC = (CMD_READ_REQUEST *)message;
   pC->cmd = htons(cmd);
   pC->nsector = htons(nsector);
   pSect = (uint32_t *)(message + sizeof(CMD_READ_REQUEST));
   for (i=0; i<nsector; i++)
     *pSect++ = htonl(sector+i);
   len = sizeof(CMD_READ_REQUEST)+(4*nsector);
   hplip_WriteHP(hplip_session, hd, channel, message, len);

   /* Read photo card response header from device. */
   memset(message, 0, sizeof(RESPONSE_SECTOR));
   rlen = sizeof(RESPONSE_SECTOR);
   len = hplip_ReadHP(hplip_session, hd, channel, message, rlen, HPLIP_EXCEPTION_TIMEOUT); 
   pR = (RESPONSE_SECTOR *)message;
   if (ntohs(pR->cmd) != (cmd | DEV_ACK))
   {
      bug("ReadSector invalid response header cmd=%x expected=%x\n", ntohs(pR->cmd), cmd | DEV_ACK);
      goto bugout;
   }      

   if (verbose > 0)
   {
      static int cnt=0;
      if (cnt++ < 1)
         fprintf(stderr, "photo card firmware version=%x\n", ntohs(pR->ver));   
   }

   /* Read photo card sector data from device. */
   rlen = nsector*FAT_HARDSECT;
   while (total < rlen)
   { 
      if ((len = hplip_ReadHP(hplip_session, hd, channel, buf+total, rlen, HPLIP_EXCEPTION_TIMEOUT)) == 0)
         break;  /* timeout */
      total+=len;
   }

   if (total != rlen)
   {
      bug("ReadSector invalid response data len=%d expected=%d\n", total, rlen);
      goto bugout;
   }      

   stat = 0;

bugout:
   return stat;    
}

int WriteSector(int sector, int nsector, void *buf, int size)
{
   char message[HPLIP_HEADER_SIZE];
   int i, len, stat=1;
   CMD_WRITE_REQUEST *pC;
   uint32_t *pSect;
   short response=0, cmd=0x0020;  /* write request */

   if (nsector <= 0 || (nsector*FAT_HARDSECT) > size)
   {
      bug("WriteSector invalid sector count=%d\n", nsector);
      goto bugout;
   }
      
   /* Write photo card command header to device. */
   pC = (CMD_WRITE_REQUEST *)message;
   pC->cmd = htons(cmd);
   pC->nsector = htons(nsector);
   pC->cs = 0;
   pSect = (uint32_t *)(message + sizeof(CMD_WRITE_REQUEST));
   for (i=0; i<nsector; i++)
     *pSect++ = htonl(sector+i);
   len = sizeof(CMD_WRITE_REQUEST)+(4*nsector);
   hplip_WriteHP(hplip_session, hd, channel, message, len);

   /* Write photo card sector data to device. */
   hplip_WriteHP(hplip_session, hd, channel, buf, size);

   /* Read response. */
   len = hplip_ReadHP(hplip_session, hd, channel, (char *)&response, sizeof(response), HPLIP_EXCEPTION_TIMEOUT); 
   if (ntohs(response) != DEV_ACK)
   {
      bug("WriteSector invalid response cmd=%x expected=%x\n", ntohs(response), DEV_ACK);
      goto bugout;
   }      
   stat = 0;

bugout:
   return stat;    
}

void usage()
{
   fprintf(stdout, "HP MFP Photo Card File Manager %s\n", VERSION);
   fprintf(stdout, "(c) 2004 Copyright Hewlett-Packard Development Company, LP\n");
   fprintf(stdout, "usage: ptest [-v] [-u uri] -c ls [-p path]  (list directory)\n");
   fprintf(stdout, "       ptest [-v] [-u uri] -c read -p path  (read file to stdout)\n");
   fprintf(stdout, "       ptest [-v] [-u uri] -c rm -p path    (delete file)\n");
   //   fprintf(stdout, "       ptest [-v] -u uri -c write -p path   (write stdin to file)\n");
}

int main(int argc, char *argv[])
{
   char cmd[16] = "", path[HPLIP_LINE_SIZE]="", uri[HPLIP_LINE_SIZE]="", dir[HPLIP_LINE_SIZE]="", spath[HPLIP_LINE_SIZE]="";
   extern char *optarg;
   char *tail;
   int i, stat=-1;
   PHOTO_CARD_ATTRIBUTES pa;
   HplipMsgAttributes ma;

   while ((i = getopt(argc, argv, "vhu:c:p:")) != -1)
   {
      switch (i)
      {
      case 'c':
         strncpy(cmd, optarg, sizeof(cmd));
         break;
      case 'p':
         strncpy(path, optarg, sizeof(path));
         break;
      case 'u':
         strncpy(uri, optarg, sizeof(uri));
         break;
      case 'v':
         verbose++;
         break;
      case 'h':
         usage();
         exit(0);
      case '?':
         usage();
         fprintf(stderr, "unknown argument: %s\n", argv[1]);
         exit(-1);
      default:
         break;
      }
   }

   hplip_Init(&hplip_session);

   if (uri[0] == 0)
      DevDiscovery(uri, sizeof(uri));
   if (uri[0] == 0)
   {
      bug("invalid uri %s or more than one device connected\n", uri);
      goto bugout;
   }   

   /* Get any parameters needed for DeviceOpen. */
   hplip_ModelQuery(uri, &ma);  

   if ((hd = hplip_OpenHP(hplip_session, uri, &ma)) < 0)
   {
      bug("unable to open device %s\n", uri);
      goto bugout;
   }   
   if ((channel = hplip_OpenChannel(hplip_session, hd, "HP-CARD-ACCESS")) < 0)
   {
      bug("unable to open hp-card-access channel %s\n", uri);
      goto bugout;
   }

   if (FatInit() != 0)
   {
      bug("unable to read photo card %s\n", uri);
      goto bugout;
   }

   FatDiskAttributes(&pa);

   /* If disk is write protected reopen channel to clear write error. */
   if (pa.WriteProtect)
   {
      hplip_CloseChannel(hplip_session, hd, channel);
      if ((channel = hplip_OpenChannel(hplip_session, hd, "HP-CARD-ACCESS")) < 0)
      {
         bug("unable to open hp-card-access channel %s\n", uri);
         goto bugout;
      }
   }

   if (strcasecmp(cmd, "ls") == 0)
   {
      /* Walk the path for each directory entry. */
      GetDir(path, dir, &tail);
      FatSetCWD(dir);
      while (tail[0] != 0)
      {
         GetDir(tail, dir, &tail);
         FatSetCWD(dir);
      }
      FatListDir();
   }
   else if (strcasecmp(cmd, "read") == 0)
   {
      dirname(path, spath);       /* extract directory */
      GetDir(spath, dir, &tail);
      FatSetCWD(dir);
      while (tail[0] != 0)
      {
         GetDir(tail, dir, &tail);
         FatSetCWD(dir);
      }    
      if ((FatReadFile(basename(path), STDOUT_FILENO)) <= 0)
      {
         bug("unable to locate file %s\n", path);
         goto bugout;
      }
   }
   else if (strcasecmp(cmd, "rm") == 0)
   {
      dirname(path, spath);       /* extract directory */
      GetDir(spath, dir, &tail);
      FatSetCWD(dir);
      while (tail[0] != 0)
      {
         GetDir(tail, dir, &tail);
         FatSetCWD(dir);
      }    
      if (FatDeleteFile(basename(path)) != 0)
      {
         bug("unable to locate file %s\n", path);
         goto bugout;
      }
   }
   else
   {
      usage();  /* invalid command */
      goto bugout;
   }   

   stat = 0;

bugout:
   if (channel >= 0)
      hplip_CloseChannel(hplip_session, hd, channel);
   if (hd >= 0)
      hplip_CloseHP(hplip_session, hd);   
   hplip_Exit(hplip_session);  

   exit (stat);
}

