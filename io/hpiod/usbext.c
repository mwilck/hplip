/*****************************************************************************\

  usbext.c - low level libusb extensions 
 
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
  Client/Server generic message format (see messaging-protocol.doc):

\*****************************************************************************/

#include "usbext.h"

/* TODO: following code is Linux specific, add conditional compile for different platforms. */ 

/* Following partial structure must match usbi.h in libusb. */
struct usb_dev_handle {
  int fd;
};

#if defined(__APPLE__) && defined(__MACH__)

#else

/* Submit URB to specified endpoint and return. */
int usb_submit_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb)
{
   int ret;

   ret = ioctl(dev->fd, USBDEVFS_SUBMITURB, urb);
   if (ret < 0)
   {
      syslog(LOG_ERR, "error submitting URB: %m %s %d", __FILE__, __LINE__);
      return -errno;
   }

   return 0;
}

/*
 * Wait for URB completion or timeout. Normal completion reaps the URB.
 * Timeout will leave the URB pending.
 */
int usb_wait_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb, int timeout)
{
   struct timeval tv, tv_ref, tv_now;
   fd_set writefds;
   void *context;
   int ret, waiting;

   /* Set timeout, current_time + timeout_in_milliseconds. */
   gettimeofday(&tv_ref, NULL);
   tv_ref.tv_sec = tv_ref.tv_sec + timeout / 1000;
   tv_ref.tv_usec = tv_ref.tv_usec + (timeout % 1000) * 1000;

   if (tv_ref.tv_usec > 1000000)
   {
      tv_ref.tv_usec -= 1000000;
      tv_ref.tv_sec++;
   }

   FD_ZERO(&writefds);
   FD_SET(dev->fd, &writefds);

   waiting = 1;
   while (((ret = ioctl(dev->fd, USBDEVFS_REAPURBNDELAY, &context)) == -1) && waiting) 
   {
      tv.tv_sec = 0;
      tv.tv_usec = 1000; // 1 msec
      select(dev->fd + 1, NULL, &writefds, NULL, &tv); //sub second wait

      /* compare with actual time, as the select timeout is not that precise */
      gettimeofday(&tv_now, NULL);

      if ((tv_now.tv_sec > tv_ref.tv_sec) || ((tv_now.tv_sec == tv_ref.tv_sec) && (tv_now.tv_usec >= tv_ref.tv_usec)))
         waiting = 0;
   }

   if (ret < 0) 
   {
      int rc;

      if (errno != EAGAIN)
      {
         syslog(LOG_ERR, "error reaping URB: %m %s %d", __FILE__, __LINE__);
         return -errno;
      }

      if (!waiting)
         rc = -ETIMEDOUT;
      else
         rc = urb->status;

      return rc;
   }

   if (context != (void *)urb)
   {
      syslog(LOG_ERR, "error wrong URB reaped: exp=%x act=%x %s %d", (int)urb, (int)context, __FILE__, __LINE__);
      return -errno;
   }

   return 0;
}

/* Manually reap pending URB. */
int usb_reap_urb_ex(usb_dev_handle *dev, struct usbdevfs_urb *urb)
{
   void *context;
   int ret;

   ret = ioctl(dev->fd, USBDEVFS_DISCARDURB, urb);
   if (ret < 0)
   {
     //      if (errno != EINVAL)
         syslog(LOG_ERR, "error discarding URB: %m urb=%x %s %d", (int)urb, __FILE__, __LINE__);
      return -errno;
   }

   ioctl(dev->fd, USBDEVFS_REAPURB, &context);
   if (context != (void *)urb)
   {
      syslog(LOG_ERR, "error wrong URB reaped: %s %d", __FILE__, __LINE__);
      return -errno;
   }

   return 0;
}

#endif
