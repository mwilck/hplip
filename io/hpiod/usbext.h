/*****************************************************************************\

  usbext.h - low level libusb extensions
 
  (c) 2005 Copyright Hewlett-Packard Development Company, LP

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

#ifndef _USBEXT_H
#define _USBEXT_H

#include <sys/ioctl.h>
#include <syslog.h>
#include <errno.h>
#include <sys/time.h>
#include <usb.h>

#if defined(__APPLE__) && defined(__MACH__)
#else
#include <linux/usbdevice_fs.h>

#ifdef __cplusplus
extern "C" {
#endif

int usb_submit_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb);
int usb_wait_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb, int timeout);
int usb_reap_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb);

#ifdef __cplusplus
}
#endif

#endif // ! defined(__APPLE__) && defined(__MACH__)

#endif // _USBEXT_H

