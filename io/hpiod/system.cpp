/*****************************************************************************\

  system.cpp - class provides common system services 
 
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

#ifdef HAVE_LIBSNMP
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/types.h>
#endif

static const char ERR_MSG[] = "msg=MessageError\nresult-code=%d\n";
static const char *SnmpPort[] = { "","public.1","public.2","public.3" };
const char *kStatusOID = "1.3.6.1.4.1.11.2.3.9.1.1.7.0";            /* device id oid */

System::System()
{
   struct sockaddr_in sin;
   int i, len, fd;
   int yes=1;
   char buf[128];

   /* Set some defaults. */
   DeviceCnt = 0;
   Reset = 0;

   INIT_LIST_HEAD(&head.list);

   pthread_mutex_init(&mutex, NULL); /* create fast mutex */

   usb_init();

   for (i=0; i<MAX_DEVICE; i++)
      pDevice[i] = NULL;

   /* Create permanent socket. */
   Permsd = socket(AF_INET, SOCK_STREAM, 0);
   if (Permsd == -1)
   {
      syslog(LOG_ERR, "unable to open permanent socket: %m\n");  
      exit(EXIT_FAILURE);
   }

   /* Get rid of "address already in use" error message. */
   if (setsockopt(Permsd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1)
   {
      syslog(LOG_ERR, "unable to setsockopt: %m\n");
      exit(EXIT_FAILURE);
   }

   bzero(&sin, sizeof(sin));
   sin.sin_family = AF_INET;
//   sin.sin_addr.s_addr = INADDR_ANY;
   sin.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
   sin.sin_port = htons(HpiodPortNumber);

   if (bind(Permsd, (struct sockaddr *)&sin, sizeof(sin)) == -1) 
   {
      syslog(LOG_ERR, "unable to bind socket %d: %m\n", HpiodPortNumber);
      exit(EXIT_FAILURE);
   }

   /* Verify port assignment, could be dynamic (port=0). */
   len = sizeof(sin);
   getsockname(Permsd,(struct sockaddr *)&sin, (socklen_t *)&len);
   HpiodPortNumber = ntohs(sin.sin_port);

   if (listen(Permsd, 20) == -1) 
   {
      syslog(LOG_ERR, "unable to listen socket %d: %m\n", HpiodPortNumber);
      exit(EXIT_FAILURE);
   }

   if((fd = open(HpiodPortFile, O_CREAT | O_TRUNC | O_WRONLY, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)) < 0)
   {
      syslog(LOG_ERR, "unable create %s: %m\n", HpiodPortFile);
      exit(EXIT_FAILURE);
   }

   len = sprintf(buf, "%d\n", HpiodPortNumber);
   write(fd, buf, len);
   close(fd);

   syslog(LOG_INFO, "%s accepting connections at %d...\n", VERSION, HpiodPortNumber); 
}

System::~System()
{
   int i;

   for (i=0; i<MAX_DEVICE; i++)
   {
      if (pDevice[i] != NULL)
      {
         delete pDevice[i];
      }
   }

   pthread_mutex_destroy(&mutex);
   close(Permsd);
}

//System::GetPair
//!  Get key value pair from buffer. Assumes one key value pair per line.
//!  Note, end-of-line '/n' is stripped out. Both key/value pairs are zero
//!  terminated.
/*!
******************************************************************************/
int System::GetPair(char *buf, char *key, char *value, char **tail)
{
   int i=0, j;

   key[0] = 0;
   value[0] = 0;

   if (buf[i] == '#')
   {
      for (; buf[i] != '\n' && i < HEADER_SIZE; i++);  /* eat comment line */
      i++;
   }

   if (strncasecmp(&buf[i], "data:", 5) == 0)
   {
      strcpy(key, "data:");   /* "data:" key has no value */
      i+=5;
   }   
   else
   {
      j = 0;
      while ((buf[i] != '=') && (i < HEADER_SIZE) && (j < LINE_SIZE))
         key[j++] = buf[i++];
      for (j--; key[j] == ' ' && j > 0; j--);  /* eat white space before = */
      key[++j] = 0;

      for (i++; buf[i] == ' ' && i < HEADER_SIZE; i++);  /* eat white space after = */

      j = 0;
      while ((buf[i] != '\n') && (i < HEADER_SIZE) && (j < LINE_SIZE))
         value[j++] = buf[i++];
      for (j--; value[j] == ' ' && j > 0; j--);  /* eat white space before \n */
      value[++j] = 0;
   }

   i++;   /* bump past '\n' */

   if (tail != NULL)
      *tail = buf + i;  /* tail points to next line */

   return i;
}

//System::IsHP
//! Given the IEEE 1284 device id string, determine if this is a HP product.
/*!
******************************************************************************/
int System::IsHP(char *id)
{
   char *pMf;

   if ((pMf = strstr(id, "MFG:")) != NULL)
      pMf+=4;
   else if ((pMf = strstr(id, "MANUFACTURER:")) != NULL)
      pMf+=13;
   else
      return 0;

   if ((strncasecmp(pMf, "HEWLETT-PACKARD", 15) == 0) ||
      (strncasecmp(pMf, "APOLLO", 6) == 0) || (strncasecmp(pMf, "HP", 2) == 0))
   {
      return 1;  /* found HP product */
   }
   return 0;   
}

//System::IsUdev
//! Given a usb or parallel device node, determine if this is a udev node (a non-legacy device node).
/*!
******************************************************************************/
int System::IsUdev(char *dnode)
{
   char *p, *tail;
   int n;

   if ((p = strstr(dnode, "/dev/usb/lp")) == NULL)
      return 1;

   p+=11;
   n = strtol(p, &tail, 10);
   if (n < 0 || n > 15)
     return 1;

   if ((p = strstr(dnode, "/dev/parport")) == NULL)
      return 1;

   p+=12;
   n = strtol(p, &tail, 10);
   if (n < 0 || n > 3)
     return 1;

   return 0; /* looks like a legacy device node */
}

int System::GeneralizeModel(char *sz, char *buf, int bufSize)
{
   char *pMd=sz;
   int i, j, dd=0;

   for (i=0; pMd[i] == ' ' && i < bufSize; i++);  /* eat leading white space */

   for (j=0; (pMd[i] != 0) && (pMd[i] != ';') && (j < bufSize); i++)
   {
      if (pMd[i]==' ' || pMd[i]=='/')
      {
         /* Remove double spaces. */
         if (!dd)
         { 
            buf[j++] = '_';   /* convert space to "_" */
            dd=1;              
         }
      }
      else
      {
         buf[j++] = pMd[i];
         dd=0;       
      }
   }

   for (j--; pMd[j] == '_' && j > 0; j--);  /* eat trailing white space */

   buf[++j] = 0;

   return j;   /* length does not include zero termination */
}

int System::GeneralizeSerial(char *sz, char *buf, int bufSize)
{
   char *pMd=sz;
   int i, j;

   for (i=0; pMd[i] == ' ' && i < bufSize; i++);  /* eat leading white space */

   for (j=0; (pMd[i] != 0) && (i < bufSize); i++)
   {
      buf[j++] = pMd[i];
   }

   for (i--; pMd[i] == '_' && i > 0; i--);  /* eat trailing white space */

   buf[++i] = 0;

   return i;   /* length does not include zero termination */
}

//System::GetModel
//! Parse the model from the IEEE 1284 device id string.
/*!
******************************************************************************/
int System::GetModel(char *id, char *buf, int bufSize)
{
   char *pMd;

   buf[0] = 0;

   if ((pMd = strstr(id, "MDL:")) != NULL)
      pMd+=4;
   else if ((pMd = strstr(id, "MODEL:")) != NULL)
      pMd+=6;
   else
      return 0;

   return GeneralizeModel(pMd, buf, bufSize);
}

#if 0
//System::GetSerialNum
//! Parse the serial number from the IEEE 1284 device id string.
/*!
******************************************************************************/
int System::GetSerialNum(char *id, char *buf, int bufSize)
{
   char *pSN;
   int i;

   buf[0] = 0;

   if ((pSN = strstr(id, "SERN:")) != NULL)
      pSN+=5;
   else if ((pSN = strstr(id, "SN:")) != NULL)
      pSN+=3;
   else
      return 0;

   for (i=0; (pSN[i] != ';') && (i < bufSize); i++)
      buf[i] = pSN[i];
   buf[i] = 0;

   return i;
}
#endif

//System::GetUriDataLink
//! Parse the data link from a uri string.
/*!
******************************************************************************/
int System::GetURIDataLink(char *uri, char *buf, int bufSize)
{
   char *p;
   int i;

   buf[0] = 0;

   if ((p = strcasestr(uri, "device=")) != NULL)
      p+=7;
   else if ((p = strcasestr(uri, "ip=")) != NULL)
      p+=3;
   else
      return 0;

   for (i=0; (p[i] != 0) && (p[i] != '&') && (i < bufSize); i++)
      buf[i] = p[i];

   buf[i] = 0;

   return i;
}

//System::GetURIModel
//! Parse the model from a uri string.
/*!
******************************************************************************/
int System::GetURIModel(char *uri, char *buf, int bufSize)
{
   char *p;
   int i;

   buf[0] = 0;

   if ((p = strstr(uri, "/")) == NULL)
      return 0;
   if ((p = strstr(p+1, "/")) == NULL)
      return 0;
   p++;

   for (i=0; (p[i] != '?') && (i < bufSize); i++)
      buf[i] = p[i];

   buf[i] = 0;

   return i;
}

//System::GetURISerial
//! Parse the serial number from a uri string.
/*!
******************************************************************************/
int System::GetURISerial(char *uri, char *buf, int bufSize)
{
   char *p;
   int i;

   buf[0] = 0;

   if ((p = strcasestr(uri, "serial=")) != NULL)
      p+=7;
   else
      return 0;

   for (i=0; (p[i] != 0) && (p[i] != '+') && (i < bufSize); i++)
      buf[i] = p[i];

   buf[i] = 0;

   return i;
}

int System::ValidURI(MsgAttributes *ma)
{
   if (strcasestr(ma->uri, "hp:") == NULL && strcasestr(ma->uri, "hpfax:") == NULL && strcasestr(ma->uri, "hpaio:") == NULL)
      return 0;  /* invalid uri */

   if (strcasestr(ma->uri, ":/usb") == NULL && strcasestr(ma->uri, ":/net") == NULL && strcasestr(ma->uri, ":/par") == NULL)
      return 0;  /* invalid uri */

   if (strcasestr(ma->uri, "ip=") != NULL)
      return 1;  /* uri is all ready generalized */

   if (strcasestr(ma->uri, "device=") != NULL && strcasestr(ma->uri, ":/usb") != NULL)
      return 0;  /* invalid uri, /dev/usb/lpxx devices are no longer suppported  */
   
   return 1;
}

/* Check for USB interface descriptor with specified class. */
int System::IsInterface(struct usb_device *dev, int dclass)
{
   struct usb_interface_descriptor *pi;
   int i, j, k;

   for (i=0; i<dev->descriptor.bNumConfigurations; i++)
   {
      for (j=0; j<dev->config[i].bNumInterfaces; j++)
      {
         for (k=0; k<dev->config[i].interface[j].num_altsetting; k++)
         {
            pi = &dev->config[i].interface[j].altsetting[k];
            if (pi->bInterfaceClass == dclass)
            {
               return 1;            /* found interface */
            }
         }
      }
   }
   return 0;    /* no interface found */
}

/* Walk the USB bus(s) looking for HP products. */
int System::UsbDiscovery(char *lst, int *cnt)
{
   struct usb_bus *bus;
   struct usb_device *dev;
   usb_dev_handle *hd;
   char model[128];
   char serial[128];
   char sz[256];
   int size=0;

   usb_find_busses();
   usb_find_devices();

   for (bus=usb_busses; bus; bus=bus->next)
   {
      for (dev=bus->devices; dev; dev=dev->next)
      {
         if ((hd = usb_open(dev)) == NULL)
         {
            syslog(LOG_ERR, "invalid usb_open: %m %s %d\n", __FILE__, __LINE__);
            continue;
         }

         model[0] = serial[0] = sz[0] = 0;

         if (dev->descriptor.idVendor == 0x3f0 && IsInterface(dev, 7))
         {
            /* Found hp device. */
            if (usb_get_string_simple(hd, dev->descriptor.iProduct, sz, sizeof(sz)) < 0)
               syslog(LOG_ERR, "invalid product id string: %m %s %d\n", __FILE__, __LINE__);
            else
               GeneralizeModel(sz, model, sizeof(model));

            if (usb_get_string_simple(hd, dev->descriptor.iSerialNumber, sz, sizeof(sz)) < 0)
               syslog(LOG_ERR, "invalid serial id string: %m %s %d\n", __FILE__, __LINE__);
            else
               GeneralizeSerial(sz, serial, sizeof(serial));

            if (!serial[0])
               strcpy(serial, "0"); /* no serial number, make it zero */

            if (model[0])
            {
               sprintf(sz, "hp:/usb/%s?serial=%s", model, serial);
               size += sprintf(lst+size,"direct %s \"HP %s\" \"%s\"\n", sz, model, sz);
               *cnt+=1;
            }
	 }
         usb_close(hd);
      }
   }

   return size;
}

#ifdef HAVE_PPORT
//System::ParDiscovery
//! Walk the parallel ports looking for HP products. 
/*!
******************************************************************************/
int System::ParDiscovery(char *lst, int *cnt)
{
   MsgAttributes ma2;
   char dev[255];
   char model[128];
   char sendBuf[2048];
   char *id;
   int i, len, size=0, result;
   Device *pD;

   for (i=0; i < 4; i++)
   {
      ma2.prt_mode = RAW_MODE;
      sprintf(ma2.uri, "hp:/par/ANY?device=/dev/parport%d", i);

      pD = NewDevice(&ma2);
      len = pD->Open(sendBuf, &result);
      if (result == R_AOK)
      {
         id = pD->GetID(); /* use cached copy */

         if (id[0] != 0 && IsHP(id))
         {
            GetModel(id, model, sizeof(model));
            sprintf(dev, "hp:/par/%s?device=/dev/parport%d", model, i);
            size += sprintf(lst+size,"direct %s \"HP %s\" \"%s\"\n", dev, model, dev);
            *cnt+=1;
         }
      }

      pD->Close(sendBuf, &result);
      DelDevice(pD->GetIndex());
   }

   return size;
}
#else
int System::ParDiscovery(char *lst, int *cnt)
{
   return 0;
}
#endif

//System::ProbeDevices
//!  Perform hp device discovery. Works simultaneously with other open clients.
/*!
******************************************************************************/
int System::ProbeDevices(char *sendBuf, char *bus)
{
   char lst[LINE_SIZE*MAX_DEVICE];
   int len, lstLen, cnt=0;

   lst[0] = 0;

   if (strcasecmp(bus, "usb") == 0)
   {
      lstLen = UsbDiscovery(lst, &cnt);
   }
   else if (strcasecmp(bus, "par") == 0)
   {
      lstLen = ParDiscovery(lst, &cnt);
   }
   else
   {
      lstLen = UsbDiscovery(lst, &cnt);
      lstLen += ParDiscovery(lst+lstLen, &cnt);
   }

   len = sprintf(sendBuf, "msg=ProbeDevicesResult\nresult-code=%d\nnum-devices=%d\nlength=%d\ndata:\n%s", R_AOK, cnt, lstLen, lst); 

   return len;
}

int System::PState(char *sendBuf)
{
   char lst[LINE_SIZE*MAX_DEVICE];
   int i, n, lstLen=0, len;
   Device *pD;
   struct list_head *p;
   SessionAttributes *psa;

   lst[0]=0;

   for (i=1, n=0; i<MAX_DEVICE && n<DeviceCnt; i++)
   {
      if (pDevice[i] != NULL)
      {
         n++;
         pD = pDevice[i];
         lstLen += sprintf(lst+lstLen, "d[%d] fd=%d clientcnt=%d chancnt=%d mlcup=%d iomode=%s mfpmode=%s %s\n", i, 
                pD->GetOpenFD(), pD->GetClientCnt(), pD->GetChannelCnt(), pD->GetMlcUp(), 
                pD->GetPrintMode()==0 ? "uni-di" : pD->GetPrintMode()==1 ? "raw" :  pD->GetPrintMode()==2 ? "mlc" :  pD->GetPrintMode()==3 ? "dot4" :  pD->GetMfpMode()==4 ? "dot4P" : "???",
                pD->GetMfpMode()==2 ? "mlc" : pD->GetMfpMode()==3 ? "dot4" : pD->GetMfpMode()==4 ? "dot4P" : "???",
                pD->GetURI());
      }
   }

   list_for_each(p, &head.list)
   {
      psa = list_entry(p, SessionAttributes, list);
      lstLen += sprintf(lst+lstLen, "t[%d] d[%d] socket=%d\n", (int)psa->tid, psa->descriptor, psa->sockid);   
   }

   len = sprintf(sendBuf, "msg=PStateResult\nresult-code=%d\nlength=%d\ndata:\n%s", R_AOK, lstLen, lst); 

   return len;
}

int System::PmlOidToHex(char *szoid, unsigned char *oid, int oidSize)
{
   char *tail;
   int i=0, val;

   if (szoid[0] == 0)
      goto bugout;

   val = strtol(szoid, &tail, 10);

   while (i < oidSize)
   {
      if (val > 128)
      {
         syslog(LOG_ERR, "unable to System::PmlOidToHex: oid=%s\n", szoid);
         goto bugout;
      }
      oid[i++] = (unsigned char)val;

      if (*tail == 0)
         break;         /* done */

      val = strtol(tail+1, &tail, 10);
   }

bugout:
   return i;
}

int System::SnmpToPml(char *snmp_oid, unsigned char *oid, int oidSize)
{
   static const char hp_pml_mib_prefix[] = "1.3.6.1.4.1.11.2.3.9.4.2";
   static const char standard_printer_mib_prefix[] = "1.3.6.1.2.1.43";
   static const char host_resource_mib_prefix[] = "1.3.6.1.2.1.25";
   int len=0;

   if (strncmp(snmp_oid, hp_pml_mib_prefix, sizeof(hp_pml_mib_prefix)-1) == 0)
   {
      /* Strip out snmp prefix and convert to hex. */
      len = 0;
      len += PmlOidToHex(&snmp_oid[sizeof(hp_pml_mib_prefix)], &oid[0], oidSize);
      len--; /* remove trailing zero in pml mib */
   }
   else if   (strncmp(snmp_oid, standard_printer_mib_prefix, sizeof(standard_printer_mib_prefix)-1) == 0)
   {
      /* Replace snmp prefix with 2 and convert to hex. */
      len = 1;
      oid[0] = 0x2;
      len += PmlOidToHex(&snmp_oid[sizeof(standard_printer_mib_prefix)], &oid[1], oidSize);  
   }
   else if   (strncmp(snmp_oid, host_resource_mib_prefix, sizeof(host_resource_mib_prefix)-1) == 0)
   {
      /* Replace snmp prefix with 3 and convert to hex. */
      len = 1;
      oid[0] = 0x3;
      len += PmlOidToHex(&snmp_oid[sizeof(host_resource_mib_prefix)], &oid[1], oidSize);
   }
   else
      syslog(LOG_ERR, "unable to System::SnmpToPml: snmp oid=%s\n", snmp_oid);

   return len;
}

#ifdef HAVE_LIBSNMP

int System::SnmpErrorToPml(int snmp_error)
{
   int err;

   switch (snmp_error)
   {
      case SNMP_ERR_NOERROR:
         err = PML_EV_OK;
         break;
      case SNMP_ERR_TOOBIG:
         err = PML_EV_ERROR_BUFFER_OVERFLOW;
         break;
      case SNMP_ERR_NOSUCHNAME:
         err = PML_EV_ERROR_UNKNOWN_OBJECT_IDENTIFIER;
         break;
      case SNMP_ERR_BADVALUE:
         err = PML_EV_ERROR_INVALID_OR_UNSUPPORTED_VALUE;
         break;
      case SNMP_ERR_READONLY:
         err = PML_EV_ERROR_OBJECT_DOES_NOT_SUPPORT_REQUESTED_ACTION;
         break;
      case SNMP_ERR_GENERR:
      default:
         err = PML_EV_ERROR_UNKNOWN_REQUEST;
         break;
   }

   return err;
}

int System::SetSnmp(char *ip, int port, char *szoid, int type, unsigned char *buffer, unsigned int size, int *pml_result, int *result)
{
   struct snmp_session session, *ss=NULL;
   struct snmp_pdu *pdu=NULL;
   struct snmp_pdu *response=NULL;
   oid anOID[MAX_OID_LEN];
   size_t anOID_len = MAX_OID_LEN;
   unsigned int i, len=0;
   uint32_t val;

   *result = R_IO_ERROR;
   *pml_result = PML_EV_ERROR_UNKNOWN_REQUEST;

   init_snmp("snmpapp");

   snmp_sess_init(&session );                   /* set up defaults */
   session.peername = ip;
   session.version = SNMP_VERSION_1;
   session.community = (unsigned char *)SnmpPort[port];
   session.community_len = strlen((const char *)session.community);
   ss = snmp_open(&session);                     /* establish the session */
   if (ss == NULL)
      goto bugout;

   pdu = snmp_pdu_create(SNMP_MSG_SET);
   read_objid(szoid, anOID, &anOID_len);

   switch (type)
   {
      case PML_DT_ENUMERATION:
      case PML_DT_SIGNED_INTEGER:
         /* Convert PML big-endian to SNMP little-endian byte stream. */
         for(i=0, val=0; i<size && i<sizeof(val); i++)    
            val = ((val << 8) | buffer[i]);
         snmp_pdu_add_variable(pdu, anOID, anOID_len, ASN_INTEGER, (unsigned char *)&val, sizeof(val));
         break;
      case PML_DT_REAL:
      case PML_DT_STRING:
      case PML_DT_BINARY:
      case PML_DT_NULL_VALUE:
      case PML_DT_COLLECTION:
      default:
         snmp_pdu_add_variable(pdu, anOID, anOID_len, ASN_OCTET_STR, buffer, size);
         break;
   }

  
   /* Send the request and get response. */
   if (snmp_synch_response(ss, pdu, &response) != STAT_SUCCESS)
      goto bugout;

   if (response->errstat == SNMP_ERR_NOERROR) 
   {
      len = size;
   }

   *pml_result = SnmpErrorToPml(response->errstat);
   *result = R_AOK;

bugout:
   if (response != NULL)
      snmp_free_pdu(response);
   if (ss != NULL)
      snmp_close(ss);
   return len;
}

int System::GetSnmp(char *ip, int port, char *szoid, unsigned char *buffer, unsigned int size, int *type, int *pml_result, int *result)
{
   struct snmp_session session, *ss=NULL;
   struct snmp_pdu *pdu=NULL;
   struct snmp_pdu *response=NULL;
   unsigned int i, len=0;
   oid anOID[MAX_OID_LEN];
   size_t anOID_len = MAX_OID_LEN;
   struct variable_list *vars;
   uint32_t val;
   unsigned char tmp[sizeof(uint32_t)];

   *result = R_IO_ERROR;
   *type = PML_DT_NULL_VALUE;
   *pml_result = PML_EV_ERROR_UNKNOWN_REQUEST;

   init_snmp("snmpapp");

   snmp_sess_init(&session );                   /* set up defaults */
   session.peername = ip;
   session.version = SNMP_VERSION_1;
   session.community = (unsigned char *)SnmpPort[port];
   session.community_len = strlen((const char *)session.community);
   session.retries = 2;
   session.timeout = 1000000;         /* 1 second */
   ss = snmp_open(&session);                     /* establish the session */
   if (ss == NULL)
      goto bugout;

   pdu = snmp_pdu_create(SNMP_MSG_GET);
   read_objid(szoid, anOID, &anOID_len);
   snmp_add_null_var(pdu, anOID, anOID_len);
  
   /* Send the request and get response. */
   if (snmp_synch_response(ss, pdu, &response) != STAT_SUCCESS)
      goto bugout;

   if (response->errstat == SNMP_ERR_NOERROR) 
   {
      vars = response->variables;
      switch (vars->type)
      {
         case ASN_INTEGER:
            *type = PML_DT_SIGNED_INTEGER;

            /* Convert SNMP little-endian to PML big-endian byte stream. */
            len = (sizeof(uint32_t) < size) ? sizeof(uint32_t) : size;
            val = *vars->val.integer;
            for(i=len; i>0; i--)
            {
               tmp[i-1] = val & 0xff;
               val >>= 8;
            }

            /* Remove any in-significant bytes. */
            for (; tmp[i]==0 && i<len; i++)
               ;
            len -= i;

            memcpy(buffer, tmp+i, len);
            break;
         case ASN_NULL:
            *type = PML_DT_NULL_VALUE;
            break;
         case ASN_OCTET_STR:
            *type = PML_DT_STRING;
            len = (vars->val_len < size) ? vars->val_len : size;
            memcpy(buffer, vars->val.string, len);
            break;
         default:
            syslog(LOG_ERR, "unable to System::GetSnmp: data type=%d\n", vars->type);
            goto bugout;
            break;
      }
   }

   *pml_result = SnmpErrorToPml(response->errstat);
   *result = R_AOK;

bugout:
   if (response != NULL)
      snmp_free_pdu(response);
   if (ss != NULL)
      snmp_close(ss);
   return len;
}

#else

int System::SetSnmp(char *ip, int port, char *szoid, int type, unsigned char *buffer, unsigned int size, int *pml_result, int *result)
{
   syslog(LOG_ERR, "no JetDirect support enabled\n");
   return 0;
}

int System::GetSnmp(char *ip, int port, char *szoid, unsigned char *buffer, unsigned int size, int *type, int *pml_result, int *result)
{
   syslog(LOG_ERR, "no JetDirect support enabled\n");
   return 0;
}

#endif /* HAVE_LIBSNMP */


//System::SetPml
//!  Set a PML object in the hp device. 
/*!
******************************************************************************/
int System::SetPml(int device, int channel, char *snmp_oid, int type, unsigned char *data, int dataLen, char *sendBuf)
{
   const char res[] = "msg=SetPMLResult\nresult-code=%d\n";
   char message[BUFFER_SIZE];
   unsigned char oid[LINE_SIZE];
   unsigned char *p=(unsigned char *)message;
   int len, dLen, result, reply, status;
   MsgAttributes ma;
   Device *pD=pDevice[device];

   if (dataLen > 1024)
   {
      syslog(LOG_ERR, "unable to System::SetPml: data size=%d\n", dataLen);
      len = sprintf(sendBuf, res, R_IO_ERROR);
      goto bugout;       
   }   
      
   if (strcasestr(pD->GetURI(), "net/") != NULL)
   {
      /* Process pml via snmp. */
      SetSnmp(((JetDirectDevice *)pD)->GetIP(), ((JetDirectDevice *)pD)->GetPort(), snmp_oid, type, data, dataLen, &status, &result);
      if (result != R_AOK)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }
   }       
   else
   {
      /* Process pml via local transport. */

      /* Convert snmp oid to pml oid. */
      dLen = SnmpToPml(snmp_oid, oid, sizeof(oid));
   
      *p++ = PML_SET_REQUEST;
      *p++ = PML_DT_OBJECT_IDENTIFIER;
      *p++ = dLen;                          /* assume oid length is < 10 bits */
      memcpy(p, oid, dLen);
      p+=dLen;
      *p = type;
      *p |= dataLen >> 8;                   /* assume data length is 10 bits */
      *(p+1) = dataLen & 0xff;    
      p += 2; 
      memcpy(p, data, dataLen);

      len = pD->WriteData((unsigned char *)message, dLen+dataLen+3+2, channel, message, &result);  
      if (result != R_AOK)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }    

      len = pD->ReadData(PML_MAX_DATALEN, channel, EXCEPTION_TIMEOUT, message, sizeof(message), &result);
      if (result != R_AOK || len == 0)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }    

      ParseMsg(message, len, &ma);

      p = ma.data;
      reply = *p++;       /* read command reply */
      status = *p++;      /* read execution outcome */

      if (reply != (PML_SET_REQUEST | 0x80) && status & 0x80)
      {
         syslog(LOG_ERR, "unable to execute System::SetPml: reply=%x outcome=%x\n", reply, status);
         sysdump(p, ma.length-2);
         len = sprintf(sendBuf, "msg=SetPMLResult\nresult-code=%d\npml-result-code=%d\n", R_IO_ERROR, status); 
         goto bugout;       
      }   
   }
   
   len = sprintf(sendBuf, "msg=SetPMLResult\nresult-code=%d\npml-result-code=%d\n", R_AOK, status); 

bugout:
   return len;
}

//System::GetPml
//!  Get a PML object from the hp device.
/*!
******************************************************************************/
int System::GetPml(int device, int channel, char *snmp_oid, char *sendBuf)
{
   const char res[] = "msg=GetPMLResult\nresult-code=%d\n";
   char message[BUFFER_SIZE];
   unsigned char oid[LINE_SIZE];
   //   unsigned char cmd[LINE_SIZE+3];
   unsigned char *p=(unsigned char *)message;
   int len, dLen, result, reply, status, dt;
   MsgAttributes ma;
   Device *pD=pDevice[device];

   if (strcasestr(pD->GetURI(), "net/") != NULL)
   {
      /* Process pml via snmp. */
      dLen = GetSnmp(((JetDirectDevice *)pD)->GetIP(), ((JetDirectDevice *)pD)->GetPort(), snmp_oid, (unsigned char *)message, sizeof(message), &dt, &status, &result);
      if (result != R_AOK)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }
      p = (unsigned char *)message;    
   }       
   else
   {
      /* Process pml via local transport. */

      /* Convert snmp oid to pml oid. */
      dLen = SnmpToPml(snmp_oid, oid, sizeof(oid));
   
      *p++ = PML_GET_REQUEST;
      *p++ = PML_DT_OBJECT_IDENTIFIER;
      *p++ = dLen;                          /* assume oid length is < 10 bits */
      memcpy(p, oid, dLen);
      len = pD->WriteData((unsigned char *)message, dLen+3, channel, message, &result);  
      if (result != R_AOK)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }    

      len = pD->ReadData(PML_MAX_DATALEN, channel, EXCEPTION_TIMEOUT, message, sizeof(message), &result);
      if (result != R_AOK || len == 0)
      {
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }    

      ParseMsg(message, len, &ma);

      p = ma.data;
      reply = *p++;       /* read command reply */
      status = *p++;      /* read execution outcome */

      if (reply != (PML_GET_REQUEST | 0x80) && status & 0x80)
      {
         syslog(LOG_ERR, "unable to execute System::GetPml: reply=%x outcome=%x\n", reply, status);
         sysdump(p, ma.length-2);
         len = sprintf(sendBuf, "msg=GetPMLResult\nresult-code=%d\npml-result-code=%d\n", R_IO_ERROR, status); 
         goto bugout;       
      }   

      dt = *p++;       /* read data type */

      if (dt == PML_DT_ERROR_CODE)
      {
         /* Ok, but invalid data type requested, get new data type. */
         p += 2;       /* eat length and err code */
         dt = *p++;  /* read data type */
      } 

      if (dt != PML_DT_OBJECT_IDENTIFIER)
      {
         syslog(LOG_ERR, "invald data type System::GetPml: type=%x\n", dt);
         len = sprintf(sendBuf, res, R_IO_ERROR);
         goto bugout;       
      }   

      dLen = *p++;     /* read oid length */
      p += dLen;       /* eat oid */

      dt = *p;    /* read data type. */
      dLen = ((*p & 0x3) << 8 | *(p+1));         /* read 10 bit len from 2 byte field */
      p += 2;                               /* eat type and length */
   }
   
   len = sprintf(sendBuf, "msg=GetPMLResult\nresult-code=%d\npml-result-code=%d\ntype=%d\nlength=%d\ndata:\n", R_AOK, status, dt, dLen); 
   memcpy(&sendBuf[len], p, dLen);
   len += dLen; 

bugout:
   return len;
}

//System::MakeUriFromIP
//!  Given an IP address read deviceID and create valid URI.
/*!
******************************************************************************/
int System::MakeUriFromIP(char *ip, int port, char *sendBuf)
{
   const char res[] = "msg=MakeURIResult\nresult-code=%d\n";
   int len=0, result, dt, status;
   char devid[1024];
   char model[128];

   if (ip[0]==0)
   {
      syslog(LOG_ERR, "invalid ip %s System::MakeUriFromIP\n", ip);
      len = sprintf(sendBuf, res, R_INVALID_IP);
      goto bugout;
   }

   if ((len = GetSnmp(ip, port, (char *)kStatusOID, (unsigned char *)devid, sizeof(devid), &dt, &status, &result)) == 0)
   {
      syslog(LOG_ERR, "unable to read System::MakeUriFromIP\n");
      len = sprintf(sendBuf, res, R_IO_ERROR);
      goto bugout;
   }

   if (IsHP(devid))
   {
      GetModel(devid, model, sizeof(model));
      if (port == 1)
         len = sprintf(sendBuf, "msg=MakeURIResult\nresult-code=%d\ndevice-uri=hp:/net/%s?ip=%s\n", R_AOK, model, ip); 
      else
         len = sprintf(sendBuf, "msg=MakeURIResult\nresult-code=%d\ndevice-uri=hp:/net/%s?ip=%s&port=%d\n", R_AOK, model, ip, port); 
   }

bugout:
   return len;
}

//System::MakeUriFromUsb
//!  Given a device node read deviceID and create valid URI.
/*!
******************************************************************************/
int System::MakeUriFromUsb(char *busnum, char *devnum, char *sendBuf)
{
   const char res[] = "msg=MakeURIResult\nresult-code=%d\n";
   struct usb_bus *bus;
   struct usb_device *dev, *found_dev=NULL;
   usb_dev_handle *hd=NULL;
   char model[128];
   char serial[128];
   char sz[256];
   int len;

   usb_find_busses();
   usb_find_devices();

   for (bus=usb_busses; bus; bus=bus->next)
      if (strcmp(bus->dirname, busnum) == 0)
         for (dev=bus->devices; dev; dev=dev->next)
	    if (strcmp(dev->filename, devnum) == 0)
                found_dev = dev;  /* found usb device that matches bus:device */

   if (found_dev == NULL)
   {
      syslog(LOG_ERR, "invalid busnum:devnum %s:%s %s %d\n", busnum, devnum, __FILE__, __LINE__);
      len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);
      goto bugout;
   }

   dev = found_dev;
   if ((hd = usb_open(dev)) == NULL)
   {
      syslog(LOG_ERR, "invalid usb_open: %m %s %d\n", __FILE__, __LINE__);
      len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);
      goto bugout;
   }

   model[0] = serial[0] = sz[0] = 0;

   if (dev->descriptor.idVendor == 0x3f0)
   {
      /* Found hp device. */
      if (usb_get_string_simple(hd, dev->descriptor.iProduct, sz, sizeof(sz)) < 0)
         syslog(LOG_ERR, "invalid product id string: %m %s %d\n", __FILE__, __LINE__);
      else
         GeneralizeModel(sz, model, sizeof(model));

      if (usb_get_string_simple(hd, dev->descriptor.iSerialNumber, sz, sizeof(sz)) < 0)
         syslog(LOG_ERR, "invalid serial id string: %m %s %d\n", __FILE__, __LINE__);
      else
         GeneralizeSerial(sz, serial, sizeof(serial));

      if (!serial[0])
         strcpy(serial, "0"); /* no serial number, make it zero */
   }
   else
   {
      syslog(LOG_ERR, "invalid vendor id: %d %s %d\n", dev->descriptor.idVendor, __FILE__, __LINE__);
      len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);
      goto bugout;
   }

   if (!model[0] || !serial[0])
   {
      len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);
      goto bugout;
   }

   len = sprintf(sendBuf, "msg=MakeURIResult\nresult-code=%d\ndevice-uri=hp:/usb/%s?serial=%s\n", R_AOK, model, serial); 

bugout:
   if (hd != NULL)
      usb_close(hd);

   return len;
}

#ifdef HAVE_PPORT
//System::MakeUriFromPar
//!  Given a device node read deviceID and create valid URI.
/*!
******************************************************************************/
int System::MakeUriFromPar(char *dnode, char *sendBuf)
{
   const char res[] = "msg=MakeURIResult\nresult-code=%d\n";
   MsgAttributes ma;
   char model[128];
   char dummyBuf[2048];
   char *id;
   int len, result;
   Device *pD=NULL;

   len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);

   if (dnode[0]==0)
   {
      syslog(LOG_ERR, "invalid device node %s System::MakeUriFromPar: %s %d\n", dnode, __FILE__, __LINE__);
      goto bugout;
   }

   ma.prt_mode = RAW_MODE;

   sprintf(ma.uri, "hp:/par/ANY?device=%s", dnode);  /* dnode = /dev/parportx or /dev/udev_name */

   pD = NewDevice(&ma);
   pD->Open(dummyBuf, &result);
   if (result != R_AOK)
   {
      syslog(LOG_ERR, "invalid device node %s System::MakeUriFromPar: %s %d\n", dnode, __FILE__, __LINE__);
      goto bugout;
   }

   id = pD->GetID(); /* use cached copy */

   if (!IsHP(id))
   {
      syslog(LOG_ERR, "invalid device node %s System::MakeUriFromPar: %s %d\n", dnode, __FILE__, __LINE__);
      goto bugout;
   }

   GetModel(id, model, sizeof(model));
   len = sprintf(sendBuf, "msg=MakeURIResult\nresult-code=%d\ndevice-uri=hp:/par/%s?device=%s\n", R_AOK, model, dnode); 

bugout:
   if (pD != NULL)
   {
      pD->Close(dummyBuf, &result);
      DelDevice(pD->GetIndex());
   }

   return len;
}
#else
int System::MakeUriFromPar(char *dnode, char *sendBuf)
{
   const char res[] = "msg=MakeURIResult\nresult-code=%d\n";
   int len;

   len = sprintf(sendBuf, res, R_INVALID_DEVICE_NODE);
   syslog(LOG_ERR, "invalid parallel port is not configured %s System::MakeUriFromPar: %s %d\n", dnode, __FILE__, __LINE__);

   return len;
}
#endif

//System::ParseMsg
//!  Parse and convert all key value pairs in message. Do sanity check on values.
/*!
******************************************************************************/
int System::ParseMsg(char *buf, int len, MsgAttributes *ma)
{
   char key[LINE_SIZE];
   char value[LINE_SIZE];
   char *tail, *tail2;
   int i, ret=R_AOK;

   ma->cmd[0] = 0;
   ma->uri[0] = 0;
   ma->service[0] = 0;
   ma->oid[0] = 0;
   ma->ip[0] = 0;
   ma->dnode[0] = 0;
   ma->bus[0] = 0;
   ma->prt_mode = UNI_MODE;
   ma->mfp_mode = MLC_MODE;
   ma->flow_ctl = GUSHER;
   ma->scan_port = SCAN_PORT0;
   ma->type = PML_DT_UNKNOWN;
   ma->descriptor = -1;
   ma->length = 0;
   ma->channel = -1;
   ma->readlen = 0;
   ma->data = NULL;
   ma->result = -1;
   ma->timeout = EXCEPTION_TIMEOUT;
   ma->ip_port = 1;
   ma->pml_result = -1;
   ma->usb_bus[0] = 0;
   ma->usb_device[0] = 0;

   if (buf == NULL)
      return R_AOK;  /* initialize ma */

   i = GetPair(buf, key, value, &tail);
   if (strcasecmp(key, "msg") != 0)
   {
      syslog(LOG_ERR, "invalid message:%s %s %d\n", key, __FILE__, __LINE__);
      return R_INVALID_MESSAGE;
   }
   strncpy(ma->cmd, value, sizeof(ma->cmd));

   while (i < len)
   {
      i += GetPair(tail, key, value, &tail);

      if (strcasecmp(key, "device-uri") == 0)
      {
         strncpy(ma->uri, value, sizeof(ma->uri));
         if (!ValidURI(ma))
         {
            syslog(LOG_ERR, "invalid uri:%s %s %d\n", ma->uri, __FILE__, __LINE__);
            ret = R_INVALID_URI;
            break;
         }
      }
      else if (strcasecmp(key, "device-id") == 0)
      {
         ma->descriptor = strtol(value, &tail2, 10);
         if (ma->descriptor <= 0 || ma->descriptor >= MAX_DEVICE || pDevice[ma->descriptor] == NULL)
         {
            syslog(LOG_ERR, "invalid device descriptor:%d %s %d\n", ma->descriptor, __FILE__, __LINE__);
            ret = R_INVALID_DESCRIPTOR;
            break;
         }
      }
      else if (strcasecmp(key, "channel-id") == 0)
      {
         ma->channel = strtol(value, &tail2, 10);
         if (ma->channel <= 0 || ma->channel >= MAX_CHANNEL)
         {
            syslog(LOG_ERR, "invalid channel descriptor:%d %s %d\n", ma->channel, __FILE__, __LINE__);
            ret = R_INVALID_CHANNEL_ID;
            break;
         }
      }
      else if (strcasecmp(key, "job-id") == 0)
      {
         ma->jobid = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "timeout") == 0)
      {
         ma->timeout = strtol(value, &tail2, 10);
         if (ma->timeout < 0 || ma->timeout > 120)
         {
            syslog(LOG_ERR, "invalid timeout:%d\n", ma->timeout);
            ret = R_INVALID_TIMEOUT;
            break;
         }
         ma->timeout *= 1000000; /* convert seconds to microseconds */
      }
      else if (strcasecmp(key, "length") == 0)
      {
         ma->length = strtol(value, &tail2, 10);
         if (ma->length > BUFFER_SIZE)
         {
            syslog(LOG_ERR, "invalid data length:%d\n", ma->length);
            ret = R_INVALID_LENGTH;
            break;
         }
      }
      else if (strcasecmp(key, "service-name") == 0)
      {
         strncpy(ma->service, value, sizeof(ma->service));
      }
      else if (strcasecmp(key, "bytes-to-read") == 0)
      {
         ma->readlen = strtol(value, &tail2, 10);
         if (ma->readlen > BUFFER_SIZE)
         {
            syslog(LOG_ERR, "invalid read length:%d\n", ma->readlen);
            ret = R_INVALID_LENGTH;
            break;
         }
      }
      else if (strcasecmp(key, "data:") == 0)
      {
         ma->data = (unsigned char *)tail;
         break;  /* done parsing */
      }
      else if (strcasecmp(key, "io-mode") == 0)
      {
         ma->prt_mode = strtol(value, &tail2, 10);      /* uni | raw | mlc */
      }
      else if (strcasecmp(key, "io-mfp-mode") == 0)
      {
         ma->mfp_mode = strtol(value, &tail2, 10);      /* mfc | dot4 */
      }
      else if (strcasecmp(key, "io-scan-port") == 0)
      {
         ma->scan_port = strtol(value, &tail2, 10);      /* normal | CLJ28xx */
      }
      else if (strcasecmp(key, "result-code") == 0)
      {
         ma->result = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "io-control") == 0)
      {
         ma->flow_ctl = strtol(value, &tail2, 10);     /* gusher | miser */
      }
      else if (strcasecmp(key, "oid") == 0)
      {
         strncpy(ma->oid, value, sizeof(ma->oid));
      }
      else if (strcasecmp(key, "type") == 0)
      {
        //         strncpy(ma->type, value, sizeof(ma->type)); 
         ma->type = strtol(value, &tail2, 10);
      }
      else if (strcasecmp(key, "pml-result-code") == 0)
      {
         ma->pml_result = strtol(value, &tail2, 10);  /* for debug */
      }
      else if (strcasecmp(key, "hostname") == 0)
      {
         strncpy(ma->ip, value, sizeof(ma->ip));
      }
      else if (strcasecmp(key, "bus") == 0)
      {
         strncpy(ma->bus, value, sizeof(ma->bus));
      }
      else if (strcasecmp(key, "usb-bus") == 0)
      {
         strncpy(ma->usb_bus, value, sizeof(ma->usb_bus));
      }
      else if (strcasecmp(key, "usb-dev") == 0)
      {
         strncpy(ma->usb_device, value, sizeof(ma->usb_device));
      }
      else if (strcasecmp(key, "port") == 0)
      {
         ma->ip_port = strtol(value, &tail2, 10);
         if (ma->ip_port < 1 || ma->ip_port > 3)
         {
            syslog(LOG_ERR, "invalid ip port:%d\n", ma->ip_port);
            ret = R_INVALID_IP_PORT;
            break;
         }
      }
      else if (strcasecmp(key, "device-file") == 0)
      {
         strncpy(ma->dnode, value, sizeof(ma->dnode));
      }
      else
      {
         /* Unknown keys are ignored (R_AOK). */
//         syslog(LOG_ERR, "invalid key:%s\n", key);
      }
   }  // end while (i < len)

   return ret;
}

int System::RegisterSession(SessionAttributes *psa)
{
   if (pthread_mutex_lock(&mutex) != 0)
   {
      syslog(LOG_ERR, "unable to lock RegisterSession: %m %s %d\n", __FILE__, __LINE__);
      return 1;
   }

   list_add(&(psa->list), &(head.list));
   pthread_mutex_unlock(&mutex);
   return 0;
}

int System::UnRegisterSession(SessionAttributes *psa)
{
   if (pthread_mutex_lock(&mutex) != 0)
   {
      syslog(LOG_ERR, "unable to lock UnRegisterSession: %m %s %d\n", __FILE__, __LINE__);
      return 1;
   }

   list_del(&(psa->list));
   pthread_mutex_unlock(&mutex);
   return 0;
}

//System::DeviceCleanUp
//!  Client was aborted pre-maturely, close the device.
/*!
******************************************************************************/
int System::DeviceCleanUp(SessionAttributes *psa)
{
   char dummyBuf[255];
   int i, n, dummy;
   Device *pD = pDevice[psa->descriptor];

   for (i=0; i<MAX_CHANNEL; i++)
   {
      if (psa->channel[i])
      {
         syslog(LOG_INFO, "channel cleanup ci=%d\n", i);
         pD->ChannelClose(i, dummyBuf, &dummy);
      }
   }

   syslog(LOG_INFO, "device cleanup uri=%s\n", pD->GetURI());
   pD->Close(dummyBuf, &dummy);
   DelDevice(psa->descriptor);

   /* Check cleanup results. */
   for (i=0, n=0; i<MAX_DEVICE && n<DeviceCnt; i++)
   {
      if (pDevice[i] != NULL)
      {
         n++;
         pD = pDevice[i];
         syslog(LOG_INFO, "device active clientcnt=%d channelcnt=%d uri=%s\n", pD->GetClientCnt(), pD->GetChannelCnt(), pD->GetURI());
      }
   }

   return 0;
}

//System::NewDevice
//!  Create or re-use device object given the URI.
/*!
******************************************************************************/
Device *System::NewDevice(MsgAttributes *ma)
{
   Device *pD=NULL;
   int i, n;

   if (ma->uri[0] == 0)
      return pD;

   if (pthread_mutex_lock(&mutex) != 0)
   {
      syslog(LOG_ERR, "unable to lock NewDevice: %m\n");
      return pD;
   }

   /* Check for existing device object based on uri. */
   for (i=1, n=0; i<MAX_DEVICE && n<DeviceCnt; i++)
   {
      if (pDevice[i] != NULL)
      {
         n++;
	 //         GetURIDataLink(ma->uri, newDL, sizeof(newDL));
	 //         GetURIDataLink(pDevice[i]->GetURI(), oldDL, sizeof(oldDL));
         if (strcmp(ma->uri, pDevice[i]->GetURI()) == 0)
         {
            pD = pDevice[i];   /* same uri */
            pD->SetClientCnt(pD->GetClientCnt()+1);

            /* If existing ProbeDevice/GeneralizeURI set DeviceOpen attributes. */
            if (strncmp(pD->GetURI(), "ANY?", 4) == 0)
            {
               pD->SetPrintMode(ma->prt_mode);            /* io mode for printing */
               pD->SetMfpMode(ma->mfp_mode);              /* io mode for mfp functions */
               pD->SetFlowCtl(ma->flow_ctl);              /* flow control for mfp mode */
               pD->SetScanPort(ma->scan_port);            /* network scan port selection */ 
            }
            goto bugout;
         }
      }
   }

   if (DeviceCnt >= MAX_DEVICE)
      goto bugout;

   /* Look for unused slot in device array. Note, slot 0 is unused. */
   for (i=1; i<MAX_DEVICE; i++)
   {
      if (pDevice[i] == NULL)
      {
         if (strcasestr(ma->uri, ":/usb") != NULL)
         {
            if (ma->prt_mode == UNI_MODE)
            {
               pD = new UniUsbDevice(this);
               pD->SetPrintMode(ma->prt_mode);            /* io mode for printing */
               pD->SetMfpMode(ma->mfp_mode);              /* io mode for mfp functions */
               pD->SetFlowCtl(ma->flow_ctl);              /* flow control for mfp mode */
            }
            else
            {
               pD = new UsbDevice(this);
               pD->SetPrintMode(ma->prt_mode);            /* io mode for printing */
               pD->SetMfpMode(ma->mfp_mode);              /* io mode for mfp functions */
               pD->SetFlowCtl(ma->flow_ctl);              /* flow control for mfp mode */
            }
         }
         else if (strcasestr(ma->uri, ":/net") != NULL)
         {
            pD = new JetDirectDevice(this);
            pD->SetScanPort(ma->scan_port);            /* network scan port selection */ 
         }
#ifdef HAVE_PPORT
         else if (strcasestr(ma->uri, ":/par") !=NULL)
         {
            if (ma->prt_mode == UNI_MODE)
            {
               pD = new UniParDevice(this);
               pD->SetPrintMode(ma->prt_mode);            /* io mode for printing */
               pD->SetMfpMode(ma->mfp_mode);              /* io mode for mfp functions */
               pD->SetFlowCtl(ma->flow_ctl);              /* flow control for mfp mode */
            }
            else
            {
               pD = new ParDevice(this);
               pD->SetPrintMode(ma->prt_mode);            /* io mode for printing */
               pD->SetMfpMode(ma->mfp_mode);              /* io mode for mfp functions */
               pD->SetFlowCtl(ma->flow_ctl);              /* flow control for mfp mode */
            }
         }
#endif
         else
         {
            goto bugout;
         }

         pD->SetIndex(i);
         pD->SetURI(ma->uri);
         pDevice[i] = pD;
         DeviceCnt++;
         break;
      }
   }     

bugout:
   pthread_mutex_unlock(&mutex);

   return pD;
}

//System::DelDevice
//!  Remove device object given the device decriptor.
/*!
******************************************************************************/
int System::DelDevice(int index)
{
   Device *pD = pDevice[index];

   if (pthread_mutex_lock(&mutex) != 0)
      syslog(LOG_ERR, "unable to lock DelDevice: %m\n");

   pD->SetClientCnt(pD->GetClientCnt()-1);

   if (pD->GetClientCnt() <= 0)
   {
      delete pD;
      pDevice[index] = NULL;
      DeviceCnt--;
   }

   pthread_mutex_unlock(&mutex);

   return 0;
}

//System::ExecuteMsg
//!  Process client request. ExecuteMsg is called by different threads.
//!  Two mutexes are used for thread synchronization. There is a System mutex
//!  and Device mutex. Thread access to these objects may cause the thread to
//!  suspend until the object is unlocked. See the following table.
//!
//! <commands>      <possible thread lock suspend>
//!                 <System mutex>  <Device mutex>
//! DeviceOpen        yes              no
//! DeviceClose       yes              no
//! DeviceID          no               no
//! DeviceStatus      no               yes
//! ChannelOpen       no               yes
//! ChannelClose      no               yes
//! ChannelDataOut    no               yes
//! ChannelDataIn     no               yes
//! ProbeDevices      yes              no
//!
//! System suspends are fast and deterministic. Device suspends by nature are not
//! deterministic, but are hardware dependent.
/*!
******************************************************************************/
int System::ExecuteMsg(SessionAttributes *psa, char *recvBuf, int rlen, char *sendBuf, int slen)
{
   int len, ret;
   MsgAttributes ma;
   Device *pD;

   if ((ret = ParseMsg(recvBuf, rlen, &ma)) != R_AOK)
   {
#ifdef HPIOD_DEBUG
      sysdump(recvBuf, rlen);
#endif 
      len = sprintf(sendBuf, ERR_MSG, ret);
      goto bugout;
   }

#ifdef HPIOD_DEBUG
   if (ma.length == 0)
   {
      recvBuf[rlen]=0;
      syslog(LOG_INFO, "tid:%d %s\n", (int)psa->tid, recvBuf);
   }
   else
   {
      syslog(LOG_INFO, "tid:%d %s di=%d ci=%d oid=%s pml_type=%d size=%d\n", (int)psa->tid, ma.cmd, ma.descriptor, ma.channel, ma.oid, ma.type, ma.length);
      if (ma.length < 64)
        sysdump(ma.data, ma.length);
   }
   //   if (ma.descriptor > 0 && pDevice[ma.descriptor])
   //   {
   //      pD = pDevice[ma.descriptor];
   //      syslog(LOG_INFO, "fd=%d clientcnt=%d channelcnt=%d channelmode=%d\n", pD->GetOpenFD(), pD->GetClientCnt(), pD->GetChannelCnt(), pD->GetChannelMode());
   //   } 
#endif

   /* Check for stateless commands first. */
   if (strcasecmp(ma.cmd, "DeviceOpen") == 0)
   {
      if (psa->descriptor != -1)
         len = sprintf(sendBuf, ERR_MSG, R_INVALID_DEVICE_OPEN); /* allow only one DeviceOpen per session */
      else if ((pD = NewDevice(&ma)) == NULL)
         len = sprintf(sendBuf, ERR_MSG, R_INVALID_URI);
      else
      {
         len = pD->Open(sendBuf, &ret);
         if (ret == R_AOK)
            psa->descriptor = pD->GetIndex();  /* track device descriptor for session clean up */     
         else
         {
            /* Open failed perform device cleanup. */
            char dummyBuf[255];               
            int dummy, index = pD->GetIndex();
            pDevice[index]->Close(dummyBuf, &dummy);
            DelDevice(index);
         }
      }
   }
   else if (strcasecmp(ma.cmd, "ProbeDevices") == 0)
   {
      len = ProbeDevices(sendBuf, ma.bus);       
   }
   else if (strcasecmp(ma.cmd, "DeviceFile") == 0)
   {
      len = sprintf(sendBuf, "msg=DeviceFileResult\nresult-code=%d\ndevice-file=%s\n", R_AOK, ma.uri);
   }
   else if (strcasecmp(ma.cmd, "MakeURI") == 0)
   {
      if (ma.ip[0])
         len = MakeUriFromIP(ma.ip, ma.ip_port, sendBuf);
      else if (strcasecmp(ma.bus, "par") == 0) 
         len = MakeUriFromPar(ma.dnode, sendBuf);    
      else if (strcasecmp(ma.bus, "usb") == 0) 
         len = MakeUriFromUsb(ma.usb_bus, ma.usb_device, sendBuf);    
      else 
      {
         syslog(LOG_ERR, "invalid message:%s %s %s %d\n", ma.cmd, ma.dnode, __FILE__, __LINE__);
         len = sprintf(sendBuf, ERR_MSG, R_INVALID_MESSAGE);
         goto bugout;
      }
   }
   else if (strcasecmp(ma.cmd, "PState") == 0)
   {
      len = PState(sendBuf);       
   }
   else
   {
      /* The following commands require a valid device descriptor. */ 
      if (ma.descriptor < 0)
      {
         syslog(LOG_ERR, "invalid device descriptor: %s %d\n", __FILE__, __LINE__);
         sysdump(recvBuf, rlen);
         len = sprintf(sendBuf, ERR_MSG, R_INVALID_MESSAGE);
         goto bugout;
      }

      if (strcasecmp(ma.cmd, "DeviceID") == 0) 
      {
         len = pDevice[ma.descriptor]->GetDeviceID(sendBuf, slen, &ret);
      }
      else if (strcasecmp(ma.cmd, "DeviceStatus") == 0)
      {
         len = pDevice[ma.descriptor]->GetDeviceStatus(sendBuf, &ret);       
      }
      else if (strcasecmp(ma.cmd, "DeviceClose") == 0)
      {
         pD = pDevice[ma.descriptor];
         len = pD->Close(sendBuf, &ret);
         DelDevice(ma.descriptor);
         psa->descriptor = -1;  /*  track device descriptor for session clean up */     
      }
      else if (strcasecmp(ma.cmd, "ChannelOpen") == 0)
      {
         int channel;
         pD = pDevice[ma.descriptor];
         len = pD->ChannelOpen(ma.service, &channel, sendBuf, &ret);
         if (ret == R_AOK)
            psa->channel[channel] = 1;   /* track channel descriptor for session clean up */
      }
      else
      {
         /* The following commands require a valid channel descriptor. */ 
         if (ma.channel < 0 || psa->channel[ma.channel] == 0)
         {
            syslog(LOG_ERR, "invalid channel descriptor: %s %d\n", __FILE__, __LINE__);
            sysdump(recvBuf, rlen);
            len = sprintf(sendBuf, ERR_MSG, R_INVALID_MESSAGE);
            goto bugout;
         }

         if (strcasecmp(ma.cmd, "ChannelDataOut") == 0)
         {
            pD = pDevice[ma.descriptor];
            len = pD->WriteData(ma.data, ma.length, ma.channel, sendBuf, &ret);               
         }
         else if (strcasecmp(ma.cmd, "ChannelDataIn") == 0)
         {
            pD = pDevice[ma.descriptor];
            len = pD->ReadData(ma.readlen, ma.channel, ma.timeout, sendBuf, slen, &ret);       
         }
         else if (strcasecmp(ma.cmd, "SetPML") == 0)
         { 
            len = SetPml(ma.descriptor, ma.channel, ma.oid, ma.type, ma.data, ma.length, sendBuf);       
         }
         else if (strcasecmp(ma.cmd, "GetPML") == 0)
         {
            len = GetPml(ma.descriptor, ma.channel, ma.oid, sendBuf);       
         }
         else if (strcasecmp(ma.cmd, "ChannelClose") == 0)
         {
            pD = pDevice[ma.descriptor];
            len = pD->ChannelClose(ma.channel, sendBuf, &ret);
            psa->channel[ma.channel] = 0;   /* track channel descriptor for session clean up */
         }
         else
         {
            /* Unknown message. */
            syslog(LOG_ERR, "invalid message:%s %s %d\n", ma.cmd, __FILE__, __LINE__);
            len = sprintf(sendBuf, ERR_MSG, R_INVALID_MESSAGE);
         }  /* channel dependent commands */
      }  /* device dependent commands */
   } /* stateless commands */

bugout:

#ifdef HPIOD_DEBUG
   ParseMsg(sendBuf, len, &ma);
   if (ma.length == 0)
   {
      syslog(LOG_INFO, "-tid:%d %s\n", (int)psa->tid, sendBuf);
   }
   else
   {
      syslog(LOG_INFO, "-tid:%d %s di=%d ci=%d result=%d pml_result=%d pml_type=%d size=%d\n", (int)psa->tid, ma.cmd, ma.descriptor, ma.channel, ma.result, ma.pml_result, ma.type, ma.length);
      if (ma.length < 64)
        sysdump(ma.data, ma.length);
   }
#endif

   return len;
}
