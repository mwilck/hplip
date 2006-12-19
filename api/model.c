/*****************************************************************************\

  model.c - model parser for hplip devices 
 
  (c) 2006 Copyright Hewlett-Packard Development Company, LP

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

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdarg.h>
#include <syslog.h>
#include "list.h"
#include "hplip_api.h"

#define SECTION_SIZE 4096 /* Rough estimate of key/value section size in bytes. */

extern char homedir[];
extern int ReadConfig();

typedef struct
{
  char *name;
  char *incFile; 
  int valueSize;  /* size of list in bytes */
  char *value;    /* list of key/value pairs */
  struct list_head list;
} LabelRecord;

static LabelRecord head;   /* list of labels from include files */

/* Find last occurance of y in x. */
static char *strrstr(const char *x, const char *y) 
{
   char *prev=NULL, *next;

   if (*y == '\0')
      return strchr(x, '\0');

   while ((next = strstr(x, y)) != NULL)
   {
      prev = next;
      x = next + 1;
   }
   return prev;
}

static int CopyLabel(char *label, char *buf, int bufSize)
{
   struct list_head *p;
   LabelRecord *pl;
   int i=0, found=0;

   /* Look for label. */
   list_for_each(p, &head.list)
   {
      pl = list_entry(p, LabelRecord, list);
      if (strcasecmp(pl->name, label) == 0)
      {
         found = 1;    /* found label */
         break;
      }
   }

   if (!found)
   {
      bug("error undefined label %s: %s %d\n", label, __FILE__, __LINE__);
      goto bugout;
   }

   if (pl->valueSize > bufSize)
   {
      bug("error label %s size=%d buf=%d: %s %d\n", label, pl->valueSize, bufSize, __FILE__, __LINE__);
      goto bugout;
   }

   memcpy(buf, pl->value, pl->valueSize);
   i=pl->valueSize;

bugout:
   return i;
}

static int ResolveAttributes(FILE *fp, char *attr, int attrSize)
{
   char label[128];
   int i=0, j, ch;

   /* Process each key/value line. */
   ch = fgetc(fp);
   while (ch != EOF)
   {
      if (ch == '[')
      {
         ungetc(ch, fp);     /* found new section, done with current section */
         break;         
      }

      if (ch == '#' || ch == ' ')
      {
         while ((ch = fgetc(fp)) != '\n' && ch != EOF);  /* skip line */
      }
      else if (ch == '\n')
      {
         /* skip blank line */
      }
      else if (ch == '%')
      {
         j=0;
         while ((ch = fgetc(fp)) != '\n' && ch != EOF)  /* get label */
         {
            if (j < sizeof(label)-1)
               label[j++] = ch;
         }
         label[j-1] = 0;
         i += CopyLabel(label, attr+i, attrSize-i);
      }
      else
      {
         if (i < attrSize-1)
            attr[i++] = ch;
         while ((ch = fgetc(fp)) != '\n' && ch != EOF)  /* get key/value line */
         {
            if (i < attrSize-1)
               attr[i++] = ch;
         }
         if (i < attrSize-1)
            attr[i++] = '\n';
      }

      if (ch == '\n')
         ch = fgetc(fp);   /* bump to next line */
      continue;
   }

   attr[i] = 0;   /* terminate string */

   return i;
}
static int RegisterLabel(FILE *fp, char *incFile, char *label)
{
   struct list_head *p;
   LabelRecord *pl;
   char buf[SECTION_SIZE];
   int i=0, stat=1, ch;

   /* Look for duplicate label. */
   list_for_each(p, &head.list)
   {
      pl = list_entry(p, LabelRecord, list);
      if (strcasecmp(pl->name, label) == 0)
      {
         bug("error duplicate label %s: %s %d\n", label, __FILE__, __LINE__);
         goto bugout;
      }
   }

   if ((pl = (LabelRecord *)malloc(sizeof(LabelRecord))) == NULL)
   {
      bug("unable to creat label record: %m %s %d\n", __FILE__, __LINE__);
      goto bugout;
   }

   pl->incFile = strdup(incFile);
   pl->name = strdup(label);

   /* Process each key/value line. */
   ch = fgetc(fp);
   while (ch != EOF)
   {
      if (ch == '[')
      {
         ungetc(ch, fp);     /* found new section, done with label */
         break;         
      }

      if (ch == '#' || ch == ' ')
      {
         while ((ch = fgetc(fp)) != '\n' && ch != EOF);  /* skip line */
      }
      else if (ch == '\n')
      {
         /* skip blank line */
      }
      else
      {
         if (i < SECTION_SIZE-1)
            buf[i++] = ch;
         while ((ch = fgetc(fp)) != '\n' && ch != EOF)  /* get key/value line */
         {
            if (i < SECTION_SIZE-1)
               buf[i++] = ch;
         }
         if (i < SECTION_SIZE-1)
            buf[i++] = '\n';
      }

      if (ch == '\n')
         ch = fgetc(fp);   /* bump to next line */
      continue;
   }

   buf[i] = 0;   /* terminate string */

   pl->value = strdup(buf);
   pl->valueSize = i;  /* size does not include zero termination */

   list_add(&(pl->list), &(head.list));
   stat = 0;

bugout:

   return stat;
}

static int UnRegisterLabel(LabelRecord *pl)
{
   if (pl->incFile)
      free(pl->incFile);
   if (pl->name)
      free(pl->name);
   if (pl->value)
      free(pl->value);
   list_del(&(pl->list));
   free(pl);
   return 0;
}

static int DelList()
{
   struct list_head *p, *n;
   LabelRecord *pl;
 
   /* Remove each label. */
   list_for_each_safe(p, n, &head.list)
   {
      pl = list_entry(p, LabelRecord, list);
      UnRegisterLabel(pl);
   }
   return 0;
}

/* Parse *.inc file. */
static int ParseInc(char *incFile)
{
   FILE *fp;
   struct list_head *p;
   LabelRecord *pl;
   char rcbuf[255];
   char section[128];
   int stat=1, n;

   /* Look for duplicate include file. */
   list_for_each(p, &head.list)
   {
      pl = list_entry(p, LabelRecord, list);
      if (strcmp(pl->incFile, incFile) == 0)
      {
         bug("error duplicate include file %s: %s %d\n", incFile, __FILE__, __LINE__);
         goto bugout;
      }
   }

   if ((fp = fopen(incFile, "r")) == NULL)
   {
      bug("open %s failed: %m %s %d\n", incFile, __FILE__, __LINE__);
      goto bugout;
   }

   section[0] = 0;

   /* Read the *.inc file, check each line for new label. */
   while ((fgets(rcbuf, sizeof(rcbuf), fp) != NULL))
   {
      if (rcbuf[0] == '[')
      {
         strncpy(section, rcbuf+1, sizeof(section)); /* found new section */
         n = strlen(section);
         section[n-2]=0; /* remove ']' and CR */
         RegisterLabel(fp, incFile, section);
      }
   }

   stat = 0;

bugout:
   if (fp)
      fclose(fp);
   return stat;
}

/* Parse *.dat file. */
static int ParseFile(char *datFile, char *model, char *attr, int attrSize)
{
   FILE *fp;
   char rcbuf[255];
   char section[128];
   char file[128];
   int found=0, n;

   if ((fp = fopen(datFile, "r")) == NULL)
      goto bugout;

   section[0] = 0;

   /* Read the *.dat file, check each line for model match. */
   while ((fgets(rcbuf, sizeof(rcbuf), fp) != NULL))
   {
      if (rcbuf[0] == '[')
      {
         strncpy(section, rcbuf+1, sizeof(section)); /* found new section */
         n = strlen(section);
         section[n-2]=0; /* remove ']' and CR */
         if (strcasecmp(model, section) == 0)
         {
            /* Found model match. */
            ResolveAttributes(fp, attr, attrSize); 
            found = 1; 
            break;
         }
      }
      else if (strncmp(rcbuf, "%include", 8) == 0)
      {
         strncpy(file, datFile, sizeof(file));        /* get dirname from *.dat file */
         n = strrstr(file, "/") - file + 1;
         strncpy(file+n, rcbuf+9, sizeof(file)-n);      /* concatenate include filename to dirname */
         n = strlen(file);
         file[n-1]=0;        /* remove CR */
         ParseInc(file);
      }
   }

bugout:
   if (fp)
      fclose(fp);

   return found;
}

/* Request device model attributes for URI. Return all attributes. */
int hplip_GetModelAttributes(char *uri, char *attr, int attrSize)
{
   char sz[256];
   char model[256];
   int stat=1, found, n;

   memset(attr, 0, attrSize);

   INIT_LIST_HEAD(&head.list);

   if (homedir[0] == 0)    
      ReadConfig();

   hplip_GetURIModel(uri, model, sizeof(model));

   /* Format "msg" for hplip_ParseMsg. */ 
   n = 23;
   if (n < attrSize-1)
      strcpy(attr, "msg=GetModelAttributes\n");

   /* Search /data/models.dat file for specified model. */
   snprintf(sz, sizeof(sz), "%s/data/models/models.dat", homedir);
   found = ParseFile(sz, model, attr+n, attrSize-n);   /* save any labels in *.inc files */

   if (!found)
   {
      DelList();   /* Unregister all labels. */

      /* Search /data/models/unreleased/unreleased.dat file for specified model. */
      snprintf(sz, sizeof(sz), "%s/data/models/unreleased/unreleased.dat", homedir);
      ParseFile(sz, model, attr, attrSize);   /* save any *.inc files */
   }

   if (!found)
   {  
      bug("no %s attributes found in models.dat: %s %d\n", model, __FILE__, __LINE__);  
      goto bugout;
   }  

   stat = 0;

bugout:   
   DelList();  /* Unregister all labels. */
   return stat;
}


