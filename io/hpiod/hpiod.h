/*****************************************************************************\

  hpiod.h - definitions for hpiod
 
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

#ifndef _HPIOD_H
#define _HPIOD_H

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <sys/time.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <signal.h>
#include <ctype.h>
#include <pthread.h>
#ifdef HAVE_PPORT
#include <linux/parport.h>
#include <linux/ppdev.h>
#endif
#include "list.h"
#include "usbext.h"

//#define HPIOD_DEBUG

#define RCFILE "/etc/hp/hplip.conf" /* The config file */
//#define PIDFILE "/var/run/hplip/hpiod.pid" /* The pidfile */
//#define PORTFILE "/var/run/hplip/hpiod.port" 
#define PIDFILE "hpiod.pid" /* The pidfile */
#define PORTFILE "hpiod.port" 
#define LINE_SIZE 256     /* Length of a line. */
#define BUFFER_SIZE 8192  /* General Read/Write buffer. */
#define MAX_DEVICE 16     /* Max devices. */
#define MAX_CHANNEL 8     /* Max channels per device. */
//#define HEADER_SIZE 256   /* Rough estimate of hpiod message header */
#define HEADER_SIZE 4096   /* Rough estimate of hpiod message header */
#define EXCEPTION_TIMEOUT 45000000  /* microseconds */

#define LIBUSB_TIMEOUT 30000              /* milliseconds */
#define LIBUSB_CONTROL_REQ_TIMEOUT 5000

typedef struct
{
   char cmd[LINE_SIZE];
   char uri[LINE_SIZE];
   char service[LINE_SIZE];   /* service-name */
   char ip[LINE_SIZE];    /* internet IP */ 
   int ip_port;
   int prt_mode;          
   int mfp_mode;
   int flow_ctl;
   int scan_port;
   char dnode[LINE_SIZE];   /* device node */
   int descriptor;       /* device descriptor (device-id) */
   int jobid;
   int length;           /* length of data in bytes */
   int result;
   int channel;          /* channel descriptor (channel-id) */
   int readlen;          /* bytes-to-read (ChannelDataIn) */
   int timeout;
   char oid[LINE_SIZE];       /* snmp oid */
   int type;             /* pml type */
   int pml_result; 
   char bus[LINE_SIZE];
   char usb_bus[16];             /* usbfs bus number */
   char usb_device[16];          /* usbfs device number */
   unsigned char *data;       /* pointer to data */
} MsgAttributes;

typedef struct
{
  int sockid;
  int descriptor;             /* device used */
  pthread_t tid;              /* thread id */
  int channel[MAX_CHANNEL];  /* channels used */
  struct list_head list;
} SessionAttributes;

#define IOCNR_GET_DEVICE_ID     1
#define IOCNR_GET_PROTOCOLS      2
#define IOCNR_SET_PROTOCOL    3
#define IOCNR_HP_SET_CHANNEL     4
#define IOCNR_GET_BUS_ADDRESS    5
#define IOCNR_GET_VID_PID     6

#define LPIOC_GET_DEVICE_ID(len) _IOC(_IOC_READ, 'P', IOCNR_GET_DEVICE_ID, len)
#define LPIOC_GET_PROTOCOLS _IOC(_IOC_READ,'P',IOCNR_GET_PROTOCOLS,sizeof(int[2]))
#define LPIOC_SET_PROTOCOL _IOC(_IOC_WRITE,'P',IOCNR_SET_PROTOCOL,0)
#define LPIOC_HP_SET_CHANNEL _IOC(_IOC_WRITE,'P',IOCNR_HP_SET_CHANNEL,0)
#define LPIOC_GET_BUS_ADDRESS _IOC(_IOC_READ,'P',IOCNR_GET_BUS_ADDRESS,sizeof(int[2]))
#define LPIOC_GET_VID_PID _IOC(_IOC_READ,'P',IOCNR_GET_VID_PID,sizeof(int[2]))

#define USB_PROTOCOL_711 1 
#define USB_PROTOCOL_712 2 
#define USB_PROTOCOL_713 3 

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

#if defined(WORDS_BIGENDIAN)
#define htole16(A) ((((uint16_t)(A) & 0xff00) >> 8) | (((uint16_t)(A) & 0x00ff) << 8))    /* host to little-endian 16-bit value */
#define letoh16 htole16                         /* little-endian to host 16-bit value */
#define htole32(A) ((((uint32_t)(A) & (uint32_t)0x000000ff) << 24) | (((uint32_t)(A) & (uint32_t)0x0000ff00) << 8) | \
                  (((uint32_t)(A) & (uint32_t)0x00ff0000) >> 8) | (((uint32_t)(A) & (uint32_t)0xff000000) >> 24))
#define letoh32 htole32
#else
#define htole16(A) (A)
#define letoh16(A) (A)
#define letoh32(A) (A)
#define htole32(A) (A)
#endif

enum RESULT_CODE
{
   R_AOK = 0,
   R_INVALID_DEVICE = 2,
   R_INVALID_DESCRIPTOR = 3,
   R_INVALID_URI = 4,
   R_INVALID_MESSAGE = 5,
   R_INVALID_LENGTH = 8,
   R_IO_ERROR = 12,
   R_NO_CUPS_PRINTERS = 17,
   R_DEVICE_BUSY = 21,
   R_NO_CUPS_SERVER = 25,
   R_INVALID_SN = 28,
   R_INVALID_CHANNEL_ID = 30,
   R_CHANNEL_BUSY = 31,
   R_INVALID_DEVICE_OPEN = 37,
   R_INVALID_DEVICE_NODE = 38,
   R_INVALID_IP = 45,
   R_INVALID_IP_PORT = 46,
   R_INVALID_TIMEOUT = 47         
};

enum CHANNEL_ID  /* MLC socket ids */ 
{
   PML_CHANNEL = 1,
   PRINT_CHANNEL = 2,
   SCAN_CHANNEL = 4,
   ECHO_CHANNEL = 6,
   FAX_SEND_CHANNEL = 7,
   CONFIG_UPLOAD_CHANNEL = 0xe,
   CONFIG_DOWNLOAD_CHANNEL = 0xf,
   MEMORY_CARD_CHANNEL = 0x11,
   EWS_CHANNEL = 0x12          /* Embeded Web Server interface ff/1/1, any unused socket id */
};
#define MAX_SOCKETID EWS_CHANNEL+1  /* must be largest numeric socketid + 1 */

void sysdump(void *data, int size);

extern int HpiodPortNumber;               /* IP port number */
extern char HpiodPidFile[];             /* full pid file path */
extern char HpiodPortFile[];             /* full port file path */

#include "system.h"
#include "device.h"
#include "channel.h"
#include "mlc.h"
#include "dot4.h"

#endif // _HPIOD_H

