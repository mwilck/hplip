/*****************************************************************************\

  device.cpp - base class for devices 
 
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
  Client/Server generic message format (see messaging-protocol.doc):

\*****************************************************************************/

#include "hpiod.h"

const unsigned char Venice_Power_On[] = {0x1b, '%','P','u','i','f','p','.',
        'p','o','w','e','r',' ','1',';',
        'u','d','w','.','q','u','i','t',';',0x1b,'%','-','1','2','3','4','5','X' };

/* Constructor should be called from System::NewDevice which is thread safe. */
Device::Device(System *pS) : pSys(pS)
{
   int i;

   URI[0] = 0;
   ID[0] = 0;
   OpenFD = -1;
   ClientCnt = 1;
   pthread_mutex_init(&mutex, NULL); /* create fast mutex */

   for (i=0; i<MAX_CHANNEL; i++)
      pChannel[i] = NULL;
   ChannelCnt = 0;
   ChannelMode = -1; 
   MlcUp = 0;
   memset(CA, 0, sizeof(CA));
   for (i=0; i<MAX_FD; i++)
   {
      FD[i].pHD = NULL;
      FD[i].urb_write_active = 0;
      FD[i].uindex = 0;
      FD[i].ucnt = 0;
   }

   memset(FD, 0, sizeof(FD));

   dev = NULL;
}

/* Destructor should be called from System::DelDevice which is thread safe. */
Device::~Device()
{
   int i;

   for (i=0; i<MAX_CHANNEL; i++)
      if (pChannel[i] != NULL)
         delete pChannel[i];

   pthread_mutex_destroy(&mutex);
}

int Device::CutBuf(int fd, void *buf, int size)
{
   int len;

   if (FD[fd].ucnt > size)
   {
      /* Return part of ubuf. */
      len = size;
      memcpy(buf, &FD[fd].ubuf[FD[fd].uindex], len);
      FD[fd].uindex += len;
      FD[fd].ucnt -= len;
   }
   else
   {
      /* Return all of ubuf. */
      len = FD[fd].ucnt;
      memcpy(buf, &FD[fd].ubuf[FD[fd].uindex], len);
      FD[fd].uindex = FD[fd].ucnt = 0;
   }

   return len;
} 

#if defined(__APPLE__) && defined(__MACH__)

int Device::Write(int fd, const void *buf, int size)
{
   syslog(LOG_ERR, "error Write: unimplemented (osx) %s %s %d\n", URI, __FILE__, __LINE__);
   return -1;
}

int Device::Read(int fd, void *buf, int size, int usec)
{
   syslog(LOG_ERR, "error Read: unimplemented (osx) %s %s %d\n", URI, __FILE__, __LINE__);
   return -2;
}

#else

/*
 * We use low level usb_submit_urb() for writing. Because usb_bulk_write() does not return actual bytes written during 
 * timeout conditions (ie: paperout). The low level URB APIs usb_submit_urb(), usb_wait_urb(), and usb_reap_urb() allow
 * us to recover from a timeout without losing bytes during the print job. David Suffield 12/15/2005
 */
int Device::Write(int fd, const void *buf, int size)
{
   int len=0, r, ep;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::Write state: %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   if ((ep = GetOutEP(dev, FD[fd].Config, FD[fd].Interface, FD[fd].AltSetting, USB_ENDPOINT_TYPE_BULK)) < 0)
   {
      syslog(LOG_ERR, "invalid bulk out endpoint %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   if (!FD[fd].urb_write_active)
   {
      FD[fd].urb_write.type = USBDEVFS_URB_TYPE_BULK;
      FD[fd].urb_write.endpoint = ep;
      FD[fd].urb_write.flags = 0;
      FD[fd].urb_write.buffer = (void *)buf;
      FD[fd].urb_write.buffer_length = size;
      FD[fd].urb_write.usercontext = (void *)ep;
      FD[fd].urb_write.signr = 0;
      FD[fd].urb_write.actual_length = 0;
      FD[fd].urb_write.number_of_packets = 0;
         
      if (usb_submit_urb_ex(FD[fd].pHD, &FD[fd].urb_write))
      {
         syslog(LOG_ERR, "invalid submit_urb %s: %m %s %d\n", URI, __FILE__, __LINE__);
         goto bugout;
      }
      FD[fd].urb_write_active = 1;
   }

   r = usb_wait_urb_ex(FD[fd].pHD, &FD[fd].urb_write, LIBUSB_TIMEOUT);
   if (r == -ETIMEDOUT)
   {
      len = -ETIMEDOUT;
      goto bugout;              /* leave urb pending for retry later */
   }
   if (r < 0)
   {
      len = r;
      syslog(LOG_ERR, "invalid urb write completion %s: %m %s %d\n", URI, __FILE__, __LINE__);
      usb_reap_urb_ex(FD[fd].pHD, &FD[fd].urb_write);
      FD[fd].urb_write_active = 0;
      goto bugout;
   }

   FD[fd].urb_write_active = 0;
   len = FD[fd].urb_write.actual_length;

bugout:
   return len;
}

int Device::Read(int fd, void *buf, int size, int usec)
{
   struct timeval t1, t2;
   int len=0, ep;
   int r, total_usec, tmo_usec=usec;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::Read state: %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   if (FD[fd].ucnt)
      return CutBuf(fd, buf, size);

   gettimeofday (&t1, NULL);     /* get start time */

   if ((ep = GetInEP(dev, FD[fd].Config, FD[fd].Interface, FD[fd].AltSetting, USB_ENDPOINT_TYPE_BULK)) < 0)
   {
      syslog(LOG_ERR, "invalid bulk in endpoint %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   while(1)
   {
      FD[fd].urb_read.type = USBDEVFS_URB_TYPE_BULK;
      FD[fd].urb_read.endpoint = ep;
      FD[fd].urb_read.flags = 0;
      FD[fd].urb_read.buffer = (void *)FD[fd].ubuf;       /* allow room for full usb packet */
      FD[fd].urb_read.buffer_length = sizeof(FD[fd].ubuf);
      FD[fd].urb_read.usercontext = (void *)ep;
      FD[fd].urb_read.signr = 0;
      FD[fd].urb_read.actual_length = 0;
      FD[fd].urb_read.number_of_packets = 0;
         
      if (usb_submit_urb_ex(FD[fd].pHD, &FD[fd].urb_read))
      {
         syslog(LOG_ERR, "invalid submit_urb %s: %m %s %d\n", URI, __FILE__, __LINE__);
         goto bugout;
      }

      r = usb_wait_urb_ex(FD[fd].pHD, &FD[fd].urb_read, tmo_usec/1000);
      if (r == -ETIMEDOUT)
      {
         len = -1;
         usb_reap_urb_ex(FD[fd].pHD, &FD[fd].urb_read);  /* remove urb */
         goto bugout;
      }
      if (r < 0)
      {
         len = -2;
         syslog(LOG_ERR, "invalid urb read completion %s: %m %s %d\n", URI, __FILE__, __LINE__);
         usb_reap_urb_ex(FD[fd].pHD, &FD[fd].urb_read);
         goto bugout;
      }

      if ((FD[fd].ucnt = FD[fd].urb_read.actual_length) == 0)
      {
         /* Bulk_read has a timeout, but bulk_read can return zero byte packet(s), so we must use our own timeout here. */
         gettimeofday(&t2, NULL);   /* get current time */

         total_usec = (t2.tv_sec - t1.tv_sec)*1000000;
         total_usec += (t2.tv_usec > t1.tv_usec) ? t2.tv_usec - t1.tv_usec : t1.tv_usec - t2.tv_usec;
         if (total_usec > usec)
         {
            len = -1;   /* timeout */
            break;
         }
         tmo_usec = usec - total_usec;    /* decrease timeout */
         continue;
      }
      len = CutBuf(fd, buf, size);
      break;
   }

bugout:
   return len;
}

#endif

/* Write HP vendor-specific ECP channel message. */
int Device::WriteECPChannel(int fd, int value)
{
   usb_dev_handle *hd;
   int interface = FD[fd].Interface;
   int len, stat=1;
   char byte;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::WriteECPChannel state: %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[fd].pHD;

   len = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_VENDOR | USB_RECIP_INTERFACE, /* bmRequestType */
             USB_REQ_GET_STATUS,        /* bRequest */
             htole16(value),        /* wValue */
             htole16(interface), /* wIndex */
             &byte, 1, LIBUSB_CONTROL_REQ_TIMEOUT);

   if (len != 1)
   {
      syslog(LOG_ERR, "invalid Device::WriteECPChannel %s: %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   stat = 0;

bugout:
   return stat;
}

/* Set Cypress USS-725 Bridge Chip to 1284.4 mode. */
int Device::BridgeChipUp(int fd)
{
   usb_dev_handle *hd;
   int len, stat=1;
   char buf[9];
   char nullByte=0;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::BridgeChipUp state: %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[fd].pHD;

   memset(buf, 0, sizeof(buf));

   /* Read register values. */
   len = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             USB_REQ_SET_FEATURE,        /* bRequest */
             0,        /* wValue */
             0, /* wIndex */
             buf, sizeof(buf), LIBUSB_CONTROL_REQ_TIMEOUT);
   if (len < 0)
   {
      syslog(LOG_ERR, "invalid Device::WriteBridgeUp %s: %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   /* Check for auto ECP mode. */
   if (buf[ECRR] != 0x43)
   {
      /* Place 725 chip in register mode. */
      len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x0758),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
      /* Turn off RLE in auto ECP mode. */
      len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x0a1d),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
      /* Place 725 chip in auto ECP mode. */
      len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x0759),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
      /* Force negotiation. */
      len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x0817),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
      /* Read register values. */
      len = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             USB_REQ_SET_FEATURE,        /* bRequest */
             0,        /* wValue */
             0, /* wIndex */
             buf, sizeof(buf), LIBUSB_CONTROL_REQ_TIMEOUT);
      if (buf[ECRR] != 0x43)
      {
         syslog(LOG_ERR, "invalid auto ecp mode Device::WriteBridgeUp %s: %s %d\n", URI, __FILE__, __LINE__);
      }
   }

   /* Reset to ECP channel 0. */
   len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x05ce),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
   Write(fd, &nullByte, 1);

   /* Switch to ECP channel 77. */
   len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x05cd),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);

   stat = 0;

bugout:
   return stat;
}

/* Set Cypress USS-725 Bridge Chip to compatibility mode. */
int Device::BridgeChipDown(int fd)
{
   usb_dev_handle *hd;
   int len, stat=1;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::BridgeChipDown state: %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[fd].pHD;

   len = usb_control_msg(hd, 
             USB_ENDPOINT_OUT | USB_TYPE_VENDOR | USB_RECIP_DEVICE, /* bmRequestType */
             0x04,        /* bRequest */
             htole16(0x080f),        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);
   if (len < 0)
   {
      syslog(LOG_ERR, "invalid Device::WriteBridgeUp %s: %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   stat = 0;

bugout:
   return stat;
}

/* Write HP vendor-specific Setup command. */
int Device::WritePhoenixSetup(int fd)
{
   usb_dev_handle *hd;
   int len, stat=1;

   if (FD[fd].pHD == NULL)
   {
      syslog(LOG_ERR, "invalid Device::WritePhoenixSetup state: %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[fd].pHD;

   len = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_CLASS | USB_RECIP_OTHER, /* bmRequestType */
             0x02,        /* bRequest */
             0,        /* wValue */
             0, /* wIndex */
             NULL, 0, LIBUSB_CONTROL_REQ_TIMEOUT);

   if (len < 0)
   {
      syslog(LOG_ERR, "invalid Device::WritePhoenixSetup %s: %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   stat = 0;

bugout:
   return stat;
}

/* Detach any kernel module that may have claimed specified inteface. */
int Device::Detach(usb_dev_handle *hd, int interface)
{
   char driver[32];

   driver[0] = 0;

#ifdef LIBUSB_HAS_DETACH_KERNEL_DRIVER_NP
   /* If any kernel module (ie:usblp) has claimed this interface, detach it. */
   usb_get_driver_np(hd, interface, driver, sizeof(driver));
   if ((driver[0] != 0) && (strcasecmp(driver, "usbfs") != 0))
   {
      syslog(LOG_INFO, "removing %s driver interface=%d for %s %s %d\n", driver, interface, URI, __FILE__, __LINE__); 
      if (usb_detach_kernel_driver_np(hd, interface) < 0)
         syslog(LOG_ERR, "could not remove %s driver %s %d\n", driver,__FILE__, __LINE__);
   }
#endif

   return 0;
}

/* Get interface descriptor for specified xx/xx/xx protocol. */
int Device::GetInterface(int dclass, int subclass, int protocol, int *config, int *interface, int *altset)
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
            if (pi->bInterfaceClass == dclass && pi->bInterfaceSubClass == subclass && pi->bInterfaceProtocol == protocol)
            {
               *config=i;            /* found interface */
               *interface=j;
               *altset=k;
               return 0;
            }
         }
      }
   }
   return 1;    /* no interface found */
}

/* Get out endpoint for specified interface descriptor. */
int Device::GetOutEP(struct usb_device *dev, int config, int interface, int altset, int type)
{
   struct usb_interface_descriptor *pi;
   int i;

   pi = &dev->config[config].interface[interface].altsetting[altset];
   for (i=0; i<pi->bNumEndpoints; i++)
   {
      if (pi->endpoint[i].bmAttributes == type && !(pi->endpoint[i].bEndpointAddress & USB_ENDPOINT_DIR_MASK))
         return pi->endpoint[i].bEndpointAddress;
   }
   return -1;
}

/* Get in endpoint for specified interface descriptor. */
int Device::GetInEP(struct usb_device *dev, int config, int interface, int altset, int type)
{
   struct usb_interface_descriptor *pi;
   int i;

   pi = &dev->config[config].interface[interface].altsetting[altset];
   for (i=0; i<pi->bNumEndpoints; i++)
   {
      if (pi->endpoint[i].bmAttributes == type && (pi->endpoint[i].bEndpointAddress & USB_ENDPOINT_DIR_MASK))
         return pi->endpoint[i].bEndpointAddress;
   }
   return -1;
}

int Device::ClaimInterface(int fd, int config, int interface, int altset)
{
   int stat=1;

   if (FD[fd].pHD != NULL)
   {
      syslog(LOG_ERR, "invalid Device::ClaimInterface, device already claimed %s: %m %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   FD[fd].Config = config;
   FD[fd].Interface = interface;
   FD[fd].AltSetting = altset;

   if ((FD[fd].pHD = usb_open(dev)) == NULL)
   {
      syslog(LOG_ERR, "invalid usb_open %s: %m %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   Detach(FD[fd].pHD, FD[fd].Interface);

#if 0   /* hp devices only have one configuration, so far ... */
   if (usb_set_configuration(FD[fd].pHD, dev->config[config].bConfigurationValue))
   {
      syslog(LOG_ERR, "invalid set_configuration %s: %m %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }
#endif

   if (usb_claim_interface(FD[fd].pHD, FD[fd].Interface))
   {
      syslog(LOG_ERR, "invalid claim_interface %s: %m %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   if (usb_set_altinterface(FD[fd].pHD, FD[fd].AltSetting))
   {
      syslog(LOG_ERR, "invalid set_altinterface %s: %m %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

#ifdef HPIOD_DEBUG
   syslog(LOG_INFO, "claimed %s interface config=%d interface=%d altset=%d\n", fd == FD_7_1_2 ? "7/1/2" : fd == FD_7_1_3 ? "7/1/3" : "ff/1/1", config, interface, altset);
#endif

   stat=0;

bugout:
   return stat;   
}

int Device::ReleaseInterface(int fd)
{
   if (FD[fd].pHD == NULL)
      return 0;

   if (FD[fd].urb_write_active)
   {
#if defined(__APPLE__) && defined(__MACH__)
#else
      usb_reap_urb_ex(FD[fd].pHD, &FD[fd].urb_write);
#endif
   }
   usb_release_interface(FD[fd].pHD, FD[fd].Interface);
   usb_close(FD[fd].pHD);
   FD[fd].pHD = NULL;

#ifdef HPIOD_DEBUG
   syslog(LOG_INFO, "released %s interface\n", fd == FD_7_1_2 ? "7/1/2" : fd == FD_7_1_3 ? "7/1/3" : "ff/1/1");
#endif

   return 0;
}

/* See if this usb device and URI match. */
int Device::IsUri(struct usb_device *dev, char *uri)
{
   usb_dev_handle *hd=NULL;
   char sz[128];
   char uriModel[128];
   char uriSerial[128];
   char gen[128];
   int stat=0;

   if ((hd = usb_open(dev)) == NULL)
   {
      syslog(LOG_ERR, "invalid usb_open: %m %s %d\n", __FILE__, __LINE__);
      goto bugout;
   }

   if (dev->descriptor.idVendor != 0x3f0)
      goto bugout;

   if (usb_get_string_simple(hd, dev->descriptor.iProduct, sz, sizeof(sz)) < 0)
   {
      syslog(LOG_ERR, "invalid product id string: %m %s %d\n", __FILE__, __LINE__);
      goto bugout;
   }

   pSys->GeneralizeModel(sz, gen, sizeof(gen));

   pSys->GetURIModel(uri, uriModel, sizeof(uriModel));
   if (strcmp(uriModel, gen) != 0)
      goto bugout;

   if (usb_get_string_simple(hd, dev->descriptor.iSerialNumber, sz, sizeof(sz)) < 0)
   {
      syslog(LOG_ERR, "invalid serial id string: %m %s %d\n", __FILE__, __LINE__);
      goto bugout;
   }

   if (sz[0])
      pSys->GeneralizeSerial(sz, gen, sizeof(gen));
   else
      strcpy(gen, "0");

   pSys->GetURISerial(uri, uriSerial, sizeof(uriSerial));
   if (strcmp(uriSerial, gen) != 0)
      goto bugout;

   stat = 1;    /* found usb device that matches uri */
     
bugout:
   if (hd != NULL)
      usb_close(hd);

   return stat;
}

struct usb_device * Device::GetDevice(char *uri)
{
   struct usb_bus *bus;
   struct usb_device *dev;

   for (bus=usb_busses; bus; bus=bus->next)
      for (dev=bus->devices; dev; dev=dev->next)
         if (IsUri(dev, uri))
            return dev;  /* found usb device that matches uri */

   return NULL;
}

int Device::DeviceID(char *buffer, int size)
{
   usb_dev_handle *hd;
   int interface;
   int len=0, rlen, maxSize;

   if (OpenFD < 0)
   {
      syslog(LOG_ERR, "invalid Device::DeviceID state: %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[OpenFD].pHD;
   interface = FD[OpenFD].Interface;

   if (hd == NULL)
   {
      syslog(LOG_ERR, "invalid Device::DeviceID state: %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   maxSize = (size > 1024) ? 1024 : size;   /* RH8 has a size limit for device id (usb) */

   /* Note, USB multibyte data fields are little-endian order, wValue and wIndex need conversion. */

   rlen = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_CLASS | USB_RECIP_INTERFACE, /* bmRequestType */
             USB_REQ_GET_STATUS,        /* bRequest */
             htole16(0),        /* wValue */
             htole16(interface), /* wIndex */
             buffer, maxSize, LIBUSB_CONTROL_REQ_TIMEOUT);

   if (rlen < 0)
   {
      syslog(LOG_ERR, "invalid Device::DeviceID: %m %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   len = ntohs(*(short *)buffer);
   if (len > (size-1))
      len = size-1;   /* leave byte for zero termination */
   if (len > 2)
      len -= 2;
   memcpy(buffer, buffer+2, len);    /* remove length */
   buffer[len]=0;

bugout:
   return len; /* length does not include zero termination */
}

int Device::DeviceStatus(unsigned int *status)
{
   usb_dev_handle *hd;
   int interface;
   int len, stat=1;
   char byte;

   if (OpenFD < 0)
   {
      syslog(LOG_ERR, "invalid Device::DeviceStatus state: %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   hd = FD[OpenFD].pHD;
   interface = FD[OpenFD].Interface;

   if (hd == NULL)
   {
      syslog(LOG_ERR, "invalid Device::DeviceStatus state: %s %s %d\n", URI,__FILE__, __LINE__);
      goto bugout;
   }

   len = usb_control_msg(hd, 
             USB_ENDPOINT_IN | USB_TYPE_CLASS | USB_RECIP_INTERFACE, /* bmRequestType */
             USB_REQ_CLEAR_FEATURE,        /* bRequest */
             htole16(0),        /* wValue */
             htole16(interface), /* wIndex */
             &byte, 1, LIBUSB_CONTROL_REQ_TIMEOUT);

   if (len < 0)
   {
      syslog(LOG_ERR, "invalid Device::DeviceStatus: %m %s %s %d\n", URI, __FILE__, __LINE__);
      goto bugout;
   }

   *status = (int)byte;
   stat = 0;

bugout:
   return stat; 
}

/* Get VStatus from S-field. */
int Device::SFieldPrinterState(char *id)
{
   char *pSf;
   int vstatus=0, ver;

   if ((pSf = strstr(id, ";S:")) == NULL)
   {
      syslog(LOG_ERR, "invalid S-field %s %s %d\n", URI, __FILE__, __LINE__);
      return vstatus;
   }

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
         syslog(LOG_ERR, "unknown S-field version=%d %s %s %d\n", ver, URI, __FILE__, __LINE__);
         pSf+=12;
         break;            
   }

   /* Extract VStatus.*/
   vstatus = 0; 
   HEX2INT(*pSf, vstatus);
   pSf++;
   vstatus = vstatus << 4;
   HEX2INT(*pSf, vstatus);

   return vstatus;
}

/* Power up printer if necessary. Most all-in-ones have no power down state (ie: OJ K80), so they are already powered up. */
int Device::PowerUp()
{
   char *pSf;

   if ((pSf = strstr(ID, "CMD:LDL")) != NULL)
     return 0;   /* crossbow don't do power-up */

   if ((pSf = strstr(ID, ";S:")) != NULL)
   {
      if (SFieldPrinterState(ID) != 3)
         return 0;     /* already powered up */
   }
   else if ((pSf = strstr(ID, "VSTATUS:")) != NULL)
   {
      if ((pSf = strstr(pSf+8, "OFFF")) == NULL)
         return 0;   /* already powered up */
   }
   else
      return 0;  /* must be laserjet, don't do power-up */

   /* Assume raw write is available. */
   Write(OpenFD, Venice_Power_On, sizeof(Venice_Power_On));   
   sleep(2);

   return 0;
}

int Device::Open(char *sendBuf, int *result)
{
   char uriModel[128];
   char model[128];
   int len=0;
   int config, interface, altset;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is already open. */ 

   //   if (ClientCnt==1)   (with threads ClientCnt can be > 1 && ID[0] == 0)
   if (ID[0] == 0)
   {
      /* First client, open actual device. */

      usb_find_busses();
      usb_find_devices();

      /* Find usb device for specified uri. */
      if ((dev = GetDevice(URI)) == NULL)
      {
         syslog(LOG_ERR, "unable to Device::Open %s %s %d\n", URI, __FILE__, __LINE__);
         *result = R_IO_ERROR;
         goto blackout;
      }
     
      /* Find usb interface for deviceid, status. */
      if (GetInterface(7, 1, 2, &config, &interface, &altset) == 0)
         OpenFD = FD_7_1_2;    /* raw, mlc, dot4 */
      else if (GetInterface(7, 1, 3, &config, &interface, &altset) == 0)
         OpenFD = FD_7_1_3;    /* mlc, dot4 */
      else
      {
         syslog(LOG_ERR, "invalid interface %s %s %d\n", URI, __FILE__, __LINE__);
         *result = R_IO_ERROR;
         goto blackout;
      }

      if (ClaimInterface(OpenFD, config, interface, altset))
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

      if (pSys->IsHP(ID))
         PowerUp();
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

   /* Make sure uri model still matches device id model. */
   pSys->GetURIModel(URI, uriModel, sizeof(uriModel));
   pSys->GetModel(ID, model, sizeof(model));
   if (strcmp(uriModel, model) != 0)
   {
      *result = R_INVALID_DEVICE_NODE;  /* found different device plugged in */  
      syslog(LOG_ERR, "invalid model %s != %s Device::Open %s %d\n", uriModel, model, __FILE__, __LINE__);
      goto blackout;
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

int Device::Close(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceCloseResult\nresult-code=%d\n";
   int len=0, i;

   *result = R_AOK;

   if (pthread_mutex_trylock(&mutex) != 0)
      goto bugout;   /* device is still in use */

   if (ClientCnt==1)
   {
      for (i=0; i<MAX_FD; i++)
      {
         if (FD[i].pHD != NULL)
            ReleaseInterface(i);
      }

      /* Reset variables here while locked, don't count on constructor with threads. */
      OpenFD = -1; 
      ID[0] = 0;
   }

   pthread_mutex_unlock(&mutex);

bugout:
   len = sprintf(sendBuf, res, *result);  

   return len;
}

int Device::GetDeviceID(char *sendBuf, int slen, int *result)
{
   const char res[] = "msg=DeviceIDResult\nresult-code=%d\n";
   int len=0, idLen;

   *result = R_AOK;

   if (pthread_mutex_lock(&mutex) == 0)
   {
      if (GetChannelMode() == DOT4_BRIDGE_MODE)
         idLen = strlen(ID);  /* usb/parallel bridge chip, use cached copy */
      else
         idLen = DeviceID(ID, sizeof(ID));  /* get new copy */
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
      syslog(LOG_ERR, "unable to lock Device::GetDeviceID: %m %s %s %d\n", URI, __FILE__, __LINE__);
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto hijmp;
   }

   if ((idLen + HEADER_SIZE) > slen)
   {
      syslog(LOG_ERR, "invalid device id size Device::GetDeviceID: %d %s %s %d\n", idLen, URI, __FILE__, __LINE__);
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

int Device::GetDeviceStatus(char *sendBuf, int *result)
{
   const char res[] = "msg=DeviceStatusResult\nresult-code=%d\nstatus-code=%d\nstatus-name=%s\n";
   const char eres[] = "msg=DeviceStatusResult\nresult-code=%d\n";
   int len=0, r=0;
   unsigned int status;
   char vstatus[16];

   *result = R_AOK;

   if (pthread_mutex_lock(&mutex) == 0)
   {
      if (GetChannelMode() == DOT4_BRIDGE_MODE)
         status = NFAULT_BIT;   /* usb/parallel bridge chip, fake status */
      else
         r = DeviceStatus(&status);
      pthread_mutex_unlock(&mutex);

      if (r != 0)
      {
         syslog(LOG_ERR, "unable to read Device::GetDeviceStatus: %m %s %s %d\n", URI, __FILE__, __LINE__);
         *result = R_IO_ERROR;
         len = sprintf(sendBuf, eres, *result);  
         goto bugout;
      }
   }
   else
   {
      syslog(LOG_ERR, "unable to lock Device::GetDeviceStatus: %m %s %s %d\n", URI, __FILE__, __LINE__);
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

int Device::WriteData(unsigned char *data, int length, int channel, char *sendBuf, int *result)
{   
   const char res[] = "msg=ChannelDataOutResult\nresult-code=%d\n";
   int sLen;

   if (pChannel[channel] == NULL)
   {
      syslog(LOG_ERR, "invalid channel descriptor Device::WriteData: %d %s %s %d\n", channel, URI, __FILE__, __LINE__);
      *result = R_INVALID_CHANNEL_ID;
      sLen = sprintf(sendBuf, res, *result);  
      goto wjmp;
   }

   if (pthread_mutex_lock(&mutex) == 0)
   {
      sLen = pChannel[channel]->WriteData(data, length, sendBuf, result);
      pthread_mutex_unlock(&mutex);
   }
   else
   {
      syslog(LOG_ERR, "unable to lock Device::WriteData: %m %s %s %d\n", URI, __FILE__, __LINE__);
      *result = R_IO_ERROR;
      sLen = sprintf(sendBuf, res, *result);  
      goto wjmp;
   }

wjmp:
   return sLen;
}

int Device::ReadData(int length, int channel, int timeout, char *sendBuf, int slen, int *result)
{   
   const char res[] = "msg=ChannelDataInResult\nresult-code=%d\n";
   int sLen;

   if (pChannel[channel] == NULL)
   {
      syslog(LOG_ERR, "invalid channel descriptor Device::ReadData: %d %s %s %d\n", channel, URI, __FILE__, __LINE__);
      *result = R_INVALID_CHANNEL_ID;
      sLen = sprintf(sendBuf, res, *result);  
      goto rjmp;
   }

   if (pthread_mutex_lock(&mutex) == 0)
   {
      sLen = pChannel[channel]->ReadData(length, timeout, sendBuf, slen, result);
      pthread_mutex_unlock(&mutex);
   }
   else
   {
      syslog(LOG_ERR, "unable to lock Device::ReadData: %m %s %s %d\n", URI, __FILE__, __LINE__);
      *result = R_IO_ERROR;
      sLen = sprintf(sendBuf, res, *result);  
      goto rjmp;
   }

rjmp:
   return sLen;
}

//Device::NewChannel
//!  Create channel object given the requested socket id and service name.
/*!
******************************************************************************/
Channel *Device::NewChannel(unsigned char sockid, char *sn)
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
	 if (sockid == EWS_CHANNEL)
            pC = new CompChannel(this);
         else if (mode == RAW_MODE)
            pC = new RawChannel(this);  /* constructor sets ClientCnt=1 */
         else if (mode == MLC_MODE)
            pC = new MlcChannel(this);  /* constructor sets ClientCnt=1 */
         else 
            pC = new Dot4Channel(this);  /* constructor sets ClientCnt=1 */

         pC->SetIndex(i);
         pC->SetSocketID(sockid);   /* static socket id is valid for MLC but not 1284.4 */
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

//Device::DelChannel
//!  Remove channel object given the channel decriptor.
/*!
******************************************************************************/
int Device::DelChannel(int chan)
{
   Channel *pC = pChannel[chan];

   pC->SetClientCnt(pC->GetClientCnt()-1);
   if (pC->GetClientCnt() <= 0)
   {
      delete pC;
      pChannel[chan] = NULL;
      ChannelCnt--;
   }
   return 0;
}

int Device::ChannelOpen(char *sn, int *channel, char *sendBuf, int *result)
{
   const char res[] = "msg=ChannelOpenResult\nresult-code=%d\n";
   Channel *pC;
   int len=0;
   unsigned char sockid;

   if (strncasecmp(sn, "print", 5) == 0)
   {
      sockid = PRINT_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-message", 10) == 0)
   {
      sockid = PML_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-scan", 7) == 0)
   {
      sockid = SCAN_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-fax-send", 11) == 0)
   {
      sockid = FAX_SEND_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-card-access", 14) == 0)
   {
      sockid = MEMORY_CARD_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-configuration-upload", 23) == 0)
   {
      sockid = CONFIG_UPLOAD_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-configuration-download", 25) == 0)
   {
      sockid = CONFIG_DOWNLOAD_CHANNEL;
   }
   else if (strncasecmp(sn, "hp-ews", 6) == 0)
   {
      sockid = EWS_CHANNEL;
   }
   else if (strncasecmp(sn, "echo", 4) == 0)
   {
      sockid = ECHO_CHANNEL;
   }
   else
   {
      syslog(LOG_ERR, "unsupported service uri:%s Device::ChannelOpen: %s %s %d\n", URI, sn, __FILE__, __LINE__);
      len = sprintf(sendBuf, res, R_INVALID_SN);
      goto bugout;
   }

   //   if (pthread_mutex_trylock(&mutex) == 0)
   if (pthread_mutex_lock(&mutex) == 0)
   {
      if ((pC = NewChannel(sockid, sn)) == NULL)
      {
         syslog(LOG_ERR, "service busy uri:%s Device::ChannelOpen: %s %s %d\n", URI, sn, __FILE__, __LINE__);
         *result = R_CHANNEL_BUSY;
         len = sprintf(sendBuf, res, *result);
      }
      else
      {
         len = pC->Open(sendBuf, result);  
         *channel = pC->GetIndex();
         if (*result != R_AOK)
         {
            len = pChannel[*channel]->Close(sendBuf, result);  
            DelChannel(*channel);
            *result = R_IO_ERROR;
            len = sprintf(sendBuf, res, *result);  
         }
      }
      pthread_mutex_unlock(&mutex);
   }
   else
   {
      syslog(LOG_ERR, "unable to lock uri:%s Device::ChannelOpen: %m %s %d\n", URI, __FILE__, __LINE__);
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

bugout:
   return len;
}

int Device::ChannelClose(int channel, char *sendBuf, int *result)
{
   Channel *pC = pChannel[channel];
   const char res[] = "msg=ChannelCloseResult\nresult-code=%d\n";
   int len=0;

   if (pC == NULL)
   {
      syslog(LOG_ERR, "invalid channel descriptor uri:%s Device::ChannelClose: %d %s %d\n", URI, channel, __FILE__, __LINE__);
      *result = R_INVALID_CHANNEL_ID;
      len = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

   //   if (pthread_mutex_trylock(&mutex) == 0)
   if (pthread_mutex_lock(&mutex) == 0)
   {
      if (pC->GetClientCnt()==1)
      {
         len = pC->Close(sendBuf, result);  
      }
      else
      {
         *result = R_AOK;
         len = sprintf(sendBuf, res, *result);  
      }
      DelChannel(channel);
      pthread_mutex_unlock(&mutex);
   }
   else
   {
      syslog(LOG_ERR, "unable to lock uri:%s Device::ChannelClose: %m %s %d\n", URI, __FILE__, __LINE__);
      *result = R_IO_ERROR;
      len = sprintf(sendBuf, res, *result);  
      goto bugout;
   }

bugout:
   return len;
}

